"""Align each witness page to the P4 token stream, page by page in order.

doc/agenda.org #build/regenerate-lear. This is alignment, not recognition: the
P4 text is known, so the OCR only has to say where each printed row begins.

Per page: a trigram vote proposes the page's offset into the token stream,
restricted to offsets at or after the previous page's (pages come in order);
difflib then aligns the page's words to a window around that offset. Each row
gets `start`, the token index of its first word, and `speech`, whether its
matched tokens are mostly speech rather than stage direction or heading.

The difflib opcodes are also the word-disagreement evidence: every place the
witness and the P4 differ. P4 is never corrected from them.
"""
from __future__ import annotations

import difflib
from collections import Counter
from dataclasses import dataclass

from globe.page_rows import PREFIX, Page, Row
from globe.tokens import Token, norm

WINDOW_SLACK = 150  # tokens after the voted offset


@dataclass
class Disagreement:
    page: int
    col: int
    seq: int
    tok_from: int  # P4 token span [tok_from, tok_to)
    tok_to: int
    p4: str
    witness: str
    op: str  # replace | delete (P4 words the witness lacks) | insert (witness words P4 lacks)


@dataclass
class PageAlignment:
    page: Page
    first: int  # first and last matched token
    last: int
    matched: int  # words matched
    words: int  # witness words considered
    ocr_to_tok: dict[int, int]  # witness word index -> token index
    ow: list[tuple[int, str, str]]  # (row index, normalised, raw)
    disagreements: list[Disagreement]


def page_words(rows: list[Row]) -> list[tuple[int, str, str]]:
    out = []
    for ri, r in enumerate(rows):
        for w in r.words:
            t = norm(w.t)
            if t:
                out.append((ri, t, w.t))
    return out


def vote_offset(ow, enc: list[str], grams: dict, floor: int) -> int:
    votes = Counter()
    for k in range(len(ow) - 2):
        for i in grams.get((ow[k][1], ow[k + 1][1], ow[k + 2][1]), ()):
            if i - k >= floor - WINDOW_SLACK:
                votes[i - k] += 1
    if not votes:
        raise ValueError("no trigram of the page occurs in the P4 at or after the previous page")
    return votes.most_common(1)[0][0]


def trigram_index(enc: list[str]) -> dict:
    grams: dict = {}
    for i in range(len(enc) - 2):
        grams.setdefault((enc[i], enc[i + 1], enc[i + 2]), []).append(i)
    return grams


def align_page(page: Page, toks: list[Token], enc: list[str], grams: dict, floor: int,
               speakers: set[str]) -> PageAlignment:
    rows = page.rows
    ow = page_words(rows)
    off = vote_offset(ow, enc, grams, floor)
    # never look back before the previous page ended: the play is read in
    # order, and two pages that open alike ("Glou. I am tied to the stake",
    # "Glou. I have a letter") aligned to the same words when it could
    # (p.866/867; doc/agenda.org #build/regenerate-lear, status)
    lo = max(0, floor, off - WINDOW_SLACK)
    hi = min(len(enc), off + len(ow) + WINDOW_SLACK)
    sm = difflib.SequenceMatcher(None, [t for _, t, _ in ow], enc[lo:hi], autojunk=False)
    m: dict[int, int] = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            m[a + k] = lo + b + k

    for r in rows:
        r.start, r.speech = None, False
    prev_end = floor - 1  # a row may not start before the previous page's last word
    for ri, r in enumerate(rows):
        ks = [k for k, (rj, _, _) in enumerate(ow) if rj == ri]
        hits = [k for k in ks if k in m and toks[m[k]].kind != "speaker"]
        if not hits:
            continue
        k0 = hits[0]
        # unmatched words before the first match are the row's own opening
        # words (OCR noise), except the speaker prefix, which is not text
        lead = sum(1 for k in ks[r.prefix_len:] if k < k0 and k not in m)
        r.start = max(m[k0] - lead, prev_end + 1)
        prev_end = m[hits[-1]]
        while toks[r.start].kind == "speaker":  # never start a row on a speaker name
            r.start += 1
        r.extra["cont"] = toks[r.start].cont
        # a row is spoken text if it opens with speech ("Capt. Sound, trumpet!
        # [A trumpet sounds.") or is mostly speech ("[Rising] Never, Regan:")
        kinds = Counter(toks[m[k]].kind for k in hits)
        r.speech = (toks[m[k0]].kind == "speech"
                    or kinds["speech"] > kinds["stage"] + kinds["head"])
        # where the row's speech ends: a trailing stage direction runs further
        spoken = [k for k in hits if toks[m[k]].kind == "speech"]
        r.extra["speech_r"] = _word_right(r, ow, ks, spoken[-1]) if spoken else r.r

    disagreements = _disagreements(page, rows, ow, sm, lo, toks, speakers, m)
    ms = sorted(m.values())
    return PageAlignment(page, ms[0], ms[-1], len(m), len(ow), m, ow, disagreements)


def _word_right(r: Row, ow, ks: list[int], k: int) -> float:
    """Right edge of the row word behind witness-word index k."""
    nth = ks.index(k)
    words = [w for w in r.words if norm(w.t)]
    w = words[nth]
    return w.x + w.w


def _is_prefix(w, speakers) -> bool:
    _, t, raw = w
    return t in speakers or bool(PREFIX.match(raw))


def _disagreements(page, rows, ow, sm, lo, toks, speakers, m) -> list[Disagreement]:
    if not m:
        return []
    first_a, last_a = min(m), max(m)
    out = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal" or a2 <= first_a or a1 > last_a:
            continue  # the window's slack either side of the page
        wit = [ow[k] for k in range(a1, a2) if not _is_prefix(ow[k], speakers)]
        if op == "insert" and not wit:
            continue  # only speaker prefixes: the TEI keeps them apart, not a disagreement
        anchor = ow[a1] if a1 < len(ow) else ow[-1]
        r = rows[anchor[0]]
        out.append(Disagreement(
            page.printed, r.col, r.seq, lo + b1, lo + b2,
            " ".join(t.raw for t in toks[lo + b1:lo + b2]),
            " ".join(w[2] for w in wit), op))
    return out


def witness_reading(al: PageAlignment, tok_from: int, tok_to: int) -> str:
    """What this alignment's witness printed over a P4 token span, as far as it
    can be located: the witness words between the matches bracketing the span."""
    inv = {t: k for k, t in al.ocr_to_tok.items()}
    before = [k for t, k in inv.items() if t < tok_from]
    after = [k for t, k in inv.items() if t >= tok_to]
    if not before or not after:
        return ""
    a, b = max(before) + 1, min(after)
    return " ".join(al.ow[k][2] for k in range(a, b))
