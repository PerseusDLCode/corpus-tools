"""Tests for commands/apply_genre_map.py."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path
from unittest.mock import call, patch

import pytest

from commands.apply_genre_map import main

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_MINIMAL_ODD = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <encodingDesc>
          <classDecl>
            <taxonomy xml:id="perseus-genre">
              <category xml:id="drama">
                <category xml:id="drama-line"/>
                <category xml:id="drama-act-scene-line"/>
              </category>
              <category xml:id="verse">
                <category xml:id="verse-stichic"/>
                <category xml:id="verse-book-line"/>
              </category>
              <category xml:id="prose">
                <category xml:id="prose-standard"/>
              </category>
            </taxonomy>
          </classDecl>
        </encodingDesc>
      </teiHeader>
      <text><body><p/></body></text>
    </TEI>
""")

_MINIMAL_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc>
        <titleStmt><title>T</title></titleStmt>
        <publicationStmt><p/></publicationStmt>
        <sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body><div type="edition"><p>Text.</p></div></body></text>
    </TEI>
""")


@pytest.fixture
def odd_file(tmp_path) -> Path:
    p = tmp_path / "perseus_base.odd"
    p.write_text(_MINIMAL_ODD, encoding="utf-8")
    return p


@pytest.fixture
def data_dir(tmp_path) -> Path:
    d = tmp_path / "data"
    for name in [
        "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
        "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
        "tlg0006/tlg001/tlg0006.tlg001.perseus-grc2.xml",
    ]:
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_MINIMAL_TEI, encoding="utf-8")
    return d


def _write_csv(path: Path, rows: list[dict]) -> Path:
    fieldnames = ["urn", "path", "author", "title", "suggested_genre", "confidence",
                  "family", "proposed_subclass", "structure_signature", "match",
                  "needs_review", "recommended_genre", "notes"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    return path


def _invoke(argv: list[str]) -> int:
    import sys
    sys.argv = argv
    with pytest.raises(SystemExit) as exc:
        main()
    return exc.value.code


# ---------------------------------------------------------------------------
# Pre-validation
# ---------------------------------------------------------------------------

class TestPreValidation:
    def test_single_invalid_genre_exits_1(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "not-a-genre"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 1
        mock_apply.assert_not_called()

    def test_multiple_invalid_genres_all_reported(self, tmp_path, data_dir, odd_file, capsys):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "bad-genre-one"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
             "recommended_genre": "bad-genre-two"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file"):
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        stderr = capsys.readouterr().err
        assert "bad-genre-one" in stderr
        assert "bad-genre-two" in stderr

    def test_no_files_modified_when_validation_fails(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
             "recommended_genre": "totally-invalid"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        mock_apply.assert_not_called()

    def test_blank_recommended_genre_not_flagged_as_invalid(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": ""},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 0
        mock_apply.assert_not_called()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class TestApplication:
    def test_applies_genre_to_each_non_blank_row(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
             "recommended_genre": "prose-standard"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 0
        assert mock_apply.call_count == 2

    def test_passes_correct_path_and_genre(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        expected_path = data_dir / "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml"
        mock_apply.assert_called_once_with(expected_path, "prose-standard", "")

    def test_skips_blank_recommended_genre(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
             "recommended_genre": ""},
            {"path": "tlg0006/tlg001/tlg0006.tlg001.perseus-grc2.xml",
             "recommended_genre": "drama-line"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert mock_apply.call_count == 2

    def test_missing_file_is_error_not_crash(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg9999/tlg001/missing.xml",
             "recommended_genre": "prose-standard"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 1
        # The valid row is still processed
        assert mock_apply.call_count == 1

    def test_transform_exception_is_error_not_crash(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-eng4.xml",
             "recommended_genre": "prose-standard"},
        ])
        def fail_first(path, genre, cert=""):
            if "grc2" in str(path):
                raise RuntimeError("XSLT failure")

        with patch("commands.apply_genre_map.apply_genre_to_file", side_effect=fail_first):
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 1

    def test_exit_0_on_all_success(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file"):
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 0

    def test_empty_csv_exits_0(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            code = _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        assert code == 0
        mock_apply.assert_not_called()


class TestNeedsReviewFlag:
    def test_bare_family_target_gets_cert_low(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        expected_path = data_dir / "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml"
        mock_apply.assert_called_once_with(expected_path, "prose", "low")

    def test_needs_review_row_gets_cert_low(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard", "needs_review": "true"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        expected_path = data_dir / "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml"
        mock_apply.assert_called_once_with(expected_path, "prose-standard", "low")

    def test_verified_subclass_gets_no_cert(self, tmp_path, data_dir, odd_file):
        csv_path = _write_csv(tmp_path / "g.csv", [
            {"path": "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml",
             "recommended_genre": "prose-standard", "needs_review": "false"},
        ])
        with patch("commands.apply_genre_map.apply_genre_to_file") as mock_apply:
            _invoke(["apply-genre-map", str(csv_path), str(data_dir), "--odd", str(odd_file)])
        expected_path = data_dir / "tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml"
        mock_apply.assert_called_once_with(expected_path, "prose-standard", "")
