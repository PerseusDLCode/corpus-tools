from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

ENTRYFREE_RE = re.compile(r"<entryFree\b[^>]*>.*?</entryFree>", re.S)
ORTH_RE = re.compile(r"<orth\b[^>]*>(.*?)</orth>", re.S)
LB_RE = re.compile(r"<lb\b[^>]*/>")
CIT_OPEN_RE = re.compile(r"<cit>")

# Candidate sense-marker shapes, verified against real gaps in the Schmidt
# lexicon before finalizing (see doc/schmidt-sense-boundary-survey-report.org):
# an arabic numeral, a lowercase letter, or a roman numeral, each followed by
# a close-paren, e.g. "1)", "a)", "II)".
DIGIT_MARKER_RE = re.compile(r"\b([1-9][0-9]?)\)")
LETTER_MARKER_RE = re.compile(r"\b([a-z])\)")
ROMAN_MARKER_RE = re.compile(r"\b([IVXivx]{1,5})\)")
ROMAN_TOKEN_RE = re.compile(r"[IVXivx]+")

# Every roman-numeral-shaped token above IV, checked against real context,
# turned out to be a citation of some kind, never a sense marker: a legal
# statute section ("sec. XXI"), a biblical chapter ("Chap. IX", "St. Luke
# XVI"), or similar (see doc/schmidt-sense-boundary-survey-report.org). The
# genuine top-level roman sense groupings found in this file never exceed
# IV. Capped here rather than guessed at a higher bound.
ROMAN_MARKER_ALLOWED_VALUES = {"I", "II", "III", "IV", "V"}

# Confirmed false-positive shapes, found by reading real context rather than
# guessed at:
#  - "(cf. def. 4)" -- a cross-reference to another sense's number, not a
#    boundary of its own (24 real instances, all identical shape).
#  - "(the sun's)" / "(his soul's)" -- a possessive gloss on a pronoun
#    antecedent; the apostrophe-s happens to end in a bare letter before ")".
#  - "(our --s)" -- Schmidt's dash-for-repeated-headword-stem convention
#    produces a bare suffix letter before ")" that isn't a marker either.
#  - "(i. e. Richard II)" -- a spelled-out regnal-number citation gloss,
#    not a roman-numeral sense marker.
#  - "(St. Luke XVI)" -- a biblical chapter citation, same shape.
#  - "(== poor I)" -- the first-person pronoun "I", indistinguishable from
#    roman numeral "I" by shape alone; see the same-entry-companion check
#    in _find_markers, which only accepts a bare "i"/"I" token when the
#    entry also contains a companion "ii"/"II" elsewhere (a real
#    top-level roman sequence has both; the pronoun never does).
ROMAN_FALSE_POSITIVE_PRECEDING_WORDS = {
    "richard", "henry", "edward", "george", "james", "charles", "pope", "luke",
}


@dataclass
class Marker:
    start: int
    end: int
    level: str  # "arabic" | "letter" | "roman"
    token: str
    lb_aligned: bool
    entry_start: bool


@dataclass
class EntrySurvey:
    orth: str
    start: int
    end: int
    lb_count: int
    markers: list[Marker] = field(default_factory=list)
    bucket: str = ""


@dataclass
class SurveyStats:
    entry_count: int = 0
    bucket_counts: Counter = field(default_factory=Counter)
    marker_level_counts: Counter = field(default_factory=Counter)


def _preceding_word(text: str, pos: int) -> str:
    """Lowercased alphabetic word immediately before pos, skipping whitespace."""
    j = pos
    while j > 0 and text[j - 1].isspace():
        j -= 1
    end = j
    while j > 0 and text[j - 1].isalpha():
        j -= 1
    return text[j:end].lower()


