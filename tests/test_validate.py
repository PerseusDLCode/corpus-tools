"""Tests for validate.py — SVRL parsing and schxslt/Schematron integration."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from validate import _parse_svrl, _parse_svrl_all, validate_file, SCHEMATRON_DIR

# ---------------------------------------------------------------------------
# SVRL fixtures
# ---------------------------------------------------------------------------

_SVRL_NS = "http://purl.oclc.org/dsdl/svrl"

_SVRL_MIXED = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svrl:schematron-output xmlns:svrl="{_SVRL_NS}" title="test">
  <svrl:active-pattern name="p1"/>
  <svrl:fired-rule context="tei:body"/>
  <svrl:failed-assert location="/TEI[1]/text[1]/body[1]" test="@xml:base">
    <svrl:text>  body must carry @xml:base  </svrl:text>
  </svrl:failed-assert>
  <svrl:successful-report location="/TEI[1]" test="true()" role="error">
    <svrl:text>Error report</svrl:text>
  </svrl:successful-report>
  <svrl:successful-report location="/TEI[1]" test="true()">
    <svrl:text>Advisory note</svrl:text>
  </svrl:successful-report>
</svrl:schematron-output>
"""

_SVRL_EMPTY = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svrl:schematron-output xmlns:svrl="{_SVRL_NS}" title="test"/>
"""

# ---------------------------------------------------------------------------
# Minimal TEI fixtures for integration tests
# ---------------------------------------------------------------------------

_VALID_NORMALIZED = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <?xml-model href="https://raw.githubusercontent.com/PerseusDLCode/perseus-schemas/main/perseus_prose.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc>
          <titleStmt><title>T</title></titleStmt>
          <publicationStmt>
            <idno type="CTS">urn:cts:greekLit:test.test1.perseus-grc2</idno>
          </publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
        <encodingDesc>
          <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
              <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n"/>
            </citeStructure>
          </refsDecl>
        </encodingDesc>
        <profileDesc>
          <textClass>
            <catRef scheme="#perseus-genre" target="#prose-standard"/>
          </textClass>
        </profileDesc>
      </teiHeader>
      <text>
        <body xml:base="urn:cts:greekLit:test.test1.perseus-grc2">
          <div type="book" n="1"><p>Test.</p></div>
        </body>
      </text>
    </TEI>
""")

# Missing catRef, xml:base, idno, citeStructure, and schema PI — fails all rules.
_BARE_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <fileDesc>
          <titleStmt><title>T</title></titleStmt>
          <publicationStmt><p/></publicationStmt>
          <sourceDesc><p/></sourceDesc>
        </fileDesc>
        <encodingDesc/>
        <profileDesc/>
      </teiHeader>
      <text><body><p>Text.</p></body></text>
    </TEI>
""")


# ---------------------------------------------------------------------------
# _parse_svrl
# ---------------------------------------------------------------------------

class TestParseSvrl:
    def test_failed_assert_is_a_failure(self):
        failures = _parse_svrl(_SVRL_MIXED)
        types = [f["type"] for f in failures]
        assert "failed-assert" in types

    def test_successful_report_with_error_role_is_a_failure(self):
        failures = _parse_svrl(_SVRL_MIXED)
        types = [f["type"] for f in failures]
        assert "successful-report" in types

    def test_non_error_report_excluded(self):
        failures = _parse_svrl(_SVRL_MIXED)
        # Only failed-assert + error-role report: 2 entries, not 3
        assert len(failures) == 2

    def test_location_preserved(self):
        failures = _parse_svrl(_SVRL_MIXED)
        assert any("/TEI" in f["location"] for f in failures)

    def test_test_attribute_preserved(self):
        failures = _parse_svrl(_SVRL_MIXED)
        fa = next(f for f in failures if f["type"] == "failed-assert")
        assert fa["test"] == "@xml:base"

    def test_message_whitespace_normalized(self):
        failures = _parse_svrl(_SVRL_MIXED)
        fa = next(f for f in failures if f["type"] == "failed-assert")
        assert fa["message"] == "body must carry @xml:base"

    def test_empty_svrl_returns_empty_list(self):
        assert _parse_svrl(_SVRL_EMPTY) == []


# ---------------------------------------------------------------------------
# _parse_svrl_all
# ---------------------------------------------------------------------------

class TestParseSvrlAll:
    def test_includes_non_error_report(self):
        findings = _parse_svrl_all(_SVRL_MIXED)
        assert len(findings) == 3

    def test_role_attribute_preserved(self):
        findings = _parse_svrl_all(_SVRL_MIXED)
        roles = {f["role"] for f in findings}
        assert "error" in roles
        assert "" in roles  # advisory report has no role

    def test_empty_svrl_returns_empty_list(self):
        assert _parse_svrl_all(_SVRL_EMPTY) == []


# ---------------------------------------------------------------------------
# validate_file — integration (requires schxslt + Saxon)
# ---------------------------------------------------------------------------

class TestValidateFile:
    def test_valid_normalized_doc_passes(self, tmp_path):
        doc = tmp_path / "valid.xml"
        doc.write_text(_VALID_NORMALIZED, encoding="utf-8")
        failures = validate_file(doc, SCHEMATRON_DIR / "perseus_normalized.sch")
        assert failures == []

    def test_bare_tei_reports_missing_catref(self, tmp_path):
        doc = tmp_path / "bare.xml"
        doc.write_text(_BARE_TEI, encoding="utf-8")
        failures = validate_file(doc, SCHEMATRON_DIR / "perseus_normalized.sch")
        messages = " ".join(f["message"] for f in failures)
        assert failures
        assert "catRef" in messages or "genre" in messages.lower()

    def test_bare_tei_reports_missing_xml_base(self, tmp_path):
        doc = tmp_path / "bare.xml"
        doc.write_text(_BARE_TEI, encoding="utf-8")
        failures = validate_file(doc, SCHEMATRON_DIR / "perseus_normalized.sch")
        messages = " ".join(f["message"] for f in failures)
        assert "xml:base" in messages

    def test_bare_tei_reports_missing_citestructure(self, tmp_path):
        doc = tmp_path / "bare.xml"
        doc.write_text(_BARE_TEI, encoding="utf-8")
        failures = validate_file(doc, SCHEMATRON_DIR / "perseus_normalized.sch")
        messages = " ".join(f["message"] for f in failures)
        assert "citeStructure" in messages or "refsDecl" in messages

    def test_returns_list_of_dicts_with_expected_keys(self, tmp_path):
        doc = tmp_path / "bare.xml"
        doc.write_text(_BARE_TEI, encoding="utf-8")
        failures = validate_file(doc, SCHEMATRON_DIR / "perseus_normalized.sch")
        assert failures
        for f in failures:
            assert {"type", "location", "test", "message"} <= f.keys()
