from __future__ import annotations

from lxml import etree

from globe_lineation import (
    ConversionError,
    ConversionStats,
    convert_body,
    q,
    reposition_milestones_start_forward,
    _dedupe_shared_verse_lines,
    _recover_pending_anchors,
)

P5_NS = "http://www.tei-c.org/ns/1.0"
P4_PARSER = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)


def _body(inner: str) -> etree._Element:
    xml = f'<TEI xmlns="{P5_NS}"><text><body>{inner}</body></text></TEI>'
    root = etree.fromstring(xml.encode("utf-8"))
    return root.find(f"{q('text')}/{q('body')}")


def _rederive_fragment(p4_body_xml: str) -> tuple[etree._Element, ConversionStats]:
    """Run a P4 body fragment through the same sequence rederive() uses:
    convert -> reposition -> recover stray anchors -> merge split lines."""
    p4_doc = f"<TEI.2><text><body>{p4_body_xml}</body></text></TEI.2>"
    p4_root = etree.fromstring(p4_doc.encode("utf-8"), P4_PARSER)
    stats = ConversionStats()
    new_body = convert_body(p4_root, stats)
    reposition_milestones_start_forward(new_body, stats)
    _recover_pending_anchors(stats)
    _dedupe_shared_verse_lines(new_body, stats)
    return new_body, stats


def _globe_milestone(l_el):
    """l_el's leading Globe milestone, or None -- assumes at most one is of
    interest for these tests (a trailing scope-terminal one, if any, is a
    distinct concern these tests avoid conflating by construction)."""
    if len(l_el) == 0:
        return None
    first = l_el[0]
    return first if first.get("ed") == "Globe" else None


def _globe_ns(body):
    return [m.get("n") for m in body.iter(q("milestone")) if m.get("ed") == "Globe"]


def _text_of(el) -> str:
    return "".join(el.itertext()).strip()


