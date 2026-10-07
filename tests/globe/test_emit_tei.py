"""doc/agenda.org #build/regenerate-lear: the placement conventions.

Each test builds a small TEI body, says which tokens begin Globe lines and
which begin other printed rows, and checks where the markers land. The
conventions are doc/forum.org #lineation/regenerate-from-witnesses,
"Conventions applied".
"""


import pytest
from lxml import etree

from globe import emit_tei
from globe import lineate
from globe import tokens
from globe.page_rows import Row, Word


TEI = "http://www.tei-c.org/ns/1.0"


def body(inner: str):
    return etree.fromstring(f'<body xmlns="{TEI}">{inner}</body>')


def row(start, num=None):
    r = Row(x=0, y=0, r=0, words=[Word(0, 1, "x")])
    r.start, r.speech, r.num = start, True, num
    return r


def emit(el, lines, extra_rows=()):
    """Mark up `el` and return it serialised."""
    toks = tokens.tokenize(el)
    marks = emit_tei.build_marks(lines, [r for ln in lines for r in ln.rows] + list(extra_rows))
    emit_tei.apply_marks(toks, marks)
    return etree.tostring(el, encoding="unicode")


def line(rows, n, page=860, num=None, div="1.1"):
    ln = lineate.Line(rows, page, div, n, num)
    return ln


def test_speech_initial_milestone_is_the_first_child_of_its_container():
    el = body('<sp><speaker>Kent.</speaker><p>I thought the king had more affected</p></sp>')
    out = emit(el, [line([row(0)], 1)])
    assert '<speaker>Kent.</speaker><p><milestone unit="line" ed="Globe" n="1"/>I thought' in out


def test_milestone_precedes_a_stage_direction_that_opens_its_line():
    el = body('<sp><speaker>Lear.</speaker><l><stage>[Rising]</stage> Never, Regan:</l></sp>')
    out = emit(el, [line([row(0)], 160)])
    assert '<l><milestone unit="line" ed="Globe" n="160"/><stage>[Rising]</stage>' in out


def test_milestone_lands_inside_the_line_when_words_come_first():
    el = body('<l>Mend when thou canst; <stage>[aside]</stage> be better</l>')
    out = emit(el, [line([row(0)], 5), line([row(4)], 6)])
    assert 'canst; <milestone unit="line" ed="Globe" n="6"/><stage>' in out


def test_shared_line_gets_one_milestone_and_the_second_half_an_lb():
    el = body('<sp><speaker>Corn.</speaker><l part="I">Is he pursued?</l></sp>'
              '<sp><speaker>Glou.</speaker><l part="F">Ay, my good lord.</l></sp>')
    out = emit(el, [line([row(0), row(4)], 111)])  # tokens: Corn. Is he pursued? Glou. Ay ...
    assert out.count("milestone") == 1
    assert '<l part="I"><milestone unit="line" ed="Globe" n="111"/>Is he pursued?' in out
    assert '<l part="F"><lb/>Ay, my good lord.' in out


def test_lb_precedes_a_stage_direction_row():
    el = body('<l>Come.</l><stage type="exit">[Exeunt Lear and Cordelia, guarded.</stage>'
              '<l>Come hither, captain</l>')
    stage_row = row(1)
    stage_row.speech = False
    out = emit(el, [line([row(0)], 26), line([row(6)], 27)], extra_rows=[stage_row])
    assert '<lb/><stage type="exit">' in out


def test_hyphenated_word_takes_the_milestone_before_the_whole_word():
    # the P4 has the word whole ("preparation"), and page_rows joins the two
    # printed halves into one token, so the milestone cannot land inside it
    el = body('<p>to a most festinate preparation: we are bound</p>')
    toks = tokens.tokenize(el)
    assert toks[4].raw == "preparation:"
    out = emit(el, [line([row(0)], 10), line([row(4)], 11)])
    assert 'festinate <milestone unit="line" ed="Globe" n="11"/>preparation:' in out


def test_a_transcribed_number_carries_no_source_or_type():
    el = body('<l>One</l><l>Two</l>')
    out = emit(el, [line([row(0)], 10, num=10), line([row(1)], 11)])
    assert '<milestone unit="line" ed="Globe" n="10"/>' in out
    assert '<milestone unit="line" ed="Globe" n="11"/>' in out
    assert "source" not in out and "type" not in out


def test_the_count_resets_at_each_scene():
    el = body('<div type="act" n="1"><div type="scene" n="1"><l>A</l></div>'
              '<div type="scene" n="2"><l>B</l></div></div>')
    out = emit(el, [line([row(0)], 1, div="1.1"), line([row(1)], 1, div="1.2")])
    assert out.count('n="1"/>A') == 1 and out.count('n="1"/>B') == 1


# ---------------------------------------------------------------- review build


def test_review_comments_strip_back_to_the_canonical_text():
    el = body('<l>One</l><l>Two</l>')
    toks = tokens.tokenize(el)
    lines = [line([row(0)], 1), line([row(1)], 2)]
    emit_tei.apply_marks(toks, emit_tei.build_marks(lines, [r for ln in lines for r in ln.rows]))
    canonical = etree.tostring(el.getroottree(), xml_declaration=True, encoding="UTF-8")
    emit_tei.apply_marks(toks, emit_tei.review_marks([(1, emit_tei.review_comment("page", "p.860"))]))
    with_review = etree.tostring(el.getroottree(), xml_declaration=True, encoding="UTF-8")
    assert b"REVIEW page: p.860" in with_review
    assert emit_tei.strip_reviews(with_review) == canonical


def test_a_review_comment_never_contains_a_double_hyphen():
    text = emit_tei.review_comment("words", "page reads 'a--b'; P4 reads 'c--d'")
    assert "--" not in text
    etree.Comment(f" REVIEW {text} ")  # would raise if it were illegal


def test_stamp_records_provenance_in_the_revision_description():
    root = etree.fromstring(f'<TEI xmlns="{TEI}"><teiHeader><revisionDesc>'
                            f'<change><ab>converted to TEI P5</ab></change>'
                            f'</revisionDesc></teiHeader></TEI>')
    emit_tei.stamp(root, "regenerate.py", "0.1.0", "abc1234", "2026-09-25", {"lr.xml": "deadbeef"})
    text = root.findtext(f".//{{{TEI}}}change/{{{TEI}}}ab")
    assert "abc1234" in text and "deadbeef" in text and "DO NOT EDIT" in text
    change = root.find(f".//{{{TEI}}}revisionDesc/{{{TEI}}}change")
    assert change.get("when") == "2026-09-25"


def test_a_rebuild_replaces_the_previous_stamp():
    """The published edition is the next build's shell (#publish/lear): its
    stamp is replaced, not added to; the 2025 conversion's entry stays."""
    root = etree.fromstring(f'<TEI xmlns="{TEI}"><teiHeader><revisionDesc>'
                            f'<change><ab>converted to TEI P5</ab></change>'
                            f'</revisionDesc></teiHeader></TEI>')
    emit_tei.stamp(root, "regenerate.py", "0.1.0", "abc1234", "2026-09-25", {"lr.xml": "deadbeef"})
    emit_tei.stamp(root, "regenerate.py", "0.1.0", "def5678", "2026-09-29", {"lr.xml": "deadbeef"})
    texts = [c.findtext(f"{{{TEI}}}ab") for c in root.iter(f"{{{TEI}}}change")]
    assert len(texts) == 2 and "def5678" in texts[0] and texts[1] == "converted to TEI P5"
