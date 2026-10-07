"""Witness registry loader: doc/agenda.org #phase0/witness-registry.

Every script that reads a witness goes through here; none names a
witness path. The registry (data/globe/witnesses.toml) says where each
witness's scans and OCR layers are and how their filenames are formed;
each witness's leaf table (data/globe/leaves-*.tsv) says which printed page
each leaf is.

The loader validates on load and refuses to run on a mismatch, naming
what is wrong: a registry that points at the wrong place and runs
anyway is the failure this module exists to prevent. Loading a witness
checks that every path exists, that the scans, each OCR layer and the
leaf table agree, and that every leaf has a scan and an OCR file.

Standard library only (tomllib).
"""

from __future__ import annotations

import csv
import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REGISTRY = REPO / "data/globe/witnesses.toml"
# Scans, OCR and IA metadata live outside the repository; leaf tables live in it.
WITNESSES = Path(os.environ.get("GLOBE_WITNESSES", REPO.parent / "globe-witnesses"))

BASES = ("audit", "reviewed", "offset")
LEAF_COLUMNS = ["leaf", "file", "printed", "basis", "note"]
MAX_LISTED = 8  # names shown per problem; the count is always exact


class RegistryError(Exception):
    """The registry, a leaf table, or the files they describe disagree."""


@dataclass(frozen=True)
class LeafRow:
    leaf: str  # as it appears in the scan filename, zero-padded
    file: str  # scan filename
    printed: int
    basis: str  # audit | reviewed | offset: where this row's number comes from
    note: str = ""


@dataclass
class LeafTable:
    path: Path
    rows: list[LeafRow]

    def __post_init__(self):
        self._by_leaf = {r.leaf: r for r in self.rows}
        by_printed: dict[int, list[LeafRow]] = {}
        for r in self.rows:
            by_printed.setdefault(r.printed, []).append(r)
        self._by_printed = by_printed

    def __len__(self) -> int:
        return len(self.rows)

    def row(self, leaf: str) -> LeafRow:
        try:
            return self._by_leaf[leaf]
        except KeyError:
            raise RegistryError(f"{self.path.name}: no row for leaf {leaf!r}") from None

    def leaf_for_printed(self, printed: int) -> str:
        """The leaf that carries this printed page. Exactly one, or an error."""
        rows = self._by_printed.get(printed, [])
        if len(rows) != 1:
            raise RegistryError(
                f"{self.path.name}: printed page {printed} matches {len(rows)} leaves, expected 1"
            )
        return rows[0].leaf


@dataclass(frozen=True)
class OcrLayer:
    witness: str
    name: str
    format: str  # "djvu" | "kraken-alto"
    path: Path | None = None  # djvu: the one file
    dir: Path | None = None  # kraken-alto: one file per leaf
    pattern: str = ""  # kraken-alto: filename pattern
    key: str = ""  # djvu: the usemap value for a leaf

    def file_for(self, leaf: str) -> Path:
        if self.format != "kraken-alto":
            raise RegistryError(f"{self.witness}/{self.name}: no per-leaf file (format {self.format})")
        return self.dir / self.pattern.format(leaf=leaf)


@dataclass
class Witness:
    id: str
    catalog: dict
    scans_dir: Path
    scan_pattern: str
    leaves: LeafTable
    layers: dict[str, OcrLayer] = field(default_factory=dict)
    metadata: dict[str, Path] = field(default_factory=dict)  # named files other than scans and OCR

    def scan_path(self, leaf: str) -> Path:
        return self.scans_dir / self.scan_pattern.format(leaf=leaf)

    def layer(self, name: str) -> OcrLayer:
        try:
            return self.layers[name]
        except KeyError:
            raise RegistryError(
                f"witness {self.id!r} has no OCR layer {name!r} (has: {', '.join(self.layers)})"
            ) from None


@dataclass
class Registry:
    witnesses: dict[str, Witness]

    def witness(self, wid: str) -> Witness:
        try:
            return self.witnesses[wid]
        except KeyError:
            raise RegistryError(f"no witness {wid!r} (registered: {', '.join(self.witnesses)})") from None

    def pairs(self) -> list[tuple[str, str]]:
        """Every (witness id, layer name), in registry order."""
        return [(w.id, name) for w in self.witnesses.values() for name in w.layers]


# ---------------------------------------------------------------- loading


