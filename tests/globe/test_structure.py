"""The play's structure around its body (src/globe/structure.py) and its
speakers (src/globe/speakers.py)."""

from __future__ import annotations

import pytest
from lxml import etree

from globe import speakers, structure

TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


@pytest.mark.parametrize(("n", "top", "kind"), [
    ("1", True, "act"), ("induction", True, "induction"), ("ind", True, "induction"),
    ("prologue", True, "prologue"), ("epilogue", True, "epilogue"),
    ("2", False, "scene"), ("prologue", False, "prologue"),  # Henry V's choruses
    ("chorus", False, "chorus"), ("chorus1", False, "chorus"),  # Gower's
])
def test_a_division_is_typed_by_what_it_is(n, top, kind):
    assert structure.division_type(n, top) == kind


def test_an_unknown_division_stops_the_build():
    with pytest.raises(structure.StructureError):
        structure.division_type("masque", True)


PRINTED = ["EARL OF NORTHUMBERLAND", "LADY NORTHUMBERLAND", "EDMUND MORTIMER, Earl of March",
           "LADY MORTIMER, daughter to Glendower", "Lord Chief-Justice of the King's Bench",
           "A Servant of the Chief-Justice", "Gentleman", "First Gentleman", "WART", "EARL OF WARWICK"]


@pytest.mark.parametrize(("label", "role"), [
    ("Lady N.", "LADY NORTHUMBERLAND"),
    ("Mort.", "EDMUND MORTIMER, Earl of March"),  # not LADY MORTIMER
    ("Ch. Just.", "Lord Chief-Justice of the King's Bench"),  # not the servant
    ("Gent.", "Gentleman"),  # not First Gentleman
    ("Wart.", "WART"),
])
def test_a_label_names_its_printed_role(label, role):
    assert PRINTED[speakers.candidates(label, PRINTED)[0][1]] == role


@pytest.mark.parametrize(("name", "group"), [
    ("All", True), ("two Gardeners", True), ("Ferdinand and Miranda", True), ("Thieves", True),
    ("Cassius", False), ("Pericles", False), ("Sir John Falstaff", False),
])
def test_groups(name, group):
    assert speakers.is_group(name) is group


def test_names_from_printed_roles():
    assert speakers.clean_name("HAMLET, son to the late") == "Hamlet"
    assert speakers.clean_name("DUKE OF FLORENCE") == "Duke of Florence"
    assert speakers.clean_name("Sec. Hun.") == "Sec. Hun"


def test_a_p4_entity_is_resolved_in_a_name():
    role = etree.fromstring('<!DOCTYPE r [<!ENTITY AElig "x">]><role>&AElig;GEON</role>',
                            etree.XMLParser(resolve_entities=False))
    assert speakers.text(role) == "ÆGEON"


P4 = """<TEI.2><text><body>
<div1 type="act" n="cast"><head>DRAMATIS PERSONÆ</head>
 <castList>
  <castItem type="role"><role id="p-1"/></castItem>
  <castItem type="role"><role id="ham.">HAMLET</role><roleDesc>a prince</roleDesc></castItem>
  <castItem type="list"><role>Officers</role><role id="p-2">Soldiers</role> and other Attendants</castItem>
  <castItem type="role"><role>FRANCISCO</role></castItem>
 </castList>
 <stage>SCENE: Elsinore.</stage>
</div1>
<div1 type="act" n="1"><div2 type="scene" n="1"><sp who="p-1"><speaker>Fran.</speaker><l>Stand</l></sp></div2></div1>
</body></text></TEI.2>"""


def _doc():
    root = etree.fromstring(f"""<TEI xmlns="{TEI}"><teiHeader><profileDesc><langUsage/></profileDesc></teiHeader>
<text><body>
<div type="act" n="cast"><head>DRAMATIS PERSONÆ</head></div>
<div type="act" n="prologue"><p>x</p></div>
<div type="act" n="1"><div type="scene" n="prologue"/><div type="scene" n="1">
<sp who="p-1"><speaker>Fran.</speaker></sp><sp who="ham. p-2"/></div></div>
</body></text></TEI>""")
    rows = [speakers.Row("x", "p-1", "person", "Francisco", "FRANCISCO", "1", "label", "cliff"),
            speakers.Row("x", "ham.", "person", "Hamlet", "HAMLET", "1", "p4", "p4"),
            speakers.Row("x", "p-2", "personGrp", "Soldiers", "Soldiers", "1", "p4", "p4")]
    return root, rows


def test_restructure():
    root, rows = _doc()
    structure.restructure(root, etree.fromstring(P4), rows)
    ns = {"t": TEI}
    body = root.find(f"{{{TEI}}}text/{{{TEI}}}body")
    assert [d.get("type") for d in body.findall(f"{{{TEI}}}div")] == ["prologue", "act"]
    assert [d.get("type") for d in body.findall(f"{{{TEI}}}div/{{{TEI}}}div")] == ["prologue", "scene"]
    front = root.find(f"{{{TEI}}}text/{{{TEI}}}front")
    assert root.find(f"{{{TEI}}}text")[0] is front  # before the body
    cl = front.find(f"{{{TEI}}}castList")
    assert cl[0].tag == f"{{{TEI}}}head"
    roles = {r.text: r for r in cl.iter(f"{{{TEI}}}role")}
    assert set(roles) == {"HAMLET", "Officers", "Soldiers", "FRANCISCO"}  # the placeholder is gone
    assert roles["HAMLET"].get("corresp") == "#ham." and roles["HAMLET"].get(XML_ID) is None
    assert roles["FRANCISCO"].get("corresp") == "#p-1"  # linked by the table, not an id
    assert roles["Officers"].get("corresp") is None
    assert roles["Soldiers"].tail == " and other Attendants"  # a list item's own words stay
    assert front.xpath("t:set/t:stage/text()", namespaces=ns) == ["SCENE: Elsinore."]
    assert [sp.get("who") for sp in body.iter(f"{{{TEI}}}sp")] == ["#p-1", "#ham. #p-2"]
    lp = root.find(f"{{{TEI}}}teiHeader/{{{TEI}}}profileDesc/{{{TEI}}}particDesc/{{{TEI}}}listPerson")
    assert [(etree.QName(e).localname, e.get(XML_ID)) for e in lp] == [
        ("person", "p-1"), ("person", "ham."), ("personGrp", "p-2")]


def test_a_speaker_missing_from_the_table_stops_the_build():
    root, rows = _doc()
    with pytest.raises(structure.StructureError, match="does not have"):
        structure.restructure(root, etree.fromstring(P4), rows[1:])
