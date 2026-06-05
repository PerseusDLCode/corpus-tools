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
    refsDecls: list[etree._Element]
    cite_structures: list[etree._Element]
    default_refsDecls: list[etree._Element]

    issues: list[str]

    def render_text(self) -> str:
        XML_ID_ATTR = "{http://www.w3.org/XML/1998/namespace}id"
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}  [reference audit]",
            f"{'='*70}",
            f"Edition URN:         {self.base_urn or '(none)'}",
            f"Has citeStructure:   {bool(self.cite_structures)}",
            f"Has default refsDecl:{bool(self.default_refsDecls)}",
            "\nREFSDECLS:",
        ]
        for rd in self.refsDecls:
            xml_id = rd.get(XML_ID_ATTR, "(none)")
            n = rd.get("n", "(none)")
            default = rd.get("default", "false")
            has_cs = bool(rd.xpath("tei:citeStructure", namespaces=NS))
            lines.append(
                f"  id={xml_id} n={n} default={default} citeStructure={has_cs}"
            )
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

        return ReferenceAuditReport(
            path=self._doc.path,
            base_urn=self._doc.base_urn,
            refsDecls=self._doc.refsDecls,
            cite_structures= self._doc.cite_structures,
            default_refsDecls= self._doc.default_refsDecl,
            issues=issues,
        )
