"""The per-play table: canonical-engLit doc/agenda.org #globe/per-play-table.

data/globe/plays.tsv says where each play's inputs are, one row per play:
the P4 source and the shell (the P5 file the build writes under), both
relative to canonical-engLit; the play's first and last printed page in
the Globe; and its file in the ShakeDraCor clone, relative to that clone.
Every script that needs one of these reads it here; none names a play's
path or pages itself.

The ShakeDraCor clone is outside these repositories, at SHAKEDRACOR
(default ../../shakedracor, where it has always been: beside the
PerseusDLCode directory, not inside it). The build reads a play's Folger
text from it for the Folger report and for proposing shared-lines.tsv
rows, and for nothing else.

Standard library only.
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TABLE = REPO / "data/globe/plays.tsv"
DRACOR = Path(os.environ.get("SHAKEDRACOR", REPO.parent.parent / "shakedracor"))

COLUMNS = ["play", "p4", "shell", "first_page", "last_page", "dracor"]


class PlayTableError(Exception):
    """A row of plays.tsv that cannot be used, or a play it does not have."""


@dataclass(frozen=True)
class Play:
    id: str
    p4: str  # the P4 source, relative to canonical-engLit
    shell: str  # the P5 file the build writes under, relative to canonical-engLit
    first: int  # first printed page
    last: int  # last printed page
    dracor: str  # the play's file, relative to the ShakeDraCor clone

    @property
    def dracor_path(self) -> Path:
        return DRACOR / self.dracor


def read(path: Path = TABLE) -> dict[str, Play]:
    """Every play in the table, by id. Like shared-lines.tsv, the file may
    come back from a spreadsheet padded with tabs and with its comments
    quoted, so comments are recognised after parsing, by their first field."""
    with path.open(newline="", encoding="utf-8") as fh:
        raw = [r for r in csv.reader(fh, delimiter="\t")
               if any(c.strip() for c in r) and not r[0].lstrip().startswith("#")]
    header = [c.strip() for c in raw[0]] if raw else []
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise PlayTableError(f"{path.name}: header lacks {', '.join(missing)} (has: "
                             f"{', '.join(c for c in header if c) or 'nothing'})")
    plays: dict[str, Play] = {}
    for line, cells in enumerate(raw[1:], start=2):
        r = dict(zip(header, [c.strip() for c in cells]))
        empty = [c for c in COLUMNS if not r.get(c)]
        if empty:
            raise PlayTableError(f"{path.name} row {line}: no {', '.join(empty)}")
        try:
            first, last = int(r["first_page"]), int(r["last_page"])
        except ValueError:
            raise PlayTableError(f"{path.name} row {line}: pages {r['first_page']!r}-"
                                 f"{r['last_page']!r} are not numbers") from None
        if first > last:
            raise PlayTableError(f"{path.name} row {line}: first page {first} is after last page {last}")
        if r["play"] in plays:
            raise PlayTableError(f"{path.name} row {line}: {r['play']} has a row already")
        plays[r["play"]] = Play(r["play"], r["p4"], r["shell"], first, last, r["dracor"])
    return plays


def get(play: str, path: Path = TABLE) -> Play:
    plays = read(path)
    if play not in plays:
        raise PlayTableError(f"{path.name} has no play {play!r} (it has: {', '.join(plays) or 'none'})")
    return plays[play]
