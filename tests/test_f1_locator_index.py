from __future__ import annotations

from f1_locator_index import build_f1_locator_index, play_locators

PLAY_F1 = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="shake000099">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Test Play</title>
      </titleStmt>
      <publicationStmt>
        <publisher>Folger Digital Texts</publisher>
        <idno>Tst</idno>
      </publicationStmt>
    </fileDesc>
  </teiHeader>
  <text>
    <body xml:base="urn:cts:engLit:shakespeare.tst.f1">
      <div type="prologue" n="PRO">
        <sp>
          <p><lb xml:id="ftln-0001" n="1"/>Prologue line one. </p>
        </sp>
      </div>
      <div type="act" n="1">
        <div type="scene" n="1">
          <l xml:id="ftln-0002" n="1">a</l>
          <l xml:id="ftln-0003" n="2">b</l>
        </div>
        <div type="scene" n="2">
          <l xml:id="ftln-0004" n="1">c</l>
        </div>
      </div>
      <div type="act" n="2">
        <div type="chorus" n="2.CHO">
          <sp>
            <l xml:id="ftln-0005" n="1">Chorus line. </l>
          </sp>
        </div>
        <div type="scene" n="1">
          <sp>
            <p><lb xml:id="ftln-0006" n="1"/>Prose line one. <lb xml:id="ftln-0007" n="2"/>Prose line two. </p>
          </sp>
        </div>
      </div>
    </body>
  </text>
</TEI>
"""


def test_ordinary_act_scene_line_locators(tmp_path):
    f1_file = tmp_path / "shakespeare.tst.f1.xml"
    f1_file.write_text(PLAY_F1, encoding="utf-8")

    locators = play_locators(f1_file)

    assert locators == {"1.1.1", "1.1.2", "1.2.1", "2.1.1", "2.1.2"}


def test_chorus_and_prologue_divs_excluded(tmp_path):
    f1_file = tmp_path / "shakespeare.tst.f1.xml"
    f1_file.write_text(PLAY_F1, encoding="utf-8")

    locators = play_locators(f1_file)

    assert not any("PRO" in loc for loc in locators)
    assert not any("CHO" in loc for loc in locators)


def test_build_f1_locator_index_keys_by_playid(tmp_path):
    play_dir = tmp_path / "tst"
    play_dir.mkdir()
    (play_dir / "shakespeare.tst.f1.xml").write_text(PLAY_F1, encoding="utf-8")

    index = build_f1_locator_index(tmp_path)

    assert set(index.keys()) == {"tst"}
    assert "1.1.1" in index["tst"]
