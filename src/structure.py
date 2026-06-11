"""Structural-citation matcher.

Reduces a document's citation structure to the citation *units* it uses, reading
both div encodings so it needs no separate Saxon canonicalization pass:

* EpiDoc:      ``<div type="textpart" subtype="Book">``  -> unit ``book``
* traditional: ``<div type="book">``                     -> unit ``book``

(``edition``/``translation`` wrappers are descended-through but never counted as
units, and units are lower-cased, mirroring ``normalize-cts.xsl``.) The same code
therefore works on raw EpiDoc source and on the canonicalized form the pipeline
produces.

``classify_structure`` distils a document into a ``StructureSignature``; ``matches``
checks whether a proposed structural subclass (from the perseus-genre taxonomy) is
consistent with that signature. A mismatch is the signal to flag the document for
review rather than trust the proposed citeStructure.
"""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

_TEI_NS = "http://www.tei-c.org/ns/1.0"
_NS = {"tei": _TEI_NS}
_DIV = f"{{{_TEI_NS}}}div"
_L = f"{{{_TEI_NS}}}l"

# div @type values that are structural wrappers, never citation units. The matcher
# descends through them but does not count them.
_NON_CITATION = frozenset({"edition", "translation", "textpart"})


def _unit(div: etree._Element) -> str | None:
    """The citation unit a <div> contributes, or None if it is a transparent wrapper.

    Reads EpiDoc ``type='textpart' subtype='X'`` and traditional ``type='X'``
    uniformly, lower-cased (so ``subtype='Book'`` and ``type='book'`` agree)."""
    t = div.get("type")
    if t == "textpart":
        st = div.get("subtype")
        return st.lower() if st else None
    if t and t not in _NON_CITATION:
        return t.lower()
    return None

# Sentinel for a citation unit realised by <l>, not by a <div type=...>.
LINE = "line"

# Expected unit hierarchy per structural subclass, outermost -> innermost. Every unit
# except the LINE sentinel is a <div type=...>; LINE (only ever terminal) means <l>.
HIERARCHY: dict[str, list[str]] = {
    "prose-standard": ["book", "chapter", "section"],
    "prose-chapter-section": ["chapter", "section"],
    "prose-book-section": ["book", "section"],
    "prose-book-chapter": ["book", "chapter"],
    "prose-chapter": ["chapter"],
    "prose-chapter-verse": ["chapter", "verse"],
    "prose-epistle": ["epistle"],
    "prose-fragment": ["fragment"],
    "prose-paragraph": ["paragraph"],
    "prose-section": ["section"],
    "verse-book-line": ["book", LINE],
    "verse-stichic": [LINE],
    "drama-line": [LINE],
    "drama-act-scene-line": ["act", "scene", LINE],
}


@dataclass(frozen=True)
class StructureSignature:
    """A document's citation structure, reduced to what the matcher needs."""

    div_types: frozenset[str]               # citation div @type values present under body
    contains: frozenset[tuple[str, str]]    # (ancestor_type, descendant_type) reachability among citation divs
    has_lines: bool                         # any <l> under body
    lines_under: frozenset[str]             # citation div @types that have an <l> descendant

    def describe(self) -> str:
        """Compact human-readable summary for the review CSV."""
        parts = sorted(self.div_types)
        if self.has_lines:
            parts.append("l")
        return "+".join(parts) if parts else "(none)"


def _body(root: etree._Element) -> etree._Element:
    bodies = root.xpath("//tei:body", namespaces=_NS)
    if bodies:
        return bodies[0]
    texts = root.xpath("//tei:text", namespaces=_NS)
    return texts[0] if texts else root


def classify_structure(root: etree._Element) -> StructureSignature:
    """Extract the citation-structure signature from a TEI tree (either encoding)."""
    body = _body(root)

    units = {d: u for d in body.iter(_DIV) if (u := _unit(d)) is not None}
    div_types = set(units.values())

    contains: set[tuple[str, str]] = set()
    lines_under: set[str] = set()
    for d, dt in units.items():
        for desc in d.iter(_DIV):
            if desc is d:
                continue
            du = units.get(desc)
            if du is not None:
                contains.add((dt, du))
        if d.find(f".//{_L}") is not None:
            lines_under.add(dt)

    has_lines = body.find(f".//{_L}") is not None
    return StructureSignature(
        div_types=frozenset(div_types),
        contains=frozenset(contains),
        has_lines=has_lines,
        lines_under=frozenset(lines_under),
    )


def matches(subclass: str, sig: StructureSignature) -> bool:
    """True if the document's structure is consistent with the proposed subclass.

    Criterion (subset/consistency, not strict equality): every div unit the subclass
    expects is present and nested in order, and the line requirement is met. Extra
    structure beyond what is expected does not fail the match; *missing* expected
    structure does — that mismatch is what flags a document for review.
    """
    try:
        expected = HIERARCHY[subclass]
    except KeyError:
        raise ValueError(
            f"Unknown structural subclass {subclass!r}. "
            f"Known: {', '.join(sorted(HIERARCHY))}"
        )

    div_units = [u for u in expected if u != LINE]
    expect_line = bool(expected) and expected[-1] == LINE

    # 1. every expected div unit is present
    if not all(u in sig.div_types for u in div_units):
        return False
    # 2. consecutive div units nest (ancestor -> descendant), tolerant of wrappers
    for ancestor, descendant in zip(div_units, div_units[1:]):
        if (ancestor, descendant) not in sig.contains:
            return False
    # 3. line requirement
    if expect_line:
        if div_units:
            if div_units[-1] not in sig.lines_under:
                return False
        elif not sig.has_lines:
            return False
    return True


def best_fit(candidates: list[str], sig: StructureSignature) -> str | None:
    """The most specific candidate subclass consistent with the signature, or None.

    Among candidates whose structure the document matches, returns the one with the
    deepest expected hierarchy (e.g. a book→chapter→section doc fits all prose
    subclasses but resolves to prose-standard; a section-only doc resolves to
    prose-section). Used to turn a family-level suggestion into the structural
    subclass the document actually warrants.
    """
    fitting = [c for c in candidates if matches(c, sig)]
    if not fitting:
        return None
    return max(fitting, key=lambda c: len(HIERARCHY[c]))


def signature_from_xml(xml: str) -> StructureSignature:
    """Parse a TEI document string and classify its structure."""
    return classify_structure(etree.fromstring(xml.encode("utf-8")))
