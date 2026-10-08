"""doc/agenda.org #build/regenerate-lear: the row rules, each on a synthetic case.

Every case here is a situation found on a real Lear page; the comment names
where. Coordinates are in pitches (u) from the column margin, with a column
measure of 22u, which is about Michigan's.
"""


import pytest
from lxml import etree

from globe import lineate
from globe import page_rows as pr
from globe import source_text
from globe import tokens
from globe.page_rows import Row, Word


U = 50.0  # pixels per pitch
MEASURE = 22.0
SPEAKERS = {"lear", "kent", "alb", "glou", "oldman", "thirdserv", "gon", "edm"}


def row(x_u, text, *, right_u=None, gap_after_prefix_u=None, y=0.0, band=None):
    """A row starting x_u pitches from the margin; words laid out left to right."""
    words, x = [], x_u * U
    for i, t in enumerate(text.split()):
        w = len(t) * 0.35 * U
        words.append(Word(x, w, t))
        x += w + (gap_after_prefix_u * U if (i == 0 and gap_after_prefix_u) else 0.3 * U)
    r = Row(x=x_u * U, y=y, r=(right_u * U) if right_u is not None else words[-1].x + words[-1].w,
            words=words)
    r.pitch, r.margin, r.measure = U, 0.0, MEASURE * U
    r.prefix_len = pr.prefix_length(r, SPEAKERS)
    gap = pr.prefix_gap(r)
    r.offset_u = x_u
    r.band = band or pr.classify_band(x_u, None if gap is None else gap / U)
    return r


# ---------------------------------------------------------------- bands


@pytest.mark.parametrize("off,band", [
    (0.0, "start"), (1.0, "start"), (1.44, "start"),  # body and speech openings
    (1.88, "turnover"), (2.4, "turnover"), (2.65, "turnover"),  # "followers?" p.861 at 1.88
    (3.1, "indented"), (4.1, "indented"),  # songs, p.853
    (5.4, "displaced"), (14.0, "displaced"),
])
def test_bands(off, band):
    assert pr.classify_band(off) == band


def test_prefix_gap_makes_a_start_row_displaced():
    # "Corn.      Get horses for your mistress." p.866: prefix, then a wide gap
    assert row(0.9, "Corn. Get horses for your mistress.", gap_after_prefix_u=6).band == "displaced"
    assert row(0.9, "Corn. Get horses for your mistress.").band == "start"


@pytest.mark.parametrize("text,n", [
    ("Glou. Where is he?", 1),
    ("Lear Out of my sight!", 1),  # period lost to OCR, p.848
    ("Aló. Shut your mouth, dame,", 1),  # "Alb." misread, p.877
    ("A1b. Speak, man.", 1),
    ("Old Man. How now! Who's there?", 2),  # two-word name, p.867
    ("Third Sery. If she live long,", 2),  # "Serv." misread, p.867
    ("Come hither, captain; hark.", 0),
])
def test_prefix_length(text, n):
    assert row(0.9, text).prefix_len == n


# ---------------------------------------------------------------- continuation


def test_turnover_after_a_full_row_continues():
    # "Reg. I pray you, sir, take patience: I have / hope" p.860: above is 0.93u short
    prev = row(1.0, "Reg. I pray you, sir, take patience: I have", right_u=MEASURE - 0.93)
    assert lineate.continues(prev, row(2.3, "hope"))


def test_turnover_band_row_after_a_short_row_is_a_line():
    # "The hedge-sparrow fed the cuckoo so long, / That it's had..." p.853: 1.07u short
    prev = row(2.1, "The hedge-sparrow fed the cuckoo so long,", right_u=MEASURE - 1.07)
    assert not lineate.continues(prev, row(2.12, "That it's had it head bit off by it young."))


def test_indented_row_is_a_line_even_after_a_full_row():
    # "His word was still,--Fie, foh, and fum," p.865: the row above is full
    prev = row(3.2, "Child Rowland to the dark tower came,", right_u=MEASURE)
    assert not lineate.continues(prev, row(3.49, "His word was still,--Fie, foh, and fum,"))


