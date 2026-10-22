"""Numerals the build re-read from the other witness, and Cliff's checks of them.

Where one witness's marginal numeral does not close against the count and the
other witness's does, regenerate.number_page takes the other's reading. Both
readings are OCR, and Kraken reads margin numerals badly (39 as 30, 130 as
150), so a re-read is not trusted until a person has looked at the page image:
data/globe/numeral-checks.tsv holds one row per re-read, `checked` filled by
Cliff, and the canonical build refuses while any re-read lacks a checked row --
the rule data/globe/shared-lines.tsv already follows. A re-read changes no
output; the check only decides whether the canonical build is written.

A row is matched to a re-read by play, page, the line's first words, and the
two readings, so it survives a rebuild but not a change to what was read.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

CHECKS = Path(__file__).resolve().parent.parent.parent / "data/globe/numeral-checks.tsv"
COLUMNS = ["play", "page", "scene", "line", "witness", "read", "other_witness", "other_read",
           "checked", "note", "cliff_note"]
LINE_WORDS = 3  # spoken words that name the line, as in shared-lines.tsv's `line`


class ChecksError(Exception):
    """numeral-checks.tsv cannot be read."""


@dataclass(frozen=True)
class Reread:
    play: str
    page: int
    scene: str
    line: str  # the line's first spoken words, lower case
    witness: str  # the witness tried first, whose numeral did not close
    read: int
    other_witness: str  # the witness whose numeral was taken
    other_read: int

    @property
    def key(self) -> tuple:
        return (self.play, self.page, self.line, self.read, self.other_read)


@dataclass
class Check:
    play: str
    page: int
    scene: str
    line: str
    witness: str
    read: int
    other_witness: str
    other_read: int
    checked: str = ""
    note: str = ""
    cliff_note: str = ""

    @property
    def key(self) -> tuple:
        return (self.play, self.page, self.line, self.read, self.other_read)

    @property
    def pending(self) -> bool:
        return not self.checked.strip()


def line_words(toks, start: int) -> str:
    words = []
    for t in toks[start:]:
        if t.kind == "speech":
            w = re.sub(r"[^\w']", "", t.t.lower())
            if w:
                words.append(w)
                if len(words) == LINE_WORDS:
                    break
    return " ".join(words)


def rereads(play: str, results, toks) -> list[Reread]:
    """Every numeral this build took from the other witness, in page order."""
    out = []
    for r in results:
        for iv in r.intervals:
            if iv.get("reread"):
                witness, read, other_witness, other_read = iv["reread"]
                out.append(Reread(play, iv["page"], iv["div"], line_words(toks, iv["start"]),
                                  witness, read, other_witness, other_read))
    return out


def read_checks(path: Path = CHECKS) -> list[Check]:
    """Read the checks, tolerating a spreadsheet's padding and quoting, as
    shared_lines.read_table does: comments are known by their first field."""
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        raw = [r for r in csv.reader(fh, delimiter="\t")
               if any(c.strip() for c in r) and not r[0].lstrip().startswith("#")]
    if not raw:
        return []
    header = [c.strip() for c in raw[0]]
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise ChecksError(f"{path.name}: header lacks {', '.join(missing)}")
    rows = []
    for n, cells in enumerate(raw[1:], start=2):
        r = dict(zip(header, [c.strip() for c in cells]))
        try:
            page, read, other = int(r["page"]), int(r["read"]), int(r["other_read"])
        except ValueError:
            raise ChecksError(f"{path.name} row {n}: page, read and other_read must be numbers") from None
        rows.append(Check(r["play"], page, r["scene"], r["line"], r["witness"], read,
                          r["other_witness"], other, r.get("checked", ""), r.get("note", ""),
                          r.get("cliff_note", "")))
    return rows


def match(found: list[Reread], checks: list[Check]) -> list[tuple[Reread, Check | None]]:
    by_key = {c.key: c for c in checks}
    return [(rr, by_key.get(rr.key)) for rr in found]


def unchecked(found: list[Reread], checks: list[Check]) -> list[Reread]:
    """Re-reads with no row, or a row Cliff has not yet checked."""
    return [rr for rr, c in match(found, checks) if c is None or c.pending]


def stale(play: str, found: list[Reread], checks: list[Check]) -> list[Check]:
    """The play's rows that no re-read in this build matches."""
    keys = {rr.key for rr in found}
    return [c for c in checks if c.play == play and c.key not in keys]


def as_row(rr: Reread, note: str = "") -> list:
    """A re-read as a numeral-checks.tsv row, `checked` empty."""
    return [rr.play, rr.page, rr.scene, rr.line, rr.witness, rr.read, rr.other_witness,
            rr.other_read, "", note, ""]


def write_checks(rows: list[list], path: Path = CHECKS) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write("# src/globe/numeral_checks.py. One row per margin numeral the build took from\n"
                "# the other witness because the first one's reading did not close the count.\n"
                "# `checked` is filled by Cliff after looking at the page image; the canonical\n"
                "# build refuses while any re-read is unlisted or unchecked. `read` is what\n"
                "# `witness` read, `other_read` what `other_witness` read and the build took.\n")
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
