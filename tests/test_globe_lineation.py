from __future__ import annotations

from lxml import etree

from globe_lineation import (
    ConversionError,
    ConversionStats,
    convert_body,
    q,
)

P4_PARSER = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)


def _p4_fragment(body_xml: str) -> etree._Element:
    doc = f"<TEI.2><text><body>{body_xml}</body></text></TEI.2>"
    return etree.fromstring(doc.encode("utf-8"), P4_PARSER)


def _convert(body_xml: str) -> tuple[etree._Element, ConversionStats]:
    root = _p4_fragment(body_xml)
    stats = ConversionStats()
    new_body = convert_body(root, stats)
    return new_body, stats


def _milestones(body):
    return body.findall(f".//{q('milestone')}")


class TestLbConversion:
    def test_numbered_globe_lb_becomes_numbered_milestone(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<p>text <lb n="12" ed="G"/></p></div2></div1>')
        ms = _milestones(body)
        assert len(ms) == 1
        assert ms[0].get("unit") == "line"
        assert ms[0].get("ed") == "Globe"
        assert ms[0].get("n") == "12"
        assert stats.milestone_globe_numbered == 1
        assert stats.milestone_globe_unnumbered == 0

    def test_unnumbered_globe_lb_becomes_unnumbered_milestone(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<p>text <lb ed="G"/></p></div2></div1>')
        ms = _milestones(body)
        assert len(ms) == 1
        assert ms[0].get("ed") == "Globe"
        assert ms[0].get("n") is None
        assert stats.milestone_globe_unnumbered == 1

    def test_f1_lb_becomes_numbered_milestone(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<p>text <lb n="99" ed="F1"/></p></div2></div1>')
        ms = _milestones(body)
        assert ms[0].get("ed") == "F1"
        assert ms[0].get("n") == "99"
        assert stats.milestone_f1 == 1

    def test_f1_lb_without_n_raises(self):
        try:
            _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                      '<p><lb ed="F1"/></p></div2></div1>')
            assert False, "expected ConversionError"
        except ConversionError:
            pass

    def test_unexpected_ed_raises(self):
        try:
            _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                      '<p><lb ed="Q" n="1"/></p></div2></div1>')
            assert False, "expected ConversionError"
        except ConversionError:
            pass


class TestLConversion:
    def test_part_preserved_no_n_added(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<l part="I">split line</l></div2></div1>')
        l = body.find(f".//{q('l')}")
        assert l.get("part") == "I"
        assert l.get("n") is None

    def test_stray_n_stripped_and_reported(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<l n="111" part="I">Is he pursued?</l></div2></div1>')
        l = body.find(f".//{q('l')}")
        assert l.get("n") is None
        assert l.get("part") == "I"
        assert len(stats.l_stray_n_stripped) == 1


class TestRegConversion:
    def test_reg_orig_collapses_to_plain_text(self):
        body, stats = _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                                '<p>any further <reg orig="de-lay">delay</reg> please</p>'
                                '</div2></div1>')
        p = body.find(f".//{q('p')}")
        # <orig>/<reg> are not in the Perseus P5 schema; the P4 shorthand collapses to
        # plain text (the regularized reading P4 itself displays), no wrapper element.
        assert p.find(q("choice")) is None
        assert p.find(q("reg")) is None
        assert p.find(q("orig")) is None
        assert "".join(p.itertext()) == "any further delay please"
        assert stats.reg_collapsed_to_text == [(
            "Act 1, Scene 1", "de-lay", "delay",
        )]

    def test_reg_missing_orig_raises(self):
        try:
            _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                      '<p><reg>delay</reg></p></div2></div1>')
            assert False, "expected ConversionError"
        except ConversionError:
            pass


class TestDivAndRole:
    def test_div1_div2_become_typed_div(self):
        body, _ = _convert('<div1 type="act" n="1"><div2 type="scene" n="2">'
                            "<p>x</p></div2></div1>")
        act = body.find(q("div"))
        assert act.get("type") == "act"
        assert act.get("n") == "1"
        scene = act.find(q("div"))
        assert scene.get("type") == "scene"
        assert scene.get("n") == "2"

    def test_role_id_becomes_xml_id(self):
        body, _ = _convert('<div1 type="act" n="cast"><castList>'
                            '<castItem type="role"><role id="lr-11">LEAR</role></castItem>'
                            "</castList></div1>")
        role = body.find(f".//{q('role')}")
        assert role.get("{http://www.w3.org/XML/1998/namespace}id") == "lr-11"
        assert "id" not in role.attrib


class TestEntitiesAndUnknown:
    def test_known_entity_resolved(self):
        p4_doc = (
            '<!DOCTYPE TEI.2 [<!ENTITY AElig "AE">]>'
            '<TEI.2><text><body><div1 type="act" n="1"><head>PERSON&AElig;</head>'
            "</div1></body></text></TEI.2>"
        )
        root = etree.fromstring(p4_doc.encode("utf-8"), P4_PARSER)
        stats = ConversionStats()
        body = convert_body(root, stats)
        head = body.find(f".//{q('head')}")
        assert head.text == "PERSONÆ" or "".join(head.itertext()) == "PERSONÆ"
        assert stats.entities_resolved.get("AElig") == 1

    def test_unhandled_element_raises(self):
        try:
            _convert('<div1 type="act" n="1"><div2 type="scene" n="1">'
                      "<bogus/></div2></div1>")
            assert False, "expected ConversionError"
        except ConversionError:
            pass

    def test_unexpected_attribute_raises(self):
        try:
            _convert('<div1 type="act" n="1" bogus="x"><div2 type="scene" n="1">'
                      "<p>x</p></div2></div1>")
            assert False, "expected ConversionError"
        except ConversionError:
            pass