def test_shared_half_following_the_first_half_continues():
    # "Corn. Is he pursued? / Glou. Ay, my good lord." p.856
    prev = row(1.0, "Corn. Is he pursued?", right_u=10.8)
    r = row(1.0, "Glou. Ay, my good lord.", gap_after_prefix_u=10)
    assert r.band == "displaced"
    assert lineate.continues(prev, r)


def test_shared_half_pushed_against_the_measure_continues():
    # "Lear. You must bear with me:" p.874: starts 8.4u left of the first half's end
    prev = row(0.0, "Will't please your highness walk?", right_u=19.2)
    r = row(5.0, "You must bear with me:", right_u=MEASURE)
    assert lineate.continues(prev, r)


def test_displaced_song_line_is_a_line():
    # "Fool. That lord that counsell'd thee / To give away thy land," p.853
    prev = row(1.0, "Fool. That lord that counsell'd thee", right_u=17.3)
    assert not lineate.continues(prev, row(5.4, "To give away thy land,", right_u=15.5))


def test_displaced_row_in_the_same_paragraph_is_prose():
    # Goneril's letter, p.873: "'Affectionate servant," set in, inside one <p>,
    # in a text that marks its verse with <l>
    body = etree.fromstring("<body><sp><l>verse</l></sp><sp><p/></sp></body>")
    p = body.find("sp/p")
    prev = row(2.8, "'Your--wife, so I would say--", right_u=15.5)
    r = row(8.9, "'Affectionate servant,", right_u=18.1)
    prev.extra["cont"] = r.extra["cont"] = p
    assert not lineate.continues(prev, r)
    r.extra["cont"] = etree.Element("l")  # the same geometry in verse would be a shared half
    assert lineate.continues(prev, r)


def test_a_paragraph_says_nothing_where_the_p4_marks_no_verse():
    # Antony I.1, p.911: "To cool a gipsy's lust." / [stage direction] /
    # "Look, where they come:", set to follow on, one Globe line (10). The
    # P4 has no <l> at all: the speech is one <p>, verse and all.
    body = etree.fromstring("<body><sp><p/></sp></body>")
    p = body.find("sp/p")
    prev = row(0.0, "To cool a gipsy's lust.", right_u=9.9)
    r = row(9.6, "Look, where they come:", right_u=20.9)
    prev.extra["cont"] = r.extra["cont"] = p
    assert lineate.continues(prev, r)


def test_shared_half_at_a_column_top_is_measured_from_each_margin():
    # "Coming from us." foot of p.858 col 2 / "Kent. My lord, when at their home" top of p.859
    prev = row(0.0, "Coming from us.", right_u=7.0)
    prev.margin = 1400.0  # column 2
    prev.x += 1400.0
    prev.r += 1400.0
    r = row(1.3, "Kent. My lord, when at their home", gap_after_prefix_u=6)
    assert lineate.continues(prev, r)


# ---------------------------------------------------------------- page preparation


def test_hyphenated_word_moves_whole_to_the_next_row():
    a, b = Row(0, 0, 0, [Word(0, 10, "most"), Word(20, 10, "festinate"), Word(40, 10, "prepara¬")]), \
        Row(0, 50, 0, [Word(0, 10, "tion:"), Word(20, 10, "we")])
    pr.join_hyphenation([a, b])
    assert [w.t for w in a.words] == ["most", "festinate"]
    assert b.words[0].t == "preparation:"


def test_dash_read_as_hyphen_before_a_speech_is_not_joined():
    # "We'll teach you—" read "you¬", then "Kent. Sir, I am too old to learn:" p.858
    a, b = Row(0, 0, 0, [Word(0, 10, "We'll"), Word(20, 10, "teach"), Word(40, 10, "you¬")]), \
        Row(0, 50, 0, [Word(0, 10, "Kent."), Word(20, 10, "Sir,")])
    pr.join_hyphenation([a, b])
    assert a.words[-1].t == "you¬" and b.words[0].t == "Kent."


