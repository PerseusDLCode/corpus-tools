"""The P4 conversion's inline elements: canonical-engLit doc/agenda.org
#build/batch-remaining. Lear and Antony use none of them; the other plays do."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import p4_convert
from globe.p4_convert import XML_LANG, q


def convert(line: str):
    root = etree.fromstring(
        f'<TEI.2><text><body><div1 type="act" n="1"><div2 type="scene" n="1">'
        f'<sp who="a"><speaker>A.</speaker>{line}</sp></div2></div1></body></text></TEI.2>')
    stats = p4_convert.ConversionStats()
    return p4_convert.convert_body(root, stats), stats


def test_gap_is_kept_with_the_dots_after_it():
    """Titus III.1: the Globe's lacuna. The dots are text and stay."""
    body, _ = convert('<l>And bootless unto them<gap/> . . . . <lb ed="G"/></l>')
    gap = body.find(f".//{q('gap')}")
    assert gap is not None and gap.tail == " . . . . "


def test_a_gap_with_content_raises():
    with pytest.raises(p4_convert.ConversionError, match="<gap> unexpectedly has content"):
        convert("<l>word<gap>lost</gap></l>")


def test_foreign_lang_becomes_xml_lang():
    body, _ = convert('<l><foreign lang="la">Et tu, Brute</foreign> ! Then fall</l>')
    f = body.find(f".//{q('foreign')}")
    assert f.get(XML_LANG) == "la" and f.get("lang") is None and f.text == "Et tu, Brute"


def test_q_drops_the_p4_default_direct_and_nothing_else():
    body, stats = convert('<p>Why, <q direct="unspecified">As by lot</q></p>')
    assert body.find(f".//{q('q')}").attrib == {} and stats.q_direct_dropped == 1
    with pytest.raises(p4_convert.ConversionError, match="only the default"):
        convert('<p><q direct="n">x</q></p>')


@pytest.mark.parametrize("tag", ["lg", "text"])
def test_inset_songs_and_letters_still_raise(tag):
    """Undecided: whether the Globe numbers their rows (#build/inset-numbering)."""
    with pytest.raises(p4_convert.ConversionError, match=f"Unhandled element <{tag}>"):
        convert(f"<{tag}><l>x</l></{tag}>")


def test_the_other_plays_entities_resolve(tmp_path):
    """#build/p4-coverage: &lsquo; &rsquo; (ham, 1h4, cor), &oelig; (2h6),
    &agrave; (1h6). The P4s name an external DTD, which is never loaded."""
    p = tmp_path / "p4.xml"
    p.write_text('<!DOCTYPE TEI.2 SYSTEM "tei2.dtd"><TEI.2><text><body><div1 type="act" n="1">'
                 '<div2 type="scene" n="1"><sp who="a"><p>&lsquo;Tis&rsquo; man&oelig;uvre voil&agrave;</p>'
                 '</sp></div2></div1></body></text></TEI.2>')
    body = p4_convert.convert_body(p4_convert.parse_p4(p), p4_convert.ConversionStats())
    assert body.find(f".//{q('p')}").text == "‘Tis’ manœuvre voilà"


def test_an_lb_with_no_ed_is_read_as_a_globe_marker():
    """#build/p4-coverage: Pericles and Troilus mark Globe rows with a bare
    <lb>; a numbered one is a transcribed Globe number, like <lb ed="G" n=...>."""
    body, stats = convert('<p>Ever at the best, hearing well <lb n="30"/>of your lordship. <lb/>Go.</p>')
    ms = body.findall(f".//{q('milestone')}")
    assert [(m.get("ed"), m.get("n"), m.get("source")) for m in ms] == [
        ("Globe", "30", p4_convert.GLOBE_EDITION_SOURCE), ("Globe", None, None)]
    assert stats.lb_no_ed_read_as_globe == 2


def test_an_lb_with_another_attribute_raises():
    with pytest.raises(p4_convert.ConversionError, match="unexpected attributes"):
        convert('<l>x <lb rend="centered"/></l>')
