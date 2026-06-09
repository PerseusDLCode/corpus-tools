"""Tests for commands/survey_corpus.py."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from commands.survey_corpus import (
    _genre_from_cts,
    _genre_from_tei,
    survey_file,
    write_attributes_csv,
    write_elements_csv,
    write_structure_csv,
)
from lxml import etree

# ---------------------------------------------------------------------------
# Minimal XML fragments
# ---------------------------------------------------------------------------

_VERSE_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc><titleStmt><title>Iliad</title></titleStmt>
          <publicationStmt><p/></publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
        <profileDesc>
          <textClass>
            <catRef scheme="#perseus-genre" target="#verse-epic"/>
          </textClass>
        </profileDesc>
      </teiHeader>
      <text xml:lang="grc">
        <body xml:base="urn:cts:greekLit:tlg0012.tlg001.perseus-grc2">
          <div type="textpart" subtype="book" n="1">
            <l n="1" met="dactylic-hexameter">Μῆνιν ἄειδε θεά</l>
            <l n="2">test</l>
          </div>
        </body>
      </text>
    </TEI>
""")

_PROSE_TEI_NO_CATREF = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc><titleStmt><title>Histories</title></titleStmt>
          <publicationStmt><p/></publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
      </teiHeader>
      <text><body xml:base="urn:cts:greekLit:tlg0003.tlg001.perseus-grc2">
        <div type="textpart" subtype="book" n="1">
          <p>Text of history.</p>
        </div>
      </body></text>
    </TEI>
""")

_WORK_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
      <ti:title xml:lang="eng">Histories</ti:title>
      <ti:genre confidence="high">prose-historiography</ti:genre>
    </ti:work>
""")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def verse_file(tmp_path) -> Path:
    p = tmp_path / "tlg0012.tlg001.perseus-grc2.xml"
    p.write_text(_VERSE_TEI, encoding="utf-8")
    return p


