from pathlib import Path

import pytest

from auditors import SchematronAuditor
from auditors.schematron_auditor import SchematronAuditFinding, SchematronAuditReport


ENCODING_SCH = Path(__file__).parent.parent / "schematron" / "perseus_encoding.sch"
NORMALIZED_SCH = Path(__file__).parent.parent / "schematron" / "perseus_normalized.sch"


class TestSchematronAuditor:
    def test_returns_report(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert isinstance(report, SchematronAuditReport)

    def test_report_path(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert report.path.name == "tlg0003.tlg001.1st1K-eng1-fragment.xml"

    def test_report_sch_path(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert report.sch_path == ENCODING_SCH

    def test_findings_are_findings(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert all(isinstance(f, SchematronAuditFinding) for f in report.findings)

    def test_detects_empty_s_elements(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert len(report.findings) == 3

    def test_empty_s_findings_are_warnings(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert all(f.role == "warning" for f in report.findings)

    def test_no_findings_when_no_empty_s(self, thucydides_grc):
        report = SchematronAuditor(thucydides_grc, ENCODING_SCH).audit()
        assert report.findings == []


class TestLegacyElements:
    def test_detects_all_legacy_elements(self, thucydides_eng1_legacy):
        # 2 said + 1 docAuthor + 1 reg, no empty <s/>
        report = SchematronAuditor(thucydides_eng1_legacy, ENCODING_SCH).audit()
        assert len(report.findings) == 4

    def test_legacy_findings_are_warnings(self, thucydides_eng1_legacy):
        report = SchematronAuditor(thucydides_eng1_legacy, ENCODING_SCH).audit()
        assert all(f.role == "warning" for f in report.findings)
        assert report.errors() == []

    def test_detects_said(self, thucydides_eng1_legacy):
        report = SchematronAuditor(thucydides_eng1_legacy, ENCODING_SCH).audit()
        said = [f for f in report.findings if "said" in f.message]
        assert len(said) == 2
        assert all("<q>" in f.message for f in said)

    def test_detects_docAuthor(self, thucydides_eng1_legacy):
        report = SchematronAuditor(thucydides_eng1_legacy, ENCODING_SCH).audit()
        doc = [f for f in report.findings if "docAuthor" in f.message]
        assert len(doc) == 1
        assert "<author>" in doc[0].message

    def test_detects_reg(self, thucydides_eng1_legacy):
        report = SchematronAuditor(thucydides_eng1_legacy, ENCODING_SCH).audit()
        reg = [f for f in report.findings if "reg" in f.message and "choice" in f.message]
        assert len(reg) == 1


class TestSchematronAuditReport:
    def test_errors_excludes_warnings(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert report.errors() == []

    def test_warnings_returns_all_findings(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert len(report.warnings()) == 3


class TestRenderText:
    def test_returns_string(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert isinstance(report.render_text(), str)

    def test_contains_filename(self, thucydides_eng1_fragment):
        text = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().render_text()
        assert "tlg0003.tlg001.1st1K-eng1-fragment.xml" in text

    def test_contains_schema_name(self, thucydides_eng1_fragment):
        text = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().render_text()
        assert "perseus_encoding.sch" in text

    def test_contains_findings_section(self, thucydides_eng1_fragment):
        text = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().render_text()
        assert "FINDINGS" in text

    def test_no_findings_message(self, thucydides_grc):
        text = SchematronAuditor(thucydides_grc, ENCODING_SCH).audit().render_text()
        assert "No findings." in text

    def test_warning_tag_in_output(self, thucydides_eng1_fragment):
        text = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().render_text()
        assert "[WARNING]" in text


class TestToJson:
    def test_returns_string(self, thucydides_eng1_fragment):
        report = SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit()
        assert isinstance(report.to_json(), str)

    def test_json_contains_path(self, thucydides_eng1_fragment):
        import json
        data = json.loads(SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().to_json())
        assert "tlg0003.tlg001.1st1K-eng1-fragment.xml" in data["path"]

    def test_json_findings_count(self, thucydides_eng1_fragment):
        import json
        data = json.loads(SchematronAuditor(thucydides_eng1_fragment, ENCODING_SCH).audit().to_json())
        assert len(data["findings"]) == 3
