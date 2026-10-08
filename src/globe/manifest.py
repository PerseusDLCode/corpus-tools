"""The witness manifest: what the build reads from the witnesses, pinned.

doc/globe-lineation.org. The page images and their OCR live outside the
repository, under GLOBE_WITNESSES (src/globe/witnesses.py). For each play,
data/globe/witness-manifest.tsv names every file the build reads -- the
Kraken ALTO leaf for each printed page, in each witness the build tries,
and each witness's leaf table -- with its sha256. The build refuses to
run if any of them is missing from the manifest or has changed.

The play's file in the ShakeDraCor clone (src/globe/plays.py) is pinned
the same way, in a row whose witness is "dracor": its sha256, and in
`catalog` the clone's commit and the play's DraCor id as they were when
the row was written (canonical-engLit doc/agenda.org #globe/pin-dracor).
The header's Folger citation is written from that row, so it names the
commit whose bytes the build checks. The clone may be absent, and then
the Folger report is skipped; a file that is there and differs is refused.

    pdm run python -m globe.manifest lr    # (re)write the play's rows

Rewriting the rows is how a deliberate change to a witness is recorded;
the diff of this table is the record of it.
"""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from globe import plays
from globe import witnesses

MANIFEST = witnesses.REPO / "data/globe/witness-manifest.tsv"
COLUMNS = ["play", "witness", "catalog", "file", "base", "path", "sha256"]
DRACOR = "dracor"  # `witness` of the row that pins a play's ShakeDraCor file
DRACOR_BASE = "SHAKEDRACOR"
DRACOR_REPO = "dracor-org/shakedracor"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


class ManifestError(Exception):
    """A file the build reads is not pinned, or is not what was pinned."""


@dataclass(frozen=True)
class Entry:
    play: str
    witness: str
    catalog: str
    file: str  # "leaves" | "<layer> p.<printed page>" | "folger"
    base: str  # GLOBE_WITNESSES | repo | SHAKEDRACOR
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


def dracor_catalog(clone: Path, rel: str) -> str:
    """Where a play's ShakeDraCor file comes from, as the manifest records
    it: the clone's commit and the play's DraCor id. A file that differs from
    that commit's is refused, so the commit recorded is true of the bytes
    pinned beside it."""
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "--no-optional-locks", "-C", str(clone), *args],
                              capture_output=True, text=True)
    if not (clone / rel).is_file():
        raise ManifestError(f"{DRACOR_BASE}/{rel} is not on this machine ({DRACOR_BASE}={clone}); "
                            f"the manifest pins it")
    head = git("rev-parse", "--short=7", "HEAD")
    if head.returncode != 0:
        raise ManifestError(f"{clone} is not a git clone with a commit: {head.stderr.strip()}")
    commit = head.stdout.strip()
    if git("status", "--porcelain", "--", rel).stdout.strip():
        raise ManifestError(f"{DRACOR_BASE}/{rel} differs from the clone's commit {commit}; "
                            f"pin a file as it is committed")
    play_id = etree.parse(str(clone / rel)).getroot().get(XML_ID)
    if not play_id:
        raise ManifestError(f"{DRACOR_BASE}/{rel} has no xml:id on its root element")
    return f"github={DRACOR_REPO} commit={commit} play={play_id}"


def dracor_pin(play: str, manifest: Path = MANIFEST) -> dict[str, str]:
    """The play's ShakeDraCor pin: `commit` and `play` (its DraCor id) from
    the row's catalog, with its `path` and `sha256`."""
    rows = [r for r in read(manifest) if r["play"] == play and r["witness"] == DRACOR]
    if len(rows) != 1:
        raise ManifestError(f"{manifest.name}: {len(rows)} ShakeDraCor rows for {play}, expected 1 "
                            f"(globe-lineation manifest {play})")
    pin = dict(kv.split("=", 1) for kv in rows[0]["catalog"].split())
    missing = [k for k in ("commit", "play") if not pin.get(k)]
    if missing:
        raise ManifestError(f"{manifest.name}: the ShakeDraCor row for {play} has no "
                            f"{' or '.join(missing)} in its catalog")
    return dict(pin, path=rows[0]["path"], sha256=rows[0]["sha256"])


def verify(play: str, reg: witnesses.Registry, order, first: int, last: int,
           manifest: Path = MANIFEST, root: Path | None = None, repo: Path | None = None,
           dracor: str | None = None, clone: Path | None = None) -> None:
    """Raise ManifestError naming every file the build would read that is
    unpinned or whose sha256 differs from the manifest's. `dracor` is the
    play's ShakeDraCor file, relative to `clone` (default plays.DRACOR): it
    must be pinned, and must be as pinned if it is there at all."""
    bases = _bases(root, repo)
    clone = clone or plays.DRACOR
    pinned = {(r["base"], r["path"]): r["sha256"] for r in read(manifest) if r["play"] == play}
    problems = []
    for e in entries(play, reg, order, first, last, root, repo):
        want = pinned.get((e.base, e.path))
        if want is None:
            problems.append(f"not in the manifest: {e.base}/{e.path}")
        elif sha256(e.resolve(bases)) != want:
            problems.append(f"sha256 differs from the manifest: {e.base}/{e.path}")
    if dracor is not None:
        want = pinned.get((DRACOR_BASE, dracor))
        if want is None:
            problems.append(f"not in the manifest: {DRACOR_BASE}/{dracor}")
        elif (clone / dracor).is_file() and sha256(clone / dracor) != want:
            problems.append(f"sha256 differs from the manifest: {DRACOR_BASE}/{dracor}")
    if problems:
        shown = problems[:witnesses.MAX_LISTED]
        more = len(problems) - len(shown)
        raise ManifestError(
            f"{manifest.name}: {len(problems)} pinned files for {play} do not match "
            f"(GLOBE_WITNESSES={bases['GLOBE_WITNESSES']}, {DRACOR_BASE}={clone}):\n  "
            + "\n  ".join(shown) + (f"\n  ... ({more} more)" if more else ""))


def write(play: str, reg: witnesses.Registry, order, first: int, last: int,
          manifest: Path = MANIFEST, root: Path | None = None, repo: Path | None = None,
          dracor: str | None = None, clone: Path | None = None) -> int:
    """Replace this play's rows with the files as they are now. Returns the row count."""
    bases = _bases(root, repo)
    clone = clone or plays.DRACOR
    keep = [r for r in read(manifest) if r["play"] != play]
    new = [dict(vars(e), sha256=sha256(e.resolve(bases)))
           for e in entries(play, reg, order, first, last, root, repo)]
    if dracor is not None:
        e = Entry(play, DRACOR, dracor_catalog(clone, dracor), "folger", DRACOR_BASE, dracor)
        new.append(dict(vars(e), sha256=sha256(clone / dracor)))
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(keep + new)
    return len(new)


def main(play: str = "lr") -> int:
    from globe import regenerate  # regenerate imports this module
    entry = plays.get(play)
    reg = witnesses.load(sorted({w for w, _ in regenerate.ORDER}))
    n = write(play, reg, regenerate.ORDER, entry.first, entry.last, dracor=entry.dracor)
    print(f"{MANIFEST.relative_to(witnesses.REPO)}: {n} rows for {play}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
