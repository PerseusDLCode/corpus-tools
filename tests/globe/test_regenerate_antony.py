"""canonical-engLit doc/agenda.org #build/regenerate-ant: what Antony added to
the table's mechanism, on Antony's own pages.

- `separate`: a row the page displaces, as if it completed the line above,
  that the Globe numbers as a line of its own;
- a row that does not apply in one witness rules that witness out for the
  page, and the next is tried with it.

The rows here are made in the test: they are the mechanism's cases, not
reviewed rows of data/globe/shared-lines.tsv. Skipped without the witness
OCR and canonical-engLit.
"""

import pytest

from globe import lineate
from globe import shared_lines
from globe.shared_lines import Row, TableError


def _inputs_present() -> bool:
    try:
        from globe import plays, regenerate, witnesses
        witnesses.load(["miun", "trent"])
        return (regenerate.CORPUS / plays.get("ant").p4).is_file()
    except Exception:
        return False


needs_inputs = pytest.mark.skipif(not _inputs_present(), reason="witness OCR or canonical-engLit not on disk")


def R(scene, page, kind, a, b, line=""):
    return Row("ant", scene, page, kind, a, b, line, "image", "", "test", "")


def _line_of(lines, text):
    return next(ln for ln in lines if any(r.text.startswith(text) for r in ln.rows))


def _failing(results, div):
    return [(iv["page"], iv["to"], iv["error"]) for r in results for iv in r.failing if iv["div"] == div]


def test_a_line_is_cut_before_a_row_and_its_number_goes_with_its_row():
    from globe.page_rows import Row as PRow
    rows = [PRow(0, y, 0, []) for y in (0, 1, 2)]
    rows[2].num = 80
    ln = lineate.Line(rows, 922, num=80)
    from globe.regenerate import split
    second = split(ln, 1)
    assert ln.rows == rows[:1] and ln.num is None
    assert second.rows == rows[1:] and second.num == 80 and second.page == 922


def test_separate_is_a_kind_the_table_reads(tmp_path):
    p = tmp_path / "t.tsv"
    p.write_text("play\tscene\tpage\tkind\tfirst_half\tsecond_half\tline\tbasis\tfolger_ids\tchecked\tnote\n"
                 "ant\t2.6\t922\tseparate\ti know thee\twell\t\timage\t\t\t\n")
    assert shared_lines.read_table(p)[0].kind == "separate"


@needs_inputs
def test_separate_cuts_a_displaced_half_into_a_line_of_its_own():
    """II.6, p.922: "Pom. I know thee now: how farest thou, / soldier? /
    Eno. Well;" -- "Well;" is set to follow on, and the page prints 80 four
    lines later only if it is a line of its own (73)."""
    from globe import regenerate
    *_, lines, results = regenerate.build("ant", [])
    assert ("2.6", 922, 80, -1) in [(iv["div"], iv["page"], iv["to"], iv["error"])
                                       for r in results for iv in r.failing]
    *_, lines, results = regenerate.build("ant", [R("2.6", 922, "separate", "i know thee", "well")])
    well = _line_of(lines, "Eno. Well;")
    assert [r.text for r in well.rows] == ["Eno. Well;"] and (well.div, well.n) == ("2.6", 73)
    assert (922, 80, -1) not in _failing(results, "2.6")
    applied = [row.kind for r in results for _, row in r.applied]
    assert applied == ["separate"]


@needs_inputs
def test_separate_at_the_head_of_a_page_keeps_it_from_continuing_the_last():
    """V.2, p.941: "Cleo. Sole sir o' the world," heads the page, displaced,
    after "As things but done by chance." on p.940; the Globe prints 120
    beside it."""
    from globe import regenerate
    rows = [R("5.2", 941, "separate", "as things but", "sole sir")]
    def line_holding_sole(toks, lines):
        return next(ln for ln in lines if ln.div == "5.2"
                    and any(toks[r.start].t == "sole" for r in ln.rows))
    _, toks, _, lines, _ = regenerate.build("ant", [])
    sole = line_holding_sole(toks, lines)
    assert toks[sole.start].t == "as" and sole.page == 940  # joined to p.940's last line
    _, toks, _, lines, results = regenerate.build("ant", rows)
    sole = line_holding_sole(toks, lines)
    assert toks[sole.start].t == "sole" and sole.page == 941 and sole.num == 120
    assert [(r.page, row.kind) for r in results for _, row in r.applied] == [(941, "separate")]


@needs_inputs
def test_a_row_that_does_not_apply_in_michigan_is_tried_in_trent():
    """Michigan p.941 carries a reader's pencilled numbers and does not hold
    the lines the row names; Trent does. The row rules Michigan out for the
    page instead of stopping the build."""
    from globe import regenerate
    rows = [R("5.2", 941, "shared", "are therefore to", "cleopatra")]
    *_, results = regenerate.build("ant", rows)
    p941 = next(r for r in results if r.page == 941)
    assert ("miun/kraken", "table") in p941.tried and p941.witness == "trent/kraken"
    assert [row.second_half for _, row in p941.applied] == ["cleopatra"]


@needs_inputs
def test_a_row_that_applies_in_no_witness_stops_the_build_naming_each():
    from globe import regenerate
    with pytest.raises(TableError, match=r"miun/kraken: .*matches 0 junctions.*; trent/kraken: "):
        regenerate.build("ant", [R("5.2", 941, "shared", "no such half", "nor this one")])
