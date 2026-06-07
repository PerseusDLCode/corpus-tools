import json

import pytest

from auditors import StructureAuditor
from auditors.structure_auditor import StructureAuditReport, CitationLevel, MilestoneInfo


class TestStructureAuditor:
    def test_returns_report(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert isinstance(report, StructureAuditReport)

    def test_structural_type_div_based(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert report.structural_type == "div-based"

    def test_structural_type_milestone_based(self, tlg0001_tlg001_perseus_grc2):
        report = StructureAuditor(tlg0001_tlg001_perseus_grc2).audit()
        assert report.structural_type in ("milestone-based", "mixed")

    def test_citation_levels_are_citation_level_objects(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert all(isinstance(lv, CitationLevel) for lv in report.citation_levels)

    def test_citation_levels_thucydides_subtypes(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        subtypes = {lv.subtype for lv in report.citation_levels}
        assert "book" in subtypes
        assert "chapter" in subtypes
        assert "section" in subtypes

    def test_citation_levels_sorted_by_depth(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        depths = [lv.depth for lv in report.citation_levels]
        assert depths == sorted(depths)

    def test_no_milestones_thucydides(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert report.milestones == []

    def test_milestones_homer(self, tlg0001_tlg001_perseus_grc2):
        report = StructureAuditor(tlg0001_tlg001_perseus_grc2).audit()
        assert isinstance(report.milestones, list)
        units = {ms.unit for ms in report.milestones}
        assert "card" in units

    def test_milestones_are_milestone_info_objects(self, tlg0001_tlg001_perseus_grc2):
        report = StructureAuditor(tlg0001_tlg001_perseus_grc2).audit()
        assert all(isinstance(ms, MilestoneInfo) for ms in report.milestones)

    def test_no_issues_thucydides(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert report.issues == []

    def test_base_urn_thucydides(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert report.base_urn == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_proposed_cite_structure_is_string(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        assert isinstance(report.proposed_cite_structure, str)

    def test_proposed_cite_structure_contains_subtypes(self, thucydides_grc):
        report = StructureAuditor(thucydides_grc).audit()
        for lv in report.citation_levels:
            assert lv.subtype in report.proposed_cite_structure


class TestRenderText:
    def test_returns_string(self, thucydides_grc):
        assert isinstance(StructureAuditor(thucydides_grc).audit().render_text(), str)

    def test_contains_filename(self, thucydides_grc):
        text = StructureAuditor(thucydides_grc).audit().render_text()
        assert "tlg0003.tlg001.perseus-grc2.xml" in text

    def test_contains_base_urn(self, thucydides_grc):
        text = StructureAuditor(thucydides_grc).audit().render_text()
        assert "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2" in text

    def test_contains_citation_levels_section(self, thucydides_grc):
        text = StructureAuditor(thucydides_grc).audit().render_text()
        assert "CITATION LEVELS:" in text

    def test_no_issues_message(self, thucydides_grc):
        text = StructureAuditor(thucydides_grc).audit().render_text()
        assert "No issues found." in text

    def test_milestones_section_homer(self, tlg0001_tlg001_perseus_grc2):
        text = StructureAuditor(tlg0001_tlg001_perseus_grc2).audit().render_text()
        assert "MILESTONES:" in text


class TestToJson:
    def test_returns_valid_json(self, thucydides_grc):
        result = StructureAuditor(thucydides_grc).audit().to_json()
        json.loads(result)

    def test_json_contains_path(self, thucydides_grc):
        data = json.loads(StructureAuditor(thucydides_grc).audit().to_json())
        assert "tlg0003.tlg001.perseus-grc2.xml" in data["path"]

    def test_json_structural_type(self, thucydides_grc):
        data = json.loads(StructureAuditor(thucydides_grc).audit().to_json())
        assert data["structural_type"] == "div-based"

    def test_json_citation_levels_list(self, thucydides_grc):
        data = json.loads(StructureAuditor(thucydides_grc).audit().to_json())
        assert isinstance(data["citation_levels"], list)
        assert len(data["citation_levels"]) > 0
