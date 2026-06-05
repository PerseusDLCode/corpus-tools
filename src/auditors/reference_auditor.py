from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lxml import etree
from lxml.etree import _Element

from tei import TEIDocument, NS, XML_BASE, XML_ID
from .auditor import Auditor


@dataclass
class ReferenceAuditReport:
    path: Path
    base_urn: str
    body_urn: str
    has_cite_structure: bool
    has_default: bool
    refsDecls: list[etree._Element]
    issues: list[str]

    def render_text(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}  [reference audit]",
            f"{'='*70}",
            f"Edition URN:      {self.base_urn or '(none)'}",
            f"Body @n URN:      {self.body_urn or '(absent)'}",
            f"Has citeStructure: {self.has_cite_structure}",
            f"Has default refsDecl: {self.has_default}",
            "\nREFSDECLS:",
        ]
        for rd in self.refsDecls:
            lines.append(
                f"  id={rd.xml_id or '(none)'} n={rd.n or '(none)'} "
                f"default={rd.default} "
                f"citeStructure={rd.has_cite_structure}"
            )
            if rd.cite_units:
                lines.append(f"    cite units: {', '.join(rd.cite_units)}")
            if rd.cref_pattern_names:
                lines.append(f"    cRefPatterns: {', '.join(rd.cref_pattern_names)}")
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

        issues: list[str] = []
        if not self._doc.base_urn:
            issues.append(
                "WARNING: CTS URN not found on <body>/@xml:base — "
                "ReferenceParser requires it there, not on <div type='edition'>/@n"
            )
        if not self.doc_has_cite_structures():
            issues.append(
                "INFO: no <citeStructure> elements found; "
                "only legacy <cRefPattern> declarations present"
            )
        if not self.doc_has_default_refsDecl():
            issues.append(
                "WARNING: <citeStructure> present but no <refsDecl default='true'>; "
                "ReferenceParser cannot auto-select a declaration"
            )

        # return ReferenceAuditReport(
        #     path=self._doc.path,
        #     base_urn=base_urn,
        #     has_cite_structure=has_cite_structure,
        #     has_default=has_default,
        #     refsDecls=refsDecls,
        #     issues=issues,
        # )
