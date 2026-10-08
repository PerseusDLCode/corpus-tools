"""doc/forum.org #lineation/shared-lines-table: proposing and applying rows.

The proposer's result on Lear is checked against the hand check recorded in
that forum entry, so a change in the matching shows up as a changed set of
junctions rather than as a quietly different table.
"""

from pathlib import Path

import pytest

from globe import plays, shared_lines
from globe.shared_lines import Pair, Row, TableError

REPO = Path(__file__).resolve().parent.parent.parent

FOLGER = plays.get("lr").dracor_path
P4 = REPO.parent / "canonical-engLit/Renaissance/Shakespeare/opensource/lr.xml"


def _inputs_present() -> bool:
    try:
        from globe import witnesses
        witnesses.load(["miun", "trent"])
        return P4.is_file() and FOLGER.is_file()
    except Exception:
        return False


needs_inputs = pytest.mark.skipif(not _inputs_present(), reason="witness OCR or Folger not on disk")


def test_a_folger_line_that_stops_where_ours_runs_on_is_not_a_match():
    """III.7: Folger ftln-2307 is "To whose hands"; the Globe's second half is
    "To whose hands have you sent the lunatic king?", a full verse line. The
    first words agree and the lines do not."""
    folger = ("to", "whose", "hands")
    ours = ("to", "whose", "hands", "have", "you", "sent", "the", "lunatic", "king")
    assert shared_lines._matches(folger, ours)  # first words alone: a match
    assert not shared_lines._same_line(folger, ours)  # whole lines: not the same line
    assert shared_lines._same_line(("then", "shall", "you", "go", "no", "further"),
                                   ("then", "shall", "you", "go", "no", "further"))


def test_a_short_half_must_match_exactly():
    """A one-word half ("Speak.", "Come.") matched any Folger pair while a
    one-word tolerance applied to it, which proposed two junctions the hand
    check did not find."""
    assert shared_lines._matches(("late", "footed", "in"), ("late", "footed", "on"))
    assert not shared_lines._matches(("come",), ("speak",))
    assert not shared_lines._matches(("thou", "liest"), ("thou", "say"))


@pytest.mark.skipif(not FOLGER.is_file(), reason="Folger edition not on disk")
def test_folger_pairs_are_read_as_ids_and_first_words():
    pairs = shared_lines.read_folger(FOLGER)
    assert len(pairs) > 150
    hit = next(p for p in pairs if p.i_id == "ftln-2484")
    assert hit.f_id == "ftln-2485"
    assert hit.i_words == ("what", "like", "offensive") and hit.f_words[:2] == ("then", "shall")


@needs_inputs
def test_the_proposer_reproduces_the_hand_check():
    """Five junctions where the Folger marks I/F *and* holds the same lines.

    The forum's hand check lists six, counting III.7, but there the Folger's
    F half is "To whose hands" and stops, where the Globe's line runs on
    (doc/agenda.org #build/regenerate-lear, status). Nothing is proposed at
    the two V.3 junctions, where the Folger disagrees or is silent."""
    from globe import regenerate

    text, toks, pages, lines, results = regenerate.build("lr", table=[])
    failing = [iv for r in results for iv in r.failing]
    rows = shared_lines.propose(lines, toks, failing, shared_lines.read_folger(FOLGER))
    assert [(r.scene, r.second_half, r.folger_ids) for r in rows] == [
        ("4.2", "then shall you", "ftln-2484 ftln-2485"),
        ("4.6", "o you mighty", "ftln-2775 ftln-2776"),
        ("4.6", "a proclaim'd prize", "ftln-2984 ftln-2985"),
        ("5.3", "in wisdom i", "ftln-3419 ftln-3420"),
        ("5.3", "o my good", "ftln-3571 ftln-3572"),
    ]
    assert all(r.basis == "folger" and r.kind == "shared" for r in rows)


@needs_inputs
def test_the_table_on_disk_closes_every_interval():
    """Applying the reviewed table must leave no failing interval: a row that
    does not close its interval is an error, not a fix."""
    from globe import regenerate

    table = shared_lines.read_table()
    assert len(table) == 9
    assert sorted(r.kind for r in table) == (["numeral"] + ["shared"] * 6 + ["turnover"] * 2)
    *_, results = regenerate.build("lr", table)
    assert [iv for r in results for iv in r.failing] == []
    applied = [row for r in results for _, row in r.applied]
    assert len(applied) == len(table)


@needs_inputs
def test_a_row_that_matches_no_junction_is_an_error():
    from globe import regenerate

    table = shared_lines.read_table() + [
        Row("5.3", 878, "shared", "no such half", "nor this one", "", "image", "", "", "")]
    with pytest.raises(TableError, match="matches 0 junctions"):
        regenerate.build("lr", table)


@needs_inputs
def test_a_numeral_row_must_name_one_line():
    from globe import regenerate

    table = [r for r in shared_lines.read_table() if r.kind != "numeral"]
    table.append(Row("1.4", 852, "numeral", "39", "30", "not a line here", "image", "", "", ""))
    with pytest.raises(TableError, match="matches 0 lines"):
        regenerate.build("lr", table)


@needs_inputs
def test_line_starts_increase_through_the_play():
    """Two pages that open alike aligned to the same words (p.866/867), so two
    Globe lines began at one token and the text carried two milestones. The
    gate cannot see it: each page's own count is unaffected."""
    from globe import regenerate

    _, _, _, lines, _ = regenerate.build("lr", shared_lines.read_table())
    assert all(b.start > a.start for a, b in zip(lines, lines[1:]))


