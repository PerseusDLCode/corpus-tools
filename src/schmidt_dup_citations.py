from __future__ import annotations

import re
from bisect import bisect_right

REF_RE = re.compile(r'<ref target="([^"]+)">([^<]*)</ref>')
CIT_RE = re.compile(r"<cit>(.*?)</cit>", re.DOTALL)
RUN_SEP_RE = re.compile(r"[\s.]*")
CIT_GAP_RE = re.compile(r"[\s.;:,!]*")


def _norm_text(text: str) -> str:
    """Collapse internal whitespace so citations that differ only in where
    the source print line happened to wrap (e.g. "Err. V, 122" vs
    "Err. V,\\n              122") still compare equal."""
    return " ".join(text.split())


def collapse_duplicate_citations(text: str) -> tuple[str, int, int]:
    """Collapse runs of 2+ byte-identical adjacent <ref target="X">text</ref>
    citations -- an artifact of automatic tagging, e.g. "Abbess" citing the
    same line 5 times in a row -- down to a single citation.

    A run immediately following a <cit> whose own last <ref> already has
    the same target+text is pure noise: the citation is already captured
    structurally inside that <cit>, so the whole run is deleted rather
    than collapsed to one -- otherwise a later pass merging orphaned
    citations into their <cit> would fold in a second, redundant <ref>.

    Raw-text substitution, not a parse/reserialize pass, per the usual
    reasoning for this hand-formatted file (see strip_bibl_wrapper.py,
    schmidt_cit_unwrap.py).

    Returns (new_text, runs_deleted_as_cit_duplicates, runs_collapsed_to_one).
    """
    refs = list(REF_RE.finditer(text))

    cit_ends: list[int] = []
    cit_keys: dict[int, tuple[str, str]] = {}
    for m in CIT_RE.finditer(text):
        inner_refs = list(REF_RE.finditer(m.group(1)))
        if inner_refs:
            last = inner_refs[-1]
            cit_ends.append(m.end())
            cit_keys[m.end()] = (last.group(1), _norm_text(last.group(2)))

    runs: list[tuple[int, int]] = []
    i = 0
    while i < len(refs):
        j = i
        key = (refs[i].group(1), _norm_text(refs[i].group(2)))
        while j + 1 < len(refs):
            between = text[refs[j].end() : refs[j + 1].start()]
            if RUN_SEP_RE.fullmatch(between) and (
                refs[j + 1].group(1),
                _norm_text(refs[j + 1].group(2)),
            ) == key:
                j += 1
            else:
                break
        if j > i:
            runs.append((i, j))
        i = j + 1

    deletions: list[tuple[int, int]] = []
    dup_of_cit = 0
    collapsed = 0

    for i, j in runs:
        start = refs[i].start()
        key = (refs[i].group(1), _norm_text(refs[i].group(2)))

        matched_cit = False
        idx = bisect_right(cit_ends, start) - 1
        if idx >= 0:
            cit_end = cit_ends[idx]
            gap = text[cit_end:start]
            if CIT_GAP_RE.fullmatch(gap) and cit_keys[cit_end] == key:
                matched_cit = True

        if matched_cit:
            del_start = len(text[:start].rstrip())
            deletions.append((del_start, refs[j].end()))
            dup_of_cit += 1
        else:
            deletions.append((refs[i].end(), refs[j].end()))
            collapsed += 1

    for start, end in sorted(deletions, reverse=True):
        text = text[:start] + text[end:]

    return text, dup_of_cit, collapsed
