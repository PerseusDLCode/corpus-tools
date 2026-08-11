from __future__ import annotations

import sys
from pathlib import Path

import pytest

from commands.number_verse_lines import main
from tei import TEIDocument, NS
from verse_numbering import number_document


def _invoke(argv: list[str]) -> int:
    sys.argv = argv
    with pytest.raises(SystemExit) as exc:
        main()
    return exc.value.code

LR_XML = (
    Path(__file__).parent.parent.parent
    / "canonical-engLit" / "data" / "shakespeare" / "lr.xml"
)


@pytest.fixture
def lr_doc():
    if not LR_XML.exists():
        pytest.skip(f"canonical-engLit lr.xml not found at {LR_XML}")
    return TEIDocument(LR_XML)


class TestAgainstRepairedLear:
    """Integration test against the real, repaired corpus file.

    Mirrors the spec's own validation checklist in
    canonical-engLit/src/mvp/number_verse_lines_spec.md.
    """

    def test_original_anchor_count(self, lr_doc):
        anchors = lr_doc.root.findall(".//tei:l[@n]", NS)
        assert len(anchors) == 182

    def test_every_l_gets_n(self, lr_doc):
        before_anchor_texts = {
            (line.get("n"), (line.text or "").strip())
            for line in lr_doc.root.findall(".//tei:l[@n]", NS)
        }
        number_document(lr_doc.root, "lr.xml")
        all_l = lr_doc.root.findall(".//tei:l", NS)
        assert all_l
        assert all(line.get("n") is not None for line in all_l)
        # anchors preserved
        after_anchor_pairs = {
            (line.get("n"), (line.text or "").strip())
            for line in all_l
            if (line.get("n"), (line.text or "").strip()) in before_anchor_texts
        }
        assert len(after_anchor_pairs) == len(before_anchor_texts)

    def test_continuation_elements_match_preceding(self, lr_doc):
        number_document(lr_doc.root, "lr.xml")
        for scene in lr_doc.root.findall(".//tei:div[@type='scene']", NS):
            last_new_line_n = None
            for line in scene.iter("{http://www.tei-c.org/ns/1.0}l"):
                part = line.get("part")
                if part == "N":
                    part = None
                if part in (None, "I", "Y"):
                    last_new_line_n = line.get("n")
                elif part in ("F", "M") and last_new_line_n is not None:
                    assert line.get("n") == last_new_line_n

    def test_strictly_increasing_except_flagged_collisions(self, lr_doc):
        _, collisions = number_document(lr_doc.root, "lr.xml")
        collision_bs = {(c.act, c.scene, c.anchor_b) for c in collisions if c.collision}
        for scene in lr_doc.root.findall(".//tei:div[@type='scene']", NS):
            act = scene.xpath("ancestor::tei:div[@type='act'][1]/@n", namespaces=NS)
            act = act[0] if act else "?"
            scene_n = scene.get("n")
            seq = [
                line for line in scene.iter("{http://www.tei-c.org/ns/1.0}l")
                if line.get("part") in (None, "N", "I", "Y")
            ]
            vals = [int(line.get("n")) for line in seq]
            for a, b in zip(vals, vals[1:]):
                if b == a and (act, scene_n, b) in collision_bs:
                    continue  # documented, unavoidable collision tie
                assert b > a, f"act {act} scene {scene_n}: {a} -> {b}"


_MINIMAL_TEI = (
    '<?xml version="1.0"?>'
    '<TEI xmlns="http://www.tei-c.org/ns/1.0"><body>'
    '<div type="act" n="1"><div type="scene" n="1"><sp>'
    "<l>a</l><l>b</l><l>c</l>"
    "</sp></div></div></body></TEI>"
)


class TestCLI:
    def test_dry_run_exits_zero_and_writes_nothing(self, tmp_path):
        source = tmp_path / "tiny.xml"
        source.write_text(_MINIMAL_TEI, encoding="utf-8")
        before = source.read_text()
        code = _invoke(["number-verse-lines", "--dry-run", str(source)])
        assert code == 0
        assert source.read_text() == before

    def test_writes_output_file(self, tmp_path):
        source = tmp_path / "tiny.xml"
        source.write_text(_MINIMAL_TEI, encoding="utf-8")
        written = tmp_path / "out.xml"
        code = _invoke(["number-verse-lines", str(source), "-o", str(written)])
        assert code == 0
        assert written.exists()
        doc = TEIDocument(written)
        ls = doc.root.findall(".//tei:l", NS)
        assert [line.get("n") for line in ls] == ["1", "2", "3"]

    def test_batch_writes_into_output_dir(self, tmp_path):
        source1 = tmp_path / "one.xml"
        source2 = tmp_path / "two.xml"
        source1.write_text(_MINIMAL_TEI, encoding="utf-8")
        source2.write_text(_MINIMAL_TEI, encoding="utf-8")
        out_dir = tmp_path / "out"
        code = _invoke(["number-verse-lines", str(source1), str(source2), "-o", str(out_dir)])
        assert code == 0
        assert (out_dir / "one.xml").exists()
        assert (out_dir / "two.xml").exists()

    def test_default_writes_in_place(self, tmp_path):
        source = tmp_path / "tiny.xml"
        source.write_text(_MINIMAL_TEI, encoding="utf-8")
        code = _invoke(["number-verse-lines", str(source)])
        assert code == 0
        doc = TEIDocument(source)
        ls = doc.root.findall(".//tei:l", NS)
        assert [line.get("n") for line in ls] == ["1", "2", "3"]

    def test_dry_run_collision_exits_one(self, tmp_path):
        source = tmp_path / "collide.xml"
        source.write_text(
            '<?xml version="1.0"?>'
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><body>'
            '<div type="act" n="1"><div type="scene" n="1"><sp>'
            '<l n="10">a</l><l>b</l><l>c</l><l>d</l><l n="13">z</l>'
            "</sp></div></div></body></TEI>",
            encoding="utf-8",
        )
        code = _invoke(["number-verse-lines", "--dry-run", str(source)])
        assert code == 1
