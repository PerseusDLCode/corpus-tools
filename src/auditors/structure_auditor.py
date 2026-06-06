from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lxml import etree

from tei import TEIDocument, NS, XML_BASE, XML_ID
from .auditor import Auditor, CitationLevel, MilestoneInfo


@dataclass
class StructureAuditReport:
    path: Path
    base_urn: str
    structural_type: str
    citation_levels: list[CitationLevel]
    milestones: list[MilestoneInfo]
    cref_patterns: list[str]
    issues: list[str]
    proposed_cite_structure: str

    def render_text(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"FILE: {self.path.name}",
            f"{'='*70}",
            f"Base URN:         {self.base_urn or '(none found)'}",
            f"Structural type:  {self.structural_type}",
            f"cRefPatterns:     {', '.join(self.cref_patterns) or '(none)'}",
            "\nCITATION LEVELS:",
            f"  {'element':<8} {'subtype':<12} {'depth':>5} {'count':>7} "
            f"{'@n':>7} {'xml:base':>9} {'xml:id':>7} {'base OK':>8}",
            f"  {'-'*8} {'-'*12} {'-'*5} {'-'*7} {'-'*7} {'-'*9} {'-'*7} {'-'*8}",
        ]
        for lv in self.citation_levels:
            lines.append(
                f"  {lv.element:<8} {lv.subtype:<12} {lv.depth:>5} {lv.count:>7} "
                f"{lv.with_n:>7} {lv.with_base:>9} {lv.with_id:>7} "
                f"{lv.base_correct:>8}"
            )
            for expected, actual in lv.base_wrong_examples:
                lines += [
                    "    xml:base problems (examples):",
                    f"      expected: {expected}",
                    f"      actual:   {actual}",
                ]
        if self.milestones:
            lines.append("\nMILESTONES:")
            for ms in self.milestones:
                lines.append(f"  unit='{ms.unit}': {ms.count}")
        if self.issues:
            lines.append("\nISSUES:")
            for issue in self.issues:
                lines.append(f"  {issue}")
        else:
            lines.append("\nNo issues found.")
        lines.append(f"\nPROPOSED citeStructure:\n{self.proposed_cite_structure}")
        return "\n".join(lines)

    def to_json(self) -> str:
        d = asdict(self)
        d["path"] = str(self.path)
        return json.dumps(d, indent=2)


# ---------------------------------------------------------------------------
# StructureAuditor
# ---------------------------------------------------------------------------

