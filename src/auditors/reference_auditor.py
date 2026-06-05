from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Generic, TypeVar

from lxml import etree

from tei import TEIDocument, NS, XML_BASE, XML_ID
from auditor import Auditor, RefsDecl


@dataclass
class ReferenceAuditReport:
    path: Path
    base_urn: str
    body_urn: str
    Has_structure: bool
    has_default: bool
    refsDecls: list[RefsDecl]
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

    def audit(self) -> ReferenceAuditReport:
        root = self._doc.root
        base_urn = self._doc.extract_base_urn()
        body_urn = self._extract_body_urn(root)

        refsDecls = self._parse_refs_decls(root)
        has_cite_structure = any(rd.has_cite_structure for rd in refsDecls)
        has_default = any(rd.default for rd in refsDecls)

        issues: list[str] = []
        if not body_urn:
            issues.append(
                "WARNING: CTS URN not found on <body>/@xml:base — "
                "ReferenceParser requires it there, not on <div type='edition'>/@n"
            )
        if not has_cite_structure:
            issues.append(
                "INFO: no <citeStructure> elements found; "
                "only legacy <cRefPattern> declarations present"
            )
        if has_cite_structure and not has_default:
            issues.append(
                "WARNING: <citeStructure> present but no <refsDecl default='true'>; "
                "ReferenceParser cannot auto-select a declaration"
            )

        return ReferenceAuditReport(
            path=self._doc.path,
            base_urn=base_urn,
            body_urn=body_urn,
            has_cite_structure=has_cite_structure,
            has_default=has_default,
            refsDecls=refsDecls,
            issues=issues,
        )

    def _extract_body_urn(self, root: etree._Element) -> str:
        body = root.find(".//tei:text/tei:body", NS)
        if body is not None:
            urn = body.get(XML_BASE, "")
            if urn.startswith("urn:cts:"):
                return urn
        return ""

    def _parse_refs_decls(self, root: etree._Element) -> list[RefsDecl]:
        result: list[RefsDecl] = []
        for rd_elem in root.xpath("//tei:encodingDesc/tei:refsDecl", namespaces=NS):
            xml_id = rd_elem.get("{http://www.w3.org/XML/1998/namespace}id", "")
            n = rd_elem.get("n", "")
            default = rd_elem.get("default", "").lower() == "true"

            cs_elems = rd_elem.xpath(".//tei:citeStructure", namespaces=NS)
            cite_units = [e.get("unit", "") for e in cs_elems if e.get("unit")]
            has_cs = bool(cs_elems)

            cref_names = list(rd_elem.xpath(
                "tei:cRefPattern/@n", namespaces=NS
            ))

            result.append(RefsDecl(
                xml_id=xml_id,
                n=n,
                default=default,
                has_cite_structure=has_cs,
                cite_units=cite_units,
                cref_pattern_names=cref_names,
            ))
        return result
