"""canonical-engLit doc/agenda.org #globe/per-play-table: data/globe/plays.tsv
is where a play's P4, shell, printed pages and DraCor file are named.

Added in corpus-tools; not among the workshop's tests.
"""

import pytest

from globe import plays
from globe.plays import PlayTableError

HEADER = "play\tp4\tshell\tfirst_page\tlast_page\tdracor\n"


def table(tmp_path, body: str, header: str = HEADER):
    path = tmp_path / "plays.tsv"
    path.write_text(header + body, encoding="utf-8")
    return path


def test_lear_is_where_the_code_used_to_say():
    """What regenerate.PLAYS and shared_lines.FOLGER held before the table."""
    lr = plays.get("lr")
    assert (lr.p4, lr.shell, lr.first, lr.last) == (
        "Renaissance/Shakespeare/opensource/lr.xml",
        "data/shakespeare/lr/shakespeare.lr.globe.xml", 847, 878)
    assert lr.dracor == "tei/king-lear.xml"
    assert lr.dracor_path == plays.DRACOR / "tei/king-lear.xml"


def test_antony_is_printed_pages_911_to_943():
    ant = plays.get("ant")
    assert (ant.first, ant.last) == (911, 943)
    assert ant.p4.endswith("/ant.xml") and ant.shell.endswith("/shakespeare.ant.globe.xml")


def test_the_dracor_clone_is_read_where_it_is_now(monkeypatch, tmp_path):
    """Play.dracor_path follows plays.DRACOR, so a clone elsewhere needs no
    change to the table."""
    monkeypatch.setattr(plays, "DRACOR", tmp_path)
    assert plays.get("lr").dracor_path == tmp_path / "tei/king-lear.xml"


def test_a_play_the_table_lacks_is_named_with_the_plays_it_has(tmp_path):
    path = table(tmp_path, "lr\ta.xml\tb.xml\t1\t2\tc.xml\n")
    with pytest.raises(PlayTableError, match=r"no play 'oth' \(it has: lr\)"):
        plays.get("oth", path)


def test_what_a_spreadsheet_does_to_the_table_is_tolerated(tmp_path):
    """Comments quoted, every line padded with tabs, a blank line."""
    path = tmp_path / "plays.tsv"
    path.write_text('"# a comment, with a comma"\t\t\t\t\t\t\n' + HEADER.rstrip("\n") + "\t\n"
                    + "\t\t\t\t\t\t\n" + "lr\ta.xml\tb.xml\t1\t2\tc.xml\t\n", encoding="utf-8")
    assert plays.read(path) == {"lr": plays.Play("lr", "a.xml", "b.xml", 1, 2, "c.xml")}


@pytest.mark.parametrize("header, body, message", [
    ("play\tp4\tshell\tfirst_page\tlast_page\n", "lr\ta\tb\t1\t2\n", "header lacks dracor"),
    (HEADER, "lr\ta\tb\t1\t2\t\n", "row 2: no dracor"),
    (HEADER, "lr\ta\tb\tx\t2\tc\n", "row 2: pages 'x'-'2' are not numbers"),
    (HEADER, "lr\ta\tb\t9\t2\tc\n", "row 2: first page 9 is after last page 2"),
    (HEADER, "lr\ta\tb\t1\t2\tc\nlr\ta\tb\t3\t4\tc\n", "row 3: lr has a row already"),
])
def test_a_row_that_cannot_be_used_is_refused_and_named(tmp_path, header, body, message):
    with pytest.raises(PlayTableError, match=message):
        plays.read(table(tmp_path, body, header))
