import json
from pathlib import Path

import pytest

from auditors import RuleAuditor, audit_rule
from auditors.rule_auditor import RuleAuditFinding, RuleAuditReport


class TestAuditRuleDecorator:
    def test_attaches_rule_id(self):
        @audit_rule("X001", role="error")
        def my_rule(doc): return None
        assert my_rule._rule_id == "X001"

    def test_attaches_role(self):
        @audit_rule("X001", role="error")
        def my_rule(doc): return None
        assert my_rule._role == "error"

    def test_default_role_is_warning(self):
        @audit_rule("X002")
        def my_rule(doc): return None
        assert my_rule._role == "warning"

    def test_preserves_function_name(self):
        @audit_rule("X003")
        def check_something(doc): return None
        assert check_something.__name__ == "check_something"


class TestRuleAuditor:
    def test_returns_report(self, thucydides_grc):
        report = RuleAuditor(thucydides_grc, []).audit()
        assert isinstance(report, RuleAuditReport)

    def test_empty_rules_produces_no_findings(self, thucydides_grc):
        report = RuleAuditor(thucydides_grc, []).audit()
        assert report.findings == []

    def test_rule_returning_none_produces_no_finding(self, thucydides_grc):
        @audit_rule("X001")
        def always_passes(doc): return None
        report = RuleAuditor(thucydides_grc, [always_passes]).audit()
        assert report.findings == []

    def test_rule_returning_single_finding(self, thucydides_grc):
        @audit_rule("X002", role="warning")
        def always_warns(doc):
            return RuleAuditFinding(rule_id="X002", role="warning", message="test warning")
        report = RuleAuditor(thucydides_grc, [always_warns]).audit()
        assert len(report.findings) == 1
        assert report.findings[0].rule_id == "X002"

    def test_rule_returning_list_of_findings(self, thucydides_grc):
        @audit_rule("X003")
        def multi(doc):
            return [
                RuleAuditFinding("X003", "info", "finding a"),
                RuleAuditFinding("X003", "info", "finding b"),
            ]
        report = RuleAuditor(thucydides_grc, [multi]).audit()
        assert len(report.findings) == 2

    def test_multiple_rules_accumulate_findings(self, thucydides_grc):
        @audit_rule("X004")
        def rule_a(doc): return RuleAuditFinding("X004", "warning", "a")

        @audit_rule("X005")
        def rule_b(doc): return RuleAuditFinding("X005", "error", "b")

        report = RuleAuditor(thucydides_grc, [rule_a, rule_b]).audit()
        assert len(report.findings) == 2

    def test_report_path(self, thucydides_grc):
        report = RuleAuditor(thucydides_grc, []).audit()
        assert isinstance(report.path, Path)


class TestRuleAuditReport:
    def test_errors_filter(self, thucydides_grc):
        @audit_rule("X006", role="error")
        def err(doc): return RuleAuditFinding("X006", "error", "e")

        @audit_rule("X007", role="warning")
        def warn(doc): return RuleAuditFinding("X007", "warning", "w")

        report = RuleAuditor(thucydides_grc, [err, warn]).audit()
        assert len(report.errors()) == 1
        assert report.errors()[0].role == "error"

    def test_warnings_filter(self, thucydides_grc):
        @audit_rule("X008", role="warning")
        def warn(doc): return RuleAuditFinding("X008", "warning", "w")

        report = RuleAuditor(thucydides_grc, [warn]).audit()
        assert len(report.warnings()) == 1

    def test_infos_filter(self, thucydides_grc):
        @audit_rule("X009", role="info")
        def info(doc): return RuleAuditFinding("X009", "info", "i")

        report = RuleAuditor(thucydides_grc, [info]).audit()
        assert len(report.infos()) == 1


class TestRenderText:
    def test_returns_string(self, thucydides_grc):
        assert isinstance(RuleAuditor(thucydides_grc, []).audit().render_text(), str)

    def test_contains_filename(self, thucydides_grc):
        text = RuleAuditor(thucydides_grc, []).audit().render_text()
        assert "tlg0003.tlg001.perseus-grc2.xml" in text

    def test_no_findings_message(self, thucydides_grc):
        text = RuleAuditor(thucydides_grc, []).audit().render_text()
        assert "No findings." in text

    def test_findings_section_present(self, thucydides_grc):
        @audit_rule("X010", role="warning")
        def warn(doc): return RuleAuditFinding("X010", "warning", "something")
        text = RuleAuditor(thucydides_grc, [warn]).audit().render_text()
        assert "FINDINGS" in text
        assert "[WARNING]" in text


class TestToJson:
    def test_returns_valid_json(self, thucydides_grc):
        result = RuleAuditor(thucydides_grc, []).audit().to_json()
        json.loads(result)

    def test_json_contains_path(self, thucydides_grc):
        data = json.loads(RuleAuditor(thucydides_grc, []).audit().to_json())
        assert "tlg0003.tlg001.perseus-grc2.xml" in data["path"]

    def test_json_findings_empty(self, thucydides_grc):
        data = json.loads(RuleAuditor(thucydides_grc, []).audit().to_json())
        assert data["findings"] == []
