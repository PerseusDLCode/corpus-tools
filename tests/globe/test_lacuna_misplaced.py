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
    kinds = ["shared", "turnover", "separate", "numeral", "lacuna", "misplaced", "miscount", "inset"]
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


def test_a_miscount_row_gives_two_printed_lines_one_number():
    """Errors V.1 p.108: eleven lines between 230 and 240, as in the 1864 printing."""
    body = body_of('<l>My wife, her sister, and a rabble more <lb ed="G"/></l>'
                   '<l>Of vile confederates. Along with them <lb ed="G"/></l>'
                   '<l>They brought one Pinch, a hungry lean-faced villain, <lb ed="G"/></l>')
    toks, rows = page(body, ["My wife, her sister, and a rabble more",
                             "Of vile confederates. Along with them",
                             "They brought one Pinch, a hungry lean-faced villain,"])
    new = lineate.globe_lines(rows, 108)
    assert len(new) == 3
    table = [shared_lines.Row("err", "2.1", 108, "miscount", "my wife her", "of vile confederates", "", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 108)
    assert len(new) == 2 and len(new[0].rows) == 2 and applied == [(0, table[0])]


def test_a_separate_row_may_start_at_words_the_witnesses_lost():
    """Love's Labour's Lost III.1 p.142: "silly thought my spleen" heads the
    right column, read "thought my spleen"; the line starts at "silly"."""
    body = body_of('<p>By virtue, thou enforcest laughter; thy silly thought my spleen; <lb ed="G"/></p>')
    toks = tokens.tokenize(body)
    i = {t.t: t.i for t in toks if t.kind == "speech"}
    a = Row(x=0.0, y=0.0, r=0.0, words=[Word(0.0, 0.0, w) for w in "By virtue, thou enforcest laughter; thy".split()],
            band="start")
    b = Row(x=0.0, y=0.0, r=0.0, words=[Word(0.0, 0.0, w) for w in "thought my spleen;".split()], band="turnover")
    a.start, a.speech, a.extra["last"] = i["by"], True, i["thy"]
    b.start, b.speech = i["thought"], True
    new = [lineate.Line([a, b], 142)]
    table = [shared_lines.Row("lll", "2.1", 142, "separate", "by virtue thou", "silly thought my", "", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 142)
    assert [toks[ln.start].t for ln in new] == ["by", "silly"] and applied == [(1, table[0])]


def test_a_separate_row_for_all_splits_every_junction_with_its_words():
    """Love's Labour's Lost V.2 p.160: the refrain 'Cuckoo;' under the same
    line in both stanzas."""
    body = body_of('<l part="I">Mocks married men; for thus sings he, <lb ed="G"/></l><l part="F">Cuckoo; <lb ed="G"/></l>'
                   '<l>Unpleasing to a married ear! <lb ed="G"/></l>'
                   '<l part="I">Mocks married men; for thus sings he, <lb ed="G"/></l><l part="F">Cuckoo; <lb ed="G"/></l>')
    toks, rows = page(body, ["Mocks married men; for thus sings he,", "Cuckoo;", "Unpleasing to a married ear!",
                             "Mocks married men; for thus sings he,", "Cuckoo;"])
    new = [lineate.Line(rows[0:2], 160), lineate.Line([rows[2]], 160), lineate.Line(rows[3:5], 160)]
    one = shared_lines.Row("lll", "2.1", 160, "separate", "mocks married men", "cuckoo", "", "image")
    with pytest.raises(shared_lines.TableError, match="matches 2 junctions"):
        regenerate.apply_table(list(new), None, toks, [one], 160)
    new = [lineate.Line(rows[0:2], 160), lineate.Line([rows[2]], 160), lineate.Line(rows[3:5], 160)]
    every = shared_lines.Row("lll", "2.1", 160, "separate", "mocks married men", "cuckoo", "all", "image")
    new, applied, _ = regenerate.apply_table(new, None, toks, [every], 160)
    assert [len(ln.rows) for ln in new] == [1, 1, 1, 1, 1] and sorted(k for k, _ in applied) == [1, 4]


def test_an_inset_row_makes_every_row_of_its_passage_a_line():
    """A Midsummer Night's Dream I.2 p.163: Bottom's "The raging rocks", set
    in, eight short rows the Globe numbers to 40; the build joins them in
    pairs, as shared halves. Rows outside the passage are left as they are."""
    body = body_of('<p>part to tear a cat in, to make all split. <lb ed="G"/></p>'
                   '<l>The raging rocks <lb ed="G"/></l><l>And shivering shocks <lb ed="G"/></l>'
                   '<l>Shall break the locks <lb ed="G"/></l><l>Of prison gates; <lb ed="G"/></l>'
                   '<p>This was lofty! Now name the rest <lb ed="G"/></p>')
    toks, rows = page(body, ["part to tear a cat in, to make all split.", "The raging rocks",
                             "And shivering shocks", "Shall break the locks", "Of prison gates;",
                             "This was lofty! Now name the rest"])
    new = [lineate.Line(rows[0:3], 163), lineate.Line(rows[3:5], 163), lineate.Line(rows[5:6], 163)]
    table = [shared_lines.Row("mnd", "2.1", 163, "inset", "the raging rocks", "of prison gates", "", "image")]
    new, applied, _ = regenerate.apply_table(new, None, toks, table, 163)
    assert [len(ln.rows) for ln in new] == [1, 1, 1, 1, 1, 1] and applied == [(1, table[0])]
    with pytest.raises(shared_lines.TableError, match="inset .* matches 1 first and 0 last"):
        regenerate.apply_table(new, None, toks, [shared_lines.Row(
            "mnd", "2.1", 163, "inset", "the raging rocks", "no such row", "", "image")], 163)
