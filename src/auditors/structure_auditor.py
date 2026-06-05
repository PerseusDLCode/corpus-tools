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

class StructureAuditor(Auditor[StructureAuditReport]):

    def audit(self) -> StructureAuditReport:
        root = self._doc.root
        base_urn = self._doc.extract_base_urn()
        cref_patterns = self._doc.parse_cref_patterns()
        structural_type = self._classify_structure(root)
        citation_levels = self._get_citation_levels(root, base_urn)

        ms_map: dict[str, int] = {}
        for m in root.xpath("//tei:milestone[@unit]", namespaces=NS):
            u = m.get("unit", "?")
            ms_map[u] = ms_map.get(u, 0) + 1
        milestones = [MilestoneInfo(u, c) for u, c in sorted(ms_map.items())]

        issues: list[str] = []
        if not base_urn:
            issues.append("CRITICAL: no CTS URN found on edition div @n")
        for lv in citation_levels:
            if lv.with_n < lv.count:
                issues.append(
                    f"WARNING: {lv.count - lv.with_n} "
                    f"<{lv.element} subtype='{lv.subtype}'> elements missing @n"
                )
            if lv.with_base == 0 and lv.count > 0:
                issues.append(
                    f"INFO: <{lv.element} subtype='{lv.subtype}'> "
                    f"has no xml:base attributes ({lv.count} elements)"
                )
            elif lv.base_correct < lv.with_base:
                wrong = lv.with_base - lv.base_correct
                issues.append(
                    f"FIX NEEDED: {wrong} <{lv.element} subtype='{lv.subtype}'> "
                    f"have incorrect xml:base"
                )

        proposed = self._propose_cite_structure(
            citation_levels, cref_patterns, structural_type
        )

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

    def _classify_structure(self, root: etree._Element) -> str:
        ms_units: dict[str, int] = {}
        for m in root.xpath("//tei:milestone[@unit]", namespaces=NS):
            u = m.get("unit", "")
            ms_units[u] = ms_units.get(u, 0) + 1

        textpart_divs = root.xpath("//tei:div[@type='textpart']", namespaces=NS)
        leaf_lines = root.xpath("//tei:l", namespaces=NS)

        if "section" in ms_units and textpart_divs:
            return "milestone-sections"
        if "card" in ms_units:
            return "milestone-cards"
        if textpart_divs:
            return "div-hierarchy"
        if leaf_lines:
            return "flat-lines"
        return "unknown"

    def _get_citation_levels(
        self, root: etree._Element, base_urn: str
    ) -> list[CitationLevel]:
        levels: list[CitationLevel] = []

        edition_div = root.xpath("//tei:div[@type='edition']", namespaces=NS)
        if not edition_div:
            return levels
        ed = edition_div[0]

        depth_map: dict[tuple[str, int], list[etree._Element]] = {}
        for div in ed.xpath(".//tei:div[@type='textpart']", namespaces=NS):
            subtype = div.get("subtype", "")
            depth = 0
            parent = div.getparent()
            while parent is not None and parent != ed:
                if parent.get("type") == "textpart":
                    depth += 1
                parent = parent.getparent()
            key = (subtype, depth)
            depth_map.setdefault(key, []).append(div)

        for (subtype, depth), divs in sorted(depth_map.items(), key=lambda x: x[0][1]):
            with_n, with_base, with_id, correct, wrong_examples = self._summarize_elements(
                divs, base_urn, expected_div_base
            )
            levels.append(CitationLevel(
                element="div",
                subtype=subtype,
                depth=depth,
                count=len(divs),
                with_n=with_n,
                with_base=with_base,
                with_id=with_id,
                base_correct=correct,
                base_wrong_examples=wrong_examples,
            ))

        for tag in ("l", "p", "ab", "seg"):
            elems = ed.xpath(f".//tei:{tag}", namespaces=NS)
            if not elems:
                continue
            with_n, with_base, with_id, correct, wrong_examples = self._summarize_elements(
                elems, base_urn, expected_leaf_base, require_n=True
            )
            sample = elems[0]
            depth = 0
            parent = sample.getparent()
            while parent is not None and parent != ed:
                if parent.get("type") == "textpart":
                    depth += 1
                parent = parent.getparent()
            levels.append(CitationLevel(
                element=tag,
                subtype="",
                depth=depth + 1,
                count=len(elems),
                with_n=with_n,
                with_base=with_base,
                with_id=with_id,
                base_correct=correct,
                base_wrong_examples=wrong_examples,
            ))

        return levels

    def _check_base_correctness(
        self,
        elements: list[etree._Element],
        base_urn: str,
        expected_fn,
        require_n: bool = False,
    ) -> tuple[int, int, list[tuple[str, str]]]:
        correct = wrong = 0
        wrong_examples: list[tuple[str, str]] = []
        for elem in elements:
            if require_n and not elem.get("n"):
                continue
            expected = expected_fn(elem, base_urn)
            actual = elem.get(XML_BASE, "MISSING")
            if actual == expected:
                correct += 1
            else:
                wrong += 1
                if len(wrong_examples) < 3:
                    wrong_examples.append((str(expected), actual))
        return correct, wrong, wrong_examples

    def _summarize_elements(
        self,
        elements: list[etree._Element],
        base_urn: str,
        expected_fn,
        require_n: bool = False,
    ) -> tuple[int, int, int, int, list[tuple[str, str]]]:
        with_n = sum(1 for e in elements if e.get("n"))
        with_base = sum(1 for e in elements if e.get(XML_BASE))
        with_id = sum(1 for e in elements if e.get(XML_ID))
        correct, _, wrong_examples = self._check_base_correctness(
            elements, base_urn, expected_fn, require_n=require_n
        )
        return with_n, with_base, with_id, correct, wrong_examples

    def _propose_cite_structure(
        self,
        citation_levels: list[CitationLevel],
        cref_patterns: list[str],
        structural_type: str,
    ) -> str:
        level_names = list(reversed(cref_patterns)) if cref_patterns else [
            lv.subtype or lv.element
            for lv in sorted(citation_levels, key=lambda x: x.depth)
        ]

        if not level_names:
            return "<!-- citeStructure: insufficient information to propose -->"

        def _element_for_level(name: str) -> str:
            if name in ("book", "chapter", "section", "poem", "act", "scene"):
                return "div"
            if name in ("line", "l"):
                return "l"
            if name in ("paragraph", "p"):
                return "p"
            return "div"

        def _wrap(name: str, inner: str) -> str:
            unit = name
            xpath = f"tei:{_element_for_level(name)}[@n]"
            if inner:
                return (
                    f'<citeStructure unit="{unit}" match="{xpath}" use="@n" delim=".">\n'
                    f"  {inner}\n"
                    f"</citeStructure>"
                )
            return f'<citeStructure unit="{unit}" match="{xpath}" use="@n"/>'

        result = ""
        for name in reversed(level_names):
            result = _wrap(name, result)

        lines = result.splitlines()
        indented = "\n".join("        " + ln for ln in lines)
        return (
            "<!-- Proposed citeStructure (verify before inserting into TEIHeader) -->\n"
            "      <citeStructure>\n"
            f"{indented}\n"
            "      </citeStructure>"
        )

