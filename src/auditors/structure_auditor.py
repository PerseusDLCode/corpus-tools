from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lxml import etree

from tei import TEIDocument, NS, XML_BASE, XML_ID
from .auditor import Auditor
from .rule_auditor import RuleAuditor, RuleAuditFinding, audit_rule


# ---------------------------------------------------------------------------
# Shared dataclasses (moved here from auditor.py)
# ---------------------------------------------------------------------------

@dataclass
class CitationLevel:
    element: str
    subtype: str
    depth: int
    count: int
    with_n: int
    with_base: int
    with_id: int
    base_correct: int
    base_wrong_examples: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class MilestoneInfo:
    unit: str
    count: int


# ---------------------------------------------------------------------------
# Structure rules
# ---------------------------------------------------------------------------

@audit_rule("STR001", role="warning")
def check_has_structure(doc: TEIDocument) -> RuleAuditFinding | None:
    has_divs = bool(doc.root.xpath("//tei:div[@type='textpart']", namespaces=NS))
    has_milestones = bool(doc.root.xpath("//tei:milestone", namespaces=NS))
    if not has_divs and not has_milestones:
        return RuleAuditFinding(
            rule_id="STR001",
            role="warning",
            message="No <div type='textpart'> or <milestone> elements found; document appears unstructured.",
        )
    return None


@audit_rule("STR002", role="info")
def check_mixed_structure(doc: TEIDocument) -> RuleAuditFinding | None:
    has_divs = bool(doc.root.xpath("//tei:div[@type='textpart']", namespaces=NS))
    has_milestones = bool(doc.root.xpath("//tei:milestone", namespaces=NS))
    if has_divs and has_milestones:
        return RuleAuditFinding(
            rule_id="STR002",
            role="info",
            message="Document uses both <div type='textpart'> and <milestone> elements; citation may be ambiguous.",
        )
    return None


@audit_rule("STR003", role="warning")
def check_divs_have_n(doc: TEIDocument) -> list[RuleAuditFinding]:
    divs = doc.root.xpath("//tei:div[@type='textpart'][not(@n)]", namespaces=NS)
    if not divs:
        return []
    subtypes = {d.get("subtype", "(none)") for d in divs}
    return [RuleAuditFinding(
        rule_id="STR003",
        role="warning",
        message=(
            f"{len(divs)} <div type='textpart'> element(s) lack @n "
            f"(subtypes: {', '.join(sorted(subtypes))}); citation by position unreliable."
        ),
    )]


@audit_rule("STR004", role="warning")
def check_xml_base_values(doc: TEIDocument) -> list[RuleAuditFinding]:
    if not doc.base_urn:
        return []
    divs_with_base = doc.root.xpath(
        "//tei:div[@type='textpart'][@xml:base]", namespaces=NS
    )
    bad = [d for d in divs_with_base if not d.get(XML_BASE, "").startswith(doc.base_urn)]
    if not bad:
        return []
    examples = bad[:3]
    msgs = [f"  {d.get(XML_BASE)}" for d in examples]
    return [RuleAuditFinding(
        rule_id="STR004",
        role="warning",
        message=(
            f"{len(bad)} <div type='textpart'>/@xml:base value(s) do not start with "
            f"the document base URN ({doc.base_urn}). Examples:\n" + "\n".join(msgs)
        ),
    )]


_STRUCTURE_RULES = [check_has_structure, check_mixed_structure, check_divs_have_n, check_xml_base_values]


# ---------------------------------------------------------------------------
# StructureAuditReport
# ---------------------------------------------------------------------------

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
            f"FILE: {self.path.name}  [structure audit]",
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
                    f"      expected prefix: {expected}",
                    f"      actual:          {actual}",
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

