"""The reviewed table of shared half-lines the page cannot show.

doc/forum.org #lineation/shared-lines-table; doc/agenda.org
#build/regenerate-lear, "Amendment <2026-09-22>: finish Lear".

A shared verse line whose second half the compositor could not displace is
set exactly like an ordinary speech opening. The page does not show the
junction and the P4 does not mark it, so neither authority can decide it.
Such lines are recorded in data/globe/shared-lines.tsv, one row per junction,
checked on the page image before the canonical build uses them.

Four kinds of row, all read by the build: two fold two lines into one, one
cuts one line in two, and one corrects a number:
  shared    a shared verse line, its second half undisplaceable;
  turnover  one speaker's verse line continued on a row the page sets
            flush at the margin instead of at the turnover indent, so the
            layout gives no sign that it continues (V.3 "Well thought on:
            take my sword," / "Give it the captain.");
  separate  the opposite of those two: a row the page displaces, as if it completed the
            line above, but which the Globe numbers as a line of its own
            (Antony II.6 "Well;", V.2 "Sole sir o' the world,", "All
            dead."); first_half is the first words of the line above,
            second_half of the row. The Folger is no guide here: it joins
            two of those three;
  numeral   a marginal number both witnesses misread.

Every row names its play, and its page must be one of that play's printed
pages (data/globe/plays.tsv): the build reads only the play's own rows, and
the header's junction count is the play's.

Rows can be *proposed* from the Folger (DraCor) edition, which marks shared
lines with @part. The Folger sits below the page, never beside it: it is
consulted for @part at a junction and nothing else -- never for counts, line
numbers or words -- and only its xml:ids are recorded, never its text, which
is modernised. A proposal is evidence for a row, not a decision: Cliff fills
`checked` after looking at the image.
"""
from __future__ import annotations

import csv
import difflib
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from globe import plays
from globe.tokens import norm

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
TABLE = Path(__file__).resolve().parent.parent.parent / "data/globe/shared-lines.tsv"

COLUMNS = ["play", "scene", "page", "kind", "first_half", "second_half", "line", "basis",
           "folger_ids", "checked", "note"]
MATCH_WORDS = 3  # words compared at each half of a junction
KINDS = ("shared", "turnover", "separate", "numeral")


class TableError(Exception):
    """A table row that does not apply, or does not close its interval."""


@dataclass
class Row:
    play: str  # the play's id in data/globe/plays.tsv
    scene: str
    page: int
    kind: str  # "shared" | "turnover" | "separate" | "numeral"
    first_half: str  # shared: first words of the first half; numeral: the printed value
    second_half: str  # shared: first words of the second half; numeral: the value read
    line: str  # numeral: first words of the line the numeral sits on; shared: empty
    basis: str  # image | folger | image+folger
    folger_ids: str = ""
    checked: str = ""
    note: str = ""

    @property
    def pending(self) -> bool:
        return not self.checked.strip()


@dataclass
class Pair:
    """A Folger shared line: an <l part="I"> and the <l part="F"> after it."""
    i_id: str
    f_id: str
    i_words: tuple[str, ...]
    f_words: tuple[str, ...]


def first_words(text: str, n: int | None = MATCH_WORDS) -> tuple[str, ...]:
    """The first `n` normalised words of `text`, or all of them for None."""
    out = []
    for w in text.split():
        t = norm(w)
        if t:
            out.append(t)
        if n is not None and len(out) == n:
            break
    return tuple(out)


def read_folger(path: Path) -> list[Pair]:
    """Every I/F pair in a play's Folger file (plays.Play.dracor_path), by its
    words. Folger text is read here and never kept: only the xml:ids leave
    this function."""
    root = etree.parse(str(path)).getroot()
    lines = [el for el in root.iter(TEI + "l")]
    pairs = []
    for i, el in enumerate(lines):
        if el.get("part") != "I":
            continue
        nxt = next((n for n in lines[i + 1:i + 3] if n.get("part") == "F"), None)
        if nxt is None:
            continue
        pairs.append(Pair(el.get(XML_ID), nxt.get(XML_ID),
                          first_words("".join(el.itertext()), None),
                          first_words("".join(nxt.itertext()), None)))
    return pairs


def line_words(lines, k: int, toks, n: int | None = MATCH_WORDS) -> tuple[str, ...]:
    """The spoken words of line `lines[k]`, within that line only; the first
    `n` of them, or all of them when `n` is None.

    Speaker names are skipped, and so are stage directions: a second half can
    open with one ("[Kneeling] O you mighty gods!"), where the Folger keeps
    the stage direction in an element of its own."""
    end = lines[k + 1].start if k + 1 < len(lines) else len(toks)
    out = []
    for t in toks[lines[k].start:end]:
        if t.kind != "speech":
            continue
        out.append(t.t)
        if n is not None and len(out) == n:
            break
    return tuple(out)


