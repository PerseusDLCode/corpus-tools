"""shared-lines.tsv kind `dropped`: a row the page prints that both witnesses'
OCR lost, its words run on in the line above (The Winter's Tale IV.2, p.317,
"sidered, as too much I cannot, to be more thank-")."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import lineate, p4_convert, regenerate, shared_lines, tokens
from globe.page_rows import Row, Word

P4 = ('<TEI.2><text><body><div1 type="act" n="4"><div2 type="scene" n="2">'
      '<sp who="pol."><speaker>Pol.</speaker><p>thou hast done; which if I have not enough '
      'considered, as too much I cannot, to be more thankful to thee shall be my study, '
      'and my profit therein the heaping friendships. </p></sp></div2></div1></body></text></TEI.2>')


def build():
    """The rows Kraken read: the second of the page's three is lost, and
    'con-' / 'ful' are joined."""
    body = p4_convert.convert_body(etree.fromstring(P4), p4_convert.ConversionStats())
    toks = tokens.tokenize(body)
    speech = [t for t in toks if t.kind == "speech"]
    rows = []
    for text, first in (("thou hast done; which if I have not enough", "thou"),
                        ("thankful to thee shall be my study, and my profit", "thankful")):
        r = Row(x=0.0, y=0.0, r=0.0, words=[Word(0.0, 0.0, w) for w in text.split()], band="start")
        r.start, r.speech = next(t.i for t in speech if t.t == first), True
        r.extra["cont"] = toks[r.start].cont
        rows.append(r)
    return toks, rows


def test_a_dropped_row_starts_a_line_where_the_lost_row_begins():
    toks, rows = build()
    new = lineate.globe_lines(rows, 317)
    assert len(new) == 2
    table = [shared_lines.Row("wt", "4.2", 317, "dropped", "thou hast done", "considered as too", "",
                              "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 317, page_rows_=rows)
    assert len(new) == 3 and new[0].rows == [rows[0]] and new[2].rows == [rows[1]]
    assert toks[new[1].start].t == "considered" and new[1].rows[0].words == []
    assert applied == [(1, table[0])]


def test_a_dropped_row_refuses_words_not_in_the_line():
    toks, rows = build()
    table = [shared_lines.Row("wt", "4.2", 317, "dropped", "thou hast done", "precious queen", "",
                              "image")]
    with pytest.raises(shared_lines.TableError, match="dropped"):
        regenerate.apply_table(lineate.globe_lines(rows, 317), None, toks, table, 317, page_rows_=rows)
