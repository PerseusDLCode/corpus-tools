from __future__ import annotations

from schmidt_sense_survey import survey, summarize

# Every fixture below is real text from data/schmidt/lexicon/
# schmidt.lexicon.perseus-eng1.xml (or, for the synthetic cases noted, built
# from real attested tokens) -- see doc/schmidt-sense-boundary-survey-report.org
# for the corpus-wide numbers these anchor.


def test_clean_lb_aligned_senses():
    # Real "Abatement," entry: sense 1 opens the entry (before any <cit>,
    # so it needs no <lb/> corroboration); sense 2 is <lb/>-aligned.
    text = (
        '<entryFree><orth>Abatement,</orth> 1) diminution, debilitation: '
        '<ref target="urn:cts:engLit:shakespeare.ham:4.7.121">Hml. IV, 7, 121</ref> '
        '(cf. <ref target="urn:cts:engLit:shakespeare.ham:4.7.121">Hml. IV, 7, 121</ref>).\n'
        '              <ref target="urn:cts:engLit:shakespeare.lr:1.4.64">Lr. I, 4, 64</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.cym:5.4.21">Cymb. V, 4,\n'
        '              21</ref>.<lb/>2) lower estimation: <cit>\n'
        "                <quote>falls into a. and low price,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.tn:1.1.13">Tw. I, 1, 13</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.orth == "Abatement,"
    assert entry.bucket == "clean"
    assert [m.token for m in entry.markers] == ["1", "2"]
    assert entry.markers[0].entry_start is True
    assert entry.markers[1].lb_aligned is True


def test_partial_mid_line_subsense_not_lb_aligned():
    # Real "Aim, vb." entry: 1) opens the entry; a) follows it MID-LINE with
    # no <lb/> ("1) to point or direct a weapon; a) absolutely:"); b), c),
    # 2) are each properly <lb/>-aligned. The unaligned "a)" makes this a
    # partial merge candidate, not clean.
    text = (
        "<entryFree><orth>Aim,</orth> vb. 1) to point or direct a weapon; a) absolutely: <cit>\n"
        "                <quote>here stand we both, and a. we at the best,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.3h6:3.1.8">H6C III, 1, 8</ref>\n'
        "              </cit>.<lb/>b) trans.: <cit>\n"
        "                <quote>...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.r2:1.1.14">R2 I, 1, 14</ref>\n'
        "              </cit>. <lb/>c) intr.: <cit>\n"
        "                <quote>...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.shr:5.2.50">Shr. V, 2, 50</ref>\n'
        "              </cit>. <lb/>2) to guess: <cit>\n"
        "                <quote>...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.2h6:2.4.58">H6B II, 4, 58</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.bucket == "partial"
    tokens = [(m.token, m.level, m.entry_start, m.lb_aligned) for m in entry.markers]
    assert tokens == [
        ("1", "arabic", True, False),
        ("a", "letter", False, False),
        ("b", "letter", False, True),
        ("c", "letter", False, True),
        ("2", "arabic", False, True),
    ]


def test_zero_lb_multi_sense():
    # Real "Abraham," entry: three numbered senses, zero <lb/> anywhere --
    # the entry never wraps a print line.
    text = (
        "<entryFree><orth>Abraham,</orth> 1) the patriarch: "
        '<ref target="urn:cts:engLit:shakespeare.r2:4.1.104">R2 IV,\n'
        "              104</ref>. "
        '<ref target="urn:cts:engLit:shakespeare.r3:4.3.38">R3 IV, 3, 38</ref>. '
        "2) Christian name of Mr.\n"
        "            Slender: "
        '<ref target="urn:cts:engLit:shakespeare.wiv:1.1.57">Wiv. I, 1, 57</ref> 3) <cit>\n'
        "                <quote>young A. Cupid,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.rom:2.1.13">Rom. II, 1, 13</ref>\n'
        "              </cit>, in derision. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.lb_count == 0
    assert entry.bucket == "zero_lb_multi_sense"
    assert [m.token for m in entry.markers] == ["1", "2", "3"]


def test_no_marker_single_sense():
    text = (
        "<entryFree><orth>Aidless,</orth> helpless, unaided: <cit>\n"
        "                <quote>an aidless vantage,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.lr:2.1.60">Lr. II, 1, 60</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.bucket == "no_marker"
    assert entry.markers == []


def test_lb_noise_only_no_marker_ever_aligns():
    # Zero recognized markers at all, but the entry does line-wrap with
    # <lb/> -- pure print-line noise, no sense-boundary signal.
    text = (
        "<entryFree><orth>Yond,</orth> that place there, over there: <cit>\n"
        "                <quote>look, how yond stars,<lb/>as thick as slaves...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.mv:5.1.60">Merch. V, 1, 60</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.lb_count == 1
    assert entry.bucket == "lb_noise_only"


def test_def_cross_reference_is_not_a_marker():
    # Real, repeated false-positive shape: "(cf. def. 4)" cites another
    # sense's number, it doesn't open one.
    text = (
        "<entryFree><orth>Amount,</orth> subst. computation: <cit>\n"
        "                <quote>...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.son:58.3">Sonn. 58, 3</ref>\n'
        "              </cit> (cf. def. 4). More text. </entryFree>"
    )
    [entry] = survey(text)
    assert entry.markers == []
    assert entry.bucket == "no_marker"


def test_possessive_and_dash_suffix_letters_are_not_markers():
    # Real false-positive shapes: "(the sun's)" (possessive gloss on a
    # pronoun antecedent) and "(our --s)" (dash-for-repeated-stem
    # convention) both happen to end in a bare letter before ")".
    text = (
        "<entryFree><orth>Thy,</orth> 1) hiding thy <mentioned>splendor</mentioned> "
        "(the sun's) shines: <cit>\n"
        "                <quote>(our --s).</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    assert [m.token for m in entry.markers] == ["1"]


def test_roman_numeral_marker_and_regnal_name_false_positive():
    # Built from real attested tokens: "Call, vb., I) to name: ... II) to
    # pronounce ..." (roman-numeral top-level senses, real Schmidt
    # convention) alongside a real false-positive shape, a spelled-out
    # regnal citation gloss "(i. e. Richard II)", which must NOT be read as
    # a sense marker.
    text = (
        "<entryFree><orth>Call,</orth> vb., I) to name: <cit>\n"
        "                <quote>thou might'st c. him a goodly person,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.tmp:1.2.415">Tp. I, 2, 415</ref>\n'
        "              </cit> (i. e. Richard II). <lb/>II) to pronounce: <cit>\n"
        "                <quote>...</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.per:1.2.92">Per. I, 2, 92</ref>\n'
        "              </cit>. </entryFree>"
    )
    [entry] = survey(text)
    tokens = [(m.token, m.level, m.entry_start, m.lb_aligned) for m in entry.markers]
    assert tokens == [
        ("I", "roman", True, False),
        ("II", "roman", False, True),
    ]
    assert entry.bucket == "clean"


def test_summarize_partitions_every_entry_exactly_once():
    text = (
        "<entryFree><orth>A,</orth> plain single-sense entry: <cit>\n"
        "                <quote>a,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.x:1.1.1">a</ref>\n'
        "              </cit>. </entryFree>"
        "<entryFree><orth>B,</orth> 1) x. 2) y: <cit>\n"
        "                <quote>b,</quote>\n"
        '                <ref target="urn:cts:engLit:shakespeare.x:1.1.2">b</ref>\n'
        "              </cit>. </entryFree>"
    )
    entries = survey(text)
    stats = summarize(entries)
    assert stats.entry_count == 2
    assert sum(stats.bucket_counts.values()) == 2
    assert stats.bucket_counts["no_marker"] == 1
    assert stats.bucket_counts["zero_lb_multi_sense"] == 1
