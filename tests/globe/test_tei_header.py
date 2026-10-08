"""doc/agenda.org #build/tei-header: the rewritten sourceDesc/editorialDecl.

Unit tests for the pure builder functions (no witness OCR needed -- catalog
facts are passed in directly). The full rewrite() path, which loads the
witness registry, is exercised by tests/test_regenerate_lear.py's
end-to-end build, tagged @needs_witnesses there.
"""

from pathlib import Path

import pytest
from lxml import etree

from globe import shared_lines
from globe import tei_header

REPO = Path(__file__).resolve().parent.parent.parent

TEI = "http://www.tei-c.org/ns/1.0"

CATALOGS = {
    "miun": {"hathitrust": "miun.aba6868.0001.001", "record": "000241315"},
    "trent": {"ia": "worksofwilliamsh0000shak_y3h8", "ark": "ark:/13960/t2h78660m"},
}


PIN = {"commit": "c34c2d4", "play": "shake000033"}


def _row(kind: str) -> shared_lines.Row:
    return shared_lines.Row(play="lr", scene="1.1", page=1, kind=kind, first_half="a",
                            second_half="b", line="", basis="image", checked="x")


def test_junction_count_excludes_numeral_rows():
    table = [_row("shared"), _row("shared"), _row("turnover"), _row("numeral")]
    assert tei_header.count_junctions(table) == 3
    assert tei_header.count_junctions([]) == 0


def test_source_desc_names_the_oclc_and_holds_no_bare_doubleday():
    sd = tei_header.build_source_desc("lr", CATALOGS)
    text = etree.tostring(sd, encoding="unicode")
    assert "08687211" in text  # the OCLC record
    assert "19--" in text  # Tufts's own records give no more precise date
    assert "1950" not in text.split("Volume One")[0]  # not asserted for Lear's own volume
    assert 'xml:id="globe-edition"' not in text  # retired: unreferenced now @source is gone


def test_source_desc_cites_both_witnesses_from_the_registry_not_hardcoded():
    sd = tei_header.build_source_desc("lr", CATALOGS)
    text = etree.tostring(sd, encoding="unicode")
    assert "miun.aba6868.0001.001" in text and "000241315" in text
    assert "worksofwilliamsh0000shak_y3h8" in text
    swapped = dict(CATALOGS, miun={"hathitrust": "x", "record": "y"})
    text2 = etree.tostring(tei_header.build_source_desc("lr", swapped), encoding="unicode")
    assert "x" in text2 and "y" in text2 and "miun.aba6868.0001.001" not in text2


def test_editorial_decl_states_the_computed_junction_count_not_a_fixed_one():
    text5 = etree.tostring(tei_header.build_editorial_decl("lr", 5, PIN), encoding="unicode")
    text8 = etree.tostring(tei_header.build_editorial_decl("lr", 8, PIN), encoding="unicode")
    assert "Five junctions" in text5
    assert "Eight junctions" in text8
    assert "5 junctions" not in text5 and "8 junctions" not in text8  # spelled, not a digit


def test_editorial_decl_drops_f1_provenance_and_states_f1_is_not_carried():
    text = etree.tostring(tei_header.build_editorial_decl("lr", 8, PIN), encoding="unicode")
    assert "Bodleian" not in text and "Through-Line-Number" not in text  # old provenance disclaimer
    assert "not carried by this edition" in text


def test_editorial_decl_cites_the_folger_at_the_pinned_commit_not_a_typed_one():
    """canonical-engLit doc/agenda.org #globe/pin-dracor: the commit and the
    DraCor id come from the manifest's row for the play's ShakeDraCor file."""
    text = " ".join(etree.tostring(tei_header.build_editorial_decl("lr", 8, PIN),
                                   encoding="unicode").split())
    assert "(ShakeDraCor, play shake000033; github.com/dracor-org/shakedracor, commit c34c2d4)" in text
    other = " ".join(etree.tostring(tei_header.build_editorial_decl(
        "lr", 8, {"commit": "abc1234", "play": "shake000099"}), encoding="unicode").split())
    assert "play shake000099; github.com/dracor-org/shakedracor, commit abc1234)" in other
    assert "c34c2d4" not in other and "shake000033" not in other


def test_canonical_and_review_filenames_follow_the_play():
    assert tei_header.canonical_filename("lr") == "shakespeare.lr.globe.xml"
    assert tei_header.review_filename("lr") == "shakespeare.lr.globe.review.xml"
    assert tei_header.canonical_filename("ant") == "shakespeare.ant.globe.xml"


def _idno(pub, type_: str) -> str:
    return pub.findtext(f'{{{TEI}}}idno[@type="{type_}"]')


def test_publication_stmt_derives_filename_and_cts_idno_not_hardcoded():
    pub = tei_header.build_publication_stmt("lr", "urn:cts:engLit:shakespeare.lr.globe")
    assert _idno(pub, "filename") == "shakespeare.lr.globe.xml"
    assert _idno(pub, "CTS") == "urn:cts:engLit:shakespeare.lr.globe"
    assert pub.find(f"{{{TEI}}}date") is None  # not yet settled
    # a different xml:base must produce a different CTS idno -- proof it's derived
    pub2 = tei_header.build_publication_stmt("lr", "urn:cts:engLit:something-else")
    assert _idno(pub2, "CTS") == "urn:cts:engLit:something-else"


def test_encoding_ps_state_the_milestone_and_lb_convention():
    ps = tei_header.build_encoding_ps()
    assert len(ps) == 2
    joined = " ".join(" ".join(etree.tostring(p, encoding="unicode").split()) for p in ps)
    assert "reconstructing the page's rows requires reading both elements" in joined
    assert "@part" in joined
    assert "<gi>" not in joined and "<att>" not in joined  # not in perseus_drama.rng's content model


