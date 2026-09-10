"""Anchor-text-fidelity regression check for the Globe re-derivation pipeline.

Not specific to any one play. Motivated by a real bug in the King Lear
pilot: an earlier cut of globe_lineation.py placed milestones trailing the
content they number (matching P4's own physical <lb> placement), which put
every transcribed Globe anchor one position out of place -- and
test_globe_lineation_reposition.py, which only checks structural shape, kept
passing throughout. See doc/agenda.org phase1/rederive-antony-p5:
"every transcribed number must still precede the same text it preceded in
the P4, checked for both reference systems. This belongs in the test suite,
not in a review pass."

The derivation this module checks: P4's own <lb n="V" ed="...">  convention
places the marker trailing the line it numbers (V labels the content BEFORE
the marker). After start-forward repositioning
(globe_lineation._shift_scope_to_start_forward), each boundary's number
shifts to the *following* boundary's original value, and (unless embedded
mid-sentence) the boundary itself physically relocates to lead the next
content element. The upshot: the P5 milestone that ends up carrying number V
should be the *same physical boundary* that, in the raw P4 source, is the
one immediately BEFORE the P4 <lb> that originally carried n="V" -- so the
"text V should lead" is exactly the text that boundary already led into
*before* conversion (its own forward-walk text in the raw P4 tree). This
lets the check be derived purely from the P4 source, independent of the
conversion code being tested.
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
    ENTITY_MAP,
    GLOBE_EDITION_SOURCE,
    NS,
    _has_content_after,
    _move_milestone_forward,
    _first_l_or_p,
    _insert_leading,
)

P5_NS = "http://www.tei-c.org/ns/1.0"
LEAD_CHARS = 40


def _local(tag) -> str:
    # A raw lxml .iter() (unfiltered by tag) yields comments, PIs, and (with
    # resolve_entities=False) _Entity nodes too, whose .tag is not a string --
    # treat those uniformly as "not a boundary/content element" rather than
    # raising, matching convert_element's own non-string-tag guard.
    if not isinstance(tag, str):
        return ""
    return etree.QName(tag).localname


def _norm(text: str) -> str:
    return " ".join(text.split())


def _text_of(el) -> str:
    return _norm("".join(el.itertext()))


def _forward_text(node, boundary_local_name: str, lead_chars: int = LEAD_CHARS) -> str:
    """Text immediately following node, skipping over immediately-adjacent
    sibling boundary markers (identified by boundary_local_name) that carry no
    text of their own -- for reading a P5 <milestone>'s own already-correct
    leading text directly off its .tail (boundary_local_name="milestone").
    Not used for P4 <lb> prediction -- see _p4_expected_leading_text, which
    additionally has to cross into the next content element when a boundary
    is the last child of its parent (P4's <lb> nests inside <p>/<sp>, so
    "falls off the end of the immediate parent" does not mean "nothing
    follows in the scope")."""
    cur = node
    while True:
        if cur.tail and cur.tail.strip():
            return _norm(cur.tail)[:lead_chars]
        nxt = cur.getnext()
        if nxt is None:
            return ""
        if _local(nxt.tag) != boundary_local_name:
            return _text_of(nxt)[:lead_chars]
        cur = nxt


def _leading_text_of(el, lead_chars: int = LEAD_CHARS) -> str:
    """The text a milestone inserted as el's leading child would carry as its
    own .tail -- mirrors globe_lineation._insert_leading (new_ms.tail =
    target.text) followed by _forward_text's own fallthrough exactly: el's
    direct text if any (NOT el's full recursive text -- el may already
    contain a later interior milestone, e.g. an F1 marker mid-line, whose
    text belongs to that interior milestone, not one newly inserted at el's
    start); otherwise, if el's own text is empty because its first child is
    itself real content with no preceding text (e.g. a <stage> direction
    opening the line), that child's own text; if the first child is itself a
    further boundary, that boundary's own forward-walk text."""
    text = el.text or ""
    if text.strip():
        return _norm(text)[:lead_chars]
    children = list(el)
    if not children:
        return ""
    first = children[0]
    if _local(first.tag) == "lb":
        return _forward_text(first, "lb", lead_chars)
    return _text_of(first)[:lead_chars]


def _first_content_text(scope_el, content_tags: set[str], lead_chars: int = LEAD_CHARS) -> str:
    for el in scope_el.iter():
        if el is scope_el:
            continue
        if _local(el.tag) in content_tags:
            return _leading_text_of(el, lead_chars)
    return ""


def _collapse_reg_shorthand(root) -> None:
    """Mutate root in place, collapsing every P4 <reg orig="X">Y</reg> element
    to plain text Y merged into the surrounding text flow -- mirrors
    globe_lineation._reg_text/convert_children's own reg-collapse exactly
    (the real conversion does this too, so a raw, uncollapsed P4 tree
    understates where a text run actually continues to in the P5 output).
    Call once on a freshly parsed P4 tree before deriving expected texts."""
    for reg in list(root.iter("reg")):
        parent = reg.getparent()
        prev = reg.getprevious()
        text = (reg.text or "") + (reg.tail or "")
        if prev is not None:
            prev.tail = (prev.tail or "") + text
        else:
            parent.text = (parent.text or "") + text
        parent.remove(reg)


def _collapse_entities(root) -> None:
    """Mutate root in place, resolving every unresolved-entity node (present
    because parse_p4 parses with resolve_entities=False) via the same
    ENTITY_MAP globe_lineation.convert_children uses, merging the resolved
    text into the surrounding flow. Without this, a text run that in the
    real P5 output continues right through e.g. "C&aelig;sar" ("Cæsar")
    would, on the raw P4 side, look like it stops dead after "C" -- the
    entity node is a genuine child node interrupting .text/.tail, same
    class of issue as <reg>."""
    for node in list(root.iter()):
        if not isinstance(node, etree._Entity):
            continue
        name = node.name
        if name not in ENTITY_MAP:
            raise AssertionError(f"Unmapped entity &{name}; while collapsing for fidelity check")
        parent = node.getparent()
        prev = node.getprevious()
        text = ENTITY_MAP[name] + (node.tail or "")
        if prev is not None:
            prev.tail = (prev.tail or "") + text
        else:
            parent.text = (parent.text or "") + text
        parent.remove(node)


def _p4_lbs(scope_el, ed: str):
    return [el for el in scope_el.iter("lb") if el.get("ed") == ed]


def _p4_next_content_element(node, scope_el):
    """First <l>/<p> in document order strictly after node, within scope_el --
    mirrors globe_lineation._next_content_element exactly, for the raw P4 tree."""
    found_self = False
    for el in scope_el.iter():
        if el is node:
            found_self = True
            continue
        if found_self and _local(el.tag) in ("l", "p"):
            return el
    return None


def _p4_expected_leading_text(lb, scope_el, lead_chars: int = LEAD_CHARS) -> str:
    """What text this P4 boundary's number should lead into after correct
    start-forward repositioning. Mirrors globe_lineation._has_content_after +
    _move_milestone_forward/_next_content_element exactly (same two-branch
    decision: embedded mid-sentence vs. terminal-and-relocated), just
    operating on raw, unconverted P4 <lb> elements (boundary tag "lb")
    instead of P5 <milestone> elements (boundary tag "milestone"), and
    returning text instead of mutating the tree."""
    node = lb
    while True:
        if node.tail and node.tail.strip():
            return _norm(node.tail)[:lead_chars]
        nxt = node.getnext()
        if nxt is None:
            # Terminal within this parent -- P4's <lb> nests inside <p>/<sp>,
            # so this does NOT mean "nothing follows in the scope": the real
            # conversion relocates a terminal boundary to lead the next
            # <l>/<p> anywhere later in scope, exactly like
            # _move_milestone_forward does for the converted output.
            target = _p4_next_content_element(lb, scope_el)
            return _leading_text_of(target, lead_chars) if target is not None else ""
        if _local(nxt.tag) != "lb":
            return _text_of(nxt)[:lead_chars]
        node = nxt


def globe_expected_texts(p4_root, lead_chars: int = LEAD_CHARS) -> dict[tuple[str, str, str], str]:
    """{(act_n, scene_n, anchor_n): text the anchor should lead into
    post-conversion}, for every transcribed Globe anchor, derived directly
    from the P4 source. Keyed by (act, scene, n) -- Globe numbering restarts
    per scene, and scene numbers themselves restart per act (every act has a
    "Scene 1"), so scene_n alone is not a unique key."""
    expected: dict[tuple[str, str, str], str] = {}
    for act in p4_root.iter("div1"):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter("div2"):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            lbs = _p4_lbs(scene, "G")
            for i, lb in enumerate(lbs):
                n = lb.get("n")
                if n is None:
                    continue
                if i == 0:
                    text = _first_content_text(scene, {"l", "p"}, lead_chars)
                else:
                    text = _p4_expected_leading_text(lbs[i - 1], scene, lead_chars)
                expected[(act_n, scene_n, n)] = text
    return expected


def globe_actual_texts(p5_root, lead_chars: int = LEAD_CHARS) -> dict[tuple[str, str, str], str]:
    actual: dict[tuple[str, str, str], str] = {}
    for act in p5_root.iter(q("div")):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter(q("div")):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for ms in scene.iter(q("milestone")):
                if ms.get("ed") != "Globe":
                    continue
                n = ms.get("n")
                if n is None:
                    continue
                actual[(act_n, scene_n, n)] = _forward_text(ms, "milestone", lead_chars)
    return actual


def f1_expected_texts(p4_root, lead_chars: int = LEAD_CHARS) -> dict[str, str]:
    """F1 has no per-scene restart -- one whole-play scope, matching
    globe_lineation.reposition_milestones_start_forward's own F1 call."""
    body = p4_root.find("text/body")
    lbs = _p4_lbs(body, "F1")
    expected: dict[str, str] = {}
    for i, lb in enumerate(lbs):
        n = lb.get("n")
        if n is None:
            continue
        if i == 0:
            text = _first_content_text(body, {"l", "p"}, lead_chars)
        else:
            text = _p4_expected_leading_text(lbs[i - 1], body, lead_chars)
        expected[n] = text
    return expected


def f1_actual_texts(p5_root, lead_chars: int = LEAD_CHARS) -> dict[str, str]:
    body = p5_root.find(f"{q('text')}/{q('body')}")
    actual: dict[str, str] = {}
    for ms in body.iter(q("milestone")):
        if ms.get("ed") != "F1":
            continue
        n = ms.get("n")
        if n is None:
            continue
        actual[n] = _forward_text(ms, "milestone", lead_chars)
    return actual


def assert_transcribed_anchors_precede_same_text(p4_root, p5_root, lead_chars: int = LEAD_CHARS) -> None:
    """The regression the Lear pilot needed and didn't have: for every
    transcribed anchor, in both reference systems, the text it precedes after
    conversion must be the same text it preceded (per its own trailing
    convention) in the P4 source. Fails loudly, with the mismatching anchors
    and both texts, rather than passing silently the way
    test_globe_lineation_reposition.py did while every Lear anchor sat one
    position out of place."""
    # Scope collapsing to text/body only -- the real conversion (convert_body)
    # never looks at the teiHeader, which can carry unrelated DTD entities
    # (e.g. a boilerplate &responsibility; disclaimer) that ENTITY_MAP was
    # never meant to cover and that this check has no reason to care about.
    p4_body = p4_root.find("text/body")
    _collapse_reg_shorthand(p4_body)
    _collapse_entities(p4_body)
    ge, ga = globe_expected_texts(p4_root, lead_chars), globe_actual_texts(p5_root, lead_chars)
    fe, fa = f1_expected_texts(p4_root, lead_chars), f1_actual_texts(p5_root, lead_chars)

    globe_mismatches = {
        key: (expected, ga.get(key)) for key, expected in ge.items() if ga.get(key) != expected
    }
    f1_mismatches = {
        key: (expected, fa.get(key)) for key, expected in fe.items() if fa.get(key) != expected
    }
    assert not globe_mismatches, f"Globe anchor(s) lead the wrong text: {globe_mismatches}"
    assert not f1_mismatches, f"F1 anchor(s) lead the wrong text: {f1_mismatches}"


# -- Parallel check: @source must travel with the transcribed @n value ------
#
# doc/agenda.org phase1/milestone-source-provenance, verbatim: "add the
# parallel assertion that every @n of transcribed origin, and only those,
# carries @source after repositioning." globe_expected_texts' own key set is
# already exactly "every Globe anchor transcribed in the P4 source" (a key
# only exists there when the P4 <lb> itself carried @n), so it doubles as the
# expected-transcribed set here -- no separate P4 walk needed.


def globe_actual_sources(p5_root) -> dict[tuple[str, str, str], str | None]:
    """{(act_n, scene_n, n): @source value (or None)}, for every Globe
    milestone that carries @n in the converted P5 tree -- keyed exactly like
    globe_actual_texts, so it can be compared key-for-key against
    globe_expected_texts' key set."""
    actual: dict[tuple[str, str, str], str | None] = {}
    for act in p5_root.iter(q("div")):
        if act.get("type") != "act":
            continue
        act_n = act.get("n")
        for scene in act.iter(q("div")):
            if scene.get("type") != "scene":
                continue
            scene_n = scene.get("n")
            for ms in scene.iter(q("milestone")):
                if ms.get("ed") != "Globe":
                    continue
                n = ms.get("n")
                if n is None:
                    continue
                actual[(act_n, scene_n, n)] = ms.get("source")
    return actual


def globe_unnumbered_with_source(p5_root) -> list[tuple[str, str]]:
    """(act_n, scene_n) of any unnumbered Globe milestone (no @n) that
    nonetheless carries @source -- should always be empty. @source only ever
    belongs alongside a transcribed @n."""
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


def f1_milestones_with_source(p5_root) -> list[str | None]:
    """@n values of any F1 milestone that carries @source -- should always be
    empty. Every F1 anchor arrives by the same route (all numbered, none
    interpolated), so none of them discriminate evidence from inference the
    way a Globe @source does; see the globe_lineation module docstring."""
    body = p5_root.find(f"{q('text')}/{q('body')}")
    return [ms.get("n") for ms in body.iter(q("milestone")) if ms.get("ed") == "F1" and ms.get("source") is not None]


def assert_transcribed_anchors_have_source(p4_root, p5_root) -> None:
    """Parallel to assert_transcribed_anchors_precede_same_text: every Globe
    anchor transcribed in the P4 source must carry source=GLOBE_EDITION_SOURCE
    in the converted P5 tree, and only those -- no unnumbered Globe milestone
    and no F1 milestone may carry @source. Both directions matter: a bug that
    just always sets @source would pass a source-only-present check
    trivially."""
    expected_keys = set(globe_expected_texts(p4_root).keys())
    actual_sources = globe_actual_sources(p5_root)

    missing = {key for key in expected_keys if actual_sources.get(key) != GLOBE_EDITION_SOURCE}
    assert not missing, f"transcribed Globe anchor(s) missing source={GLOBE_EDITION_SOURCE!r}: {missing}"

    extra = {
        key: source
        for key, source in actual_sources.items()
        if key not in expected_keys and source is not None
    }
    assert not extra, f"Globe anchor(s) outside the transcribed set unexpectedly carry @source: {extra}"

    unnumbered_offenders = globe_unnumbered_with_source(p5_root)
    assert not unnumbered_offenders, (
        f"unnumbered Globe milestone(s) unexpectedly carry @source: {unnumbered_offenders}"
    )

    f1_offenders = f1_milestones_with_source(p5_root)
    assert not f1_offenders, f"F1 milestone(s) unexpectedly carry @source: {f1_offenders}"


# -- Unit-level proof the check has teeth -----------------------------------
#
# A small synthetic P4 fixture, converted correctly (via the real pipeline)
# and also converted by a deliberately reintroduced version of the historical
# bug (milestones left trailing, i.e. un-repositioned) -- confirming the
# check passes on the former and fails on the latter, without needing a
# throwaway branch or touching any real corpus file.

_SYNTHETIC_P4 = (
    '<TEI.2><text><body>'
    '<div1 type="act" n="1"><div2 type="scene" n="1">'
    '<p>In three our kingdom <lb ed="G"/></p>'
    '<p>To shake all cares <lb n="41" ed="G"/><lb n="311" ed="F1"/></p>'
    '<p>Conferring them <lb ed="G"/><lb n="312" ed="F1"/></p>'
    "</div2></div1>"
    "</body></text></TEI.2>"
)


def _synthetic_p4_root():
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    return etree.fromstring(_SYNTHETIC_P4.encode("utf-8"), parser)


class TestFidelityCheckHasTeeth:
    def test_passes_against_correctly_repositioned_output(self):
        p4_root = _synthetic_p4_root()
        stats = ConversionStats()
        p5_body = convert_body(p4_root, stats)
        reposition_milestones_start_forward(p5_body, stats)
        p5_root = etree.Element(q("TEI"))
        text_el = etree.SubElement(p5_root, q("text"))
        text_el.append(p5_body)

        # Should not raise: the real pipeline's repositioning is correct.
        assert_transcribed_anchors_precede_same_text(p4_root, p5_root)

    def test_fails_against_the_historical_trailing_placement_bug(self):
        # Reintroduce the pre-fix behavior directly: convert the body WITHOUT
        # repositioning, so every milestone sits exactly where P4's <lb>
        # physically was (trailing its content) -- the bug that shipped one
        # position out of place for all 274 Lear anchors.
        p4_root = _synthetic_p4_root()
        stats = ConversionStats()
        p5_body = convert_body(p4_root, stats)  # deliberately skip reposition_milestones_start_forward
        p5_root = etree.Element(q("TEI"))
        text_el = etree.SubElement(p5_root, q("text"))
        text_el.append(p5_body)

        with pytest.raises(AssertionError):
            assert_transcribed_anchors_precede_same_text(p4_root, p5_root)


def _broken_shift_scope_source_stuck(scope_el, ed: str, scope_label: str, stats: ConversionStats) -> None:
    """A deliberately reintroduced version of the exact bug
    doc/agenda.org phase1/milestone-source-provenance warns about: @n shifts
    correctly (identical logic, and reuse of the real move/relabel helpers,
    to globe_lineation._shift_scope_to_start_forward), but @source is never
    read, shifted, or cleared -- it is simply left wherever _convert_lb put
    it, stranding it one boundary-slot behind every shifted @n. This is *not*
    a copy-paste of an old version of the fixed function; it's the bug the
    fix specifically guards against, reconstructed to prove the new check
    catches it."""
    milestones = [m for m in scope_el.iter(q("milestone")) if m.get("ed") == ed]
    if not milestones:
        return
    original_values = [m.get("n") for m in milestones]
    shifted_values = original_values[1:] + [None]
    for m, new_n in zip(milestones, shifted_values):
        embedded_in_prose = _has_content_after(m)
        if new_n is not None:
            m.set("n", new_n)
        elif "n" in m.attrib:
            del m.attrib["n"]
        # @source deliberately untouched here -- this is the bug.
        if not embedded_in_prose:
            _move_milestone_forward(m, scope_el)
    leading_value = original_values[0]
    if leading_value is not None:
        new_ms = etree.Element(q("milestone"))
        new_ms.set("unit", "line")
        new_ms.set("ed", ed)
        new_ms.set("n", leading_value)
        # @source deliberately not inherited here either -- same bug.
        target = _first_l_or_p(scope_el)
        _insert_leading(target, new_ms)
        stats.synthesized_leading_milestones.append((ed, scope_label, leading_value))


def _broken_reposition_source_stuck(new_body, stats: ConversionStats) -> None:
    """Same scope-selection order as reposition_milestones_start_forward, but
    using the source-stuck broken shift above instead of the real one."""
    _broken_shift_scope_source_stuck(new_body, "F1", "(whole play)", stats)
    for scene in new_body.iter(q("div")):
        if scene.get("type") != "scene":
            continue
        act_n = scene.xpath("ancestor::tei:div[@type='act'][1]/@n", namespaces=NS)
        label = f"Act {act_n[0] if act_n else '?'}, Scene {scene.get('n')}"
        _broken_shift_scope_source_stuck(scene, "Globe", label, stats)


class TestSourceCheckHasTeeth:
    def test_passes_when_source_travels_with_the_shifted_value(self):
        p4_root = _synthetic_p4_root()
        stats = ConversionStats()
        p5_body = convert_body(p4_root, stats)
        reposition_milestones_start_forward(p5_body, stats)  # real, fixed repositioning
        p5_root = etree.Element(q("TEI"))
        text_el = etree.SubElement(p5_root, q("text"))
        text_el.append(p5_body)

        # Should not raise: @source shifted in lockstep with @n.
        assert_transcribed_anchors_have_source(p4_root, p5_root)

    def test_fails_when_source_stays_on_the_original_element(self):
        p4_root = _synthetic_p4_root()
        stats = ConversionStats()
        p5_body = convert_body(p4_root, stats)
        _broken_reposition_source_stuck(p5_body, stats)  # deliberately broken repositioning
        p5_root = etree.Element(q("TEI"))
        text_el = etree.SubElement(p5_root, q("text"))
        text_el.append(p5_body)

        with pytest.raises(AssertionError):
            assert_transcribed_anchors_have_source(p4_root, p5_root)


# -- Retroactive regression guard against the real, already-shipped Lear pair --

LEAR_P4 = Path(__file__).parent.parent.parent / "canonical-engLit" / "Renaissance" / "Shakespeare" / "opensource" / "lr.xml"
LEAR_P5 = Path(__file__).parent.parent.parent / "canonical-engLit" / "data" / "shakespeare" / "lr" / "shakespeare.lr.globe.xml"


@pytest.mark.skipif(not LEAR_P4.exists() or not LEAR_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_lear_anchors_precede_same_text_as_p4():
    p4_root = parse_p4(LEAR_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(LEAR_P5), p5_parser).getroot()
    assert_transcribed_anchors_precede_same_text(p4_root, p5_root)


@pytest.mark.skipif(not LEAR_P4.exists() or not LEAR_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_lear_transcribed_anchors_have_source():
    p4_root = parse_p4(LEAR_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(LEAR_P5), p5_parser).getroot()
    assert_transcribed_anchors_have_source(p4_root, p5_root)


ANTONY_P4 = Path(__file__).parent.parent.parent / "canonical-engLit" / "Renaissance" / "Shakespeare" / "opensource" / "ant.xml"
ANTONY_P5 = Path(__file__).parent.parent.parent / "canonical-engLit" / "data" / "shakespeare" / "ant" / "shakespeare.ant.globe.xml"


@pytest.mark.skipif(not ANTONY_P4.exists() or not ANTONY_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_antony_anchors_precede_same_text_as_p4():
    p4_root = parse_p4(ANTONY_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(ANTONY_P5), p5_parser).getroot()
    assert_transcribed_anchors_precede_same_text(p4_root, p5_root)


@pytest.mark.skipif(not ANTONY_P4.exists() or not ANTONY_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_real_antony_transcribed_anchors_have_source():
    p4_root = parse_p4(ANTONY_P4)
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(ANTONY_P5), p5_parser).getroot()
    assert_transcribed_anchors_have_source(p4_root, p5_root)