def test_fragments_at_one_height_are_one_row():
    # "Her. Again!" and "[Third trumpet." segmented apart, out of order, p.876
    rows = [Row(700, 100, 900, [Word(700, 200, "[Third"), Word(910, 90, "trumpet.")]),
            Row(40, 102, 300, [Word(40, 100, "Her."), Word(160, 140, "Again!")])]
    merged = pr.merge_same_row(rows, 50)
    assert len(merged) == 1
    assert [w.t for w in merged[0].words] == ["Her.", "Again!", "[Third", "trumpet."]
    assert merged[0].x == 40


def test_a_row_across_the_gutter_is_split():
    # p.866: one baseline ran "...but let them" (col 1) into "tion: we are bound..." (col 2)
    left = [Row(0, y, 1100, [Word(0, 1100, "x")]) for y in range(0, 1000, 50)]
    right = [Row(1300, y, 2400, [Word(1300, 1100, "y")]) for y in range(0, 1000, 50)]
    both = Row(0, 5, 2400, [Word(0, 400, "let"), Word(500, 500, "them"), Word(1300, 300, "tion:")])
    cols = pr.split_columns(left + right + [both])
    assert any(r.words[0].t == "tion:" for r in cols[1])
    assert not any("tion:" in r.text for r in cols[0])


def test_numeral_outside_the_frame_is_an_annotation():
    # miun p.861: a reader's "7" (read "1") 2.0u beyond the measure; print sits inside
    printed, notes = pr.split_annotations([(10, 290, 1000.0), (20, 1, 1100.0)], measure=1000.0, pitch=50.0)
    assert [n for _, n, _ in printed] == [290]
    assert [n for _, n, _ in notes] == [1]


def test_running_head_and_foot_are_furniture():
    head = [Row(600, 96, 800, [Word(600, 200, "KING")]), Row(1400, 118, 1450, [Word(1400, 50, "849")])]
    body = [Row(50, 160 + 30 * k, 700, [Word(50, 600, f"w{k}")]) for k in range(100)]
    foot = [Row(700, 3230, 760, [Word(700, 60, "21")])]  # a signature mark, p.848: 100px below the text
    text, furniture = pr.split_furniture(head + body + foot, pitch=30, height=3300)
    assert [r.words[0].t for r in furniture] == ["KING", "849", "21"]
    assert len(text) == 100


# ---------------------------------------------------------------- lines and tokens


def test_rows_without_speech_are_not_lines_and_turnovers_join():
    rows = []
    for x, text, speech in [(1.0, "Lear. O, reason not the need: our basest", True),
                            (2.4, "beggars", True),
                            (8.0, "[Kneeling.", False),
                            (0.0, "Are in the poorest thing superfluous:", True)]:
        r = row(x, text, right_u=MEASURE if text.endswith("basest") else None)
        r.start, r.speech = len(rows), speech
        rows.append(r)
    lines = lineate.globe_lines(rows, 861)
    assert [[r.text for r in ln.rows] for ln in lines] == [
        ["Lear. O, reason not the need: our basest", "beggars"],
        ["Are in the poorest thing superfluous:"]]


def test_speakers_are_alignment_tokens_but_not_text():
    body = etree.fromstring('<body xmlns="http://www.tei-c.org/ns/1.0"><div type="act" n="1">'
                            '<div type="scene" n="1"><sp><speaker>Old Man.</speaker>'
                            '<l>How now!</l></sp></div></div></body>')
    toks = tokens.tokenize(body)
    assert [(t.t, t.kind) for t in toks] == [("old", "speaker"), ("man", "speaker"),
                                             ("how", "speech"), ("now", "speech")]
    assert tokens.speaker_names(toks) == {"oldman"}
    assert toks[2].div == "1.1"


