from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lxml import etree

_TEI_NS = "http://www.tei-c.org/ns/1.0"
_XML_NS = "http://www.w3.org/XML/1998/namespace"
_NS = {"tei": _TEI_NS, "xml": _XML_NS}
_FAMILY_IDS = {"drama", "verse", "prose"}


@dataclass(frozen=True)
class GenreTaxonomy:
    valid: frozenset[str]
    families: dict[str, str]  # leaf genre id -> family id

    def family(self, genre: str) -> str:
        try:
            return self.families[genre]
        except KeyError:
            raise ValueError(
                f"Unknown genre {genre!r}. Valid genres: {', '.join(sorted(self.valid))}"
            )


def load(odd_path: Path) -> GenreTaxonomy:
    """Parse the perseus-genre taxonomy from a TEI ODD file.

    Returns a GenreTaxonomy whose .valid is the frozenset of leaf genre ids
    and whose .families maps each leaf to its parent family (drama/verse/prose).
    """
    tree = etree.parse(str(odd_path))
    results = tree.xpath(
        "//tei:taxonomy[@xml:id='perseus-genre']",
        namespaces=_NS,
    )
    if not results:
        raise ValueError(f"No <taxonomy xml:id='perseus-genre'> found in {odd_path}")
    taxonomy = results[0]

    families: dict[str, str] = {}
    for family_cat in taxonomy.xpath("tei:category", namespaces=_NS):
        fid = family_cat.get(f"{{{_XML_NS}}}id")
        if fid not in _FAMILY_IDS:
            continue
        for leaf in family_cat.xpath(
            ".//tei:category[not(tei:category)]", namespaces=_NS
        ):
            lid = leaf.get(f"{{{_XML_NS}}}id")
            if lid:
                families[lid] = fid

    return GenreTaxonomy(valid=frozenset(families), families=families)
