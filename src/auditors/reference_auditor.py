from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tei import TEIDocument, NS, XML_BASE, XML_ID
from .auditor import Auditor
from .rule_auditor import RuleAuditor, RuleAuditFinding, audit_rule


# ---------------------------------------------------------------------------
# Reference rules
# ---------------------------------------------------------------------------

@audit_rule("REF001", role="warning")
def check_base_urn(doc: TEIDocument) -> RuleAuditFinding | None:
    if not doc.base_urn:
        return RuleAuditFinding(
            rule_id="REF001",
            role="warning",
            message=(
                "CTS URN not found on <body>/@xml:base — "
                "ReferenceParser requires it there, not on <div type='edition'>/@n"
            ),
        )
    return None


@audit_rule("REF002", role="info")
def check_cite_structures(doc: TEIDocument) -> RuleAuditFinding | None:
    if not doc.cite_structures:
        return RuleAuditFinding(
            rule_id="REF002",
            role="info",
            message=(
                "No <citeStructure> elements found; "
                "only legacy <cRefPattern> declarations present"
            ),
        )
    return None


@audit_rule("REF003", role="warning")
def check_default_refsDecl(doc: TEIDocument) -> RuleAuditFinding | None:
    if not doc.default_refsDecl:
        return RuleAuditFinding(
            rule_id="REF003",
            role="warning",
            message=(
                "<citeStructure> present but no <refsDecl default='true'>; "
                "ReferenceParser cannot auto-select a declaration"
            ),
        )
    return None


_REFERENCE_RULES = [check_base_urn, check_cite_structures, check_default_refsDecl]


# ---------------------------------------------------------------------------
# ReferenceAuditReport
# ---------------------------------------------------------------------------

@dataclass
class ReferenceAuditReport:
    path: Path
    base_urn: str
    refsDecl_count: int
    refsDecl_ids: list[str]
    refsDecl_has_cite_structure: list[bool]
    has_cite_structures: bool
    has_default_refsDecl: bool
    issues: list[str]

    def render_text(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}  [reference audit]",
            f"{'='*70}",
            f"Edition URN:         {self.base_urn or '(none)'}",
            f"Has citeStructure:   {self.has_cite_structures}",
            f"Has default refsDecl:{self.has_default_refsDecl}",
            "\nREFSDECLS:",
        ]
        for i, xml_id in enumerate(self.refsDecl_ids):
            has_cs = self.refsDecl_has_cite_structure[i] if i < len(self.refsDecl_has_cite_structure) else False
            lines.append(f"  id={xml_id or '(none)'} citeStructure={has_cs}")
        if self.issues:
            lines.append("\nISSUES:")
            for issue in self.issues:
                lines.append(f"  {issue}")
        else:
            lines.append("\nNo issues found.")
        return "\n".join(lines)

    def to_json(self) -> str:
        d = asdict(self)
        d["path"] = str(self.path)
        return json.dumps(d, indent=2)


# ---------------------------------------------------------------------------
# ReferenceAuditor
# ---------------------------------------------------------------------------

class ReferenceAuditor(Auditor[ReferenceAuditReport]):

    def doc_has_refsDecls(self) -> bool:
        return len(self._doc.refsDecls) > 0

    def doc_has_cite_structures(self) -> bool:
        return len(self._doc.cite_structures) > 0

    def doc_has_default_refsDecl(self) -> bool:
        return len(self._doc.default_refsDecl) > 0

    def default_refsDecl_is_citeStructure(self) -> bool:
        default_refsDecls = self._doc.default_refsDecl
        citestructures = self._doc.cite_structures
        if not default_refsDecls or not citestructures:
            return False
        parent = citestructures[0].xpath("./parent::tei:refsDecl", namespaces=NS)
        return bool(parent) and parent[0] == default_refsDecls[0]

    def audit(self) -> ReferenceAuditReport:
        rule_report = RuleAuditor(self._doc, _REFERENCE_RULES).audit()

        refsDecls = self._doc.refsDecls

        return ReferenceAuditReport(
            path=self._doc.path,
            base_urn=self._doc.base_urn,
            refsDecl_count=len(refsDecls),
            refsDecl_ids=[rd.get(XML_ID, "") for rd in refsDecls],
            refsDecl_has_cite_structure=[
                bool(rd.xpath("tei:citeStructure", namespaces=NS)) for rd in refsDecls
            ],
            has_cite_structures=self.doc_has_cite_structures(),
            has_default_refsDecl=self.doc_has_default_refsDecl(),
            issues=[f.message for f in rule_report.findings],
        )
