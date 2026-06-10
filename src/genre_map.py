"""Map the LLM's prior literary-genre suggestions to proposed structural subclasses.

The corpus was annotated under the old literary taxonomy (``verse-epic``,
``attic-tragedy``, ``prose-historiography``, …). The structural scheme keeps those
``<ti:genre>`` values as the *suggestion*; this module maps each to a *proposed*
structural subclass, which is then verified against the document's actual citation
structure (see ``structure.py``). The mapping is intentionally lossy — all non-epic
verse collapses to ``verse-stichic`` — so genuine mismatches surface for review.
"""

from __future__ import annotations

from genres import GenreTaxonomy

# Old literary genre id -> proposed structural subclass id.
LITERARY_TO_STRUCTURAL: dict[str, str] = {
    # drama
    "attic-tragedy": "drama-line",
    "attic-comedy": "drama-line",
    "roman-comedy": "drama-line",
    "roman-tragedy": "drama-line",
    "early-modern-drama": "drama-act-scene-line",
    # verse
    "verse-epic": "verse-book-line",
    "verse-didactic": "verse-stichic",
    "verse-elegiac": "verse-stichic",
    "verse-lyric-choral": "verse-stichic",
    "verse-lyric-pindaric": "verse-stichic",
    "verse-lyric-monodic": "verse-stichic",
    "verse-satiric": "verse-stichic",
    "verse-epigram": "verse-stichic",
    "verse-iambic": "verse-stichic",
    # prose
    "prose-historiography": "prose-standard",
    "prose-philosophy": "prose-standard",
    "prose-dialogue": "prose-standard",
    "prose-oratory": "prose-standard",
    "prose-biography": "prose-standard",
    "prose-epistolary": "prose-standard",
    "prose-geography": "prose-standard",
}


def propose_subclass(value: str, taxonomy: GenreTaxonomy) -> str:
    """Resolve an existing ``<ti:genre>`` value to a proposed structural subclass.

    Accepts an old literary id (mapped), an already-structural subclass id
    (passed through), or a bare family id (resolved to the family default).
    Returns "" for unknown or empty values.

    This is the family-level default; ``generate_genre_map`` refines it to the
    structural subclass the document's markup actually warrants (see
    ``structure.best_fit``).
    """
    value = (value or "").strip()
    if not value or value == "unknown":
        return ""
    if value in taxonomy.subclasses:
        return value
    if value in taxonomy.families:
        return taxonomy.family_default[value]
    return LITERARY_TO_STRUCTURAL.get(value, "")


def family_of(value: str, taxonomy: GenreTaxonomy) -> str:
    """The family (drama/verse/prose) implied by a ``<ti:genre>`` value, or "".

    The literary suggestion is reliable at the family level; the structural subclass
    is then chosen from the document's markup, not from the (contested) literary label.
    """
    proposed = propose_subclass(value, taxonomy)
    return taxonomy.family(proposed) if proposed else ""
