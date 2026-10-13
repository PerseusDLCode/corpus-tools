"""shared-lines.tsv kinds `lacuna` and `misplaced`, from Richard II
(canonical-engLit doc/agenda.org #build/batch-remaining)."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import emit_tei, lineate, p4_convert, regenerate, shared_lines, tei_header, tokens
from globe.p4_convert import q
from globe.page_rows import Row, Word


def body_of(lines_xml: str):
    root = etree.fromstring(
        f'<TEI.2><text><body><div1 type="act" n="2"><div2 type="scene" n="1"><sp who="a">'
        f'<speaker>North.</speaker>{lines_xml}</sp></div2></div1></body></text></TEI.2>')
    return p4_convert.convert_body(root, p4_convert.ConversionStats())


def test_a_line_of_dots_alone_is_an_ellipsis():
    body = body_of('<l>................... <lb ed="G"/></l>')
    l = body.find(f".//{q('l')}")
    assert l.text is None and l[0].tag == q("ellipsis")
    assert l[0][0].get("function") == "ellipsis" and l[0][0].text == "................... "


def page(body, texts_and_rows):
    """Rows for the page, each aligned to the first token of its words."""
    toks = tokens.tokenize(body)
    rows, at = [], next(t.i for t in toks if t.kind == "speech")  # after the speaker
    for text in texts_and_rows:
        r = Row(x=0.0, y=0.0, r=0.0, words=[Word(0.0, 0.0, w) for w in text.split()], band="start")
        if any(tokens.norm(w) for w in text.split()):
            r.start, r.speech = at, True
            at += sum(1 for w in text.split() if tokens.norm(w))
        rows.append(r)
    return toks, rows


def test_a_lacuna_row_inserts_the_wordless_line_and_numbers_it():
    body = body_of('<l>That Harry Duke of Hereford, <lb ed="G" n="280"/></l>'
                   '<l>................... <lb ed="G"/></l>'
                   '<l>That late broke from the Duke of Exeter, <lb ed="G"/></l>')
    toks, rows = page(body, ["That Harry Duke of Hereford,", ". .", "That late broke from the Duke of Exeter,"])
    rows[1].num = 280
    new = lineate.globe_lines(rows, 364)
    assert len(new) == 2
    table = [shared_lines.Row("r2", "2.1", 364, "lacuna", "that harry duke", "", "", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 364, page_rows_=rows)
    assert [ln.num for ln in new] == [None, 280, None]
    assert new[1].lacuna_at == new[2].start and applied == [(1, table[0])]
    assert emit_tei.wordless_l_before(toks, new[1].start) is not None


def test_a_lacuna_row_refuses_when_the_p4_has_no_wordless_line():
    body = body_of('<l>That Harry Duke of Hereford, <lb ed="G"/></l>'
                   '<l>That late broke from the Duke of Exeter, <lb ed="G"/></l>')
    toks, rows = page(body, ["That Harry Duke of Hereford,", ". .", "That late broke from the Duke of Exeter,"])
    table = [shared_lines.Row("r2", "2.1", 364, "lacuna", "that harry duke", "", "", "image")]
    with pytest.raises(shared_lines.TableError, match="no wordless"):
        regenerate.apply_table(lineate.globe_lines(rows, 364), None, toks, table, 364, page_rows_=rows)


def test_a_misplaced_numeral_moves_to_the_line_it_numbers():
    body = body_of('<l>Your grace mistakes; only to be brief, <lb ed="G"/></l>'
                   '<l>Left I his title out. <lb ed="G"/></l>')
    toks, rows = page(body, ["Your grace mistakes; only to be brief,", "Left I his title out."])
    rows[1].num = 10
    new = lineate.globe_lines(rows, 370)
    table = [shared_lines.Row("r2", "3.3", 370, "misplaced", "10", "left i his", "your grace mistakes", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 370)
    assert [ln.num for ln in new] == [10, None] and applied == [(0, table[0])]


def test_neither_kind_counts_as_a_junction_in_the_header():
    kinds = ["shared", "turnover", "separate", "numeral", "lacuna", "misplaced"]
    table = [shared_lines.Row("r2", "1.1", 356, k, "a", "b", "", "image") for k in kinds]
    assert tei_header.count_junctions(table) == 3



def test_a_numeral_row_with_no_printed_value_removes_the_reading():
    """Measure V.1 p.92: "even now, I" -- the "I" both witnesses read as a 1."""
    body = body_of('<l>me to a whore. Your highness said even now, I <lb ed="G"/></l>'
                   '<l>made you a duke <lb ed="G"/></l>')
    toks, rows = page(body, ["me to a whore. Your highness said even now,", "made you a duke"])
    rows[0].num = 1
    new = lineate.globe_lines(rows, 92)
    table = [shared_lines.Row("mm", "5.1", 92, "numeral", "", "1", "me to a whore", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 92)
    assert [ln.num for ln in new] == [None, None] and applied == [(0, table[0])]
