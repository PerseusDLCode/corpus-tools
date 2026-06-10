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

# Prior LLM suggestion is the OLD literary genre; it maps to prose-standard.
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

# Structureless body -> will NOT match prose-standard -> review.
_MINIMAL_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>T</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body><div type="edition"><p>Text.</p></div></body></text>
    </TEI>
""")

# Full book->chapter->section structure (EpiDoc) -> matches prose-standard -> ready.
_TEI_WITH_URN = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>T</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body xml:base="urn:cts:greekLit:tlg0003.tlg001.perseus-grc2">
        <div type="edition">
          <div type="textpart" subtype="book" n="1">
            <div type="textpart" subtype="chapter" n="1">
              <div type="textpart" subtype="section" n="1"><p>Text.</p></div>
            </div>
          </div>
        </div>
      </body></text>
    </TEI>
""")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def data_dir(tmp_path) -> Path:
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
    def test_one_row_per_tei_file(self, data_dir, genre_taxonomy):
        assert len(generate_rows(data_dir, genre_taxonomy)) == 3

    def test_row_has_all_fieldnames(self, data_dir, genre_taxonomy):
        for row in generate_rows(data_dir, genre_taxonomy):
            assert set(row.keys()) == set(FIELDNAMES)

    def test_annotated_work_keeps_literary_suggestion(self, data_dir, genre_taxonomy):
        thucydides = [r for r in generate_rows(data_dir, genre_taxonomy)
                      if r["author"] == "Thucydides"]
        assert len(thucydides) == 2
        for r in thucydides:
            assert r["suggested_genre"] == "prose-historiography"
            assert r["confidence"] == "high"

    def test_literary_suggestion_mapped_to_structural_subclass(self, data_dir, genre_taxonomy):
        thucydides = [r for r in generate_rows(data_dir, genre_taxonomy)
                      if r["author"] == "Thucydides"]
        for r in thucydides:
            assert r["proposed_subclass"] == "prose-standard"
            assert r["family"] == "prose"

    def test_unannotated_work_has_no_suggestion(self, data_dir, genre_taxonomy):
        euripides = [r for r in generate_rows(data_dir, genre_taxonomy)
                     if r["author"] == "Euripides"]
        assert len(euripides) == 1
        assert euripides[0]["suggested_genre"] == ""
        assert euripides[0]["proposed_subclass"] == ""
        assert euripides[0]["needs_review"] == "true"

    def test_recommended_genre_prefilled_from_proposed(self, data_dir, genre_taxonomy):
        for row in generate_rows(data_dir, genre_taxonomy):
            assert row["recommended_genre"] == row["proposed_subclass"]

    def test_structured_doc_verifies_ready(self, data_dir, genre_taxonomy):
        rows = generate_rows(data_dir, genre_taxonomy)
        grc = next(r for r in rows if "tlg0003" in r["path"] and "grc2" in r["path"])
        assert grc["structure_signature"] == "book+chapter+section"
        assert grc["match"] == "ready"
        assert grc["needs_review"] == "false"

    def test_structureless_doc_flagged_review(self, data_dir, genre_taxonomy):
        rows = generate_rows(data_dir, genre_taxonomy)
        eng = next(r for r in rows if "tlg0003" in r["path"] and "eng4" in r["path"])
        assert eng["match"] == "review"
        assert eng["needs_review"] == "true"
        # falls back to the family default subclass
        assert eng["proposed_subclass"] == "prose-standard"

    def test_section_only_doc_resolves_to_prose_section(self, tmp_path, genre_taxonomy):
        # a shallow prose doc resolves to prose-section (not the book->chapter->section
        # default) and verifies ready
        section_tei = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <TEI xmlns="http://www.tei-c.org/ns/1.0">
              <teiHeader><fileDesc><titleStmt><title>T</title></titleStmt>
                <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
              </fileDesc></teiHeader>
              <text><body><div type="edition">
                <div type="textpart" subtype="section" n="1"><p>x</p></div>
              </div></body></text>
            </TEI>
        """)
        d = tmp_path / "data"
        w = d / "tlg0059" / "tlg030"
        w.mkdir(parents=True)
        (d / "tlg0059" / "__cts__.xml").write_text(
            _TEXTGROUP_CTS.replace("tlg0003", "tlg0059").replace("Thucydides", "Plato"),
            encoding="utf-8",
        )
        (w / "__cts__.xml").write_text(
            _WORK_CTS_ANNOTATED.replace("tlg0003", "tlg0059").replace("tlg001", "tlg030"),
            encoding="utf-8",
        )
        (w / "tlg0059.tlg030.perseus-grc2.xml").write_text(section_tei, encoding="utf-8")

        row = generate_rows(d, genre_taxonomy)[0]
        assert row["family"] == "prose"
        assert row["proposed_subclass"] == "prose-section"
        assert row["match"] == "ready"
        assert row["structure_signature"] == "section"

    def test_path_is_relative_to_data_dir(self, data_dir, genre_taxonomy):
        for row in generate_rows(data_dir, genre_taxonomy):
            assert not Path(row["path"]).is_absolute()
            assert (data_dir / row["path"]).exists()

    def test_urn_read_from_body_xml_base(self, data_dir, genre_taxonomy):
        rows = generate_rows(data_dir, genre_taxonomy)
        grc_row = next(r for r in rows if "perseus-grc2" in r["path"] and "tlg0003" in r["path"])
        assert grc_row["urn"] == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_title_extracted_from_work_cts(self, data_dir, genre_taxonomy):
        thucydides = [r for r in generate_rows(data_dir, genre_taxonomy)
                      if r["author"] == "Thucydides"]
        for r in thucydides:
            assert r["title"] == "History of the Peloponnesian War"

    def test_author_extracted_from_textgroup_cts(self, data_dir, genre_taxonomy):
        authors = {r["author"] for r in generate_rows(data_dir, genre_taxonomy)}
        assert authors == {"Thucydides", "Euripides"}

    def test_rows_sorted_by_path(self, data_dir, genre_taxonomy):
        paths = [r["path"] for r in generate_rows(data_dir, genre_taxonomy)]
        assert paths == sorted(paths)

    def test_empty_data_dir_returns_no_rows(self, tmp_path, genre_taxonomy):
        (tmp_path / "data").mkdir()
        assert generate_rows(tmp_path / "data", genre_taxonomy) == []

    def test_work_with_no_tei_files_produces_no_rows(self, tmp_path, genre_taxonomy):
        d = tmp_path / "data"
        w = d / "tlg0003" / "tlg001"
        w.mkdir(parents=True)
        (d / "tlg0003" / "__cts__.xml").write_text(_TEXTGROUP_CTS, encoding="utf-8")
        (w / "__cts__.xml").write_text(_WORK_CTS_ANNOTATED, encoding="utf-8")
        assert generate_rows(d, genre_taxonomy) == []


# ---------------------------------------------------------------------------
# CSV output (integration via main)
# ---------------------------------------------------------------------------

class TestCsvOutput:
    def test_csv_has_header_row(self, data_dir, odd_path, tmp_path):
        from commands.generate_genre_map import main
        import sys
        out = tmp_path / "genres.csv"
        sys.argv = ["generate-genre-map", str(data_dir), str(out), "--odd", str(odd_path)]
        main()
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == FIELDNAMES

    def test_csv_row_count_matches_tei_files(self, data_dir, odd_path, tmp_path):
        from commands.generate_genre_map import main
        import sys
        out = tmp_path / "genres.csv"
        sys.argv = ["generate-genre-map", str(data_dir), str(out), "--odd", str(odd_path)]
        main()
        with out.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 3
