from __future__ import annotations

from lxml import etree

from globe_lineation import q
from globe_anchor_intervals import compute_document_intervals

P5_NS = "http://www.tei-c.org/ns/1.0"


def _doc(scene_xml: str) -> etree._Element:
    xml = (
        f'<TEI xmlns="{P5_NS}"><text><body>'
        f'<div type="act" n="1">{scene_xml}</div>'
        "</body></text></TEI>"
    )
    return etree.fromstring(xml.encode("utf-8"))


class TestIntervalClosure:
    def test_closing_interval(self):
        # 3 boundaries between anchors 10 and 13 -> gap 3, exactly closes.
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l>b <milestone unit="line" ed="Globe"/></l>'
            '<l>c <milestone unit="line" ed="Globe"/></l>'
            '<l>d <milestone unit="line" ed="Globe" n="13"/></l>'
            "</div>"
        )
        root = _doc(scene)
        intervals = compute_document_intervals(root)
        assert len(intervals) == 1
        iv = intervals[0]
        assert iv.anchor_a == 10 and iv.anchor_b == 13
        assert iv.gap == 3
        assert iv.boundaries_between == 3
        assert iv.closes
        assert iv.excess == 0

    def test_non_closing_interval_split_line(self):
        # 4 boundaries between anchors 10 and 13 (one extra, a split line) -> excess +1.
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l>b1 <milestone unit="line" ed="Globe"/></l>'
            '<l>b2 <milestone unit="line" ed="Globe"/></l>'
            '<l>c <milestone unit="line" ed="Globe"/></l>'
            '<l>d <milestone unit="line" ed="Globe" n="13"/></l>'
            "</div>"
        )
        root = _doc(scene)
        intervals = compute_document_intervals(root)
        iv = intervals[0]
        assert iv.boundaries_between == 4
        assert iv.gap == 3
        assert not iv.closes
        assert iv.excess == 1
        assert len(iv.boundaries) == 4

    def test_closing_interval_prose_target(self):
        # Same as test_closing_interval but with <p> instead of <l> -- confirms
        # compute_scene_intervals/._following_text are element-agnostic, matching
        # Antony and Cleopatra's all-prose P4 source (zero <l> elements).
        scene = (
            '<div type="scene" n="1">'
            '<p>a <milestone unit="line" ed="Globe" n="10"/></p>'
            '<p>b <milestone unit="line" ed="Globe"/></p>'
            '<p>c <milestone unit="line" ed="Globe"/></p>'
            '<p>d <milestone unit="line" ed="Globe" n="13"/></p>'
            "</div>"
        )
        root = _doc(scene)
        intervals = compute_document_intervals(root)
        assert len(intervals) == 1
        iv = intervals[0]
        assert iv.anchor_a == 10 and iv.anchor_b == 13
        assert iv.gap == 3
        assert iv.boundaries_between == 3
        assert iv.closes
        assert iv.excess == 0

    def test_non_closing_interval_prose_target(self):
        scene = (
            '<div type="scene" n="1">'
            '<p>a <milestone unit="line" ed="Globe" n="10"/></p>'
            '<p>b1 <milestone unit="line" ed="Globe"/></p>'
            '<p>b2 <milestone unit="line" ed="Globe"/></p>'
            '<p>c <milestone unit="line" ed="Globe"/></p>'
            '<p>d <milestone unit="line" ed="Globe" n="13"/></p>'
            "</div>"
        )
        root = _doc(scene)
        intervals = compute_document_intervals(root)
        iv = intervals[0]
        assert iv.boundaries_between == 4
        assert iv.gap == 3
        assert not iv.closes
        assert iv.excess == 1
        assert len(iv.boundaries) == 4

    def test_scene_with_fewer_than_two_anchors_contributes_nothing(self):
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe"/></l>'
            '<l>b <milestone unit="line" ed="Globe" n="5"/></l>'
            "</div>"
        )
        root = _doc(scene)
        assert compute_document_intervals(root) == []

    def test_multiple_scenes_do_not_cross_boundaries(self):
        scenes = (
            '<div type="scene" n="1">'
            '<l><milestone unit="line" ed="Globe" n="1"/></l>'
            '<l><milestone unit="line" ed="Globe" n="2"/></l>'
            "</div>"
            '<div type="scene" n="2">'
            '<l><milestone unit="line" ed="Globe" n="1"/></l>'
            '<l><milestone unit="line" ed="Globe" n="2"/></l>'
            "</div>"
        )
        root = _doc(scenes)
        intervals = compute_document_intervals(root)
        assert len(intervals) == 2
        assert {iv.scene for iv in intervals} == {"1", "2"}


class TestUnpairedPartFlagging:
    """doc/agenda.org phase1/fix-globe-anchor-placement, Defect 3: an interval
    whose non-closure traces to an unpaired/asymmetric @part marker (left
    unresolved by globe_lineation._dedupe_shared_verse_lines) is flagged for
    the alignment-oracle task, distinct from an ordinary unexplained gap."""

    def test_unpaired_part_boundary_flags_its_interval(self):
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l part="I">b <milestone unit="line" ed="Globe"/></l>'
            '<l>c <milestone unit="line" ed="Globe"/></l>'
            '<l>d <milestone unit="line" ed="Globe" n="12"/></l>'
            "</div>"
        )
        root = _doc(scene)
        iv = compute_document_intervals(root)[0]
        assert not iv.closes
        assert iv.has_flagged_boundary
        assert iv.boundaries[0].flagged

    def test_clean_pair_does_not_flag(self):
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l part="I">b <milestone unit="line" ed="Globe"/></l>'
            '<l part="F">c <milestone unit="line" ed="Globe"/></l>'
            '<l>d <milestone unit="line" ed="Globe" n="12"/></l>'
            "</div>"
        )
        root = _doc(scene)
        iv = compute_document_intervals(root)[0]
        assert not iv.has_flagged_boundary
        assert all(not b.flagged for b in iv.boundaries)

    def test_no_part_at_all_does_not_flag(self):
        # The known real case (Lear II.4's "Return you to my sister."/"Never,
        # Regan:") -- no @part anywhere, so nothing for this mechanism to
        # detect; it is a real unresolved split, but a different, silent
        # kind that this flag (by design) does not claim to catch.
        scene = (
            '<div type="scene" n="1">'
            '<l>a <milestone unit="line" ed="Globe" n="10"/></l>'
            '<l>b <milestone unit="line" ed="Globe"/></l>'
            '<l>c <milestone unit="line" ed="Globe"/></l>'
            '<l>d <milestone unit="line" ed="Globe" n="12"/></l>'
            "</div>"
        )
        root = _doc(scene)
        iv = compute_document_intervals(root)[0]
        assert not iv.has_flagged_boundary
