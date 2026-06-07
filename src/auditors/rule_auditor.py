from __future__ import annotations

import functools
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from tei import TEIDocument
from .auditor import Auditor


@dataclass
class RuleAuditFinding:
    rule_id: str
    role: str       # "error", "warning", "info"
    message: str
    location: str = ""


RuleFunction = Callable[["TEIDocument"], "RuleAuditFinding | list[RuleAuditFinding] | None"]


def audit_rule(rule_id: str, role: str = "warning", description: str = "") -> Callable:
    def decorator(fn: RuleFunction) -> RuleFunction:
        @functools.wraps(fn)
        def wrapper(doc: TEIDocument) -> RuleAuditFinding | list[RuleAuditFinding] | None:
            return fn(doc)
        wrapper._rule_id = rule_id
        wrapper._role = role
        wrapper._description = description
        return wrapper
    return decorator


@dataclass
class RuleAuditReport:
    path: Path
    findings: list[RuleAuditFinding] = field(default_factory=list)

    def errors(self) -> list[RuleAuditFinding]:
        return [f for f in self.findings if f.role == "error"]

    def warnings(self) -> list[RuleAuditFinding]:
        return [f for f in self.findings if f.role == "warning"]

    def infos(self) -> list[RuleAuditFinding]:
        return [f for f in self.findings if f.role == "info"]

    def render_text(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}  [rule audit]",
            f"{'='*70}",
        ]
        if self.findings:
            lines.append(f"\nFINDINGS ({len(self.findings)}):")
            for f in self.findings:
                lines.append(f"  [{f.role.upper()}] {f.rule_id}"
                             + (f" — {f.location}" if f.location else ""))
                lines.append(f"    {f.message}")
        else:
            lines.append("\nNo findings.")
        return "\n".join(lines)

    def to_json(self) -> str:
        d = asdict(self)
        d["path"] = str(self.path)
        return json.dumps(d, indent=2)


class RuleAuditor(Auditor[RuleAuditReport]):

    def __init__(self, doc: TEIDocument, rules: list[RuleFunction]) -> None:
        super().__init__(doc)
        self._rules = rules

    def audit(self) -> RuleAuditReport:
        findings: list[RuleAuditFinding] = []
        for rule in self._rules:
            result = rule(self._doc)
            if result is None:
                pass
            elif isinstance(result, list):
                findings.extend(result)
            else:
                findings.append(result)
        return RuleAuditReport(path=self._doc.path, findings=findings)
