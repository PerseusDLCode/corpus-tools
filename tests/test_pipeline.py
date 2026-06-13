"""Tests for pipeline.py — genre helpers, CTS URN computation, output resolution, and pipeline runs."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pipeline import (
    PIPELINES,
    _resolve_output,
    compute_cts_urn,
    read_genre,
    run_pipeline,
)


# ---------------------------------------------------------------------------
# Minimal TEI fixtures — just enough structure for all five stylesheets to run
# ---------------------------------------------------------------------------

_PROSE = """\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="old-schema.rnc"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Test Prose</title></titleStmt>
      <publicationStmt><p>Test</p></publicationStmt>
      <sourceDesc><p>Test</p></sourceDesc>
    </fileDesc>
    <encodingDesc/>
    <profileDesc>
      <textClass>
        <catRef scheme="#perseus-genre" target="#prose-standard"/>
      </textClass>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
      <div type="edition">
        <div type="textpart" subtype="book" n="1">
          <div type="textpart" subtype="chapter" n="1">
            <div type="textpart" subtype="section" n="1"><p>Test.</p></div>
          </div>
        </div>
      </div>
    </body>
  </text>
</TEI>
"""

_VERSE_EPIC = """\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="old-schema.rnc"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Test Verse</title></titleStmt>
      <publicationStmt><p>Test</p></publicationStmt>
      <sourceDesc><p>Test</p></sourceDesc>
    </fileDesc>
    <encodingDesc/>
    <profileDesc>
      <textClass>
        <catRef scheme="#perseus-genre" target="#verse-book-line"/>
      </textClass>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
      <div type="edition">
        <div type="textpart" subtype="book" n="1">
          <l n="1" ana="#met-dact">Line one.</l>
          <l n="2" met="u">Line two.</l>
          <l n="3">Line three.</l>
        </div>
      </div>
    </body>
  </text>
</TEI>
"""

_DRAMA = """\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="old-schema.rnc"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Test Drama</title></titleStmt>
      <publicationStmt><p>Test</p></publicationStmt>
      <sourceDesc><p>Test</p></sourceDesc>
    </fileDesc>
    <encodingDesc/>
    <profileDesc>
      <textClass>
        <catRef scheme="#perseus-genre" target="#drama-line"/>
      </textClass>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
      <div type="edition">
        <div type="episode" n="">
          <l n="1">Line one.</l>
          <l n="2">Line two.</l>
        </div>
      </div>
    </body>
  </text>
</TEI>
"""

_UNANNOTATED = """\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="old-schema.rnc"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Test</title></titleStmt>
      <publicationStmt><p>Test</p></publicationStmt>
      <sourceDesc><p>Test</p></sourceDesc>
    </fileDesc>
    <encodingDesc/>
    <profileDesc/>
  </teiHeader>
  <text>
    <body>
      <div type="edition">
        <div type="textpart" subtype="book" n="1"><p>Test.</p></div>
      </div>
    </body>
  </text>
</TEI>
"""

_UNKNOWN_GENRE = """\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="old-schema.rnc"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Test</title></titleStmt>
      <publicationStmt><p>Test</p></publicationStmt>
      <sourceDesc><p>Test</p></sourceDesc>
    </fileDesc>
    <encodingDesc/>
    <profileDesc>
      <textClass>
        <catRef scheme="#perseus-genre" target="#not-a-real-category"/>
      </textClass>
    </profileDesc>
  </teiHeader>
  <text><body><div type="edition"><p>Test.</p></div></body></text>
