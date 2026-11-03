"""Check a published Globe poem's line numbers against the page numerals.

doc/globe-lineation.org, "The poems". The poems are not regenerated: their
published files (canonical-engLit data/shakespeare/{poem}/) carry a line
number on every <l>, continuous through the poem (the Sonnets restart at each
sonnet). This check reads each witness page's rows with the play build's
machinery (page_rows, align_play, lineate), aligns them to the published
file's own words, divides them into Globe lines with the play rules, numbers
them on from the poem's first line, and reports:

  - every interval between two printed numerals that does not close;
  - every line whose count differs from the published <l n>.

It reads, it never writes. Per page it takes the witness whose rows close
best (Michigan, then Trent), as the build does, but without the build's
numeral re-reads or table: a numeral one witness misreads shows as a failing
pair (Lucrece p.1026, Trent's 1742 is Michigan's 1740).

Differences from the play build, all local to this module:
  - marginal numerals of four digits are read (Venus and Lucrece run past
    999); page_rows.NUMERAL allows three, and is restored after the check;
  - only rows that begin in an <l> are lines: a dedication or an Argument
    (prose) is not part of the count;
  - the poem's lines before its first checked page can be given (`start_n`),
    for an opening page the OCR cannot place.

Known limits, recorded with each poem below: a title set across both columns
in mid-page breaks the reading order of page_rows (it reads one pair of
columns per page), so the poem or section that begins below it does not
align; a printed row of asterisks the Globe numbers (The Passionate Pilgrim
118) has no row to align; and small type numerals (The Phoenix and Turtle)
are read as letters.
"""
from __future__ import annotations

import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from globe import align_play, lineate, page_rows, regenerate, tokens, witnesses

TEI = "{http://www.tei-c.org/ns/1.0}"
ORDER = [("miun", "kraken"), ("trent", "kraken")]


@dataclass(frozen=True)
class Poem:
    first: int  # printed pages (Michigan 1866; Trent sets them alike)
    last: int
    start_n: int = 0  # lines before `first`, read by eye
    restart: bool = False  # numbered from 1 in each <div type="poem"> (the Sonnets)
    note: str = ""


POEMS = {
    "ven": Poem(1000, 1011, note="checked to its last numeral, 1189: every line agrees"),
    "luc": Poem(1012, 1027, start_n=14,
                note="begins on p.1011 below the end of Venus; there Michigan's left margin is "
                     "clipped and the columns interleave, so lines 1-14 were read on the scan "
                     "(10 beside 'When Collatine unwisely did not let')"),
    "son": Poem(1028, 1046, restart=True, note="no line numerals are printed; checks rows only. One known false report: on p.1041 Michigan's scan clips the left margin ('hree themes'), so the turnover 'affords.' (Sonnet 105.12) reads as a line and 105.13-14 count one high"),
    "lc": Poem(1047, 1049, note="every numeral closes at 329 lines"),
    "pp": Poem(1050, 1054,
               note="fails where the check cannot follow the page: line 118 is a row of "
                    "asterisks (no row to align), and p.1052 sets 'SONNETS TO SUNDRY NOTES OF "
                    "MUSIC' across the columns in mid-page; the published numbers agree with "
                    "every numeral checked by eye (1864 printing p.1055, 201-290)"),
    "pht": Poem(1054, 1054,
                note="the numerals are small type, read as letters ('ro', '6o'); checked by eye "
                     "on the 1864 printing, p.1057, 10-60"),
}


@dataclass
class Result:
    poem: str
    lines: list = field(default_factory=list)
    pages: list = field(default_factory=list)  # (page, witness, lines, numerals, error)
    failing: list = field(default_factory=list)  # intervals
    differing: list = field(default_factory=list)  # (counted n, published n, page, first row)
    published: int = 0  # <l> in the published file


@contextmanager
def four_digit_numerals():
    saved = page_rows.NUMERAL
    page_rows.NUMERAL = re.compile(r"\d{1,4}")
    try:
        yield
    finally:
        page_rows.NUMERAL = saved


def edition(poem: str) -> Path:
    return regenerate.CORPUS / "data" / "shakespeare" / poem / f"shakespeare.{poem}.globe.xml"


