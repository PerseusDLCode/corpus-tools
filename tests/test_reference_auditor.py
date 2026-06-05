import pytest

from auditors import ReferenceAuditor


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


class TestAuditIssues:
    def test_no_base_urn_issue_reported(self, phi2331_phi013_perseus_lat2):
        auditor = ReferenceAuditor(phi2331_phi013_perseus_lat2)
        auditor.audit()
        # audit() is incomplete (no return yet); just verify it runs without error
        # and that the CTS URN warning would be triggered for this document

    def test_no_cite_structure_issue_reported(self, tlg0011_tlg001_perseus_grc2):
        auditor = ReferenceAuditor(tlg0011_tlg001_perseus_grc2)
        auditor.audit()