def read_leaf_table(path: Path) -> LeafTable:
    if not path.is_file():
        raise RegistryError(f"leaf table missing: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames is None or [c for c in LEAF_COLUMNS[:4] if c not in reader.fieldnames]:
            raise RegistryError(f"{path.name}: needs columns {LEAF_COLUMNS[:4]}, has {reader.fieldnames}")
        rows = []
        for i, r in enumerate(reader, start=2):
            try:
                printed = int(r["printed"])
            except ValueError:
                raise RegistryError(f"{path.name} line {i}: printed {r['printed']!r} is not an integer") from None
            rows.append(LeafRow(r["leaf"], r["file"], printed, r["basis"], r.get("note") or ""))
    return LeafTable(path, rows)


def _names(items) -> str:
    items = sorted(items)
    shown = ", ".join(items[:MAX_LISTED])
    return shown + (f", ... ({len(items) - MAX_LISTED} more)" if len(items) > MAX_LISTED else "")


def _files_in(directory: Path) -> set[str]:
    return {p.name for p in directory.iterdir() if p.is_file() and not p.name.startswith(".")}


def _compare(label: str, expected: set[str], present: set[str], problems: list[str]) -> None:
    if missing := expected - present:
        problems.append(f"{label}: {len(missing)} missing: {_names(missing)}")
    if extra := present - expected:
        problems.append(f"{label}: {len(extra)} not in the leaf table: {_names(extra)}")


def validate_witness(w: Witness) -> None:
    """Raise RegistryError naming every problem found, not just the first."""
    problems: list[str] = []
    table = w.leaves
    counts = [f"leaf table {len(table)}"]

    leaves = [r.leaf for r in table.rows]
    if dup := {x for x in leaves if leaves.count(x) > 1}:
        problems.append(f"{table.path.name}: duplicate leaf: {_names(dup)}")
    printed = [r.printed for r in table.rows]
    if dup := {str(x) for x in printed if printed.count(x) > 1}:
        problems.append(f"{table.path.name}: printed page on more than one leaf: {_names(dup)}")
    if bad := {r.basis for r in table.rows} - set(BASES):
        problems.append(f"{table.path.name}: basis must be one of {BASES}, found {_names(bad)}")
    wrong = [r.leaf for r in table.rows if r.file != w.scan_pattern.format(leaf=r.leaf)]
    if wrong:
        problems.append(
            f"{table.path.name}: {len(wrong)} rows whose file is not the registry's scan pattern "
            f"{w.scan_pattern!r}: {_names(wrong)}"
        )

    expected_scans = {w.scan_pattern.format(leaf=x) for x in leaves}
    if not w.scans_dir.is_dir():
        problems.append(f"scans directory missing: {w.scans_dir}")
    else:
        present = _files_in(w.scans_dir)
        counts.append(f"scans {len(present)}")
        _compare("scans", expected_scans, present, problems)

    for name, path in w.metadata.items():
        if not path.is_file():
            problems.append(f"{w.id} metadata {name!r}: file missing: {path}")

    for layer in w.layers.values():
        tag = f"{w.id}/{layer.name}"
        if layer.format == "kraken-alto":
            if not layer.dir.is_dir():
                problems.append(f"{tag}: directory missing: {layer.dir}")
                continue
            expected = {layer.pattern.format(leaf=x) for x in leaves}
            present = _files_in(layer.dir)
            counts.append(f"{layer.name} ALTO {len(present)}")
            _compare(f"{tag} ALTO", expected, present, problems)
        elif layer.format == "djvu":
            if not layer.path.is_file():
                problems.append(f"{tag}: file missing: {layer.path}")
                continue
            keys = set(re.findall(r'usemap="([^"]+)"', layer.path.read_text(encoding="utf-8")))
            expected = {layer.key.format(leaf=x) for x in leaves}
            counts.append(f"{layer.name} djvu objects {len(keys)}")
            if missing := expected - keys:
                problems.append(f"{tag}: {len(missing)} leaves have no text in {layer.path.name}: {_names(missing)}")
        else:
            problems.append(f"{tag}: unknown format {layer.format!r}")

    if problems:
        raise RegistryError(
            f"witness {w.id!r} does not match its registry ({'; '.join(counts)}):\n  " + "\n  ".join(problems)
        )


def _layer(wid: str, name: str, spec: dict, repo: Path) -> OcrLayer:
    fmt = spec.get("format")
    try:
        if fmt == "djvu":
            return OcrLayer(wid, name, fmt, path=repo / spec["path"], key=spec["key"])
        if fmt == "kraken-alto":
            return OcrLayer(wid, name, fmt, dir=repo / spec["dir"], pattern=spec["pattern"])
    except KeyError as e:
        raise RegistryError(f"{wid}/{name}: registry entry lacks {e.args[0]!r}") from None
    raise RegistryError(f"{wid}/{name}: unknown format {fmt!r}")


def load(only: list[str] | None = None, registry: Path = REGISTRY, repo: Path = REPO,
         root: Path = WITNESSES) -> Registry:
    """Load and validate the registry. `only` limits it to those witness ids,
    for a script that reads one witness and should not depend on the other."""
    if not registry.is_file():
        raise RegistryError(f"registry missing: {registry}")
    with registry.open("rb") as fh:
        raw = tomllib.load(fh)
    if only is not None:
        if unknown := set(only) - set(raw):
            raise RegistryError(f"no witness {_names(unknown)} in {registry.name} (has: {', '.join(raw)})")
        raw = {k: v for k, v in raw.items() if k in only}

    witnesses: dict[str, Witness] = {}
    for wid, spec in raw.items():
        try:
            w = Witness(
                id=wid,
                catalog=spec.get("catalog", {}),
                scans_dir=root / spec["scans"]["dir"],
                scan_pattern=spec["scans"]["pattern"],
                leaves=read_leaf_table(repo / spec["leaves"]),
                layers={
                    name: _layer(wid, name, lspec, root) for name, lspec in spec.get("ocr", {}).items()
                },
                metadata={name: root / rel for name, rel in spec.get("metadata", {}).items()},
            )
        except KeyError as e:
            raise RegistryError(f"{wid}: registry entry lacks {e.args[0]!r}") from None
        validate_witness(w)
        witnesses[wid] = w
    return Registry(witnesses)
