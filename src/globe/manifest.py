"""The witness manifest: what the build reads from the witnesses, pinned.

doc/globe-lineation.org. The page images and their OCR live outside the
repository, under GLOBE_WITNESSES (src/globe/witnesses.py). For each play,
data/globe/witness-manifest.tsv names every file the build reads -- the
Kraken ALTO leaf for each printed page, in each witness the build tries,
and each witness's leaf table -- with its sha256. The build refuses to
run if any of them is missing from the manifest or has changed.

    pdm run python -m globe.manifest lr    # (re)write the play's rows

Rewriting the rows is how a deliberate change to a witness is recorded;
the diff of this table is the record of it.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

from globe import witnesses

MANIFEST = witnesses.REPO / "data/globe/witness-manifest.tsv"
COLUMNS = ["play", "witness", "catalog", "file", "base", "path", "sha256"]


class ManifestError(Exception):
    """A file the build reads is not pinned, or is not what was pinned."""


@dataclass(frozen=True)
class Entry:
    play: str
    witness: str
    catalog: str
    file: str  # "leaves" | "alto <printed page>"
    base: str  # GLOBE_WITNESSES | repo
    path: str  # relative to base

    def resolve(self, bases: dict[str, Path]) -> Path:
        return bases[self.base] / self.path


def _bases(root: Path | None, repo: Path | None) -> dict[str, Path]:
    return {"GLOBE_WITNESSES": root or witnesses.WITNESSES, "repo": repo or witnesses.REPO}


def _relative(path: Path, bases: dict[str, Path]) -> tuple[str, str]:
    for base, root in bases.items():
        if path.is_relative_to(root):
            return base, path.relative_to(root).as_posix()
    raise ManifestError(f"{path} is under neither GLOBE_WITNESSES ({bases['GLOBE_WITNESSES']}) "
                        f"nor the repository ({bases['repo']})")


def entries(play: str, reg: witnesses.Registry, order, first: int, last: int,
            root: Path | None = None, repo: Path | None = None) -> list[Entry]:
    """Every witness file the build reads for this play, in build order."""
    bases = _bases(root, repo)
    out = []
    for wid in dict.fromkeys(w for w, _ in order):
        w = reg.witness(wid)
        catalog = " ".join(f"{k}={v}" for k, v in w.catalog.items())
        out.append(Entry(play, wid, catalog, "leaves", *_relative(w.leaves.path, bases)))
        for _, layer in (o for o in order if o[0] == wid):
            L = w.layer(layer)
            for p in range(first, last + 1):
                path = L.file_for(w.leaves.leaf_for_printed(p))
                out.append(Entry(play, wid, catalog, f"{layer} p.{p}", *_relative(path, bases)))
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(manifest: Path = MANIFEST) -> list[dict]:
    if not manifest.is_file():
        return []
    with manifest.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def verify(play: str, reg: witnesses.Registry, order, first: int, last: int,
           manifest: Path = MANIFEST, root: Path | None = None, repo: Path | None = None) -> None:
    """Raise ManifestError naming every file the build would read that is
    unpinned or whose sha256 differs from the manifest's."""
    bases = _bases(root, repo)
    pinned = {(r["base"], r["path"]): r["sha256"] for r in read(manifest) if r["play"] == play}
    problems = []
    for e in entries(play, reg, order, first, last, root, repo):
        want = pinned.get((e.base, e.path))
        if want is None:
            problems.append(f"not in the manifest: {e.base}/{e.path}")
        elif sha256(e.resolve(bases)) != want:
            problems.append(f"sha256 differs from the manifest: {e.base}/{e.path}")
    if problems:
        shown = problems[:witnesses.MAX_LISTED]
        more = len(problems) - len(shown)
        raise ManifestError(
            f"{manifest.name}: {len(problems)} witness files for {play} do not match "
            f"(GLOBE_WITNESSES={bases['GLOBE_WITNESSES']}):\n  " + "\n  ".join(shown)
            + (f"\n  ... ({more} more)" if more else ""))


def write(play: str, reg: witnesses.Registry, order, first: int, last: int,
          manifest: Path = MANIFEST, root: Path | None = None, repo: Path | None = None) -> int:
    """Replace this play's rows with the files as they are now. Returns the row count."""
    bases = _bases(root, repo)
    keep = [r for r in read(manifest) if r["play"] != play]
    new = [dict(vars(e), sha256=sha256(e.resolve(bases)))
           for e in entries(play, reg, order, first, last, root, repo)]
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(keep + new)
    return len(new)


def main(play: str = "lr") -> int:
    from globe import regenerate  # regenerate imports this module
    _, _, first, last = regenerate.PLAYS[play]
    reg = witnesses.load(sorted({w for w, _ in regenerate.ORDER}))
    n = write(play, reg, regenerate.ORDER, first, last)
    print(f"{MANIFEST.relative_to(witnesses.REPO)}: {n} rows for {play}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
