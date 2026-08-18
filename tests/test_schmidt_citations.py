from __future__ import annotations

from lxml import etree

from schmidt_citations import (
    apply_fixes,
    apply_fixes_to_text,
    find_collapsed_citations,
    find_unresolved_citations,
    scenes_per_act,
)
from tln_globe_map import CorpusMap, build_corpus_map


PLAY_TEI = """<?xml version="1.0" encoding="utf-8"?>
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
    <body>
      <div type="act" n="1">
        <div type="scene" n="1">
          <l xml:id="ftln-0001" n="1.1.1">a</l>
          <l xml:id="ftln-0002" n="1.1.2">b</l>
          <l xml:id="ftln-0003" n="1.1.3">c</l>
        </div>
        <div type="scene" n="2">
          <l xml:id="ftln-0004" n="1.2.1">d</l>
          <l xml:id="ftln-0005" n="1.2.2">e</l>
        </div>
      </div>
      <div type="act" n="2">
        <div type="scene" n="1">
          <l xml:id="ftln-0006" n="2.1.1">f</l>
          <l xml:id="ftln-0007" n="2.1.2">g</l>
          <l xml:id="ftln-0008" n="2.1.3">h</l>
          <l xml:id="ftln-0009" n="2.1.4">i</l>
          <l xml:id="ftln-0010" n="2.1.5">j</l>
        </div>
      </div>
    </body>
  </text>
</TEI>
"""

LEXICON_TEI = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text>
    <body>
      <bibl n="shak. tst 1.1.1">I, 1, 1</bibl>
      <bibl n="shak. tst 2.99.7">II, 3</bibl>
      <bibl n="shak. tst 1.99.2">I, 2</bibl>
      <bibl n="shak. tst 2.99.99">Tst. II, 3</bibl>
      <bibl n="shak. tst 2.99.50">II, 50</bibl>
    </body>
  </text>
</TEI>
"""


def _setup(tmp_path):
    tei_dir = tmp_path / "tei"
    tei_dir.mkdir()
    (tei_dir / "test-play.xml").write_text(PLAY_TEI)

    corpus_data = build_corpus_map(tei_dir)
    corpus_map = CorpusMap(corpus_data)
    scenes = {
        play: scenes_per_act(tei_dir, corpus_data, play) for play in corpus_data["plays"]
    }
    return corpus_data, corpus_map, scenes


def _lexicon_root():
    return etree.fromstring(LEXICON_TEI.encode())


def test_scenes_per_act(tmp_path):
    _, _, scenes = _setup(tmp_path)
    assert scenes == {"tst": {"1": 2, "2": 1}}


def test_single_scene_act_bare_display_is_fixed(tmp_path):
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)

    assert len(fixes) == 1
    fix = fixes[0]
    assert fix.play == "tst"
    assert fix.old_n == "shak. tst 2.99.7"
    assert fix.new_n == "shak. tst 2.1.3"
    assert fix.tln == 8


def test_multi_scene_act_with_bare_display_is_not_fixed(tmp_path):
    # Act 1 has two scenes, so "I, 2" (bare Roman-numeral display) has a real
    # scene to disambiguate -- the single-scene-Act collapse doesn't apply.
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    assert not any(f.old_n == "shak. tst 1.99.2" for f in fixes)


def test_single_scene_act_with_non_bare_display_is_not_fixed(tmp_path):
    # "Tst. II, 3" carries a leading title abbreviation -- not the bare
    # "Roman, line" shape this bug produces, so it's left alone.
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    assert not any(f.old_n == "shak. tst 2.99.99" for f in fixes)


def test_unresolvable_reconstruction_is_not_fixed(tmp_path):
    # "II, 50" is a bare Roman/line pair in a single-scene Act, but Act 2
    # Scene 1 only has 5 lines -- the reconstructed ref can't resolve, so no
    # fix is emitted rather than an unverified guess.
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    assert not any(f.old_n == "shak. tst 2.99.50" for f in fixes)


def test_already_resolving_citation_is_not_touched(tmp_path):
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    assert not any(f.old_n == "shak. tst 1.1.1" for f in fixes)


def test_apply_fixes_mutates_the_element(tmp_path):
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    apply_fixes(fixes)

    biblio = root.xpath(
        "//tei:bibl[starts-with(@n, 'shak. tst 2.1.')]",
        namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
    )
    assert len(biblio) == 1
    assert biblio[0].get("n") == "shak. tst 2.1.3"


def test_apply_fixes_to_text_only_touches_the_fixed_attribute_values(tmp_path):
    # Simulates the real lexicon's hand-wrapped formatting -- the fix must
    # not disturb anything but the n="..." value itself.
    text = (
        '<bibl\n              n="shak. tst 2.99.7">II, 3</bibl>. <bibl\n'
        '  n="shak. tst 1.1.1">I, 1, 1</bibl>\n'
    )
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)

    fixed_text = apply_fixes_to_text(text, fixes)
    assert fixed_text == (
        '<bibl\n              n="shak. tst 2.1.3">II, 3</bibl>. <bibl\n'
        '  n="shak. tst 1.1.1">I, 1, 1</bibl>\n'
    )


def test_find_unresolved_citations_excludes_fixed_and_already_resolving(tmp_path):
    _, corpus_map, scenes = _setup(tmp_path)
    root = _lexicon_root()
    fixes = find_collapsed_citations(root, corpus_map, scenes)
    fixed_elements = {f.element for f in fixes}

    unresolved = find_unresolved_citations(root, corpus_map, fixed_elements)
    unresolved_ns = {n for _play, n, _disp in unresolved}

    assert unresolved_ns == {"shak. tst 1.99.2", "shak. tst 2.99.99", "shak. tst 2.99.50"}