@pytest.fixture
def prose_file_with_cts(tmp_path) -> Path:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "__cts__.xml").write_text(_WORK_CTS, encoding="utf-8")
    p = work_dir / "tlg0003.tlg001.perseus-grc2.xml"
    p.write_text(_PROSE_TEI_NO_CATREF, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _genre_from_tei
# ---------------------------------------------------------------------------

class TestGenreFromTei:
    def test_reads_catref_target(self, verse_file):
        root = etree.parse(str(verse_file)).getroot()
        assert _genre_from_tei(root) == "verse-epic"

    def test_strips_hash_prefix(self, verse_file):
        root = etree.parse(str(verse_file)).getroot()
        assert not _genre_from_tei(root).startswith("#")

    def test_returns_empty_when_no_catref(self, prose_file_with_cts):
        root = etree.parse(str(prose_file_with_cts)).getroot()
        assert _genre_from_tei(root) == ""


# ---------------------------------------------------------------------------
# _genre_from_cts
# ---------------------------------------------------------------------------

class TestGenreFromCts:
    def test_reads_genre_from_cts_xml(self, prose_file_with_cts):
        assert _genre_from_cts(prose_file_with_cts) == "prose-historiography"

    def test_returns_empty_when_no_cts_file(self, verse_file):
        assert _genre_from_cts(verse_file) == ""

    def test_returns_empty_when_no_genre_element(self, tmp_path):
        work_dir = tmp_path / "w"
        work_dir.mkdir()
        (work_dir / "__cts__.xml").write_text(
            '<?xml version="1.0"?><ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"/>',
            encoding="utf-8",
        )
        f = work_dir / "text.xml"
        f.write_text(_PROSE_TEI_NO_CATREF, encoding="utf-8")
        assert _genre_from_cts(f) == ""


# ---------------------------------------------------------------------------
# survey_file
# ---------------------------------------------------------------------------

class TestSurveyFile:
    def test_counts_elements_by_genre(self, verse_file):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(verse_file, el_counts, file_sets, attr_vals, struct_rows)
        # 'l' elements with genre 'verse-epic' should be counted
        assert ("l", "verse-epic") in el_counts
        assert el_counts[("l", "verse-epic")] == 2

    def test_file_set_populated(self, verse_file):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(verse_file, el_counts, file_sets, attr_vals, struct_rows)
        assert verse_file in file_sets[("l", "verse-epic")]

    def test_captures_met_attribute(self, verse_file):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(verse_file, el_counts, file_sets, attr_vals, struct_rows)
        assert ("l", "met", "verse-epic", "dactylic-hexameter") in attr_vals

    def test_captures_subtype_attribute(self, verse_file):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(verse_file, el_counts, file_sets, attr_vals, struct_rows)
        assert ("div", "subtype", "verse-epic", "book") in attr_vals

    def test_appends_structure_row(self, verse_file):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(verse_file, el_counts, file_sets, attr_vals, struct_rows)
        assert len(struct_rows) == 1
        assert struct_rows[0]["genre"] == "verse-epic"
        assert struct_rows[0]["structural_type"] == "div-based"

    def test_fallback_to_cts_genre(self, prose_file_with_cts):
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(prose_file_with_cts, el_counts, file_sets, attr_vals, struct_rows)
        assert ("p", "prose-historiography") in el_counts

    def test_bad_xml_skipped_gracefully(self, tmp_path):
        bad = tmp_path / "bad.xml"
        bad.write_text("not xml", encoding="utf-8")
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(bad, el_counts, file_sets, attr_vals, struct_rows)
        assert el_counts == {}

    def test_unknown_genre_when_no_annotation(self, tmp_path):
        f = tmp_path / "unannotated.xml"
        f.write_text(_PROSE_TEI_NO_CATREF, encoding="utf-8")
        el_counts: dict = {}
        file_sets: dict = {}
        attr_vals: dict = {}
        struct_rows: list = []
        survey_file(f, el_counts, file_sets, attr_vals, struct_rows)
        genres = {k[1] for k in el_counts}
        assert genres == {"unknown"}


# ---------------------------------------------------------------------------
# CSV writers
# ---------------------------------------------------------------------------

class TestWriteElementsCsv:
    def test_writes_expected_columns(self, tmp_path):
        out = tmp_path / "elements.csv"
        el_counts = {("l", "verse-epic"): 10, ("p", "prose-historiography"): 5}
        file_sets = {("l", "verse-epic"): {Path("a")}, ("p", "prose-historiography"): {Path("b")}}
        write_elements_csv(out, el_counts, file_sets)
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"element", "genre", "file_count", "instance_count"}

    def test_sorted_by_instance_count_desc(self, tmp_path):
        out = tmp_path / "elements.csv"
        el_counts = {("p", "prose-historiography"): 5, ("l", "verse-epic"): 10}
        file_sets = {("p", "prose-historiography"): set(), ("l", "verse-epic"): set()}
        write_elements_csv(out, el_counts, file_sets)
        with out.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["element"] == "l"
        assert int(rows[0]["instance_count"]) == 10


class TestWriteAttributesCsv:
    def test_writes_expected_columns(self, tmp_path):
        out = tmp_path / "attributes.csv"
        attr_vals = {("l", "met", "verse-epic", "dactylic-hexameter"): 100}
        write_attributes_csv(out, attr_vals)
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"element", "attribute", "genre", "value", "count"}

    def test_caps_values_at_max(self, tmp_path):
        out = tmp_path / "attributes.csv"
        # Create 35 distinct values (above the _MAX_VALUES=30 cap)
        attr_vals = {
            ("div", "subtype", "prose-historiography", f"val{i}"): i
            for i in range(35)
        }
        write_attributes_csv(out, attr_vals)
        with out.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 30


class TestWriteStructureCsv:
    def test_writes_expected_columns(self, tmp_path):
        out = tmp_path / "structure.csv"
        rows = [{
            "urn": "urn:cts:greekLit:x",
            "path": "/a/b.xml",
            "genre": "verse-epic",
            "structural_type": "div-based",
            "div_subtypes": "book",
            "milestone_units": "",
            "issues": "",
        }]
        write_structure_csv(out, rows)
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {
                "urn", "path", "genre", "structural_type",
                "div_subtypes", "milestone_units", "issues",
            }