def propose(play: str, lines, toks, failing, pairs: list[Pair]) -> list[Row]:
    """A row for every +1 interval holding a junction the Folger marks I/F.

    `failing` is the driver's failing intervals, `pairs` the play's Folger
    pairs (read_folger). Only adjacent line pairs
    inside a failing interval are considered, and a junction is proposed only
    where both halves match a Folger pair on their first words. Folger
    spelling is modernised, so a half of three words matches when one
    differs; shorter halves must match exactly (see _matches)."""
    by_line = {}
    for k, ln in enumerate(lines):
        by_line[(ln.div, ln.n)] = k
    out = []
    for iv in failing:
        if iv["error"] != 1:
            continue
        lo = iv["counted_n"] - iv["counted_gap"]
        for n in range(lo, iv["counted_n"] + 1):
            k = by_line.get((iv["div"], n))
            if k is None or k + 1 >= len(lines):
                continue
            b = lines[k + 1]
            aw, bw = line_words(lines, k, toks, None), line_words(lines, k + 1, toks, None)
            hit = next((p for p in pairs if _same_line(p.i_words, aw) and _same_line(p.f_words, bw)), None)
            if hit is not None:
                out.append(Row(play, iv["div"], b.page, "shared",
                               " ".join(aw[:MATCH_WORDS]), " ".join(bw[:MATCH_WORDS]), "",
                               "folger", f"{hit.i_id} {hit.f_id}", "",
                               "proposed from the Folger; check the image"))
    return out


def _matches(folger: tuple[str, ...], ours: tuple[str, ...]) -> bool:
    """Folger spelling is modernised, so one word in three may differ. A half
    of one or two words must match exactly: with a tolerance, a one-word half
    ("Speak.", "Come.") matches any pair at all."""
    if not folger or not ours:
        return False
    n = min(len(folger), len(ours))
    allowed = 1 if n >= MATCH_WORDS else 0
    return sum(1 for a, b in zip(folger[:n], ours[:n]) if a != b) <= allowed


SAME_LINE_RATIO = 0.75  # word-level similarity for two lines to be the same line


def _same_line(folger: tuple[str, ...], ours: tuple[str, ...]) -> bool:
    """Do a Folger line and one of ours hold the same line of verse?

    The first words are not enough. At III.7 the Folger's half is "To whose
    hands" and stops there, where the Globe's line runs on to "...have you
    sent the lunatic king?" -- a full line, which cannot be a displaced second
    half. Matching on first words alone proposed that junction, and the same
    match was made by hand (doc/forum.org #lineation/shared-lines-table).
    So the two must also end together: the words are compared whole, allowing
    for modernised spelling."""
    if not folger or not ours:
        return False
    if abs(len(folger) - len(ours)) > 1:
        return False
    return difflib.SequenceMatcher(None, folger, ours, autojunk=False).ratio() >= SAME_LINE_RATIO


# ---------------------------------------------------------------- the table


def read_table(path: Path = TABLE) -> list[Row]:
    """Read the table, tolerating what a spreadsheet does to it.

    Cliff edits this file, and saving it from a spreadsheet pads every line to
    the full column count with tabs and quotes any line holding a comma -- so a
    comment can arrive as '"# cannot show, or numeral..."'. Comments are
    therefore recognised after parsing, by their first field, never by the raw
    line, and trailing empty columns are ignored."""
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
        raise TableError(f"{path.name}: header lacks {', '.join(missing)} (has: "
                         f"{', '.join(c for c in header if c) or 'nothing'})")
    known = plays.read()
    rows = []
    for line, cells in enumerate(raw[1:], start=2):
        r = dict(zip(header, [c.strip() for c in cells]))
        if r["play"] not in known:
            raise TableError(f"{path.name} row {line}: play {r['play']!r} is not in "
                             f"{plays.TABLE.name} (it has: {', '.join(known)})")
        if r["kind"] not in KINDS:
            raise TableError(f"{path.name} row {line}: unknown kind {r['kind']!r}")
        try:
            page = int(r["page"])
        except ValueError:
            raise TableError(f"{path.name} row {line}: page {r['page']!r} is not a number") from None
        pl = known[r["play"]]
        if not pl.first <= page <= pl.last:
            raise TableError(f"{path.name} row {line}: page {page} is not one of {pl.id}'s "
                             f"printed pages ({pl.first}-{pl.last})")
        rows.append(Row(r["play"], r["scene"], page, r["kind"], r["first_half"], r["second_half"],
                        r.get("line", ""), r["basis"], r.get("folger_ids", ""),
                        r.get("checked", ""), r.get("note", "")))
    return rows


def for_play(rows: list[Row], play: str) -> list[Row]:
    """The play's own rows: what the build applies, and what the header counts."""
    return [r for r in rows if r.play == play]


def write_table(rows: list[Row], path: Path = TABLE, header_note: str = "") -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write("# doc/forum.org #lineation/shared-lines-table. One row per junction the page\n"
                "# cannot show, or numeral both witnesses misread. `checked` is filled by Cliff,\n"
                "# after looking at the page image; the canonical build refuses to use a row\n"
                "# that is still empty. Folger ids are pointers, never a source of text.\n")
        if header_note:
            f.write(f"# {header_note}\n")
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([r.play, r.scene, r.page, r.kind, r.first_half, r.second_half, r.line,
                        r.basis, r.folger_ids, r.checked, r.note])
