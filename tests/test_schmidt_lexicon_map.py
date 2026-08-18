from __future__ import annotations

import re

import pytest

from tei import TEIDocument
from tln_globe_map import CorpusMap, build_corpus_map


# Schmidt's Shakespeare Lexicon (canonical-engLit/data/schmidt) cites plays
# as `<bibl n="shak. {siglum} {act}.{scene}.{line}">`, using the same
# lowercase sigla and Globe act.scene.line format as the ShakeDraCor-derived
# corpus map. This module exercises the map against ~205k real citations
# pulled from the lexicon, as an end-to-end check independent of the
# hand-built fixtures in test_tln_globe_map.py.
#
# Citations are extracted by parsing @n on every <bibl> element, not by
# regex over the raw XML text: an earlier version of this fixture required
# `<bibl n="` to be textually adjacent and silently missed every citation
# whose source XML wraps the n= attribute onto its own line, undercounting
# the true citation count by ~26k. corpus-tools's repair-schmidt-citations
# command (src/schmidt_citations.py) parses citations the same way.
CITATION_ATTR_RE = re.compile(r'^shak\. ([a-z0-9]+) (.+)$')
CLEAN_GLOBE_REF_RE = re.compile(r'^\d+\.\d+\.\d+$')

# Schmidt sigla for non-dramatic works (poems), which have no counterpart
# in ShakeDraCor's plays-only corpus.
NON_DRAMATIC_SIGLA = {"e3", "lc", "luc", "pht", "pp", "son", "ven"}

# Observed 2026-08-18, after running repair-schmidt-citations (which fixes
# the single-scene-Act collapse bug -- see schmidt-lexicon-tln-crosswalk
# project memory): 204,766 clean act.scene.line citations, 196,012 resolved
# (95.72%). The remaining shortfall is a mix of causes documented in
# canonical-engLit/doc/schmidt-lexicon-tln-crosswalk-report.org (small gaps
# in ShakeDraCor's own Folger through-line sequence -- see
# test_wiv_4_4_9_is_a_known_source_gap below -- plus still-undiagnosed
# patterns this repair pass deliberately left alone). Thresholds sit with
# headroom below the observed numbers so the test guards against
# regressions, not noise.
MIN_RESOLUTION_RATE = 0.955
MIN_CLEAN_CITATIONS = 200_000


@pytest.fixture(scope="session")
def schmidt_citations(schmidt_lexicon_path):
    doc = TEIDocument(schmidt_lexicon_path)
    citations = []
    for bibl in doc.root.iter("{http://www.tei-c.org/ns/1.0}bibl"):
        n = bibl.get("n")
        if n is None:
            continue
        m = CITATION_ATTR_RE.match(n)
        if m:
            citations.append((m.group(1), m.group(2)))
    return citations


@pytest.fixture(scope="session")
def corpus_data(shakedracor_tei_dir):
    return build_corpus_map(shakedracor_tei_dir)


@pytest.fixture(scope="session")
def corpus_map(corpus_data):
    return CorpusMap(corpus_data)


def test_dramatic_sigla_all_have_a_known_play(schmidt_citations, corpus_data):
    known_plays = set(corpus_data["plays"])
    sigla = {play for play, _ref in schmidt_citations}
    unknown = sigla - known_plays - NON_DRAMATIC_SIGLA
    assert unknown == set(), (
        f"Schmidt sigla with no matching ShakeDraCor play: {sorted(unknown)}"
    )


def test_clean_globe_refs_resolve_above_threshold(schmidt_citations, corpus_map):
    attempted = 0
    resolved = 0
    for play, ref in schmidt_citations:
        if play in NON_DRAMATIC_SIGLA:
            continue
        ref = ref.strip()
        if not CLEAN_GLOBE_REF_RE.match(ref):
            continue
        attempted += 1
        if corpus_map.line_number_map(play, globe=ref) is not None:
            resolved += 1

    assert attempted >= MIN_CLEAN_CITATIONS, (
        f"only {attempted} clean citations extracted; lexicon fixture may have changed"
    )
    rate = resolved / attempted
    assert rate >= MIN_RESOLUTION_RATE, (
        f"resolution rate dropped to {rate:.2%} ({resolved}/{attempted})"
    )


def test_hamlet_to_be_or_not_to_be_resolves(corpus_map):
    assert corpus_map.line_number_map("ham", globe="3.1.64") == {
        "tln": 1762, "globe": "3.1.64", "part": None, "element": "l",
    }


def test_wiv_4_4_9_is_a_known_source_gap(corpus_map):
    # ShakeDraCor's own Merry Wives transcription jumps from through-line
    # n="4.4.8" straight to n="4.4.10" -- no line carries "4.4.9". Schmidt
    # cites it (`shak. wiv 4.4.9`), but it can't resolve until ShakeDraCor's
    # source is corrected upstream. This documents one concrete instance of
    # the gap behind test_clean_globe_refs_resolve_above_threshold's shortfall.
    assert corpus_map.line_number_map("wiv", globe="4.4.8") is not None
    assert corpus_map.line_number_map("wiv", globe="4.4.9") is None
    assert corpus_map.line_number_map("wiv", globe="4.4.10") is not None