@needs_inputs
def test_iii_7_reads_speak_as_a_continuation_not_a_shared_half():
    """The page prints "Speak." flush at the margin, and Folger ftln-2308 ends
    with it. "Late footed in the kingdom?" stands alone."""
    from globe import regenerate

    _, toks, _, lines, _ = regenerate.build("lr", shared_lines.read_table())
    alone = next(l for l in lines if l.div == "3.7" and l.n == 45)
    assert [r.text for r in alone.rows] == ["Late footed in the kingdom?"]
    folded = next(l for l in lines if l.div == "3.7" and l.n == 46)
    assert [r.text for r in folded.rows][-1] == "Speak."
    assert len(folded.rows) == 3  # line, turnover, and the flush continuation


@needs_inputs
def test_an_unmarked_turnover_row_folds_the_row_below_into_its_line():
    """V.3 250: the Folger makes "Well thought on. Take my sword. Give it the
    Captain." one line (ftln-3550), and the page sets its continuation flush
    at the margin rather than at the turnover indent, so nothing in the
    layout says it continues. Cliff chose the Folger reading."""
    from globe import regenerate

    _, toks, _, lines, _ = regenerate.build("lr", shared_lines.read_table())
    ln = next(l for l in lines if l.div == "5.3" and l.n == 250)
    assert [r.text for r in ln.rows] == ["Edm. Well thought on: take my sword,",
                                         "Give it the captain."]
    assert ln.num == 250  # the page prints 250 beside it
    after = next(l for l in lines if l.div == "5.3" and l.n == 251)
    assert after.rows[0].text.startswith("Alb. Haste thee")


def test_pending_rows_are_those_with_an_empty_checked_column():
    assert Row("5.3", 878, "shared", "a", "b", "", "image", "", "", "").pending
    assert not Row("5.3", 878, "shared", "a", "b", "", "image", "", "2026-09-22 cliff", "").pending


@needs_inputs
def test_the_folger_check_measures_how_far_short_can_be_trusted():
    """doc/forum.org #lineation/shared-lines-table: the Folger informs a table
    row, it never outranks the page. The measurement is the reason: it marks a
    half of 41 of our 233 shared lines as standing alone (ana="#short"),
    including II.1.111 "Is he pursued?" / "Ay, my good lord.", which the forum
    records as verified by hand against the printed page."""
    from globe import folger_check
    from globe import regenerate

    _, toks, _, lines, _ = regenerate.build("lr", shared_lines.read_table())
    result = folger_check.compare(lines, toks, FOLGER)
    assert result["aligned"] > 0.9
    c = result["counts"]
    assert c["part"] == 183 and c["short"] == 41 and c["silent"] == 7
    assert result["pairs"] == 202 and result["together"] == 181 and result["split"] == 6
    contradicted = {(r[0], r[1]) for r in result["rows"] if r[4] == "short"}
    assert ("2.1", 111) in contradicted


def test_the_table_survives_a_spreadsheet_round_trip(tmp_path):
    """Saving the table from a spreadsheet pads every line to the column count
    and quotes any line with a comma, so a comment arrives as
    '"# cannot show, or a numeral..."'. Comments are recognised by their first
    field after parsing, never by the raw line."""
    p = tmp_path / "t.tsv"
    p.write_text(
        '# doc/forum.org #lineation/shared-lines-table\t\t\t\t\t\t\t\t\t\n'
        '"# cannot show, or numeral both witnesses misread"\t\t\t\t\t\t\t\t\t\n'
        "scene\tpage\tkind\tfirst_half\tsecond_half\tline\tbasis\tfolger_ids\tchecked\tnote\n"
        "4.2\t868\tshared\twhat like offensive\tthen shall you\t\tfolger\tftln-1 ftln-2\t2026-09-22 cliff\tseen\n"
        "\t\t\t\t\t\t\t\t\t\n")
    rows = shared_lines.read_table(p)
    assert len(rows) == 1
    assert rows[0].scene == "4.2" and rows[0].page == 868 and not rows[0].pending


def test_a_table_without_its_header_says_so(tmp_path):
    p = tmp_path / "t.tsv"
    p.write_text("4.2\t868\tshared\ta\tb\t\tfolger\t\t\t\n")
    with pytest.raises(TableError, match="header lacks"):
        shared_lines.read_table(p)


@needs_inputs
def test_part_vs_page_lists_every_disagreement():
    """@part was added by the P4's encoding process, not the keyboarders, so
    it is not part of the double-keyed text's authority. The page decides and
    nothing is retagged; this report is what that costs the markup."""
    from globe import regenerate

    text, toks, pages, lines, results = regenerate.build("lr", shared_lines.read_table())
    import tempfile
    from pathlib import Path as P
    with tempfile.TemporaryDirectory() as d:
        rows = regenerate.report_part_vs_page(P(d) / "x.tsv", lines, toks, text.body,
                                              shared_lines.read_table())
    kinds = {}
    for r in rows:
        kinds[r[3]] = kinds.get(r[3], 0) + 1
    assert sum(kinds.values()) == 21
    assert kinds["P4 marks neither half"] == 13
    assert kinds["P4 marks one half only"] == 3
    assert kinds["P4 marks a pair the page does not fold"] == 5
    # IV.6 871 is not a disagreement: there the P4 marks the pair, though the
    # page cannot show it and a table row was needed for the count
    assert not any(r[0] == "4.6" and r[1] == 40 for r in rows)
