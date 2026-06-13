from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from tei import NS, XML_NS
_FAMILY_IDS = {"drama", "verse", "prose"}

# Each family's default structural subclass. A document classified only by family
# (no subclass) is run with this subclass's citeStructure but flagged for review.
# Kept here rather than in the ODD (minimal scheme); validated against the ODD at load.
_FAMILY_DEFAULT = {
    "drama": "drama-line",
    "verse": "verse-stichic",
    "prose": "prose-standard",
}


@dataclass(frozen=True)
class GenreTaxonomy:
    """The perseus-genre structural-citation taxonomy.

    The classification has two tiers: a *family* (drama/verse/prose), which selects
    the schema, and a structural *subclass* (e.g. verse-book-line), which selects the
    CTS citeStructure. A bare family id is itself a legal catRef target meaning
    "family default applied, needs review".
    """

    families: frozenset[str]            # {drama, verse, prose}
    subclasses: frozenset[str]          # {prose-standard, verse-stichic, ...}
    subclass_family: dict[str, str]     # subclass id -> family id
    family_default: dict[str, str]      # family id -> default subclass id

    @property
    def valid(self) -> frozenset[str]:
        """All legal catRef targets: every subclass plus every (bare) family id."""
        return self.families | self.subclasses

    def family(self, target: str) -> str:
        """Return the family for a target that is either a subclass or a bare family id."""
        if target in self.families:
            return target
        try:
            return self.subclass_family[target]
        except KeyError:
            raise ValueError(
                f"Unknown genre target {target!r}. "
                f"Valid targets: {', '.join(sorted(self.valid))}"
            )

    def is_family(self, target: str) -> bool:
        """True if target is a bare family id (the needs-review / family-default case)."""
        return target in self.families

    def subclass_for(self, target: str) -> str:
        """Resolve a target to a concrete subclass.

        A subclass id returns itself; a bare family id returns that family's default
        subclass. Raises ValueError for unknown targets.
        """
        if target in self.subclasses:
            return target
        if target in self.families:
            return self.family_default[target]
        raise ValueError(
            f"Unknown genre target {target!r}. "
            f"Valid targets: {', '.join(sorted(self.valid))}"
        )


def load(odd_path: Path) -> GenreTaxonomy:
    """Parse the perseus-genre taxonomy from a TEI ODD file.

    The taxonomy is family categories (drama/verse/prose) each containing leaf
    structural-subclass categories. Returns a GenreTaxonomy mapping each subclass to
    its family. Raises ValueError if the taxonomy is missing or a family default
    subclass is absent.
    """
    tree = etree.parse(str(odd_path))
    results = tree.xpath(
        "//tei:taxonomy[@xml:id='perseus-genre']",
        namespaces=NS,
    )
    if not results:
        raise ValueError(f"No <taxonomy xml:id='perseus-genre'> found in {odd_path}")
    taxonomy = results[0]

    families: set[str] = set()
    subclass_family: dict[str, str] = {}
    for family_cat in taxonomy.xpath("tei:category", namespaces=NS):
        fid = family_cat.get(f"{{{XML_NS}}}id")
        if fid not in _FAMILY_IDS:
            continue
        families.add(fid)
        for leaf in family_cat.xpath(
            ".//tei:category[not(tei:category)]", namespaces=NS
        ):
            lid = leaf.get(f"{{{XML_NS}}}id")
            if lid:
                subclass_family[lid] = fid

    subclasses = frozenset(subclass_family)
    family_default = {f: _FAMILY_DEFAULT[f] for f in families if f in _FAMILY_DEFAULT}
    missing = {d for d in family_default.values() if d not in subclasses}
    if missing:
        raise ValueError(
            f"Family default subclass(es) absent from {odd_path}: {', '.join(sorted(missing))}"
        )

    return GenreTaxonomy(
        families=frozenset(families),
        subclasses=subclasses,
        subclass_family=subclass_family,
        family_default=family_default,
    )