def is_verse(tok) -> bool:
    return tok.cont is not None and etree.QName(tok.cont).localname == "l"


def check(poem: str, first: int | None = None, last: int | None = None,
          start_n: int | None = None) -> Result:
    spec = POEMS[poem]
    first = spec.first if first is None else first
    last = spec.last if last is None else last
    start_n = spec.start_n if start_n is None else start_n
    body = etree.parse(str(edition(poem))).getroot().find(f".//{TEI}body")
    toks = tokens.tokenize(body)
    if spec.restart:
        for t in toks:  # each sonnet is a division of its own, counted from 1
            d = next((a for a in t.node.iterancestors(f"{TEI}div") if a.get("type") == "poem"), None)
            t.div = f"0.{d.get('n')}" if d is not None else "0.0"
    enc = [t.t for t in toks]
    grams = align_play.trigram_index(enc)
    reg = witnesses.load(sorted({w for w, _ in ORDER}))
    res = Result(poem, published=sum(1 for _ in body.iter(f"{TEI}l")))
    state = regenerate.NumberState(div="0.0", n=start_n)
    floor = 0
    with four_digit_numerals():
        for p in range(first, last + 1):
            best = None
            for wid, layer in ORDER:
                w = reg.witness(wid)
                leaf = w.leaves.leaf_for_printed(p)
                f = w.layer(layer).file_for(leaf)
                if not Path(f).exists():
                    continue
                pg = page_rows.read_page(f, p, f"{wid}/{layer}", leaf, set(), w.watermark)
                try:
                    al = align_play.align_page(pg, toks, enc, grams, floor, set())
                except ValueError:
                    continue  # no word of the page is the poem's
                new = lineate.globe_lines(pg.rows, p)
                joined = bool(new and res.lines
                              and lineate.continues(res.lines[-1].rows[-1], new[0].rows[0]))
                head = new.pop(0) if joined else None
                new = [ln for ln in new if ln.start is not None and is_verse(toks[ln.start])]
                ivs, st = regenerate.number_page(new, toks, state, p, f"{wid}/{layer}",
                                                 carried=head.num if head is not None else None)
                err = sum(abs(iv["error"]) for iv in ivs)
                if best is None or err < best[0]:
                    best = (err, f"{wid}/{layer}", new, ivs, st, head, al)
                if err == 0:
                    break
            if best is None:
                res.pages.append((p, "", 0, [], None))
                continue
            err, key, new, ivs, st, head, al = best
            floor = max(floor, al.last + 1)
            if head is not None:
                res.lines[-1].rows += head.rows
            res.lines += new
            state = st
            res.pages.append((p, key, len(new), [iv["to"] for iv in ivs], err))
            res.failing += [iv for iv in ivs if iv["error"]]
    for ln in res.lines:
        pub = toks[ln.start].cont.get("n")
        if str(ln.n) != pub:
            res.differing.append((ln.n, pub, ln.page, ln.rows[0].text[:60]))
    return res


def report(res: Result) -> str:
    out = []
    for p, key, n, nums, err in res.pages:
        out.append(f"p.{p} {key or 'no witness page aligns'}: {n} lines, numerals {nums}"
                   + (f", error {err}" if err else ""))
    for iv in res.failing:
        out.append(f"  FAIL p.{iv['page']} {iv['witness']} {iv['frm']} -> {iv['to']}: "
                   f"counted {iv['counted_gap']}, printed {iv['printed_gap']}")
    out.append(f"{res.poem}: {len(res.lines)} lines counted, {res.published} <l> published; "
               f"{len(res.failing)} failing intervals; {len(res.differing)} lines whose count "
               f"differs from the published @n")
    out += [f"  counted {a}, published {b}, p.{c}: {d}" for a, b, c, d in res.differing[:25]]
    if POEMS[res.poem].note:
        out.append(f"note: {POEMS[res.poem].note}")
    return "\n".join(out)


def main(poem: str) -> int:
    if poem not in POEMS:
        print(f"poem-check: {poem!r} is not one of {', '.join(POEMS)}", file=sys.stderr)
        return 2
    res = check(poem)
    print(report(res), file=sys.stderr)
    return 0 if not res.failing and not res.differing else 1
