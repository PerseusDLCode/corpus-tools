from __future__ import annotations

from lxml import etree

from tei import NS
from verse_numbering import number_document, number_scene, collect_scene_lines

TEI_NS = NS["tei"]


def _tei(tag: str) -> str:
    return f"{{{TEI_NS}}}{tag}"


def _build_play(acts: list[tuple[str, list[tuple[str, list[str]]]]]) -> etree._Element:
    """acts: [(act_n, [(scene_n, [line_spec, ...])])]

    line_spec is either a plain string (new-line, no @n, no @part), or a
    "part:text" / "part:text:n" string to set @part and/or @n explicitly.
    A line_spec of "STAGE" inserts a <stage><l>...</l></stage> to test exclusion.
    """
    root = etree.Element(_tei("TEI"), nsmap={None: TEI_NS})
    body = etree.SubElement(root, _tei("body"))
    for act_n, scenes in acts:
        act = etree.SubElement(body, _tei("div"), type="act", n=act_n)
        for scene_n, lines in scenes:
            scene = etree.SubElement(act, _tei("div"), type="scene", n=scene_n)
            sp = etree.SubElement(scene, _tei("sp"))
            for spec in lines:
                parts = spec.split(":")
                text = parts[0]
                part = parts[1] if len(parts) > 1 and parts[1] else None
                n = parts[2] if len(parts) > 2 and parts[2] else None
                line_el = etree.SubElement(sp, _tei("l"))
                line_el.text = text
                if part:
                    line_el.set("part", part)
                if n:
                    line_el.set("n", n)
    return root


def _scene(root: etree._Element, act_n: str = "1", scene_n: str = "1") -> etree._Element:
    return root.xpath(
        f"//tei:div[@type='act'][@n='{act_n}']/tei:div[@type='scene'][@n='{scene_n}']",
        namespaces=NS,
    )[0]


def _seq_values(scene: etree._Element) -> list[int]:
    lines = [
        line for line in scene.iter(_tei("l"))
        if line.get("part") in (None, "N", "I", "Y")
    ]
    return [int(line.get("n")) for line in lines]


