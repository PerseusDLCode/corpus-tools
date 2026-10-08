"""doc/agenda.org #validate/schmidt-smoke: the checker's rules, on a small
scene, and its result on the real Lear, as recorded in the agenda status."""

from pathlib import Path

import pytest

from globe import schmidt_smoke as sm

REPO = Path(__file__).resolve().parent.parent.parent

TEI = "http://www.tei-c.org/ns/1.0"


def ms(n):
    return f'<milestone unit="line" ed="Globe" n="{n}"/>'


SCENE = f"""<TEI xmlns="{TEI}"><text><body>
  <div type="act" n="1"><div type="scene" n="2">
    <sp><speaker>Edm.</speaker>
      <p>{ms(1)}Why so earnestly seek you to put up that {ms(2)}letter? The
      untented woundings of a father's curse {ms(3)}dissipation of cohorts,
      nuptial breaches, and I know not what.</p></sp>
    <sp><speaker>Glou.</speaker><stage>Reads.</stage>
      <l>{ms(4)}Dower'd with our curse, and stranger'd with our oath,</l>
      <l>{ms(5)}Keep in-a-door, and ye shall have more</l>
      <l>{ms(6)}Wherefore should I stand,--in the plague of custom,</l>
      <l>{ms(7)}And permit the curiosity of nations to deprive me?</l></sp>
    <sp><speaker>Lear.</speaker>
      <p>{ms(8)}Is there any cause in nature that makes these hard hearts? <stage>[To
      {ms(9)}Edgar]</stage> You, sir, I entertain for one of my hundred;</p></sp>
  </div></div>
</body></text></TEI>"""


@pytest.fixture
def scenes(tmp_path):
    p = tmp_path / "lr.xml"
    p.write_text(SCENE)
    return sm.read_edition(p)


def verdict(scenes, ref, headword, quote="", display="Lr. I, 2, 1"):
    cit = {"p5_ref_target": f"urn:cts:engLit:shakespeare.lr:{ref}", "p4_display_text": display}
    q = {"key": "K", "headword": headword, "has_quote": "true" if quote else "false",
         "quote_expanded": quote}
    return sm.check(cit, q, scenes)


def test_speakers_and_stage_directions_are_not_text(scenes):
    assert "edm" not in scenes["1.2"].words and "reads" not in scenes["1.2"].words
    assert scenes["1.2"].lines[3][0] == "dissipation"


def test_a_line_beginning_inside_a_stage_direction(scenes):
    """III.6.83: the row begins at "gar]" of "[To Ed- | gar]", so the
    milestone is inside the <stage>; its words are still line 9's."""
    assert scenes["1.2"].lines[9][:3] == ["you", "sir", "i"]
    assert verdict(scenes, "1.2.9", "Hundred,", "I entertain you for one of my hundred")["verdict"] == \
        "quotation on cited line, with differences"


def test_quotation_on_the_cited_line(scenes):
    assert verdict(scenes, "1.2.1", "Earnestly,", "why so earnestly seek you")["verdict"] == \
        "quotation on cited line"


def test_a_quotation_running_onto_the_next_line_passes_on_either(scenes):
    q = "seek you to put up that letter?"
    assert verdict(scenes, "1.2.2", "Letter,", q)["verdict"] == "quotation on cited line"


def test_ellipsis_splits_the_quotation(scenes):
    q = "wherefore should I . . . permit the curiosity of nations"
    assert verdict(scenes, "1.2.7", "Curiosity,", q)["verdict"] == "quotation on cited line"


def test_a_dash_separates_words(scenes):
    """'stand,--in' is two words, as the P4 prints many a broken speech."""
    assert verdict(scenes, "1.2.6", "Plague,", "stand in the plague of custom")["verdict"] == \
        "quotation on cited line"


def test_elided_and_full_spellings_are_one(scenes):
    q = "dowered with our curse, and strangered with our oath,"
    assert verdict(scenes, "1.2.4", "Dower,", q)["verdict"] == "quotation on cited line"


