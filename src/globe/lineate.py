"""Printed rows -> Globe lines -> numbers, and the gate.

doc/agenda.org #build/regenerate-lear; doc/forum.org
#lineation/regenerate-from-witnesses ("The gate").

A Globe line is a start-band row carrying speech, plus every turnover or
displaced row after it until the next start-band row. So a turnover and the
second half of a shared line both continue their line; neither is numbered.
Rows with no speech (stage directions, headings) are not lines.

Numbers are counted from the start of each scene: line 1 is the scene's first
line, and the count runs on across page breaks. The page's printed marginal
numbers are not used to number anything. They are the check: each sits on the
last row of its line, and must equal that line's count. A page with no
printed number is checked by the next numbered page of the same scene.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass, field

from lxml import etree

from globe.page_rows import Row
from globe.tokens import Token

FULL_MEASURE_U = 1.0  # a row this close to the measure is full
SHARED_REACH_U = 9.0  # a shared half starts no further left of the first half's end than this


@functools.lru_cache(maxsize=8)
def marks_verse(root) -> bool:
    """Does this text mark verse with <l> anywhere? Only then does a <p> mean
    prose. Seven P4s -- 1h4, 1h6, 2h4, 2h6, 3h6, ant and aww -- set every
    speech in <p>, verse or prose, so their <p> says nothing either way
    (canonical-engLit doc/agenda.org #build/regenerate-ant)."""
    return bool(root.xpath("boolean(//*[local-name()='l'])"))


def continues(prev: Row, r: Row) -> bool:
    """Does indented row `r` continue the Globe line whose last row is `prev`?

    A start-band or indented row never does: an indented row is a verse line
    set in (a song). Otherwise, set by the compositor for one of three
    reasons, and only two of them continue a line:
    - turnover: the row above ran out of room, so it runs to the full measure;
    - shared half-line: set to follow on from where the first half's speech
      ended, or pushed left until it fits against the measure;
    - indented verse (songs, rhymes, letters): neither; the row is a line.
    Measured over all of Lear (doc/agenda.org #build/regenerate-lear, status):
    turnovers follow rows at most 0.93u short of the measure, song lines in
    the turnover band follow rows at least 1.07u short -- a thin margin, so
    rows near it are listed for review; shared halves start within 8.4u of the
    first half's end, song lines at least 10u before it."""
    if r.band in ("start", "indented"):
        return False
    if r.band == "turnover" and prev.short_u < FULL_MEASURE_U:
        return True
    if r.band == "displaced":
        cont = r.extra.get("cont")
        if (cont is not None and etree.QName(cont).localname == "p" and prev.extra.get("cont") is cont
                and marks_verse(cont.getroottree().getroot())):
            # a displaced row within the same P4 paragraph as the row above is
            # prose (a letter's subscription, Lear IV.6): shared halves are
            # verse, and in prose every printed row is a line. Only where the
            # P4 marks verse: in Antony the same paragraph holds a verse line
            # split by a stage direction ("To cool a gipsy's lust." /
            # "Look, where they come:", I.1), set to follow on like a shared half
            return False
        # in pitches from each row's own column margin, so a shared half at the
        # top of a column is measured against the foot of the previous one
        after = r.u(r.text_x) - prev.u(prev.extra.get("speech_r", prev.r))
        return after >= -SHARED_REACH_U or r.short_u < FULL_MEASURE_U
    return False


@dataclass
class Line:
    rows: list[Row]
    page: int
    div: str = ""
    n: int = 0
    num: int | None = None  # printed marginal number on this line, if any
    num_page: int | None = None

    @property
    def start(self) -> int:
        return self.rows[0].start


@dataclass
class PageGate:
    page: int
    witness: str
    printed: list[int] = field(default_factory=list)
    counted: list[int] = field(default_factory=list)  # the count at each printed number
    stray: list[int] = field(default_factory=list)  # numbers on no line (a non-line row)
    lines: int = 0
    first_n: str = ""
    last_n: str = ""

    @property
    def verdict(self) -> str:
        if self.stray or any(p != c for p, c in zip(self.printed, self.counted)):
            return "fail"
        return "pass" if self.printed else "unchecked"


def globe_lines(rows: list[Row], page: int) -> list[Line]:
    """Group one page's aligned rows (in reading order) into Globe lines. A
    continuation row at the top of a page continues the previous page's last
    line; the caller joins those (see number_lines)."""
    lines: list[Line] = []
    for r in rows:
        if r.start is None or not r.speech:
            continue
        if not lines or not continues(lines[-1].rows[-1], r):
            lines.append(Line([r], page))
        else:
            lines[-1].rows.append(r)
    for ln in lines:
        nums = [r.num for r in ln.rows if r.num is not None]
        ln.num = nums[-1] if nums else None
    return lines


def carry_over(prev: list[Line], lines: list[Line]) -> list[Line]:
    """A page (or column) that opens with a turnover continues the line above."""
    if lines and prev and continues(prev[-1].rows[-1], lines[0].rows[0]):
        head = lines.pop(0)
        prev[-1].rows += head.rows
        if head.num is not None:
            prev[-1].num = head.num
    return lines


def number_lines(lines: list[Line], toks: list[Token]) -> None:
    """Count from each scene's start. `lines` is the whole play, in order."""
    div, n = None, 0
    for ln in lines:
        d = toks[ln.start].div
        if d != div:
            div, n = d, 0
        n += 1
        ln.div, ln.n = d, n


def gate(page: int, witness: str, lines: list[Line], rows: list[Row]) -> PageGate:
    g = PageGate(page, witness)
    mine = [ln for ln in lines if ln.page == page]
    g.lines = len(mine)
    if mine:
        g.first_n = f"{mine[0].div}.{mine[0].n}"
        g.last_n = f"{mine[-1].div}.{mine[-1].n}"
    here = {id(r) for r in rows}
    on_lines = set()
    for ln in lines:
        for r in ln.rows:
            if r.num is not None and id(r) in here:
                on_lines.add(id(r))
                # the number labels the line it sits on
                g.printed.append(r.num)
                g.counted.append(ln.n)
    g.stray = [r.num for r in rows if r.num is not None and id(r) not in on_lines]
    return g
