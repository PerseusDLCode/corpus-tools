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
    def test_numbered_boundary_moves_to_lead_the_line_it_labels(self):
        # Globe 41 currently trails "To shake..." (P4/END convention: it labels the
        # content before it). After repositioning it should physically become the
        # LEADING child of that same line's <l> -- not just document-order-adjacent,
        # actually nested inside the <l> whose content it describes.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>In three our kingdom <milestone unit="line" ed="Globe"/></l>'
            '<l>To shake all cares <milestone unit="line" ed="Globe" n="41"/></l>'
            '<l>Conferring them <milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines) == 3

        # Line 1 ("In three our kingdom") now has NO milestone of its own -- its
        # original (unnumbered) trailing marker moved forward to lead line 2.
        assert len(lines[0]) == 0
        assert _text_of(lines[0]) == "In three our kingdom"

        # Line 2 ("To shake all cares") now LEADS with Globe 41, moved in from
        # line 1's old trailing position.
        assert len(lines[1]) == 1
        ms1 = lines[1][0]
        assert ms1.get("ed") == "Globe" and ms1.get("n") == "41"
        assert ms1.tail.strip() == "To shake all cares"

        # Line 3 leads with an unnumbered marker (moved in from line 2's old,
        # already-unnumbered, trailing position) *and* keeps its own original
        # marker trailing after it -- that one is the scope's genuine terminal
        # boundary (nothing follows it in scope to shift its number from, and
        # nowhere forward to move it to), also now unnumbered.
        assert len(lines[2]) == 2
        leading, trailing = lines[2]
        assert leading.get("ed") == "Globe" and leading.get("n") is None
        assert leading.tail.strip() == "Conferring them"
        assert trailing.get("ed") == "Globe" and trailing.get("n") is None
        assert trailing.tail is None

    def test_leading_milestone_synthesized_when_first_boundary_was_numbered(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>first line <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l>second line <milestone unit="line" ed="Globe" n="11"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        first_l = body.find(f".//{q('l')}")
        assert first_l.text is None
        leading_ms = first_l[0]
        assert leading_ms.get("ed") == "Globe"
        assert leading_ms.get("n") == "10"
        assert leading_ms.tail.strip() == "first line"
        assert len(stats.synthesized_leading_milestones) == 1
        assert stats.synthesized_leading_milestones[0][2] == "10"

    def test_no_leading_milestone_when_first_boundary_unnumbered(self):
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>first line <milestone unit="line" ed="Globe"/></l>'
            '<l>second line <milestone unit="line" ed="Globe" n="11"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        first_l = body.find(f".//{q('l')}")
        assert first_l.text == "first line "
        assert stats.synthesized_leading_milestones == []

    def test_last_line_of_scope_keeps_its_own_now_unnumbered_marker(self):
        # The very last boundary in scope has nothing to shift into it and nowhere
        # forward to move to -- it stays trailing its own line, unnumbered, alongside
        # the (also unnumbered) marker moved in to lead that same last line.
        body = _body(
            '<div type="act" n="1"><div type="scene" n="1">'
            '<l>only numbered line <milestone unit="line" ed="Globe" n="7"/></l>'
            '<l>last line <milestone unit="line" ed="Globe"/></l>'
            "</div></div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        lines = body.findall(f".//{q('l')}")
        assert len(lines[1]) == 2
        leading, trailing = lines[1]
        assert leading.get("n") is None and leading.tail.strip() == "last line"
        assert trailing.get("n") is None and trailing.tail is None


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

        assert stats.synthesized_leading_milestones == []

    def test_no_leading_milestone_synthesized_even_when_first_boundary_numbered(self):
        # Contrast with TestVerseRepositioning's identical-shape scenario: a
        # verse scope synthesizes a leading milestone here; a prose scope
        # never does, since prose milestones are never part of the shift
        # chain that motivates synthesizing one in the first place.
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
        assert stats.synthesized_leading_milestones == []

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
        body = _body(
            '<div type="act" n="1">'
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="5"/></l>'
            "</div>"
            '<div type="scene" n="2">'
            '<l>b <milestone unit="line" ed="Globe" n="1"/></l>'
            "</div>"
            "</div>"
        )
        stats = ConversionStats()
        reposition_milestones_start_forward(body, stats)
        scenes = body.findall(f".//{q('div')}[@type='scene']")
        # Each scene's single line is both the first and last content element of its
        # own scope, so it ends up with two markers: the synthesized leading one
        # (carrying the scene's own transcribed number) and its own original,
        # now-unnumbered terminal one -- and scene 2 never inherits scene 1's "5".
        assert _globe_ns(scenes[0]) == ["5", None]
        assert _globe_ns(scenes[1]) == ["1", None]
        assert stats.synthesized_leading_milestones == [
            ("Globe", "Act 1, Scene 1", "5"),
            ("Globe", "Act 1, Scene 2", "1"),
        ]


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
        # scene 1's own boundary moved forward -- across the scene boundary, since F1
        # does not reset -- to lead scene 2's line, now carrying scene 2's number (11).
        # Scene 1 keeps only the synthesized leading marker (its own boundary moved
        # away entirely); scene 2's line, being both first and last of the F1 scope's
        # remaining content, keeps both the moved-in "11" and its own now-unnumbered
        # terminal marker.
        assert f1_scene1 == ["10"]
        assert f1_scene2 == ["11", None]
        assert stats.synthesized_leading_milestones == [("F1", "(whole play)", "10")]


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
        # milestone must not enter the <l> shift chain at all -- neither
        # contributing its value to it nor receiving a shifted-in one.
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
        # "a" and "b" shift as an ordinary verse pair (10 -> 11 moves onto
        # line b; a synthesized leading marker restores 10 to the scope's
        # own first position, same as any single-verse-chain scope) -- the
        # prose milestone's "99" plays no part in that arithmetic.
        assert lines[0][0].get("n") == "10"
        assert lines[1][0].get("n") == "11"


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
