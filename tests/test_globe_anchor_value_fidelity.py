"""Anchor-VALUE-fidelity regression check for the Globe re-derivation pipeline.

Renamed from test_globe_anchor_fidelity.py (doc/agenda.org
phase1/fix-globe-anchor-placement): the previous version derived its
"expected" placement by re-invoking the same private decision logic
(_has_content_after, _move_milestone_forward, _first_l_or_p) the code under
test uses, which is a tautology -- it cannot catch a systematic,
same-direction placement bug, because the oracle and the implementation
agree by construction. That is exactly how it passed on the historical bug
this module's docstring used to describe (every Lear anchor one position
out) and, closer to home, could not have caught Defect 1 (verse markers
shifted the same wrong direction as prose markers) either.

What this file verifies instead -- placement-independent, so it survives
future placement changes without becoming a tautology again: every
transcribed Globe/F1 number in the P4 source appears *exactly once* as a P5
milestone @n after conversion (extended with the numbers Defect 2 recovers
from a stray <l @n>, and asserting -- not assuming -- that Defect 3's
split-line merge never silently drops a *numbered* boundary), and @source
travels with exactly that same expected-transcribed set. A hand-verified
placement fixture (whether a given number leads the *correct* text) is
deliberately a separate, later task -- phase1/globe-anchor-fixture -- built
from page images, not from this pipeline's own P4 tree.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from globe_lineation import (
    q,
    rederive,
    parse_p4,
    ConversionStats,
    convert_body,
    reposition_milestones_start_forward,
    _recover_pending_anchors,
    _dedupe_shared_verse_lines,
    _stray_n_is_recoverable,
    GLOBE_EDITION_SOURCE,
)

P5_NS = "http://www.tei-c.org/ns/1.0"


def _local(tag) -> str:
    if not isinstance(tag, str):
        return ""
    return etree.QName(tag).localname


# -- Expected sets, derived structurally from the P4 source ------------------
#
# Globe is keyed (act_n, scene_n, n) since numbering restarts per scene (and
# scene numbers themselves restart per act); F1 is keyed by bare n (one
# whole-play scope, matching reposition_milestones_start_forward's own F1
# call). Reusing _stray_n_is_recoverable here is not the tautology the old
# file's placement helpers were: recoverability is a structural fact about
# the P4 source (does the preceding <l> carry its own <lb ed="G">?), not a
# placement decision the conversion pipeline makes -- the oracle and the
# implementation should of course agree on what the source itself says.


def p4_expected_globe_values(p4_root) -> set[tuple[str, str, str]]:
    expected: set[tuple[str, str, str]] = set()
    for act in p4_root.iter("div1"):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter("div2"):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for lb in scene.iter("lb"):
                if lb.get("ed") == "G" and lb.get("n") is not None:
                    expected.add((act_n, scene_n, lb.get("n")))
            for l in scene.iter("l"):
                n = l.get("n")
                if n is not None and _stray_n_is_recoverable(l):
                    expected.add((act_n, scene_n, n))
    return expected


def p4_expected_f1_values(p4_root) -> set[str]:
    body = p4_root.find("text/body")
    return {lb.get("n") for lb in body.iter("lb") if lb.get("ed") == "F1" and lb.get("n") is not None}


def p5_actual_globe_values(p5_root) -> set[tuple[str, str, str]]:
    actual: set[tuple[str, str, str]] = set()
    for act in p5_root.iter(q("div")):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter(q("div")):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for ms in scene.iter(q("milestone")):
                if ms.get("ed") == "Globe" and ms.get("n") is not None:
                    actual.add((act_n, scene_n, ms.get("n")))
    return actual


def p5_actual_f1_values(p5_root) -> set[str]:
    body = p5_root.find(f"{q('text')}/{q('body')}")
    return {ms.get("n") for ms in body.iter(q("milestone")) if ms.get("ed") == "F1" and ms.get("n") is not None}


def assert_transcribed_values_survive(p4_root, p5_root) -> None:
    """Every transcribed Globe/F1 number in the P4 source -- including the
    two Defect-2 recoverable-stray-anchor cases -- appears exactly once as a
    P5 milestone @n, and nothing else does. This is deliberately silent on
    *where* a number ends up (that's the placement question this file no
    longer tries to adjudicate); it only checks that no number is invented,
    lost, or duplicated across the conversion, recovery, and merge passes."""
    ge, ga = p4_expected_globe_values(p4_root), p5_actual_globe_values(p5_root)
    fe, fa = p4_expected_f1_values(p4_root), p5_actual_f1_values(p5_root)

    missing_globe = ge - ga
    extra_globe = ga - ge
    missing_f1 = fe - fa
    extra_f1 = fa - fe
    assert not missing_globe, f"transcribed Globe anchor(s) went missing: {missing_globe}"
    assert not extra_globe, f"Globe anchor(s) appeared with no P4 source: {extra_globe}"
    assert not missing_f1, f"transcribed F1 anchor(s) went missing: {missing_f1}"
    assert not extra_f1, f"F1 anchor(s) appeared with no P4 source: {extra_f1}"


# -- Parallel check: @source must travel with the transcribed @n value ------


def p5_globe_sources(p5_root) -> dict[tuple[str, str, str], str | None]:
    sources: dict[tuple[str, str, str], str | None] = {}
    for act in p5_root.iter(q("div")):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter(q("div")):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for ms in scene.iter(q("milestone")):
                if ms.get("ed") == "Globe" and ms.get("n") is not None:
                    sources[(act_n, scene_n, ms.get("n"))] = ms.get("source")
    return sources


def p5_globe_unnumbered_with_source(p5_root) -> list[tuple[str, str]]:
    offenders: list[tuple[str, str]] = []
    for act in p5_root.iter(q("div")):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter(q("div")):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for ms in scene.iter(q("milestone")):
                if ms.get("ed") == "Globe" and ms.get("n") is None and ms.get("source") is not None:
                    offenders.append((act_n, scene_n))
    return offenders


def p5_f1_with_source(p5_root) -> list[str | None]:
    body = p5_root.find(f"{q('text')}/{q('body')}")
    return [ms.get("n") for ms in body.iter(q("milestone")) if ms.get("ed") == "F1" and ms.get("source") is not None]


def assert_transcribed_anchors_have_source(p4_root, p5_root) -> None:
    expected_keys = p4_expected_globe_values(p4_root)
    actual_sources = p5_globe_sources(p5_root)

    missing = {key for key in expected_keys if actual_sources.get(key) != GLOBE_EDITION_SOURCE}
    assert not missing, f"transcribed Globe anchor(s) missing source={GLOBE_EDITION_SOURCE!r}: {missing}"

    extra = {
        key: source
        for key, source in actual_sources.items()
        if key not in expected_keys and source is not None
    }
    assert not extra, f"Globe anchor(s) outside the transcribed set unexpectedly carry @source: {extra}"

    unnumbered_offenders = p5_globe_unnumbered_with_source(p5_root)
    assert not unnumbered_offenders, (
        f"unnumbered Globe milestone(s) unexpectedly carry @source: {unnumbered_offenders}"
    )

    f1_offenders = p5_f1_with_source(p5_root)
    assert not f1_offenders, f"F1 milestone(s) unexpectedly carry @source: {f1_offenders}"


# -- Unit-level proof the check has teeth -----------------------------------
#
# Full pipeline (convert -> reposition -> recover -> dedupe) on a synthetic
# P4 fixture that exercises both the ordinary and the recoverable-stray-anchor
# shapes, then deliberately corrupted in each of the ways the real invariants
# guard against.

_SYNTHETIC_P4 = (
    "<TEI.2><text><body>"
    '<div1 type="act" n="1"><div2 type="scene" n="1">'
    '<sp><speaker>A.</speaker><l>earlier line <lb ed="G"/></l></sp>'
    '<sp><speaker>X.</speaker><l>line before, no Globe boundary</l></sp>'
    '<sp><speaker>B.</speaker><l n="111" part="I">Is he pursued? <lb ed="G"/></l></sp>'
    '<sp><speaker>C.</speaker><l part="F">Ay, my good lord. <lb ed="G"/></l></sp>'
    '<sp><speaker>D.</speaker><l>line after <lb n="41" ed="G"/><lb n="311" ed="F1"/></l></sp>'
    "</div2></div1>"
    "</body></text></TEI.2>"
)


def _synthetic_p4_root():
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    return etree.fromstring(_SYNTHETIC_P4.encode("utf-8"), parser)


def _run_full_pipeline(p4_root):
    stats = ConversionStats()
    p5_body = convert_body(p4_root, stats)
    reposition_milestones_start_forward(p5_body, stats)
    _recover_pending_anchors(stats)
    _dedupe_shared_verse_lines(p5_body, stats)
    p5_root = etree.Element(q("TEI"))
    text_el = etree.SubElement(p5_root, q("text"))
    text_el.append(p5_body)
    return p5_root


class TestValueFidelityCheckHasTeeth:
    def test_passes_against_the_real_pipeline(self):
        p4_root = _synthetic_p4_root()
        p5_root = _run_full_pipeline(p4_root)
        assert_transcribed_values_survive(p4_root, p5_root)
        assert_transcribed_anchors_have_source(p4_root, p5_root)

    def test_fails_when_recovery_is_skipped(self):
        # Without _recover_pending_anchors, the "111" stray anchor is simply
        # stripped as noise -- exactly the historical bug this check exists
        # to catch (doc/agenda.org phase1/fix-globe-anchor-placement, Defect 2).
        p4_root = _synthetic_p4_root()
        stats = ConversionStats()
        p5_body = convert_body(p4_root, stats)
        reposition_milestones_start_forward(p5_body, stats)
        _dedupe_shared_verse_lines(p5_body, stats)  # recovery deliberately skipped
        p5_root = etree.Element(q("TEI"))
        text_el = etree.SubElement(p5_root, q("text"))
        text_el.append(p5_body)

        with pytest.raises(AssertionError, match="missing"):
            assert_transcribed_values_survive(p4_root, p5_root)

    def test_fails_when_a_numbered_boundary_is_silently_deleted(self):
        # Simulates a Defect-3 merge bug that deletes a numbered F-half
        # boundary without transferring its value first.
        p4_root = _synthetic_p4_root()
        p5_root = _run_full_pipeline(p4_root)
        body = p5_root.find(f"{q('text')}/{q('body')}")
        target = next(
            ms for ms in body.iter(q("milestone"))
            if ms.get("ed") == "Globe" and ms.get("n") == "111"
        )
        target.getparent().remove(target)

        with pytest.raises(AssertionError, match="missing"):
            assert_transcribed_values_survive(p4_root, p5_root)

    def test_fails_when_source_is_missing_from_a_transcribed_anchor(self):
        p4_root = _synthetic_p4_root()
        p5_root = _run_full_pipeline(p4_root)
        body = p5_root.find(f"{q('text')}/{q('body')}")
        target = next(
            ms for ms in body.iter(q("milestone"))
            if ms.get("ed") == "Globe" and ms.get("n") == "111"
        )
        del target.attrib["source"]

        with pytest.raises(AssertionError, match="missing source"):
            assert_transcribed_anchors_have_source(p4_root, p5_root)

    def test_fails_when_source_appears_on_an_unnumbered_milestone(self):
        p4_root = _synthetic_p4_root()
        p5_root = _run_full_pipeline(p4_root)
        body = p5_root.find(f"{q('text')}/{q('body')}")
        target = next(
            ms for ms in body.iter(q("milestone"))
            if ms.get("ed") == "Globe" and ms.get("n") is None
        )
        target.set("source", GLOBE_EDITION_SOURCE)

        with pytest.raises(AssertionError, match="unnumbered"):
            assert_transcribed_anchors_have_source(p4_root, p5_root)

    def test_fails_when_an_f1_milestone_carries_source(self):
        p4_root = _synthetic_p4_root()
        p5_root = _run_full_pipeline(p4_root)
        body = p5_root.find(f"{q('text')}/{q('body')}")
        target = next(ms for ms in body.iter(q("milestone")) if ms.get("ed") == "F1")
        target.set("source", GLOBE_EDITION_SOURCE)

        with pytest.raises(AssertionError, match="F1 milestone"):
            assert_transcribed_anchors_have_source(p4_root, p5_root)


# -- Retroactive regression guard against the real, already-shipped plays ----

LEAR_P4 = Path(__file__).parent.parent.parent / "canonical-engLit" / "Renaissance" / "Shakespeare" / "opensource" / "lr.xml"
LEAR_P5 = Path(__file__).parent.parent.parent / "canonical-engLit" / "data" / "shakespeare" / "lr" / "shakespeare.lr.globe.xml"


@pytest.mark.skipif(not LEAR_P4.exists() or not LEAR_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_lear_transcribed_values_survive():
    p4_root = parse_p4(LEAR_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(LEAR_P5), p5_parser).getroot()
    assert_transcribed_values_survive(p4_root, p5_root)


@pytest.mark.skipif(not LEAR_P4.exists() or not LEAR_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_lear_transcribed_anchors_have_source():
    p4_root = parse_p4(LEAR_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(LEAR_P5), p5_parser).getroot()
    assert_transcribed_anchors_have_source(p4_root, p5_root)


ANTONY_P4 = Path(__file__).parent.parent.parent / "canonical-engLit" / "Renaissance" / "Shakespeare" / "opensource" / "ant.xml"
ANTONY_P5 = Path(__file__).parent.parent.parent / "canonical-engLit" / "data" / "shakespeare" / "ant" / "shakespeare.ant.globe.xml"


@pytest.mark.skipif(not ANTONY_P4.exists() or not ANTONY_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_antony_transcribed_values_survive():
    p4_root = parse_p4(ANTONY_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(ANTONY_P5), p5_parser).getroot()
    assert_transcribed_values_survive(p4_root, p5_root)


@pytest.mark.skipif(not ANTONY_P4.exists() or not ANTONY_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_antony_transcribed_anchors_have_source():
    p4_root = parse_p4(ANTONY_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(ANTONY_P5), p5_parser).getroot()
    assert_transcribed_anchors_have_source(p4_root, p5_root)