class TestNoAnchors:
    def test_numbers_from_one(self):
        root = _build_play([("1", [("1", ["a", "b", "c"])])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        assert _seq_values(scene) == [1, 2, 3]
        assert not collisions


class TestBetweenAnchors:
    def test_even_gap(self):
        # anchor 10 at position 0, anchor 20 at position 5: 4 elements between,
        # gap 10 -> evenly spaced 12, 14, 16, 18
        root = _build_play([("1", [("1", ["a::10", "b", "c", "d", "e", "f::20"])])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        assert _seq_values(scene) == [10, 12, 14, 16, 18, 20]
        assert not any(c.collision for c in collisions)

    def test_uneven_gap_strictly_increasing(self):
        # gap 9, 8 elements between (lines_between=8 < gap=9, no collision)
        specs = ["a::10"] + [f"l{i}" for i in range(8)] + ["z::19"]
        root = _build_play([("1", [("1", specs)])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        vals = _seq_values(scene)
        assert vals[0] == 10
        assert vals[-1] == 19
        assert all(b > a for a, b in zip(vals, vals[1:]))
        assert not any(c.collision for c in collisions)

    def test_anchor_values_unchanged(self):
        root = _build_play([("1", [("1", ["a::10", "b", "c", "z::20"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        lines = list(scene.iter(_tei("l")))
        assert lines[0].get("n") == "10"
        assert lines[-1].get("n") == "20"


class TestCollision:
    def test_flagged_when_oversubscribed(self):
        # gap 3 (10->13), but 3 elements between -> lines_between(3) >= gap(3): collision
        root = _build_play([("1", [("1", ["a::10", "b", "c", "d", "z::13"])])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        assert any(c.collision for c in collisions)
        assert any("collision" in str(w) for w in warnings)

    def test_not_flagged_when_room_available(self):
        root = _build_play([("1", [("1", ["a::10", "b", "c", "z::20"])])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        assert not any(c.collision for c in collisions)

    def test_collision_output_still_monotonic_before_the_touch(self):
        # Even under a collision, everything up to the unavoidable final tie
        # must still be strictly increasing from the starting anchor.
        root = _build_play([("1", [("1", ["a::10", "b", "c", "d", "z::13"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        vals = _seq_values(scene)
        assert vals[0] == 10
        # non-decreasing everywhere; at most the last step may tie the anchor
        assert all(b >= a for a, b in zip(vals, vals[1:]))


class TestBeforeFirstAnchor:
    def test_backward_numbering(self):
        # first anchor "v" at new-line position k=3 (1-indexed) -> 2 preceding
        # elements get v-2, v-1
        root = _build_play([("1", [("1", ["a", "b", "c::10"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        assert _seq_values(scene) == [8, 9, 10]


class TestAfterLastAnchor:
    def test_forward_increment(self):
        root = _build_play([("1", [("1", ["a::10", "b", "c"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        assert _seq_values(scene) == [10, 11, 12]


class TestContinuationElements:
    def test_fm_copy_preceding_new_line(self):
        root = _build_play([("1", [("1", ["a::10", "b:F", "c:M", "d::20"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        lines = list(scene.iter(_tei("l")))
        assert lines[0].get("n") == "10"
        assert lines[1].get("n") == "10"
        assert lines[2].get("n") == "10"
        assert lines[3].get("n") == "20"

    def test_continuation_before_any_new_line_warns(self):
        root = _build_play([("1", [("1", ["a:F", "b::10"])])])
        scene = _scene(root)
        warnings, _ = number_scene(scene, "test.xml")
        assert any("precedes any new-line" in str(w) for w in warnings)


class TestPartNEquivalence:
    def test_part_n_treated_as_new_line(self):
        root = _build_play([("1", [("1", ["a::10", "b:N", "c::20"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        vals = _seq_values(scene)
        assert vals == [10, 15, 20]

    def test_part_i_and_y_are_new_line(self):
        root = _build_play([("1", [("1", ["a::10", "b:I", "c:Y", "d::20"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")
        assert _seq_values(scene) == [10, 13, 17, 20]


class TestNeverModifiesExistingAnchors:
    def test_anchor_text_and_n_untouched(self):
        root = _build_play([("1", [("1", ["a::10", "b", "z::20"])])])
        scene = _scene(root)
        anchor = list(scene.iter(_tei("l")))[0]
        assert anchor.get("n") == "10"
        number_scene(scene, "test.xml")
        assert anchor.get("n") == "10"
        assert anchor.text == "a"


class TestMalformedAnchor:
    def test_non_numeric_n_left_untouched_and_warned(self):
        # "131 132" mirrors a real corpus anomaly (cor.xml): a prose passage
        # mistagged as <l> carrying two space-separated Globe numbers.
        root = _build_play([("1", [("1", ["a::10", "b::131 132", "c", "d::200"])])])
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        lines = list(scene.iter(_tei("l")))
        assert lines[1].get("n") == "131 132"  # untouched
        assert any("non-numeric" in str(w) for w in warnings)
        # numbering on either side still proceeds without crashing
        assert lines[0].get("n") == "10"
        assert lines[2].get("n") is not None
        assert lines[3].get("n") == "200"

    def test_does_not_raise(self):
        root = _build_play([("1", [("1", ["a::5 6", "b", "c"])])])
        scene = _scene(root)
        number_scene(scene, "test.xml")  # must not raise


class TestEmptyScene:
    def test_no_l_elements_warns_no_crash(self):
        root = etree.Element(_tei("TEI"), nsmap={None: TEI_NS})
        body = etree.SubElement(root, _tei("body"))
        act = etree.SubElement(body, _tei("div"), type="act", n="1")
        etree.SubElement(act, _tei("div"), type="scene", n="1")
        scene = _scene(root)
        warnings, collisions = number_scene(scene, "test.xml")
        assert any("no <l> elements" in str(w) for w in warnings)
        assert collisions == []


class TestStageExclusion:
    def test_l_inside_stage_not_numbered_or_counted(self):
        root = etree.Element(_tei("TEI"), nsmap={None: TEI_NS})
        body = etree.SubElement(root, _tei("body"))
        act = etree.SubElement(body, _tei("div"), type="act", n="1")
        scene = etree.SubElement(act, _tei("div"), type="scene", n="1")
        sp = etree.SubElement(scene, _tei("sp"))
        l1 = etree.SubElement(sp, _tei("l"))
        l1.text = "a"
        l1.set("n", "10")
        stage = etree.SubElement(sp, _tei("stage"))
        stage_l = etree.SubElement(stage, _tei("l"))
        stage_l.text = "sung aside"
        l2 = etree.SubElement(sp, _tei("l"))
        l2.text = "b"
        assert len(collect_scene_lines(scene)) == 2
        number_scene(scene, "test.xml")
        assert stage_l.get("n") is None
        assert l2.get("n") == "11"


class TestNumberDocument:
    def test_processes_every_scene(self):
        root = _build_play([
            ("1", [("1", ["a", "b"]), ("2", ["c::5", "d"])]),
            ("2", [("1", ["e", "f"])]),
        ])
        warnings, collisions = number_document(root, "test.xml")
        for scene in root.iter(_tei("div")):
            if scene.get("type") != "scene":
                continue
            for line in scene.iter(_tei("l")):
                assert line.get("n") is not None
