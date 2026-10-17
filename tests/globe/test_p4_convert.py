"""The P4 conversion's inline elements: canonical-engLit doc/agenda.org
#build/batch-remaining. Lear and Antony use none of them; the other plays do."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import p4_convert
from globe.p4_convert import XML_ID, XML_LANG, q


def convert(line: str):
    root = etree.fromstring(
        f'<TEI.2><text><body><div1 type="act" n="1"><div2 type="scene" n="1">'
        f'<sp who="a"><speaker>A.</speaker>{line}</sp></div2></div1></body></text></TEI.2>')
    stats = p4_convert.ConversionStats()
    return p4_convert.convert_body(root, stats), stats


def test_the_globe_lacuna_is_an_ellipsis_holding_its_dots():
    """Titus III.1.36: the source marks the omission itself, so <ellipsis>,
    not <gap>; the dots are its <metamark>, and what follows them its tail."""
    body, _ = convert('<l>And bootless unto them<gap/> . . . . <lb ed="G"/></l>')
    assert body.find(f".//{q('gap')}") is None
    e = body.find(f".//{q('ellipsis')}")
    m = e.find(q("metamark"))
    assert (m.get("function"), m.text) == ("ellipsis", " . . . . ")
    assert not (e.tail or "").strip()


def test_a_gap_with_content_or_without_dots_raises():
    with pytest.raises(p4_convert.ConversionError, match="unexpectedly has"):
        convert("<l>word<gap>lost</gap> . .</l>")
    with pytest.raises(p4_convert.ConversionError, match="not followed by the Globe's dots"):
        convert("<l>word<gap/> more words</l>")


def test_foreign_lang_becomes_xml_lang():
    body, _ = convert('<l><foreign lang="la">Et tu, Brute</foreign> ! Then fall</l>')
    f = body.find(f".//{q('foreign')}")
    assert f.get(XML_LANG) == "la" and f.get("lang") is None and f.text == "Et tu, Brute"


def test_q_drops_the_p4_default_direct_and_nothing_else():
    body, stats = convert('<p>Why, <q direct="unspecified">As by lot</q></p>')
    assert body.find(f".//{q('q')}").attrib == {} and stats.q_direct_dropped == 1
    with pytest.raises(p4_convert.ConversionError, match="only the default"):
        convert('<p><q direct="n">x</q></p>')


def test_a_song_keeps_its_lg_and_a_split_one_its_links():
    """#build/inset-numbering: Twelfth Night's catch and Hamlet's songs are one
    <lg> in several parts; P4's @id/@next/@part are xml:id, a pointer, I/M/F."""
    body, _ = convert('<lg id="s1" next="s2" part="I" type="song"><l>a</l></lg>'
                      '<lg id="s2" next="s3" part="Y" type="song"><l>b</l></lg>'
                      '<lg id="s3" part="F" type="song"><l>c</l></lg>')
    lgs = body.findall(f".//{q('lg')}")
    assert [(g.get(XML_ID), g.get("next"), g.get("part"), g.get("type")) for g in lgs] == [
        ("s1", "#s2", "I", "song"), ("s2", "#s3", "M", "song"), ("s3", None, "F", "song")]
    with pytest.raises(p4_convert.ConversionError, match="unexpected attributes"):
        convert('<lg rend="x"><l>a</l></lg>')
    with pytest.raises(p4_convert.ConversionError, match="only I, Y and F"):
        convert('<lg part="N"><l>a</l></lg>')


def test_an_inset_text_is_a_floating_text():
    """A masque, a letter or a song set in a speech is a <text> in the P4; P5's
    <floatingText> holds a <body> of its own."""
    body, _ = convert('<l>Now, music.</l><text><body><head>SONG.</head>'
                      '<lg type="song"><l>Pardon, goddess</l></lg></body></text>')
    ft = body.find(f".//{q('floatingText')}")
    assert ft is not None and ft.find(f"{q('body')}/{q('head')}").text == "SONG."
    assert ft.find(f".//{q('lg')}").get("type") == "song"


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


def test_a_p_n_is_recovered_as_the_globe_anchor_opening_the_speech():
    """#build/p4-coverage: R2 II.3 '<p n="40">Then learn to know him now'."""
    body, stats = convert('<p n="40">Then learn to know him now; <lb ed="G"/>this is the duke.</p>')
    p = body.find(f".//{q('p')}")
    first = p[0]
    assert p.get("n") is None and p.text is None
    assert (first.get("ed"), first.get("n"), first.get("source")) == ("Globe", "40", p4_convert.GLOBE_EDITION_SOURCE)
    assert first.tail == "Then learn to know him now; "
    assert [n for _, n, _ in stats.p_n_recovered] == ["40"]