def test_stripping_a_milestone_keeps_the_words_around_it():
    p = etree.fromstring('<p xmlns="http://www.tei-c.org/ns/1.0">It did always seem so '
                         '<milestone unit="line" ed="Globe"/>to us: but '
                         '<milestone unit="line" ed="F1" n="7"/>now</p>')
    before = tokens.word_stream(p)
    assert source_text.strip_line_milestones(p) == {"Globe": 1, "F1": 1}
    assert len(p) == 0
    assert tokens.word_stream(p) == before


# ---------------------------------------------------------------- alignment


def test_a_stray_match_at_the_page_foot_does_not_end_the_page():
    """Antony p.929 ends "pinion of his wing,"; the P4 reads "off his", and
    "of his" matched "Lord of his fortunes" 60 words on, so p.930's first nine
    rows fell before its floor. Page word index -> P4 token index."""
    from globe.align_play import page_end
    page = {k: 15190 + k for k in range(16)}  # ... "he sends so poor a pinion"
    assert page_end(page) == 15205
    assert page_end({**page, 16: 15266, 17: 15267}) == 15205  # "of his", 60 on
    assert page_end({**page, 18: 15297}) == 15205  # the watermark's "OF" (p.915)
    held = {**page, 16: 15266, 17: 15267, 18: 15268}  # three in a run: the page's own
    assert page_end(held) == 15268
    assert page_end({k: 100 + k for k in range(5)}) == 104  # no jump: the last match


def test_the_scanners_watermark_is_furniture_wherever_the_foot_rule_misses_it():
    """Antony p.915 (Michigan): the text and a printer's signature run so low
    that no 2u gap stands above the watermark, and its "OF" was counted as a
    line. A row in the foot zone like a watermark line, OCR errors and all."""
    marks = ["Digitized by", "UNIVERSITY OF MICHIGAN", "Original from"]
    rows = [Row(0, 3688, 0, [Word(0, 1, "That"), Word(0, 1, "he")]),
            Row(0, 3785, 0, [Word(0, 1, "8–2")]),
            Row(0, 3833, 0, [Word(0, 1, "Original"), Word(0, 1, "fro")]),
            Row(0, 3894, 0, [Word(0, 1, "JNIVERSITY"), Word(0, 1, "OF"), Word(0, 1, "MICHIGA")]),
            Row(0, 100, 0, [Word(0, 1, "UNIVERSITY"), Word(0, 1, "OF"), Word(0, 1, "MICHIGAN")])]
    text, off = pr.split_watermark(rows, marks, 3950)
    assert [r.text for r in off] == ["Original fro", "JNIVERSITY OF MICHIGA"]
    assert [r.y for r in text] == [3688, 3785, 100]  # the signature stays; nothing above the foot zone goes
    assert pr.split_watermark(rows, (), 3950) == (rows, [])  # Trent declares no watermark


def test_the_margin_follows_a_column_that_drifts():
    """Trent, Antony p.923: flush rows drift from x=37 to x=48 down the
    column (pitch 30), and a turnover near the foot, 2.7u in from the local
    margin, read past 2.8u from the column's one margin: indented, a line."""
    pitch = 30.0
    body = [Row(37 + 11 * k / 59, 100 + 30 * k, 600, [Word(0, 1, "x")]) for k in range(60)]
    turnover = Row(48 + 2.65 * pitch, 100 + 30 * 58 + 15, 300, [Word(0, 1, "fortunes.")])
    margins = pr.local_margins(body + [turnover], pitch)
    assert abs(margins[0] - 37) < 1 and abs(margins[59] - 48) < 1
    assert 2.4 < (turnover.x - margins[-1]) / pitch < 2.8  # the turnover band
    assert (turnover.x - pr.column_margin(body, pitch)) / pitch > 2.8  # one margin: indented
    few = body[:10]
    assert pr.local_margins(few, pitch) == [pr.column_margin(few, pitch)] * 10