def _header_tree():
    xml = f"""<TEI xmlns="{TEI}"><teiHeader>
      <fileDesc>
        <publicationStmt><p>STALE-PUBLICATIONSTMT</p></publicationStmt>
        <sourceDesc><biblStruct><monogr><title>STALE-SOURCEDESC</title></monogr></biblStruct></sourceDesc>
      </fileDesc>
      <encodingDesc>
        <refsDecl n="CTS" xml:id="CTS"><citeStructure match="/TEI/text/body" use="@xml:base"/></refsDecl>
        <editorialDecl><p>old F1 provenance disclaimer</p></editorialDecl>
      </encodingDesc>
      <revisionDesc><change><ab>x</ab></change></revisionDesc>
    </teiHeader><text><body xml:base="urn:cts:engLit:shakespeare.lr.globe"/></text></TEI>"""
    return etree.fromstring(xml)


def _rewrite(root):
    table = [shared_lines.Row("lr", "1.1", 1, "shared", "a", "b", "", "image", checked="x")]
    import unittest.mock as mock
    with mock.patch("globe.tei_header.witnesses.load") as load:
        w = mock.Mock()
        w.catalog = CATALOGS["miun"]
        wt = mock.Mock()
        wt.catalog = CATALOGS["trent"]
        load.return_value.witness.side_effect = lambda wid: {"miun": w, "trent": wt}[wid]
        tei_header.rewrite(root, "lr", table)


def test_rewrite_replaces_the_shells_refsdecl():
    """The shell's refsDecl is discarded: on mvp it cites lines by position
    among <lb ed="G">, which the regenerated body does not have
    (canonical-engLit doc/forum.org #encoding/shakespeare-citestructures)."""
    root = _header_tree()
    root.find(f"{{{TEI}}}teiHeader/{{{TEI}}}encodingDesc/{{{TEI}}}refsDecl").set("marker", "shell")
    _rewrite(root)
    refs = root.findall(f"{{{TEI}}}teiHeader/{{{TEI}}}encodingDesc/{{{TEI}}}refsDecl")
    assert len(refs) == 1 and refs[0].get("marker") is None
    ns = {"t": TEI}
    assert refs[0].xpath("t:citeStructure/t:citeStructure/@match", namespaces=ns) == [
        "div[@type='act'][@n != 'cast']"]
    scene = refs[0].xpath(".//t:citeStructure[@unit='scene']", namespaces=ns)[0]
    assert scene.get("n") == "chunk"
    assert [c.get("match") for c in refs[0].iter(f"{{{TEI}}}citeStructure") if c.get("unit") == "line"] == [
        ".//milestone[@unit='line'][@ed='Globe']", "sp//milestone[@unit='line'][@ed='Globe']"]


def _body(inner):
    return etree.fromstring(f'<body xmlns="{TEI}">{inner}</body>')


MS = '<milestone unit="line" ed="Globe" n="1"/>'


def test_every_line_citable_in_a_scene_or_an_act_level_speech():
    tei_header.check_every_line_citable(_body(
        f'<div type="act" n="cast"><castList/></div>'
        f'<div type="act" n="prologue"><sp><l>{MS}O for a Muse</l></sp></div>'
        f'<div type="act" n="1"><div type="scene" n="1"><sp><l>{MS}My lord</l></sp></div></div>'))


def test_a_line_outside_any_speech_or_scene_stops_the_build():
    with pytest.raises(ValueError, match="1 of 1 Globe line milestones are not citable"):
        tei_header.check_every_line_citable(_body(f'<div type="act" n="prologue"><l>{MS}O for a Muse</l></div>'))


def test_a_line_in_the_cast_list_stops_the_build():
    with pytest.raises(ValueError, match="not citable"):
        tei_header.check_every_line_citable(_body(f'<div type="act" n="cast"><sp><l>{MS}x</l></sp></div>'))


def test_rewrite_replaces_source_desc_and_editorial_decl():
    root = _header_tree()
    table = [shared_lines.Row("lr", "1.1", 1, "shared", "a", "b", "", "image", checked="x")]
    import unittest.mock as mock
    with mock.patch("globe.tei_header.witnesses.load") as load:
        w = mock.Mock()
        w.catalog = CATALOGS["miun"]
        wt = mock.Mock()
        wt.catalog = CATALOGS["trent"]
        load.return_value.witness.side_effect = lambda wid: {"miun": w, "trent": wt}[wid]
        tei_header.rewrite(root, "lr", table)
    pub_text = etree.tostring(root.find(f"{{{TEI}}}teiHeader/{{{TEI}}}fileDesc/{{{TEI}}}publicationStmt"),
                              encoding="unicode")
    source_text = etree.tostring(root.find(f"{{{TEI}}}teiHeader/{{{TEI}}}fileDesc/{{{TEI}}}sourceDesc"),
                                 encoding="unicode")
    editorial_text = etree.tostring(
        root.find(f"{{{TEI}}}teiHeader/{{{TEI}}}encodingDesc/{{{TEI}}}editorialDecl"), encoding="unicode")
    assert "STALE-PUBLICATIONSTMT" not in pub_text
    assert 'idno type="CTS">urn:cts:engLit:shakespeare.lr.globe<' in pub_text
    assert "STALE-SOURCEDESC" not in source_text
    assert "old F1 provenance disclaimer" not in editorial_text
    assert "One junctions" in editorial_text  # one shared row in the fake table, spelled out
    ps = root.findall(f"{{{TEI}}}teiHeader/{{{TEI}}}encodingDesc/{{{TEI}}}p")
    assert len(ps) == 2