class TestVerseRepositioning:
    """A terminal verse marker (nothing follows within its own <l>) moves to
    lead the NEXT <l>, carrying its OWN original @n/@source unchanged --
    never relabeled with some other marker's value. Confirmed against the
    real Lear P4 (doc/agenda.org phase1/fix-globe-anchor-placement, review
    [2026-09-12]): a marker trailing line k already carries the number that
    belongs to line k+1 (P4's own convention), so once the marker is
    physically moved forward, its own value is already correct -- no
    relabeling step exists in the corrected model at all."""

    def test_numbered_boundary_moves_to_lead_the_NEXT_line_keeping_its_own_value(self):
        # This is the direct regression guard for the historical bug: a
        # naive "shift the value list by one, then move" implementation
        # relabels line 2's marker with line 3's original value and moves
        # it to lead line 2 itself -- i.e. Globe 41 ends up leading "To
        # shake all cares" (the line it trails), not "Conferring them" (the
        # line P4's own convention says it belongs to).
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>In three our kingdom <milestone unit="line" ed="Globe"/></l>'
            '<l>To shake all cares <milestone unit="line" ed="Globe" n="41" source="#globe-edition"/></l>'
            '<l>Conferring them <milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines) == 3

        # Line 1's own (unnumbered) trailing marker moved forward to lead line 2.
        assert len(lines[0]) == 0
        assert _text_of(lines[0]) == "In three our kingdom"

        # Line 2 leads with the marker moved in from line 1 (unnumbered) --
        # NOT with "41", which belongs to line 3.
        assert len(lines[1]) == 1
        ms1 = lines[1][0]
        assert ms1.get("ed") == "Globe" and ms1.get("n") is None
        assert ms1.tail.strip() == "To shake all cares"

        # Line 3 leads with "41" (its own value, unchanged, source intact --
        # moved here from trailing line 2) and keeps its own original
        # (unnumbered) marker trailing after it: the scope's genuine
        # terminal boundary, nowhere forward to move to.
        assert len(lines[2]) == 2
        leading, trailing = lines[2]
        assert leading.get("ed") == "Globe" and leading.get("n") == "41"
        assert leading.get("source") == "#globe-edition"
        assert leading.tail.strip() == "Conferring them"
        assert trailing.get("ed") == "Globe" and trailing.get("n") is None
        assert trailing.tail is None

    def test_first_lines_own_numbered_boundary_moves_to_the_second_line_no_synthesis(self):
        # No "leading milestone synthesis" exists in the corrected model --
        # a scope's first line simply ends up with no marker of its own if
        # its boundary moves away, exactly like any other terminal marker.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>first line <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l>second line <milestone unit="line" ed="Globe" n="11"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines[0]) == 0
        assert _text_of(lines[0]) == "first line"

        assert len(lines[1]) == 2
        leading, trailing = lines[1]
        assert leading.get("n") == "10" and leading.tail.strip() == "second line"
        assert trailing.get("n") == "11" and trailing.tail is None

    def test_first_lines_own_unnumbered_boundary_moves_too(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>first line <milestone unit="line" ed="Globe"/></l>'
            '<l>second line <milestone unit="line" ed="Globe" n="11"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines[0]) == 0
        assert len(lines[1]) == 2
        leading, trailing = lines[1]
        assert leading.get("n") is None and leading.tail.strip() == "second line"
        assert trailing.get("n") == "11" and trailing.tail is None

    def test_last_line_of_scope_keeps_its_own_now_terminal_marker(self):
        # The very last boundary in scope has nowhere forward to move to --
        # it stays trailing its own line, value unchanged, alongside the
        # marker moved in to lead that same last line.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>only numbered line <milestone unit="line" ed="Globe" n="7"/></l>'
            '<l>last line <milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines[0]) == 0
        assert len(lines[1]) == 2
        leading, trailing = lines[1]
        assert leading.get("n") == "7" and leading.tail.strip() == "last line"
        assert trailing.get("n") is None and trailing.tail is None


class TestEmbeddedNumberedGlobeMarker:
    """Found regenerating the real Lear file (review [2026-09-12]): the
    interval-closure histogram moved far more than a placement-only fix
    should, isolated to Act III Scene 4. Root cause: Globe numbers whole
    verse lines and never typeset sub-lines the way F1 does, so a
    *numbered* Globe marker embedded mid-<l> is never already correct the
    way an embedded F1 marker is -- P4 recorded it roughly where the
    marginal decade-mark visually fell, which can land mid-line even for a
    single, unwrapped verse line (confirmed against the printed Globe page,
    p. 864: Globe 70 numbers the *whole* line "Hang fated o'er men's faults
    light on thy daughters!", even though P4 embeds the tag before
    "daughters!"). It must move to lead its own containing <l>, not stay
    embedded and not move to the next <l> either. The same <l>'s own
    separate (usually unnumbered) terminal marker is a different boundary
    -- the genuine one to the *next* <l> -- and goes through the ordinary
    terminal-shift path untouched by this."""

    def test_embedded_numbered_globe_marker_moves_to_lead_its_own_line(self):
        # Mirrors the real Lear shape exactly: "Hang fated o'er men's
        # faults light on thy <lb n="70" ed="G"/>daughters! <lb ed="G"/>".
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>Hang fated o\'er men\'s faults light on thy '
            '<milestone unit="line" ed="Globe" n="70" source="#globe-edition"/>'
            "daughters! "
            '<milestone unit="line" ed="Globe"/></l>'
            "<l>He hath no daughters, sir. "
            '<milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")

        # Line 1 now leads with "70" (moved from mid-line to the front),
        # carrying the FULL original text as its tail, and keeps its own
        # separate terminal marker (unnumbered) -- which has itself moved
        # forward to lead line 2, per the ordinary terminal-shift rule.
        assert len(lines[0]) == 1
        leading = lines[0][0]
        assert leading.get("n") == "70" and leading.get("source") == "#globe-edition"
        assert leading.tail.strip() == "Hang fated o'er men's faults light on thy daughters!"

        assert len(lines[1]) == 2
        l2_leading, l2_trailing = lines[1]
        assert l2_leading.get("n") is None  # the moved-in terminal boundary from line 1
        assert l2_leading.tail.strip() == "He hath no daughters, sir."
        assert l2_trailing.get("n") is None  # line 2's own terminal boundary
        assert l2_trailing.tail is None

    def test_own_line_terminal_marker_still_escapes_when_a_prior_pass_already_moved_an_f1_marker_in(self):
        # Regression: mirrors the real Lear shape exactly (F1 1923 already
        # moved in from the preceding line by F1's own earlier pass, before
        # Globe's embedded "150" and Globe's OWN separate terminal marker
        # are classified). A first cut of this fix interleaved the two
        # move kinds and, processing "150" before the terminal marker,
        # left the terminal one stranded in the wrong <l> -- moving "150"
        # to the front made the terminal marker's very next sibling an F1
        # marker with real trailing text, which _has_content_after
        # (correctly, in general) reads as "content follows", misclassifying
        # a genuine terminal boundary as embedded. Classifying everything
        # before either kind of move runs (see _shift_scope_to_start_forward)
        # fixes this: the terminal marker must still escape to lead the
        # next <l>, independent of what happens to "150".
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>Before line <milestone unit="line" ed="F1" n="1922"/></l>'
            '<l>Our flesh and blood is grown so '
            '<milestone unit="line" ed="F1" n="1923"/>'
            "vile, "
            '<milestone unit="line" ed="Globe" n="150" source="#globe-edition"/>'
            "my lord, "
            '<milestone unit="line" ed="Globe"/></l>'
            "<l>That it doth hate what gets it. "
            '<milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")

        assert len(lines[0]) == 0  # "Before line": F1 1922 moved out

        middle = lines[1]
        assert len(middle) == 3
        assert middle[0].get("ed") == "Globe" and middle[0].get("n") == "150"
        assert middle[0].get("source") == "#globe-edition"
        # No text lost across the reshuffle, regardless of which sibling
        # ends up carrying which fragment.
        assert _text_of(middle) == "Our flesh and blood is grown so vile, my lord,"

        # The critical assertion: the terminal Globe marker from "Our
        # flesh..." must have escaped to LEAD "That it doth hate...",
        # not been stranded in the wrong <l>.
        last = lines[2]
        assert last[0].get("ed") == "Globe" and last[0].get("n") is None
        assert last[0].tail.strip() == "That it doth hate what gets it."

    def test_embedded_unnumbered_globe_marker_is_untouched(self):
        # An embedded marker with no @n carries no citable value and
        # affects no interval count either way -- left exactly where P4
        # put it, same as any other embedded marker.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>some text <milestone unit="line" ed="Globe"/>more text '
            '<milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        line = body.find(f".//{q('l')}")
        assert len(line) == 2
        embedded, trailing = line
        assert embedded.tail.strip() == "more text"
        assert line.text == "some text "


class TestProseRepositioning:
    """P4's prose convention already places a boundary marker immediately before
    the text it numbers -- correct as it stands (doc/agenda.org
    phase1/fix-globe-anchor-placement, Defect 1). Only milestones whose direct
    parent is <l> enter the shift chain; a scope built entirely of <p> (as
    Antony and Cleopatra's currently is) is therefore untouched by
    reposition_milestones_start_forward: no value shift, no physical move, and
    no leading milestone synthesized, however many <p> boundaries it holds."""

    def test_numbered_boundary_stays_exactly_where_it_was(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<p>In three our kingdom <milestone unit="line" ed="Globe"/></p>'
            '<p>To shake all cares <milestone unit="line" ed="Globe" n="41"/></p>'
            '<p>Conferring them <milestone unit="line" ed="Globe"/></p>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        paras = body.findall(f".//{q('p')}")
        assert len(paras) == 3

        assert len(paras[0]) == 1
        ms0 = paras[0][0]
        assert ms0.get("ed") == "Globe" and ms0.get("n") is None
        assert ms0.tail is None

        assert len(paras[1]) == 1
        ms1 = paras[1][0]
        assert ms1.get("ed") == "Globe" and ms1.get("n") == "41"
        assert ms1.tail is None
        assert _text_of(paras[1]) == "To shake all cares"

        assert len(paras[2]) == 1
        ms2 = paras[2][0]
        assert ms2.get("ed") == "Globe" and ms2.get("n") is None
        assert ms2.tail is None

    def test_prose_untouched_even_when_first_boundary_numbered(self):
        # Contrast with TestVerseRepositioning's identical-shape scenario: a
        # verse scope moves its first line's own boundary forward here; a
        # prose scope never moves anything at all.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<p>first para <milestone unit="line" ed="Globe" n="10"/></p>'
            '<p>second para <milestone unit="line" ed="Globe" n="11"/></p>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        first_p = body.find(f".//{q('p')}")
        assert first_p.text == "first para "
        assert first_p[0].get("n") == "10"

    def test_last_paragraph_of_scope_keeps_its_own_marker_untouched(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<p>only numbered para <milestone unit="line" ed="Globe" n="7"/></p>'
            '<p>last para <milestone unit="line" ed="Globe"/></p>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        paras = body.findall(f".//{q('p')}")
        assert len(paras[0]) == 1 and paras[0][0].get("n") == "7"
        assert len(paras[1]) == 1
        ms = paras[1][0]
        assert ms.get("n") is None and ms.tail is None


class TestGlobeScopedPerScene:
    def test_globe_numbering_does_not_cross_scene_boundary(self):
        # Two lines per scene, so a boundary would visibly cross into the
        # next scene if scoping weren't respected -- scene 1's second line
        # ("a2") must not receive anything from scene 2 (there is nothing
        # before it in its own scope to receive), and scene 1's own "5"
        # must not leak into scene 2's first line ("b1").
        body = _body(
            '<div type="act" n="1">'
            '<div type="scene" n="1">'
            '<l>a1 <milestone unit="line" ed="Globe" n="5"/></l>'
            '<l>a2 <milestone unit="line" ed="Globe"/></l>'
            "</div>"
            '<div type="scene" n="2">'
            '<l>b1 <milestone unit="line" ed="Globe" n="1"/></l>'
            '<l>b2 <milestone unit="line" ed="Globe"/></l>'
            "</div>"
            "</div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        scenes = body.findall(f".//{q('div')}[@type='scene']")
        lines1 = scenes[0].findall(f".//{q('l')}")
        lines2 = scenes[1].findall(f".//{q('l')}")

        assert len(lines1[0]) == 0  # a1: own boundary moved to a2
        assert _globe_ns(scenes[0]) == ["5", None]  # a2 leads with 5, keeps its own terminal
        assert lines1[1][0].get("n") == "5"

        assert len(lines2[0]) == 0  # b1: own boundary moved to b2 -- not scene 1's "5"
        assert _globe_ns(scenes[1]) == ["1", None]
        assert lines2[1][0].get("n") == "1"


class TestF1WholePlayScope:
    def test_f1_shifts_continuously_across_scenes(self):
        body = _body(
            '<div type="act" n="1">'
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="F1" n="10"/></l>'
            "</div>"
            '<div type="scene" n="2">'
            '<l>b <milestone unit="line" ed="F1" n="11"/></l>'
            "</div>"
            "</div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        scenes = body.findall(f".//{q('div')}[@type='scene']")
        f1_scene1 = [m.get("n") for m in scenes[0].iter(q("milestone")) if m.get("ed") == "F1"]
        f1_scene2 = [m.get("n") for m in scenes[1].iter(q("milestone")) if m.get("ed") == "F1"]
        # Scene 1's own marker ("10") moves forward across the scene
        # boundary -- since F1 is a single whole-play scope, not per-scene
        # -- to lead scene 2's line, carrying its OWN value (10), unchanged.
        # Scene 1 ends with nothing; scene 2 leads with the moved-in "10"
        # and keeps its own "11" trailing, terminal (nothing follows in the
        # whole-play scope).
        assert f1_scene1 == []
        assert f1_scene2 == ["10", "11"]


class TestProseEmbedded:
    """A milestone embedded mid-sentence in running prose is untouched entirely
    (Defect 1's mode gate excludes every <p>-parented milestone from the shift
    chain, not just ones that happen to sit at a paragraph boundary) -- these
    tests previously asserted the pre-fix behavior (value relabeled in place);
    now they confirm no shift of any kind happens for prose."""

    def test_mid_sentence_boundary_not_shifted(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1"><sp><speaker>Glou.</speaker>'
            '<p>I thought the king had more affected '
            '<milestone unit="line" ed="Globe"/>the '
            '<milestone unit="line" ed="Globe" n="41"/>'
            "Duke of Albany than Cornwall. "
            '<milestone unit="line" ed="Globe"/></p>'
            "</sp></div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        p = body.find(f".//{q('p')}")
        milestones = p.findall(q("milestone"))
        assert len(milestones) == 3
        assert milestones[0].get("n") is None
        assert milestones[0].tail.strip().startswith("the")
        assert milestones[1].get("n") == "41"
        assert milestones[1].tail.strip().startswith("Duke of Albany")
        assert milestones[2].get("n") is None

    def test_boundary_immediately_before_a_different_edition_marker_not_shifted(self):
        # P4 routinely places Globe and F1 markers back-to-back
        # (<lb ed="G"/><lb n="311" ed="F1"/>of what...) -- confirms the mode
        # gate excludes both regardless of this adjacency shape.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1"><sp><speaker>Gon.</speaker>'
            "<p>Sister, it is not a little I have to say "
            '<milestone unit="line" ed="Globe"/>'
            '<milestone unit="line" ed="F1" n="311"/>'
            "of what most nearly appertains to us both. "
            '<milestone unit="line" ed="Globe" n="290"/></p>'
            "</sp></div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        p = body.find(f".//{q('p')}")
        globe_ms = [m for m in p.findall(q("milestone")) if m.get("ed") == "Globe"]
        assert len(globe_ms) == 2
        assert globe_ms[0].get("n") is None
        assert globe_ms[1].get("n") == "290"


class TestMixedModeScope:
    def test_prose_milestone_interleaved_in_a_verse_scene_is_skipped_by_the_chain(self):
        # A scene that's mostly verse but has one prose interjection: the <p>
        # milestone must not enter the <l> chain at all -- neither
        # contributing to it nor receiving anything from it. The verse
        # chain's own forward-move must also skip straight past the <p>
        # (searching specifically for the next <l>, never a <p>) rather
        # than mistaking it for a valid move target.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<p>an aside <milestone unit="line" ed="Globe" n="99"/></p>'
            '<l>b <milestone unit="line" ed="Globe" n="11"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        p = body.find(f".//{q('p')}")
        assert len(p) == 1 and p[0].get("n") == "99"
        assert _text_of(p) == "an aside"
        lines = body.findall(f".//{q('l')}")
        # "a"'s own boundary (10) moves forward past the <p> to lead "b",
        # carrying its own value unchanged; "b" keeps its own "11" trailing
        # (terminal, nothing follows in scope). The prose "99" is untouched.
        assert len(lines[0]) == 0
        assert len(lines[1]) == 2
        leading, trailing = lines[1]
        assert leading.get("n") == "10" and trailing.get("n") == "11"


class TestStrayAnchorRecovery:
    """Defect 2 (doc/agenda.org phase1/fix-globe-anchor-placement): a stray @n
    on <l> is recovered as a transcribed Globe anchor when the immediately
    preceding <l> (crossing <sp> boundaries) lacks its own <lb ed="G">."""

    def test_recovered_when_preceding_line_lacks_boundary(self):
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            "<sp><speaker>A.</speaker><l>only line</l></sp>"
            '<sp><speaker>B.</speaker><l n="42">Is he pursued?</l></sp>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        assert lines[1][0].get("ed") == "Globe"
        assert lines[1][0].get("n") == "42"
        assert lines[1][0].get("source") == "#globe-edition"
        assert stats.recovered_transcribed_anchors == [
            (stats.recovered_transcribed_anchors[0][0], "42")
        ]
        assert stats.l_stray_n_stripped == []

    def test_still_stripped_as_noise_when_preceding_line_has_boundary(self):
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<l>only line <lb n="12" ed="G"/></l>'
            '<l n="13">next line</l>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        assert lines[1].get("n") is None
        assert len(stats.l_stray_n_stripped) == 1
        assert stats.recovered_transcribed_anchors == []

    def test_stripped_as_noise_when_no_preceding_line_at_all(self):
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<l n="111" part="I">Is he pursued?</l>'
            "</div2></div1>"
        )
        line = new_body.find(f".//{q('l')}")
        assert line.get("n") is None
        assert len(stats.l_stray_n_stripped) == 1
        assert stats.recovered_transcribed_anchors == []


class TestSharedVerseLineMerge:
    """Defect 3: a verse line split across two speakers gets one Globe
    milestone, on the I-half; a spurious duplicate on the F-half is deleted."""

    def test_clean_pair_with_a_physical_split_boundary_is_deleted(self):
        # Mirrors Lear II.1's "I'll not be there,"/"Nor I, I assure thee,
        # Regan." shape: no stray @n involved, just the ordinary shift chain
        # giving both halves their own (unnumbered) leading milestone.
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<sp><speaker>A.</speaker><l>before <lb ed="G"/></l></sp>'
            '<sp><speaker>B.</speaker><l part="I">I\'ll not be there, <lb ed="G"/></l></sp>'
            '<sp><speaker>C.</speaker><l part="F">Nor I, I assure thee. <lb ed="G"/></l></sp>'
            '<sp><speaker>D.</speaker><l>after <lb ed="G"/></l></sp>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        i_half, f_half = lines[1], lines[2]
        assert len(i_half) == 1 and i_half[0].get("ed") == "Globe"
        assert len(f_half) == 0
        assert len(stats.split_line_boundaries_deleted) == 1
        assert stats.split_line_pairs_already_clean == []

    def test_clean_pair_with_no_physical_split_boundary_is_a_no_op(self):
        # Mirrors Lear III.7's "If this man come to good."/"If she live
        # long," shape: P4 never recorded a boundary at the split point at
        # all (no <lb ed="G"> on the preceding line) -- nothing to delete.
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<sp><speaker>A.</speaker><l>before <lb ed="G"/></l></sp>'
            '<sp><speaker>B.</speaker><l part="I">If this man come to good. </l></sp>'
            '<sp><speaker>C.</speaker><l part="F">If she live long, <lb ed="G"/></l></sp>'
            '<sp><speaker>D.</speaker><l>after <lb ed="G"/></l></sp>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        i_half, f_half = lines[1], lines[2]
        # I-half still carries whatever the ordinary chain gave it (here, the
        # boundary shifted in from "before", unnumbered) -- merge only acts
        # when the F-half actually has something to consolidate away.
        assert len(i_half) == 1 and i_half[0].get("n") is None
        assert len(f_half) == 0
        assert stats.split_line_boundaries_deleted == []
        assert len(stats.split_line_pairs_already_clean) == 1

    def test_recovered_anchor_on_the_f_half_relocates_to_the_i_half(self):
        # The real Lear III.7 shape: the transcribed number sits on the
        # F-half's <l> tag (the compositor's choice, per Defect 3's own
        # text) -- recovery restores it there first, and the merge pass
        # relocates it onto the I-half where the model says it belongs.
        new_body, stats = _rederive_fragment(
            "<div1 type=\"act\" n=\"1\"><div2 type=\"scene\" n=\"1\">"
            '<sp><speaker>Second Serv.</speaker>'
            '<l>I\'ll never care what wickedness I do, <lb ed="G"/></l>'
            '<l part="I">If this man come to good. </l></sp>'
            '<sp><speaker>Third Serv.</speaker>'
            '<l n="100" part="F">If she live long, <lb ed="G"/></l>'
            '<l>And in the end meet the old course of death, <lb ed="G"/></l>'
            '<l>Women will all turn monsters. <lb ed="G"/></l></sp>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        i_half, f_half = lines[1], lines[2]
        assert i_half.get("part") == "I" and f_half.get("part") == "F"
        assert len(i_half) == 1
        assert i_half[0].get("n") == "100"
        assert i_half[0].get("source") == "#globe-edition"
        assert len(f_half) == 0
        assert stats.recovered_transcribed_anchors == [
            (stats.recovered_transcribed_anchors[0][0], "100")
        ]

    def test_recovered_anchor_already_on_the_i_half_needs_no_relocation(self):
        # The real Lear II.1 shape: the transcribed number already sits on
        # the I-half's <l> tag; the line immediately before it ("This hurt
        # you see...") has no Globe <lb> at all (only F1) -- that absence is
        # exactly what makes n="111" recoverable rather than noise. Recovery
        # inserts fresh (nothing was shifted in from a line that never
        # contributed to the chain); the merge pass then deletes the
        # F-half's now-redundant ordinary leading milestone.
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<sp><speaker>A.</speaker><l>earlier line <lb ed="G"/></l></sp>'
            '<sp><speaker>X.</speaker><l>line before (no Globe boundary)</l></sp>'
            '<sp><speaker>B.</speaker><l n="111" part="I">Is he pursued? <lb ed="G"/></l></sp>'
            '<sp><speaker>C.</speaker><l part="F">Ay, my good lord. <lb ed="G"/></l></sp>'
            '<sp><speaker>D.</speaker><l>line after <lb ed="G"/></l></sp>'
            "</div2></div1>"
        )
        lines = new_body.findall(f".//{q('l')}")
        i_half, f_half = lines[2], lines[3]
        assert len(i_half) == 1
        assert i_half[0].get("n") == "111"
        assert i_half[0].get("source") == "#globe-edition"
        assert len(f_half) == 0

    def test_conflicting_numbered_halves_raises(self):
        def _run():
            return _rederive_fragment(
                '<div1 type="act" n="1"><div2 type="scene" n="1">'
                "<sp><speaker>Z.</speaker><l>zero</l></sp>"
                '<sp><speaker>A.</speaker><l n="5" part="I">a</l></sp>'
                '<sp><speaker>B.</speaker><l n="6" part="F">b</l></sp>'
                "<sp><speaker>C.</speaker><l>c</l></sp>"
                "</div2></div1>"
            )
        try:
            _run()
            assert False, "expected ConversionError"
        except ConversionError:
            pass

    def test_unpaired_part_marker_is_flagged_not_guessed(self):
        new_body, stats = _rederive_fragment(
            '<div1 type="act" n="1"><div2 type="scene" n="1">'
            '<sp><speaker>A.</speaker><l part="I">a <lb ed="G"/></l></sp>'
            '<sp><speaker>B.</speaker><l>b (no part) <lb ed="G"/></l></sp>'
            '<sp><speaker>C.</speaker><l part="F">c <lb ed="G"/></l></sp>'
            "</div2></div1>"
        )
        # "a" (part=I) is not immediately followed by a part=F line, and "c"
        # (part=F) is not immediately preceded by a part=I line -- both
        # unpaired, both left untouched, both flagged. Nothing is merged or
        # deleted (the ordinary chain's own terminal-line pattern -- "c" is
        # the scope's last line and keeps both a moved-in leading marker and
        # its own now-unnumbered trailing one -- is unrelated to this check).
        assert len(stats.unpaired_part_markers) == 2
        assert stats.split_line_boundaries_deleted == []
