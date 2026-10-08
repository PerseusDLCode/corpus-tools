"""Check the regenerated shared-line structure against the Folger.

doc/forum.org #lineation/shared-lines-table. The Folger (DraCor) marks a
shared verse line with @part I/F and a line that stands alone, metrically
short, with ana="#short". The two are mutually exclusive there, so between
them they record the Folger's whole opinion about every short line.

This module reports, it never decides: the page is the authority for Globe
line division, and the measurements below show why #short cannot outrank it.
Its only use in the build is as evidence for a data/globe/shared-lines.tsv row at a
junction the page cannot show, which is what the forum entry allows.

The Folger's text is modernised, so its lines are located in ours by aligning
its spoken words to the P4's and taking each line's first word. About 95% of
its words align; a line whose first words do not are reported as unmatched
rather than guessed at.
"""
from __future__ import annotations

import bisect
import difflib
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from globe.tokens import norm

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


@dataclass
class FolgerLine:
    id: str
    part: str | None  # "I" | "F" | None
    short: bool  # ana="#short"
    start: int  # index into the Folger word stream
    our: int | None = None  # index of the Globe line it falls in


def read_lines(path: Path) -> tuple[list[str], list[FolgerLine]]:
    """The Folger's spoken word stream, and its verse lines within it, from
    the play's file in the ShakeDraCor clone (plays.Play.dracor_path)."""
    root = etree.parse(str(path)).getroot()
    words: list[str] = []
    lines: list[FolgerLine] = []
    for sp in root.iter(TEI + "sp"):
        for el in sp:
            if etree.QName(el).localname not in ("l", "p"):
                continue
            start = len(words)
            words += [n for n in (norm(w) for w in "".join(el.itertext()).split()) if n]
            if len(words) > start:
                lines.append(FolgerLine(el.get(XML_ID), el.get("part"),
                                        el.get("ana") == "#short", start))
    return words, lines


def locate(words, flines, toks, lines) -> float:
    """Set each Folger line's `our`, by aligning the two word streams.
    Returns the share of Folger words that aligned."""
    ours = [(t.i, t.t) for t in toks if t.kind == "speech"]
    sm = difflib.SequenceMatcher(None, words, [t for _, t in ours], autojunk=False)
    at: dict[int, int] = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            at[a + k] = ours[b + k][0]
    starts = [ln.start for ln in lines]
    for f in flines:
        tok = at.get(f.start)
        if tok is None:
            continue
        i = bisect.bisect_right(starts, tok) - 1
        f.our = i if i >= 0 else None
    return len(at) / len(words) if words else 0.0


def folds(lines, toks) -> list[tuple[int, object]]:
    """Every Globe line of ours that folds two speeches into one line: the
    shared lines, however they were found (the page's layout, or the table)."""
    def speech_of(ti):
        el = toks[ti].cont
        while el is not None and etree.QName(el).localname != "sp":
            el = el.getparent()
        return el

    out = []
    for k, ln in enumerate(lines):
        if len(ln.rows) < 2:
            continue
        first = speech_of(ln.start)
        for r in ln.rows[1:]:
            if r.start is not None and speech_of(r.start) is not first:
                out.append((k, ln))
                break
    return out


def compare(lines, toks, path: Path) -> dict:
    """What the Folger says about our shared lines, and ours about its pairs."""
    words, flines = read_lines(path)
    aligned = locate(words, flines, toks, lines)
    by_line: dict[int, list[FolgerLine]] = {}
    for f in flines:
        if f.our is not None:
            by_line.setdefault(f.our, []).append(f)

    rows, counts = [], {"part": 0, "short": 0, "silent": 0}
    for k, ln in folds(lines, toks):
        fs = by_line.get(k, [])
        if any(f.part in ("I", "F") for f in fs):
            verdict = "part"
        elif any(f.short for f in fs):
            verdict = "short"
        else:
            verdict = "silent"
        counts[verdict] += 1
        rows.append([ln.div, ln.n, ln.page, "our shared line", verdict,
                     " ".join(f.id for f in fs),
                     " / ".join(r.text[:40] for r in ln.rows)])

    pairs = [(flines[i], flines[i + 1]) for i in range(len(flines) - 1)
             if flines[i].part == "I" and flines[i + 1].part == "F"]
    split = 0
    for a, b in pairs:
        if a.our is None or b.our is None or a.our == b.our:
            continue
        split += 1
        ln = lines[a.our]
        rows.append([ln.div, ln.n, ln.page, "folger pair split across our lines", "differ",
                     f"{a.id} {b.id}",
                     " / ".join(r.text[:40] for r in lines[a.our].rows + lines[b.our].rows)])
    return dict(rows=rows, counts=counts, pairs=len(pairs), split=split,
                together=sum(1 for a, b in pairs if a.our is not None and a.our == b.our),
                aligned=aligned, lines=len(flines))