def _build_proposed_cite_structure(levels: list[CitationLevel]) -> str:
    sorted_levels = sorted(levels, key=lambda lv: lv.depth)
    if not sorted_levels:
        return "(no citation structure detected)"

    delimiters = [":", ".", "."]
    lines = ['<refsDecl default="true">']
    indent = "  "
    for i, lv in enumerate(sorted_levels):
        delim = delimiters[i] if i < len(delimiters) else "."
        is_last = (i == len(sorted_levels) - 1)
        closing = "/>" if is_last else ">"
        match_xpath = f"tei:div[@subtype='{lv.subtype}']" if lv.element == "div" else f"tei:milestone[@unit='{lv.subtype}']"
        lines.append(
            f"{indent * (i + 1)}"
            f'<citeStructure unit="{lv.subtype}" match="{match_xpath}" use="@n" delim="{delim}"{closing}'
        )
    for i in range(len(sorted_levels) - 2, -1, -1):
        lines.append(f"{indent * (i + 1)}</citeStructure>")
    lines.append("</refsDecl>")
    return "\n".join(lines)


class StructureAuditor(Auditor[StructureAuditReport]):

    def audit(self) -> StructureAuditReport:
        root = self._doc.root
        base_urn = self._doc.base_urn

        # --- Citation levels from div[@type='textpart'] ---
        all_divs = root.xpath("//tei:div[@type='textpart']", namespaces=NS)
        by_subtype: dict[str, list] = defaultdict(list)
        for d in all_divs:
            subtype = d.get("subtype", "")
            by_subtype[subtype].append(d)

        citation_levels: list[CitationLevel] = []
        for subtype, divs in by_subtype.items():
            depth = len(divs[0].xpath(
                "ancestor::tei:div[@type='textpart']", namespaces=NS
            )) + 1
            with_n = sum(1 for d in divs if d.get("n") is not None)
            with_base = sum(1 for d in divs if d.get(XML_BASE) is not None)
            with_id = sum(1 for d in divs if d.get(XML_ID) is not None)
            base_vals = [d.get(XML_BASE, "") for d in divs if d.get(XML_BASE)]
            base_correct = sum(1 for v in base_vals if v.startswith(base_urn)) if base_urn else 0
            wrong = [(base_urn, v) for v in base_vals if not v.startswith(base_urn)][:3]
            citation_levels.append(CitationLevel(
                element="div",
                subtype=subtype,
                depth=depth,
                count=len(divs),
                with_n=with_n,
                with_base=with_base,
                with_id=with_id,
                base_correct=base_correct,
                base_wrong_examples=wrong,
            ))
        citation_levels.sort(key=lambda lv: lv.depth)

        # --- Milestones ---
        all_milestones = root.xpath("//tei:milestone", namespaces=NS)
        by_unit: dict[str, int] = defaultdict(int)
        for ms in all_milestones:
            unit = ms.get("unit", "")
            by_unit[unit] += 1
        milestones = [MilestoneInfo(unit=u, count=c) for u, c in sorted(by_unit.items())]

        # --- cRefPatterns ---
        cref_els = root.xpath("//tei:refsDecl/tei:cRefPattern", namespaces=NS)
        cref_patterns = [el.get("n", "") for el in cref_els]

        # --- Structural type ---
        has_divs = bool(citation_levels)
        has_milestones = bool(milestones)
        if has_divs and has_milestones:
            structural_type = "mixed"
        elif has_divs:
            structural_type = "div-based"
        elif has_milestones:
            structural_type = "milestone-based"
        else:
            structural_type = "unknown"

        # --- Rules ---
        rule_report = RuleAuditor(self._doc, _STRUCTURE_RULES).audit()
        issues = [f.message for f in rule_report.findings]

        # --- Proposed citeStructure ---
        proposed = _build_proposed_cite_structure(citation_levels)

        return StructureAuditReport(
            path=self._doc.path,
            base_urn=base_urn,
            structural_type=structural_type,
            citation_levels=citation_levels,
            milestones=milestones,
            cref_patterns=cref_patterns,
            issues=issues,
            proposed_cite_structure=proposed,
        )