def test_a_different_word_division_is_a_difference_not_a_failure(scenes):
    r = verdict(scenes, "1.2.5", "Adoor;", "keep in adoor,")
    assert r["verdict"] == "quotation on cited line, with differences" and r["match"] == "spacing"


def test_a_single_letter_abbreviation_is_the_headword(scenes):
    assert verdict(scenes, "1.2.3", "Dissipation,", "d. of cohorts,")["verdict"] == \
        "quotation on cited line"


def test_headword_inflected_and_compound(scenes):
    assert verdict(scenes, "1.2.2", "Untented,")["verdict"] == "headword on cited line"
    assert verdict(scenes, "1.2.2", "Wounding,")["verdict"] == "headword on cited line"
    assert verdict(scenes, "1.2.4", "Stranger,")["verdict"] == "headword on cited line"


def test_a_prose_word_at_the_edge_of_the_next_line_is_a_row_break(scenes):
    """Schmidt's printing ended line 2 one word later: 'dissipation' is the
    first word of our line 3."""
    assert verdict(scenes, "1.2.2", "Dissipation,")["verdict"] == "prose row break"


def test_a_verse_word_one_line_off_is_reported(scenes):
    r = verdict(scenes, "1.2.6", "Curiosity,")
    assert r["verdict"] == "headword off by 1" and r["found_at"] == "1.2.7"


def test_another_play_or_scene_is_not_a_citation_of_this_play(scenes):
    assert verdict(scenes, "4.1.94", "Doubtful,", display="Shr. Ind. 1, 94.")["verdict"] == sm.NOT_THIS_PLAY
    assert verdict(scenes, "5.154.2", "Brand,", display="154, 2")["verdict"] == sm.NOT_THIS_PLAY


def test_the_plays_own_abbreviation_is_read_from_its_citations():
    cits = [{"p4_display_text": d} for d in ("Lr. I, 4, 138", "Lr. II, 4, 161", "IV, 2, 3", "Shr. Ind. 1, 94.")]
    assert sm.own_abbreviation(cits) == "Lr."
    assert sm.own_abbreviation([{"p4_display_text": "H6A I, 1, 98"}]) is None


def test_a_run_of_citations_off_by_one_amount_is_reported():
    """Antony II.7: Schmidt's citations ran five ahead of ours from 69 to 118."""
    def row(cited, verdict, offset=""):
        return {"cited": cited, "verdict": verdict, "offset": offset}
    rows = [row("2.7.60", "quotation on cited line"),
            row("2.7.69", "quotation elsewhere in scene", 5), row("2.7.72", "headword off by 1", 1),
            row("2.7.74", "quotation elsewhere in scene", 5), row("2.7.78", "quotation elsewhere in scene", 5),
            row("2.7.82", "quotation elsewhere in scene", 5), row("2.7.88", "quotation on cited line"),
            row("2.7.90", "prose row break", 1), row("3.1.4", "not a citation of this play")]
    assert sm.runs(rows) == [dict(scene="2.7", first=74, last=82, offset=5, citations=3)]


def test_nothing_on_or_near_the_line(scenes):
    assert verdict(scenes, "1.2.1", "Acheron,")["verdict"] == "headword not found near cited line"


INPUTS = [sm.edition_for("lr"), sm.SCHMIDT / "citations.tsv", sm.SCHMIDT / "citation_quotes.tsv"]


@pytest.mark.skipif(not all(p.is_file() for p in INPUTS), reason="Schmidt tables or Lear build not on disk")
def test_real_lear_as_recorded():
    """The figures in the agenda status of #validate/schmidt-smoke."""
    from collections import Counter
    rows, _ = sm.run("lr")
    counts = Counter(r["verdict"] for r in rows)
    assert len(rows) == 2286
    assert sum(counts[v] for v in sm.PASS) == 2163
    assert counts[sm.NOT_THIS_PLAY] == 30
    assert counts["prose row break"] == 14