</TEI>
"""


_TEST_URN = "urn:cts:greekLit:test.test1"


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# read_genre
# ---------------------------------------------------------------------------

class TestReadGenre:
    def test_reads_prose_genre(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        assert read_genre(src) == "prose-standard"

    def test_reads_verse_genre(self, tmp_path):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        assert read_genre(src) == "verse-book-line"

    def test_reads_drama_genre(self, tmp_path):
        src = _write(tmp_path, "test.xml", _DRAMA)
        assert read_genre(src) == "drama-line"

    def test_returns_empty_when_unannotated(self, tmp_path):
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        assert read_genre(src) == ""


# ---------------------------------------------------------------------------
# genre_family
# ---------------------------------------------------------------------------

class TestGenreFamily:
    def test_prose_genre_maps_to_prose(self, genre_taxonomy):
        assert genre_taxonomy.family("prose-standard") == "prose"

    def test_verse_genre_maps_to_verse(self, genre_taxonomy):
        assert genre_taxonomy.family("verse-book-line") == "verse"

    def test_drama_genre_maps_to_drama(self, genre_taxonomy):
        assert genre_taxonomy.family("drama-line") == "drama"

    def test_all_genres_map_to_a_family(self, genre_taxonomy):
        for g in genre_taxonomy.valid:
            assert genre_taxonomy.family(g) in {"prose", "verse", "drama"}

    def test_unknown_genre_raises(self, genre_taxonomy):
        with pytest.raises(ValueError, match="Unknown genre"):
            genre_taxonomy.family("not-a-genre")


# ---------------------------------------------------------------------------
# compute_cts_urn
# ---------------------------------------------------------------------------

class TestComputeCtsUrn:
    def test_canonical_path_returns_full_urn(self, tmp_path):
        p = tmp_path / "canonical-greekLit" / "data" / "tlg0003" / "tlg001"
        p.mkdir(parents=True)
        f = p / "tlg0003.tlg001.perseus-grc2.xml"
        f.touch()
        assert compute_cts_urn(f) == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_canonical_latinLit_path(self, tmp_path):
        p = tmp_path / "canonical-latinLit" / "data" / "phi1017" / "phi007"
        p.mkdir(parents=True)
        f = p / "phi1017.phi007.perseus-lat2.xml"
        f.touch()
        assert compute_cts_urn(f) == "urn:cts:latinLit:phi1017.phi007.perseus-lat2"

    def test_non_canonical_path_returns_empty(self, tmp_path):
        f = tmp_path / "editing" / "tlg0003.tlg001.perseus-grc2.xml"
        f.parent.mkdir(parents=True)
        f.touch()
        assert compute_cts_urn(f) == ""

    def test_underscore_separator_also_matches(self, tmp_path):
        p = tmp_path / "canonical_greekLit" / "data" / "tlg0003" / "tlg001"
        p.mkdir(parents=True)
        f = p / "tlg0003.tlg001.perseus-grc2.xml"
        f.touch()
        assert compute_cts_urn(f) == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"


# ---------------------------------------------------------------------------
# _resolve_output
# ---------------------------------------------------------------------------

class TestResolveOutput:
    def test_none_output_returns_source(self, tmp_path):
        src = tmp_path / "file.xml"
        assert _resolve_output(src, None, False) == src

    def test_explicit_file_path_returned_unchanged(self, tmp_path):
        src = tmp_path / "file.xml"
        out = tmp_path / "out.xml"
        assert _resolve_output(src, str(out), False) == out

    def test_existing_directory_puts_file_inside(self, tmp_path):
        src = tmp_path / "file.xml"
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        result = _resolve_output(src, str(out_dir), False)
        assert result == out_dir / "file.xml"

    def test_batch_mode_puts_file_inside_dir(self, tmp_path):
        src = tmp_path / "file.xml"
        out_dir = tmp_path / "out"
        result = _resolve_output(src, str(out_dir), True)
        assert result == out_dir / "file.xml"
        assert out_dir.is_dir()

    def test_batch_mode_creates_directory(self, tmp_path):
        src = tmp_path / "file.xml"
        out_dir = tmp_path / "new_dir"
        _resolve_output(src, str(out_dir), True)
        assert out_dir.is_dir()


# ---------------------------------------------------------------------------
# run_pipeline — integration
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_prose_pipeline_sets_schema_pi(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_prose.rng" in result

    def test_prose_pipeline_sets_cts_idno(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'idno type="CTS"' in result

    def test_prose_pipeline_sets_xml_base_on_body(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "xml:base=" in result

    def test_prose_pipeline_adds_book_chapter_section_citestructure(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'unit="book"' in result
        assert 'unit="chapter"' in result
        assert 'unit="section"' in result

    def test_prose_pipeline_removes_edition_wrapper(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'type="edition"' not in result

    def test_prose_section_pipeline_adds_single_section_citestructure(self, tmp_path):
        section_doc = _PROSE.replace(
            'target="#prose-standard"', 'target="#prose-section"'
        ).replace(
            '<div type="textpart" subtype="book" n="1">\n'
            '          <div type="textpart" subtype="chapter" n="1">\n'
            '            <div type="textpart" subtype="section" n="1"><p>Test.</p></div>\n'
            '          </div>\n'
            '        </div>',
            '<div type="textpart" subtype="section" n="1"><p>Test.</p></div>',
        )
        src = _write(tmp_path, "test.xml", section_doc)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'unit="section"' in result
        assert 'unit="book"' not in result
        assert 'unit="chapter"' not in result

    def test_drama_pipeline_sets_schema_pi(self, tmp_path):
        src = _write(tmp_path, "test.xml", _DRAMA)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["drama"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_drama.rng" in result

    def test_drama_pipeline_uses_descendant_line_match(self, tmp_path):
        src = _write(tmp_path, "test.xml", _DRAMA)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["drama"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'match=".//l"' in result

    def test_verse_pipeline_sets_schema_pi(self, tmp_path):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["verse"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_verse.rng" in result

    def test_verse_pipeline_adds_book_line_citestructure(self, tmp_path):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["verse"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'unit="book"' in result
        assert 'unit="line"' in result

    def test_verse_pipeline_normalizes_ana_to_met(self, tmp_path):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["verse"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'met="dactylic-hexameter"' in result
        assert "ana=" not in result

    def test_verse_pipeline_strips_placeholder_met(self, tmp_path):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["verse"], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert 'met="u"' not in result

    def test_canonical_path_produces_full_urn(self, tmp_path):
        canon = tmp_path / "canonical-greekLit" / "data" / "tlg0003" / "tlg001"
        canon.mkdir(parents=True)
        src = canon / "tlg0003.tlg001.perseus-grc2.xml"
        src.write_text(_PROSE, encoding="utf-8")
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out)
        result = out.read_text()
        assert "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2" in result

    def test_unannotated_file_raises(self, tmp_path):
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        out = tmp_path / "out.xml"
        with pytest.raises(Exception, match="xsl:message"):
            run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})

    def test_unknown_genre_category_raises(self, tmp_path):
        src = _write(tmp_path, "test.xml", _UNKNOWN_GENRE)
        out = tmp_path / "out.xml"
        with pytest.raises(Exception, match="xsl:message"):
            run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})

    def test_non_canonical_path_without_cts_base_raises(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        with pytest.raises(Exception, match="xsl:message"):
            run_pipeline(PIPELINES["prose"], src, out)

    def test_output_file_is_written(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        assert out.exists()
        assert out.stat().st_size > 0

    def test_temp_files_are_cleaned_up(self, tmp_path):
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        import tempfile
        before = set(Path(tempfile.gettempdir()).glob("tmp*.xml"))
        run_pipeline(PIPELINES["prose"], src, out, **{"cts-base": _TEST_URN})
        after = set(Path(tempfile.gettempdir()).glob("tmp*.xml"))
        assert after == before


# ---------------------------------------------------------------------------
# set-genre + normalize dispatch — integration
# ---------------------------------------------------------------------------

class TestSetGenreAndNormalize:
    def test_set_genre_adds_catref(self, tmp_path):
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        out = tmp_path / "out.xml"
        from transformer import transform
        xml = transform(src, "set-genre.xsl", target="prose-standard")
        out.write_text(xml, encoding="utf-8")
        assert read_genre(out) == "prose-standard"

    def test_set_genre_then_normalize_dispatches_to_prose(self, tmp_path, genre_taxonomy):
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        annotated = tmp_path / "annotated.xml"
        from transformer import transform
        xml = transform(src, "set-genre.xsl", target="prose-standard")
        annotated.write_text(xml, encoding="utf-8")

        out = tmp_path / "out.xml"
        genre = read_genre(annotated)
        family = genre_taxonomy.family(genre)
        run_pipeline(PIPELINES[family], annotated, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_prose.rng" in result

    def test_normalize_dispatch_uses_correct_pipeline_for_drama(self, tmp_path, genre_taxonomy):
        src = _write(tmp_path, "test.xml", _DRAMA)
        out = tmp_path / "out.xml"
        genre = read_genre(src)
        family = genre_taxonomy.family(genre)
        run_pipeline(PIPELINES[family], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_drama.rng" in result

    def test_normalize_dispatch_uses_correct_pipeline_for_verse(self, tmp_path, genre_taxonomy):
        src = _write(tmp_path, "test.xml", _VERSE_EPIC)
        out = tmp_path / "out.xml"
        genre = read_genre(src)
        family = genre_taxonomy.family(genre)
        run_pipeline(PIPELINES[family], src, out, **{"cts-base": _TEST_URN})
        result = out.read_text()
        assert "perseus_verse.rng" in result


# ---------------------------------------------------------------------------
# main() CLI dispatch
# ---------------------------------------------------------------------------

class TestMainDispatch:
    """Test the argparse layer and sys.argv routing in pipeline.main()."""

    def test_no_subcommand_exits_nonzero(self):
        from pipeline import main
        with patch.object(sys, "argv", ["corpus-tools"]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code != 0

    def test_set_genre_writes_catref(self, tmp_path, odd_path):
        from pipeline import main
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        out = tmp_path / "out.xml"
        with patch.object(sys, "argv", [
            "corpus-tools", "set-genre",
            "--genre", "prose-standard",
            "--odd", str(odd_path),
            "-o", str(out),
            str(src),
        ]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert read_genre(out) == "prose-standard"

    def test_set_genre_invalid_genre_exits_nonzero(self, tmp_path, odd_path):
        from pipeline import main
        src = _write(tmp_path, "test.xml", _UNANNOTATED)
        with patch.object(sys, "argv", [
            "corpus-tools", "set-genre",
            "--genre", "not-a-real-genre",
            "--odd", str(odd_path),
            str(src),
        ]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code != 0

    def test_normalize_dispatches_and_writes_output(self, tmp_path, odd_path):
        from pipeline import main
        src = _write(tmp_path, "test.xml", _PROSE)
        out = tmp_path / "out.xml"
        with patch.object(sys, "argv", [
            "corpus-tools", "normalize",
            "--odd", str(odd_path),
            "--cts-base", _TEST_URN,
            "-o", str(out),
            str(src),
        ]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert "perseus_prose.rng" in out.read_text()

    def test_validate_valid_file_exits_zero(self, tmp_path):
        from pipeline import main
        src = _write(tmp_path, "test.xml", _PROSE)
        with patch("validate.validate_file", return_value=[]):
            with patch.object(sys, "argv", ["corpus-tools", "validate", str(src)]):
                with pytest.raises(SystemExit) as exc:
                    main()
        assert exc.value.code == 0

    def test_validate_invalid_file_exits_nonzero(self, tmp_path):
        from pipeline import main
        src = _write(tmp_path, "test.xml", _PROSE)
        fake_failure = {"type": "failed-assert", "location": "/TEI[1]", "test": "x", "message": "Missing"}
        with patch("validate.validate_file", return_value=[fake_failure]):
            with patch.object(sys, "argv", ["corpus-tools", "validate", str(src)]):
                with pytest.raises(SystemExit) as exc:
                    main()
        assert exc.value.code != 0
