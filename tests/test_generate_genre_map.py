"""Tests for commands/generate_genre_map.py."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from commands.generate_genre_map import FIELDNAMES, generate_rows

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

_TEXTGROUP_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts"
                  urn="urn:cts:greekLit:tlg0003">
      <ti:groupname xml:lang="en">Thucydides</ti:groupname>
    </ti:textgroup>
""")

_EURIPIDES_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts"
                  urn="urn:cts:greekLit:tlg0006">
      <ti:groupname xml:lang="en">Euripides</ti:groupname>
    </ti:textgroup>
""")

_WORK_CTS_ANNOTATED = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
      <ti:title xml:lang="eng">History of the Peloponnesian War</ti:title>
      <ti:genre confidence="high">prose-historiography</ti:genre>
    </ti:work>
""")

_WORK_CTS_UNANNOTATED = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0006.tlg001" xml:lang="grc">
      <ti:title xml:lang="eng">Medea</ti:title>
    </ti:work>
""")

_MINIMAL_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>T</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body><div type="edition"><p>Text.</p></div></body></text>
    </TEI>
""")

_TEI_WITH_URN = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>T</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body xml:base="urn:cts:greekLit:tlg0003.tlg001.perseus-grc2">
        <div type="edition"><p>Text.</p></div>
      </body></text>
    </TEI>
""")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def data_dir(tmp_path) -> Path:
    """
    data/
      tlg0003/                         (Thucydides)
        __cts__.xml
        tlg001/
          __cts__.xml  (annotated: prose-historiography, high)
          tlg0003.tlg001.perseus-grc2.xml
          tlg0003.tlg001.perseus-eng4.xml
      tlg0006/                         (Euripides)
        __cts__.xml
        tlg001/
          __cts__.xml  (unannotated)
          tlg0006.tlg001.perseus-grc2.xml
    """
    d = tmp_path / "data"

    tg1 = d / "tlg0003"
    w1 = tg1 / "tlg001"
    w1.mkdir(parents=True)
    (tg1 / "__cts__.xml").write_text(_TEXTGROUP_CTS, encoding="utf-8")
    (w1 / "__cts__.xml").write_text(_WORK_CTS_ANNOTATED, encoding="utf-8")
    (w1 / "tlg0003.tlg001.perseus-grc2.xml").write_text(_TEI_WITH_URN, encoding="utf-8")
    (w1 / "tlg0003.tlg001.perseus-eng4.xml").write_text(_MINIMAL_TEI, encoding="utf-8")

    tg2 = d / "tlg0006"
    w2 = tg2 / "tlg001"
    w2.mkdir(parents=True)
    (tg2 / "__cts__.xml").write_text(_EURIPIDES_CTS, encoding="utf-8")
    (w2 / "__cts__.xml").write_text(_WORK_CTS_UNANNOTATED, encoding="utf-8")
    (w2 / "tlg0006.tlg001.perseus-grc2.xml").write_text(_MINIMAL_TEI, encoding="utf-8")

    return d


# ---------------------------------------------------------------------------
# generate_rows
# ---------------------------------------------------------------------------

class TestGenerateRows:
    def test_one_row_per_tei_file(self, data_dir):
        rows = generate_rows(data_dir)
        assert len(rows) == 3

    def test_row_has_all_fieldnames(self, data_dir):
        rows = generate_rows(data_dir)
        for row in rows:
            assert set(row.keys()) == set(FIELDNAMES)

    def test_annotated_work_fills_suggested_genre(self, data_dir):
        rows = generate_rows(data_dir)
        thucydides = [r for r in rows if r["author"] == "Thucydides"]
        assert len(thucydides) == 2
        for r in thucydides:
            assert r["suggested_genre"] == "prose-historiography"
            assert r["confidence"] == "high"

    def test_unannotated_work_has_empty_suggested_genre(self, data_dir):
        rows = generate_rows(data_dir)
        euripides = [r for r in rows if r["author"] == "Euripides"]
        assert len(euripides) == 1
        assert euripides[0]["suggested_genre"] == ""
        assert euripides[0]["confidence"] == ""

    def test_recommended_genre_prefilled_from_suggested(self, data_dir):
        rows = generate_rows(data_dir)
        for row in rows:
            assert row["recommended_genre"] == row["suggested_genre"]

    def test_notes_column_is_blank(self, data_dir):
        rows = generate_rows(data_dir)
        for row in rows:
            assert row["notes"] == ""

    def test_path_is_relative_to_data_dir(self, data_dir):
        rows = generate_rows(data_dir)
        for row in rows:
            # Should not be absolute
            assert not Path(row["path"]).is_absolute()
            # Should resolve to an existing file
            assert (data_dir / row["path"]).exists()

    def test_urn_read_from_body_xml_base(self, data_dir):
        rows = generate_rows(data_dir)
        grc_row = next(r for r in rows if "perseus-grc2" in r["path"] and "tlg0003" in r["path"])
        assert grc_row["urn"] == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_title_extracted_from_work_cts(self, data_dir):
        rows = generate_rows(data_dir)
        thucydides = [r for r in rows if r["author"] == "Thucydides"]
        for r in thucydides:
            assert r["title"] == "History of the Peloponnesian War"

    def test_author_extracted_from_textgroup_cts(self, data_dir):
        rows = generate_rows(data_dir)
        authors = {r["author"] for r in rows}
        assert authors == {"Thucydides", "Euripides"}

    def test_rows_sorted_by_path(self, data_dir):
        rows = generate_rows(data_dir)
        paths = [r["path"] for r in rows]
        assert paths == sorted(paths)

    def test_empty_data_dir_returns_no_rows(self, tmp_path):
        (tmp_path / "data").mkdir()
        rows = generate_rows(tmp_path / "data")
        assert rows == []

    def test_work_with_no_tei_files_produces_no_rows(self, tmp_path):
        d = tmp_path / "data"
        w = d / "tlg0003" / "tlg001"
        w.mkdir(parents=True)
        (d / "tlg0003" / "__cts__.xml").write_text(_TEXTGROUP_CTS, encoding="utf-8")
        (w / "__cts__.xml").write_text(_WORK_CTS_ANNOTATED, encoding="utf-8")
        rows = generate_rows(d)
        assert rows == []


# ---------------------------------------------------------------------------
# CSV output (integration via main)
# ---------------------------------------------------------------------------

class TestCsvOutput:
    def test_csv_has_header_row(self, data_dir, tmp_path):
        from commands.generate_genre_map import main
        import sys
        out = tmp_path / "genres.csv"
        sys.argv = ["generate-genre-map", str(data_dir), str(out)]
        main()
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == FIELDNAMES

    def test_csv_row_count_matches_tei_files(self, data_dir, tmp_path):
        from commands.generate_genre_map import main
        import sys
        out = tmp_path / "genres.csv"
        sys.argv = ["generate-genre-map", str(data_dir), str(out)]
        main()
        with out.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 3
