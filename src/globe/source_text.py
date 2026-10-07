"""The P4, converted to P5 and stripped of every line milestone.

doc/agenda.org #build/regenerate-lear: "no existing Globe milestone survives;
no ed="F1" milestone is carried at all". The conversion is vendored
(src/globe/p4_convert.py). What P4 transcribed is read separately, by p4_anchors(),
for the old-against-new report.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from globe import p4_convert
from globe import tokens
from globe.p4_convert import q


@dataclass
class P4Text:
    body: etree._Element
    stats: p4_convert.ConversionStats
    stripped: dict[str, int]  # ed -> milestones removed


def remove_keeping_tail(el: etree._Element) -> None:
    """Remove an element, keeping its tail text in place."""
    parent = el.getparent()
    tail = el.tail or ""
    prev = el.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or "") + tail
    else:
        parent.text = (parent.text or "") + tail
    parent.remove(el)


def strip_line_milestones(body: etree._Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    for m in list(body.iter(q("milestone"))):
        if m.get("unit") == "line" and m.get("ed") in ("Globe", "F1"):
            counts[m.get("ed")] = counts.get(m.get("ed"), 0) + 1
            remove_keeping_tail(m)
    return counts


def load_p4(path: Path) -> P4Text:
    stats = p4_convert.ConversionStats()
    body = p4_convert.convert_body(p4_convert.parse_p4(path), stats)
    stripped = strip_line_milestones(body)
    return P4Text(body, stats, stripped)


@dataclass
class Anchor:
    """A number the P4 transcribed from the Globe's margin: <lb ed="G" n="..."/>.

    The P4 ends every printed row with an <lb ed="G"/>, so a numbered one
    labels the row that follows it (the P4 row, which is not the Globe's: see
    CLAUDE.md, "The P4's prose line breaks do not match"). The row runs from
    the first token after the marker to the next Globe marker, numbered or
    not. Indices are into the stripped token stream, tokens.tokenize(load_p4().body)."""
    n: str
    div: str
    row_start: int
    row_end: int


def p4_anchors(path: Path) -> list[Anchor]:
    """Every numbered Globe marker in the P4, with its row. doc/agenda.org
    #build/old-vs-new-from-p4: the old edition's numbers come from the P4,
    never from the shell.

    A stray @n on <l> (two in Lear) is not a marker and is not read: the
    conversion only records it (ConversionStats.pending_anchor_recovery)."""
    body = p4_convert.convert_body(p4_convert.parse_p4(path), p4_convert.ConversionStats())
    marks: list[tokens.Mark] = []
    raw = [t.t for t in tokens.tokenize(body, marks)]
    strip_line_milestones(body)
    stripped = [t.t for t in tokens.tokenize(body)]
    # Stripping joins the words either side of a marker that has no space
    # around it ("in?--<lb ed="F1"/>When" becomes one token), so indices are
    # carried across by alignment, P4 against itself.
    to_new: dict[int, int] = {}
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, raw, stripped, autojunk=False).get_opcodes():
        if tag not in ("equal", "replace"):
            raise ValueError(f"stripping line markers changed the P4's words: {tag} at {a1}")
        for k in range(a1, a2 + 1):
            to_new.setdefault(k, b1 + (k - a1) if tag == "equal" else b1)
    anchors = []
    for i, m in enumerate(marks):
        if m.n is None:
            continue
        end = next((x.before for x in marks[i + 1:]), len(raw))
        anchors.append(Anchor(m.n, m.div, to_new[m.before], to_new[end]))
    return anchors