def _find_markers(entry_text: str) -> list[Marker]:
    candidates: list[tuple[int, int, str, str]] = []

    for m in DIGIT_MARKER_RE.finditer(entry_text):
        preceding = entry_text[max(0, m.start() - 6):m.start()].rstrip().lower()
        if preceding.endswith("def."):
            continue
        candidates.append((m.start(), m.end(), "arabic", m.group(1)))

    for m in LETTER_MARKER_RE.finditer(entry_text):
        prev_char = entry_text[m.start() - 1] if m.start() > 0 else ""
        if prev_char in ("'", "-"):
            continue
        candidates.append((m.start(), m.end(), "letter", m.group(1)))

    roman_candidates = []
    for m in ROMAN_MARKER_RE.finditer(entry_text):
        if not ROMAN_TOKEN_RE.fullmatch(m.group(1)):
            continue
        if m.group(1).upper() not in ROMAN_MARKER_ALLOWED_VALUES:
            continue
        if _preceding_word(entry_text, m.start()) in ROMAN_FALSE_POSITIVE_PRECEDING_WORDS:
            continue
        roman_candidates.append((m.start(), m.end(), "roman", m.group(1)))

    # A bare "i"/"I" is indistinguishable from the pronoun "I" by shape
    # alone (e.g. "(== poor I)."); only trust it as a marker when the entry
    # also has a companion "ii"/"II" -- a real top-level roman sequence has
    # both, the pronoun never does.
    has_companion_ii = any(c[3].lower() == "ii" for c in roman_candidates)
    for c in roman_candidates:
        if c[3].lower() == "i" and not has_companion_ii:
            continue
        candidates.append(c)

    candidates.sort(key=lambda c: c[0])

    lb_ends = [m.end() for m in LB_RE.finditer(entry_text)]
    first_cit = CIT_OPEN_RE.search(entry_text)
    first_cit_pos = first_cit.start() if first_cit else len(entry_text)

    markers = []
    for idx, (start, end, level, token) in enumerate(candidates):
        lb_aligned = any(
            lb_end <= start and entry_text[lb_end:start].strip() == ""
            for lb_end in lb_ends
        )
        entry_start = idx == 0 and start < first_cit_pos
        markers.append(Marker(start, end, level, token, lb_aligned, entry_start))

    return markers


def _classify(lb_count: int, markers: list[Marker]) -> str:
    """Bucket an entry by sense-boundary signal strength. Mutually exclusive
    and exhaustive: every entry lands in exactly one of these five buckets.
    """
    if not markers:
        return "lb_noise_only" if lb_count > 0 else "no_marker"

    # The first marker, if nothing but headword/grammar-tag prose precedes
    # it (no <cit> yet), is opening sense 1 rather than closing a transition
    # -- it never needs <lb/> corroboration since there's nothing before it
    # to break from (e.g. "Aim, vb. 1) to point ..."; "Advantage, subst. ...
    # 1) profit, gain: <cit>").
    transitions = markers[1:] if markers[0].entry_start else markers
    if not transitions:
        return "clean"
    if lb_count == 0:
        return "zero_lb_multi_sense"
    if all(m.lb_aligned for m in transitions):
        return "clean"
    return "partial"


def survey(text: str) -> list[EntrySurvey]:
    """Classify every <entryFree> in a Schmidt-lexicon-shaped text by how
    reliably its dictionary senses are signalled by Schmidt's own inline
    numbering convention (1)/2)/a)/b)/I)/II)) and by <lb/>, ahead of any
    future <sense>-reconstruction work. Read-only analysis: does not modify
    the text. Raw-text scan, no DTD-loading parse, matching the rest of
    this round's tooling.
    """
    entries = []
    for m in ENTRYFREE_RE.finditer(text):
        entry_text = m.group(0)
        orth_m = ORTH_RE.search(entry_text)
        orth = re.sub(r"\s+", " ", orth_m.group(1)).strip() if orth_m else ""
        lb_count = len(LB_RE.findall(entry_text))
        markers = _find_markers(entry_text)
        bucket = _classify(lb_count, markers)
        entries.append(EntrySurvey(
            orth=orth, start=m.start(), end=m.end(),
            lb_count=lb_count, markers=markers, bucket=bucket,
        ))
    return entries


def summarize(entries: list[EntrySurvey]) -> SurveyStats:
    stats = SurveyStats(entry_count=len(entries))
    for entry in entries:
        stats.bucket_counts[entry.bucket] += 1
        for marker in entry.markers:
            stats.marker_level_counts[marker.level] += 1
    return stats
