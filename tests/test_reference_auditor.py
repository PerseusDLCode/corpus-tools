from pathlib import Path

import pytest
from lxml import etree

from auditors import ReferenceAuditor
from auditors.reference_auditor import ReferenceAuditReport


class TestDocHasRefsDecls:
    def test_true_when_single(self, thucydides_grc):
        assert ReferenceAuditor(thucydides_grc).doc_has_refsDecls()

    def test_true_when_multiple(self, phi1017_phi007_perseus_lat2):
        assert ReferenceAuditor(phi1017_phi007_perseus_lat2).doc_has_refsDecls()

    def test_true_sophocles(self, tlg0011_tlg001_perseus_grc2):
        assert ReferenceAuditor(tlg0011_tlg001_perseus_grc2).doc_has_refsDecls()


class TestDocHasCiteStructures:
    def test_true_thucydides(self, thucydides_grc):
        assert ReferenceAuditor(thucydides_grc).doc_has_cite_structures()

    def test_false_sophocles(self, tlg0011_tlg001_perseus_grc2):
        assert not ReferenceAuditor(tlg0011_tlg001_perseus_grc2).doc_has_cite_structures()

    def test_false_virgil(self, phi1017_phi007_perseus_lat2):
        assert not ReferenceAuditor(phi1017_phi007_perseus_lat2).doc_has_cite_structures()

    def test_false_aristotle_grc(self, tlg0086_tlg034_perseus_grc2):
        assert not ReferenceAuditor(tlg0086_tlg034_perseus_grc2).doc_has_cite_structures()


class TestDocHasDefaultRefsDecl:
    def test_true_thucydides(self, thucydides_grc):
        assert ReferenceAuditor(thucydides_grc).doc_has_default_refsDecl()

    def test_false_sophocles(self, tlg0011_tlg001_perseus_grc2):
        assert not ReferenceAuditor(tlg0011_tlg001_perseus_grc2).doc_has_default_refsDecl()

    def test_false_virgil(self, phi1017_phi007_perseus_lat2):
        assert not ReferenceAuditor(phi1017_phi007_perseus_lat2).doc_has_default_refsDecl()

    def test_false_homer(self, tlg0001_tlg001_perseus_grc2):
        assert not ReferenceAuditor(tlg0001_tlg001_perseus_grc2).doc_has_default_refsDecl()


class TestDefaultRefsDecIsACiteStructure:
    def test_true_thucydides(self, thucydides_grc):
        # tlg0003 has one refsDecl[@default='true'] that contains a citeStructure
        assert ReferenceAuditor(thucydides_grc).default_refsDecl_is_citeStructure()

    def test_false_no_default_refs_decl(self, phi1017_phi007_perseus_lat2):
        assert not ReferenceAuditor(phi1017_phi007_perseus_lat2).default_refsDecl_is_citeStructure()

    def test_false_no_cite_structures(self, tlg0011_tlg001_perseus_grc2):
        assert not ReferenceAuditor(tlg0011_tlg001_perseus_grc2).default_refsDecl_is_citeStructure()

    def test_false_no_default_and_no_cite_structure(self, tlg0086_tlg034_perseus_grc2):
        assert not ReferenceAuditor(tlg0086_tlg034_perseus_grc2).default_refsDecl_is_citeStructure()


class TestAudit:
    def test_returns_report(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert isinstance(report, ReferenceAuditReport)

    def test_report_path(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert isinstance(report.path, Path)
        assert report.path.name == "tlg0003.tlg001.perseus-grc2.xml"

    def test_report_base_urn(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert report.base_urn == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_report_base_urn_absent(self, phi2331_phi013_perseus_lat2):
        report = ReferenceAuditor(phi2331_phi013_perseus_lat2).audit()
        assert report.base_urn == ""

    def test_report_refs_decls_are_elements(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert all(isinstance(rd, etree._Element) for rd in report.refsDecls)

    def test_report_refs_decls_count(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert len(report.refsDecls) == 1

    def test_report_cite_structures(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert len(report.cite_structures) == 1

    def test_report_cite_structures_empty(self, tlg0011_tlg001_perseus_grc2):
        report = ReferenceAuditor(tlg0011_tlg001_perseus_grc2).audit()
        assert report.cite_structures == []

    def test_report_default_refs_decls(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert len(report.default_refsDecls) == 1

    def test_report_default_refs_decls_empty(self, phi1017_phi007_perseus_lat2):
        report = ReferenceAuditor(phi1017_phi007_perseus_lat2).audit()
        assert report.default_refsDecls == []

    def test_no_issues_thucydides(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert report.issues == []

    def test_issue_missing_base_urn(self, phi2331_phi013_perseus_lat2):
        report = ReferenceAuditor(phi2331_phi013_perseus_lat2).audit()
        assert any("CTS URN not found" in issue for issue in report.issues)

    def test_issue_no_cite_structure(self, tlg0011_tlg001_perseus_grc2):
        report = ReferenceAuditor(tlg0011_tlg001_perseus_grc2).audit()
        assert any("citeStructure" in issue for issue in report.issues)

    def test_issue_no_default_refs_decl(self, tlg0011_tlg001_perseus_grc2):
        report = ReferenceAuditor(tlg0011_tlg001_perseus_grc2).audit()
        assert any("default" in issue for issue in report.issues)


class TestRenderText:
    def test_returns_string(self, thucydides_grc):
        report = ReferenceAuditor(thucydides_grc).audit()
        assert isinstance(report.render_text(), str)

    def test_contains_filename(self, thucydides_grc):
        text = ReferenceAuditor(thucydides_grc).audit().render_text()
        assert "tlg0003.tlg001.perseus-grc2.xml" in text

    def test_contains_base_urn(self, thucydides_grc):
        text = ReferenceAuditor(thucydides_grc).audit().render_text()
        assert "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2" in text

    def test_no_issues_message(self, thucydides_grc):
        text = ReferenceAuditor(thucydides_grc).audit().render_text()
        assert "No issues found." in text

    def test_issues_section_present(self, phi2331_phi013_perseus_lat2):
        text = ReferenceAuditor(phi2331_phi013_perseus_lat2).audit().render_text()
        assert "ISSUES:" in text

    def test_missing_urn_issue_in_render(self, phi2331_phi013_perseus_lat2):
        text = ReferenceAuditor(phi2331_phi013_perseus_lat2).audit().render_text()
        assert "CTS URN not found" in text

    def test_refs_decls_section_present(self, thucydides_grc):
        text = ReferenceAuditor(thucydides_grc).audit().render_text()
        assert "REFSDECLS:" in text

    def test_none_value_when_urn_absent(self, phi2331_phi013_perseus_lat2):
        text = ReferenceAuditor(phi2331_phi013_perseus_lat2).audit().render_text()
        assert "(none)" in text
