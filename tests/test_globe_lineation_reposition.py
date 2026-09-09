from __future__ import annotations

from lxml import etree

from globe_lineation import (
    ConversionStats,
    q,
    reposition_milestones_start_forward,
)

P5_NS = "http://www.tei-c.org/ns/1.0"


def _body(inner: str) -> etree._Element:
    xml = f'<TEI xmlns="{P5_NS}"><text><body>{inner}</body></text></TEI>'
    root = etree.fromstring(xml.encode("utf-8"))
    return root.find(f"{q('text')}/{q('body')}")


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
    def test_mid_sentence_boundary_relabeled_in_place_not_moved(self):
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
        # first (originally unnumbered, trailing "affected") now carries 41 --
        # relabeled in place, NOT moved, since real text follows it mid-paragraph.
        assert milestones[0].get("n") == "41"
        assert milestones[0].tail.strip() == "the"
        # second (originally 41, trailing "the") is now unnumbered -- nothing to
        # shift into it (the third was already unnumbered) -- still relabeled in
        # place, still leading "Duke of Albany...".
        assert milestones[1].get("n") is None
        assert milestones[1].tail.strip().startswith("Duke of Albany")

    def test_boundary_immediately_before_a_different_edition_marker_is_not_moved(self):
        # Regression: P4 routinely places Globe and F1 markers back-to-back
        # (<lb ed="G"/><lb n="311" ed="F1"/>of what...). The Globe marker's own
        # .tail is empty there even though real prose immediately follows its F1
        # neighbor -- it must NOT be treated as terminal just because nothing
        # trails *it specifically*.
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
        # both stay in place (relabeled only): the first is not swept forward past
        # "of what most nearly appertains..." just because its immediate neighbor
        # is an F1 marker rather than text.
        assert len(globe_ms) == 2
        assert globe_ms[0].get("n") == "290"
        assert globe_ms[0].tail is None or globe_ms[0].tail.strip() == ""
        assert globe_ms[1].get("n") is None
