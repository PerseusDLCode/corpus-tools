from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tei import TEIDocument
from validate import validate_file_all
from .auditor import Auditor


@dataclass
class SchematronAuditFinding:
    kind: str     # 'failed-assert' or 'successful-report'
    role: str     # 'error', 'warning', 'info', or ''
    location: str
    test: str
    message: str


@dataclass
class SchematronAuditReport:
    path: Path
    sch_path: Path
    findings: list[SchematronAuditFinding] = field(default_factory=list)

    def errors(self) -> list[SchematronAuditFinding]:
        return [f for f in self.findings
                if f.kind == "failed-assert" or f.role == "error"]

    def warnings(self) -> list[SchematronAuditFinding]:
        return [f for f in self.findings if f.role in ("warning", "warn")]

    def render_text(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}  [schematron audit]",
            f"{'='*70}",
            f"Schema: {self.sch_path.name}",
        ]
        if self.findings:
            lines.append(f"\nFINDINGS ({len(self.findings)}):")
            for f in self.findings:
                tag = f.role.upper() if f.role else f.kind
                lines.append(f"  [{tag}] {f.location}")
                lines.append(f"    {f.message}")
        else:
            lines.append("\nNo findings.")
        return "\n".join(lines)

    def to_json(self) -> str:
        d = asdict(self)
        d["path"] = str(self.path)
        d["sch_path"] = str(self.sch_path)
        return json.dumps(d, indent=2)


class SchematronAuditor(Auditor[SchematronAuditReport]):

    def __init__(self, doc: TEIDocument, sch_path: Path | str) -> None:
        super().__init__(doc)
        self.sch_path = Path(sch_path)

    def audit(self) -> SchematronAuditReport:
        raw = validate_file_all(self._doc.path, self.sch_path)
        findings = [
            SchematronAuditFinding(
                kind=r["type"],
                role=r.get("role", ""),
                location=r["location"],
                test=r["test"],
                message=r["message"],
            )
            for r in raw
        ]
        return SchematronAuditReport(
            path=self._doc.path,
            sch_path=self.sch_path,
            findings=findings,
        )
