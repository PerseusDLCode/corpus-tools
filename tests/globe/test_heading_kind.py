"""shared-lines.tsv kind `heading`: the title of a song the Globe numbers as a
line, Cymbeline II.3 "SONG." (not the dirge's in IV.2, which it does not)."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import emit_tei, lineate, p4_convert, regenerate, shared_lines, tokens
from globe.page_rows import Row, Word

P4 = ('<TEI.2><text><body><div1 type="act" n="2"><div2 type="scene" n="3">'
      '<sp who="clo."><speaker>Clo.</speaker><p>And then let her consider. </p>'
      '<lg type="song"><head>SONG.</head><l>Hark, hark! the lark at heaven\'s gate sings, </l>'
      '<l>And Phoebus \'gins arise, </l></lg></sp></div2></div1></body></text></TEI.2>')


def rows_for(toks):
    out = []
    for text in ("And then let her consider.", "SONG.", "Hark, hark! the lark at heaven's gate sings,",
                 "And Phoebus 'gins arise,"):
        words = [w for w in text.split() if tokens.norm(w)]
        out.append((text, len(words)))
    rows, at = [], next(t.i for t in toks if t.kind == "speech")
    for text, n in out:
        r = Row(x=0.0, y=0.0, r=0.0, words=[Word(0.0, 0.0, w) for w in text.split()], band="start")
        r.start, r.speech = at, text != "SONG."
        r.extra["cont"] = toks[at].cont
        at += n
        rows.append(r)
    return rows


def build():
    body = p4_convert.convert_body(etree.fromstring(P4), p4_convert.ConversionStats())
    toks = tokens.tokenize(body)
    return body, toks, rows_for(toks)


def test_a_title_is_no_line_without_a_row_for_it():
    _, toks, rows = build()
    assert toks[rows[1].start].kind == "head"
    assert len(lineate.globe_lines(rows, 952)) == 3


def test_a_heading_row_adds_the_title_as_a_line():
    _, toks, rows = build()
    new = lineate.globe_lines(rows, 952)
    table = [shared_lines.Row("cym", "2.3", 952, "heading", "and then let her", "song", "", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 952, page_rows_=rows)
    assert len(new) == 4 and new[1].rows == [rows[1]]
    assert applied == [(1, table[0])]


def test_a_heading_row_refuses_a_title_that_is_not_there():
    _, toks, rows = build()
    table = [shared_lines.Row("cym", "2.3", 952, "heading", "and then let her", "dirge", "", "image")]
    with pytest.raises(shared_lines.TableError, match="head rows"):
        regenerate.apply_table(lineate.globe_lines(rows, 952), None, toks, table, 952, page_rows_=rows)


def test_the_milestone_of_a_title_line_stays_inside_the_head():
    body, toks, rows = build()
    head = next(t for t in toks if t.kind == "head")
    el = etree.Element("milestone")
    emit_tei.insert_before(el, head, stay=("head",))
    assert el.getparent().tag.endswith("head")
