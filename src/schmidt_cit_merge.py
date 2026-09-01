from __future__ import annotations

import re
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass, field

CIT_OPEN_RE = re.compile(r"<cit>")
CIT_CLOSE_RE = re.compile(r"</cit>")
ENTRYFREE_CLOSE_RE = re.compile(r"</entryFree>")
LB_RE = re.compile(r"<lb\b[^>]*/>")
REF_RE = re.compile(r"<ref\b[^>]*>.*?</ref>", re.S)

# A gap between orphaned refs is safe to drop outright only when it carries
# no recoverable meaning of its own: a single separator character (or
# nothing at all). See doc/forum.org #citations/orphaned-cit-merge --
# Cliff: once refs are adjacent siblings inside <cit>, an individual
# separator's "this punctuation mark separated ref A from ref B" meaning is
# unrecoverable regardless of where the character ends up.
PUNCT_RE = re.compile(r"^[.,;]?$")

# Recognized apparatus/cross-reference patterns -- schema-valid only when
# wrapped in <note> (perseus_lexical.rng's <cit> content model is
# element-only: no bare text, <mentioned> not allowed directly, <note> is).
# Kept deliberately narrow and verified against real Schmidt gaps rather
# than guessed at; anything else stops the merge instead of being forced
# into a shape it wasn't confirmed to have.
CF_RE = re.compile(r"^[.,;]?\s*\(?cf\.$", re.I)
QV_RE = re.compile(r"^\(?q\.\s*v\.\)?\.?$", re.I)
QQFF_RE = re.compile(r"^\(?(?:Qq?|Ff?)\.\s*<mentioned>.*?</mentioned>\)\.?$", re.I | re.S)
# Closes a "(cf." (etc.) opened by the immediately preceding recognized gap --
# confirmed the overwhelmingly common shape of a bare ")." gap in this file.
CLOSE_PAREN_RE = re.compile(r"^\)\.?$")

WS_RE = re.compile(r"\s+")
LEADING_WS_RE = re.compile(r"^\s*")
TRAILING_WS_RE = re.compile(r"\s*$")


def _normalize(gap: str) -> str:
    return WS_RE.sub(" ", gap.strip())


def _classify(gap: str) -> str:
    norm = _normalize(gap)
    if PUNCT_RE.match(norm):
        return "punct"
    if CF_RE.match(norm) or QV_RE.match(norm) or QQFF_RE.match(norm) or CLOSE_PAREN_RE.match(norm):
        return "apparatus"
    return "other"


def _wrap_note(gap: str) -> str:
    """Wrap a gap's non-whitespace core in <note>, preserving surrounding whitespace."""
    lead = LEADING_WS_RE.match(gap).group()
    trail = TRAILING_WS_RE.search(gap).group()
    core = gap[len(lead): len(gap) - len(trail)] if trail else gap[len(lead):]
    return f"{lead}<note>{core}</note>{trail}"


@dataclass
class MergeStats:
    cits_merged: int = 0
    refs_absorbed: int = 0
    notes_wrapped: int = 0
    full_merges: int = 0
    partial_merges: int = 0
    residual_gaps: Counter = field(default_factory=Counter)


def merge_orphaned_citations(text: str) -> tuple[str, MergeStats]:
    """Absorb bare <ref> siblings trailing a <cit> into that <cit>, up to
    (not including) the next <cit>, the enclosing </entryFree>, or the next
    <lb/> (senses change there) -- an automatic-tagging artifact where <cit>
    only ever captured the first citation after a <quote>, leaving every
    further citation for that quote as an orphaned sibling (e.g. "an
    hundred," had 10 citations on the printed page; only the first ended up
    inside its <cit>).

    Each gap between orphaned refs is classified and handled independently,
    absorbing refs left to right until a gap fails to classify:

    - pure separator punctuation (a lone ``.``, ``,``, ``;``, or nothing) is
      dropped -- except the final one immediately before the absorption
      boundary, which is left outside the merged <cit> untouched (it closes
      the whole sense rather than separating two citations, and reads more
      naturally as ``</cit>. <cit>`` than ``</cit><cit>``);
    - a recognized apparatus/cf./q. v. pattern is wrapped in <note> and kept,
      satisfying <cit>'s element-only content model;
    - anything else stops the merge right there (partial merge -- absorb
      what's safe, leave the rest still-orphaned) rather than guess. This
      is expected to concentrate in prose introducing a new sense with no
      <cit>/<lb/> marking of its own -- deferred to future <lb/>-based
      <sense> reconstruction work, not resolved here.

    Raw-text substitution, not a parse/reserialize pass, per the usual
    reasoning for this hand-formatted file. <cit> elements never nest in
    this file (verified), so the absorption boundary is unambiguous.
    """
    cit_opens = [m.start() for m in CIT_OPEN_RE.finditer(text)]
    cit_closes = [(m.start(), m.end()) for m in CIT_CLOSE_RE.finditer(text)]
    entryfree_closes = [m.start() for m in ENTRYFREE_CLOSE_RE.finditer(text)]
    lb_starts = [m.start() for m in LB_RE.finditer(text)]

    stats = MergeStats()
    edits: list[tuple[int, int, str]] = []

    for close_start, close_end in cit_closes:
        i = bisect_right(cit_opens, close_end)
        next_open = cit_opens[i] if i < len(cit_opens) else len(text)
        j = bisect_right(entryfree_closes, close_end)
        next_ef = entryfree_closes[j] if j < len(entryfree_closes) else len(text)
        k = bisect_right(lb_starts, close_end)
        next_lb = lb_starts[k] if k < len(lb_starts) else len(text)
        boundary = min(next_open, next_ef, next_lb)

        span = text[close_end:boundary]
        refs = [(m.start(), m.end()) for m in REF_RE.finditer(span)]
        if not refs:
            continue

        n = len(refs)
        gaps = []
        pos = 0
        for r_start, r_end in refs:
            gaps.append(span[pos:r_start])
            pos = r_end
        gaps.append(span[pos:])  # trailing gap after the last ref

        gap_kinds = []
        for idx in range(n):
            kind = _classify(gaps[idx])
            if kind == "other":
                break
            gap_kinds.append(kind)
        m = len(gap_kinds)

        if m < n:
            stats.residual_gaps[_normalize(gaps[m])] += 1
        if m == 0:
            continue

        pieces = []
        for idx in range(m):
            if gap_kinds[idx] == "apparatus":
                pieces.append(_wrap_note(gaps[idx]))
                stats.notes_wrapped += 1
            # punct gaps are dropped -- omitted entirely
            r_start, r_end = refs[idx]
            pieces.append(span[r_start:r_end])

        last_absorbed_end = refs[m - 1][1]
        trailing_kind = _classify(gaps[n]) if m == n else None
        if trailing_kind == "apparatus":
            pieces.append(_wrap_note(gaps[n]))
            stats.notes_wrapped += 1
            merge_end_abs = boundary
        else:
            if trailing_kind == "other":
                stats.residual_gaps[_normalize(gaps[n])] += 1
            merge_end_abs = close_end + last_absorbed_end

        edits.append((close_start, merge_end_abs, "".join(pieces) + "</cit>"))
        stats.cits_merged += 1
        stats.refs_absorbed += m
        if m == n:
            stats.full_merges += 1
        else:
            stats.partial_merges += 1

    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]

    return text, stats
