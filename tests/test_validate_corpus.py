"""Tests for commands/validate_corpus.py."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from commands.validate_corpus import (
    _genre_from_cts,
    _genre_from_tei,
    _parse_genre_map,
    _parse_jing_line,
)

# ---------------------------------------------------------------------------
# Minimal XML fragments
# ---------------------------------------------------------------------------

_VERSE_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc><titleStmt><title>T</title></titleStmt>
          <publicationStmt><p/></publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
        <profileDesc>
          <textClass>
            <catRef scheme="#perseus-genre" target="#verse-epic"/>
          </textClass>
        </profileDesc>
      </teiHeader>
      <text><body><div type="textpart" subtype="book" n="1"><l n="1">x</l></div></body></text>
    </TEI>
""")

_PROSE_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc><titleStmt><title>T</title></titleStmt>
          <publicationStmt><p/></publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
      </teiHeader>
      <text><body><p>text</p></body></text>
    </TEI>
""")

_WORK_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0003.tlg001">
      <ti:genre confidence="high">prose-historiography</ti:genre>
    </ti:work>
""")

_GENRES_CSV = textwrap.dedent("""\
    urn,path,author,title,suggested_genre,confidence,recommended_genre,notes
    urn:cts:greekLit:tlg0003.tlg001.perseus-grc2,tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml,Thucydides,Histories,prose-historiography,high,prose-historiography,
""")


# ---------------------------------------------------------------------------
# _parse_jing_line
# ---------------------------------------------------------------------------

class TestParseJingLine:
    def test_parses_element_error(self):
        line = (
            "/path/to/file.xml:47:26: error: "
            'element "extent" not allowed anywhere; expected the element end-tag'
        )
        result = _parse_jing_line(line)
        assert result is not None
        file_stem, subject, msg = result
        assert file_stem == "file"
        assert subject == "extent"
        assert "extent" in msg
        assert "expected" not in msg

    def test_parses_attribute_error(self):
        line = (
            '/data/x.xml:10:5: error: attribute "foo" not allowed here; expected ...'
        )
        result = _parse_jing_line(line)
        assert result is not None
        _, subject, _ = result
        assert subject == "foo"

    def test_parses_incomplete_element_error(self):
        line = (
            '/data/x.xml:5:2: error: element "refsDecl" incomplete; expected element "citeStructure"'
        )
        result = _parse_jing_line(line)
        assert result is not None
        _, subject, msg = result
        assert subject == "refsDecl"
        assert "incomplete" in msg

    def test_fatal_level_parsed(self):
        line = '/data/x.xml:1:1: fatal: Content is not allowed in prolog.'
        result = _parse_jing_line(line)
        assert result is not None

    def test_returns_none_for_non_matching_line(self):
        assert _parse_jing_line("") is None
        assert _parse_jing_line("Jing version 20241231") is None

    def test_expected_clause_stripped_from_message(self):
        line = (
            '/a/b.xml:1:1: error: element "unclear" not allowed anywhere; '
            'expected the element end-tag or element "abbr"'
        )
        result = _parse_jing_line(line)
        assert result is not None
        _, _, msg = result
        assert "expected" not in msg

    def test_file_stem_extracted_correctly(self):
        line = (
            '/data/tlg0001.tlg001.perseus-grc2.xml:5:3: error: element "q" not allowed anywhere'
        )
        result = _parse_jing_line(line)
        assert result is not None
        file_stem, _, _ = result
        assert file_stem == "tlg0001.tlg001.perseus-grc2"


# ---------------------------------------------------------------------------
# _genre_from_tei
# ---------------------------------------------------------------------------

class TestGenreFromTei:
    def test_reads_catref_target(self, tmp_path):
        f = tmp_path / "verse.xml"
        f.write_text(_VERSE_TEI, encoding="utf-8")
        assert _genre_from_tei(f) == "verse-epic"

    def test_returns_empty_for_no_catref(self, tmp_path):
        f = tmp_path / "prose.xml"
        f.write_text(_PROSE_TEI, encoding="utf-8")
        assert _genre_from_tei(f) == ""

    def test_returns_empty_on_parse_error(self, tmp_path):
        f = tmp_path / "bad.xml"
        f.write_text("not xml", encoding="utf-8")
        assert _genre_from_tei(f) == ""


# ---------------------------------------------------------------------------
# _genre_from_cts
# ---------------------------------------------------------------------------

class TestGenreFromCts:
    def test_reads_genre_element(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        (work_dir / "__cts__.xml").write_text(_WORK_CTS, encoding="utf-8")
        f = work_dir / "text.xml"
        f.write_text(_PROSE_TEI, encoding="utf-8")
        assert _genre_from_cts(f) == "prose-historiography"

    def test_returns_empty_when_no_cts_file(self, tmp_path):
        f = tmp_path / "text.xml"
        f.write_text(_PROSE_TEI, encoding="utf-8")
        assert _genre_from_cts(f) == ""


# ---------------------------------------------------------------------------
# _parse_genre_map
# ---------------------------------------------------------------------------

class TestParseGenreMap:
    def test_maps_stem_to_recommended_genre(self, tmp_path):
        csv_path = tmp_path / "genres.csv"
        csv_path.write_text(_GENRES_CSV, encoding="utf-8")
        mapping = _parse_genre_map(csv_path)
        assert mapping.get("tlg0003.tlg001.perseus-grc2") == "prose-historiography"

    def test_empty_recommended_genre_excluded(self, tmp_path):
        csv_path = tmp_path / "genres.csv"
        csv_path.write_text(
            "urn,path,author,title,suggested_genre,confidence,recommended_genre,notes\n"
            "u,tlg0003/tlg001/x.xml,A,T,,,\n",
            encoding="utf-8",
        )
        mapping = _parse_genre_map(csv_path)
        assert "x" not in mapping


# ---------------------------------------------------------------------------
# main() integration — mock jing subprocess
# ---------------------------------------------------------------------------

class TestMainWithMockedJing:
    def test_writes_rng_errors_csv(self, tmp_path, odd_path):
        work_dir = tmp_path / "data" / "tlg0003" / "tlg001"
        work_dir.mkdir(parents=True)
        (work_dir / "__cts__.xml").write_text(_WORK_CTS, encoding="utf-8")
        tei = work_dir / "tlg0003.tlg001.perseus-grc2.xml"
        tei.write_text(_PROSE_TEI, encoding="utf-8")

        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        (schema_dir / "perseus_prose.rng").write_text("<grammar/>", encoding="utf-8")

        fake_jing_output = (
            f'{tei}:1:1: error: element "q" not allowed anywhere; expected ...\n'
            f'{tei}:2:1: error: element "q" not allowed anywhere; expected ...\n'
        )
        mock_result = MagicMock()
        mock_result.stdout = fake_jing_output

        import sys
        out_dir = tmp_path / "out"
        sys.argv = [
            "validate-corpus",
            str(tmp_path / "data"),
            "--schema-dir", str(schema_dir),
            "--output-dir", str(out_dir),
            "--odd", str(odd_path),
        ]

        with patch("commands.validate_corpus.subprocess.run", return_value=mock_result) as mock_run:
            # First call is `which jing` check — make it succeed; second is actual jing
            mock_run.side_effect = [
                MagicMock(returncode=0),   # which jing
                mock_result,               # jing validation
            ]
            from commands.validate_corpus import main
            main()

        out_csv = out_dir / "rng_errors.csv"
        assert out_csv.exists()
        with out_csv.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["element"] == "q"
        assert int(rows[0]["instance_count"]) == 2
        assert int(rows[0]["file_count"]) == 1
