from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lxml import etree

from genres import load as load_genres
from genre_map import family_of
from pipeline import compute_cts_urn, read_existing_cts_urn
from structure import best_fit, classify_structure
from tei import CTS_NS

FIELDNAMES = [
    "urn",
    "path",
    "author",
    "title",
    "suggested_genre",      # the LLM's prior literary suggestion (provenance)
    "confidence",           # the LLM's confidence
    "family",               # prose/verse/drama, from the proposed subclass
    "proposed_subclass",    # literary suggestion mapped to a structural subclass
    "structure_signature",  # the document's actual citation structure
    "match",                # ready | review | "" (no suggestion)
    "needs_review",         # true | false
    "recommended_genre",    # human-overridable; pre-filled with proposed_subclass
    "notes",
]


# ---------------------------------------------------------------------------
# Metadata readers
# ---------------------------------------------------------------------------

def _read_groupname(textgroup_cts: Path) -> str:
    try:
        names = etree.parse(str(textgroup_cts)).xpath("//ti:groupname", namespaces={"ti": CTS_NS})
        return names[0].text.strip() if names and names[0].text else ""
    except Exception:
        return ""


def _read_work_title(work_cts: Path) -> str:
    try:
        titles = etree.parse(str(work_cts)).xpath("//ti:title", namespaces={"ti": CTS_NS})
        return titles[0].text.strip() if titles and titles[0].text else ""
    except Exception:
        return ""


def _read_genre_annotation(work_cts: Path) -> tuple[str, str]:
    """Return (genre_id, confidence) from <ti:genre>, or ('', '') if absent."""
    try:
        genres = etree.parse(str(work_cts)).xpath("//ti:genre", namespaces={"ti": CTS_NS})
        if genres:
            return genres[0].text or "", genres[0].get("confidence", "")
        return "", ""
    except Exception:
        return "", ""


def _get_urn(tei_file: Path) -> str:
    """Return URN from body/@xml:base, falling back to path-derived URN."""
    return read_existing_cts_urn(tei_file) or compute_cts_urn(tei_file) or tei_file.stem


def _is_work_level(path: Path, data_dir: Path) -> bool:
    try:
        return len(path.relative_to(data_dir).parts) == 3
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Verification (suggest -> verify): does the doc's structure match the proposal?
# ---------------------------------------------------------------------------

def verify_structure(tei_file: Path, family: str, taxonomy) -> tuple[str, str, str]:
    """Choose a structural subclass from the document's markup and verify it.

    Given the family implied by the prior suggestion, pick the most specific subclass
    in that family the document's structure supports (structure.best_fit). Returns
    (structure_signature, proposed_subclass, match):

    * a fitting subclass -> ("...", subclass, "ready")
    * family known but nothing fits -> ("...", family default, "review")
    * no family / parse error -> ("...", "", "review"/"" )
    """
    try:
        root = etree.parse(str(tei_file)).getroot()
        sig = classify_structure(root)
    except Exception:
        return "(parse-error)", (taxonomy.family_default.get(family, "") if family else ""), "review"

    signature = sig.describe()
    if not family:
        return signature, "", ""

    candidates = [s for s in taxonomy.subclasses if taxonomy.subclass_family[s] == family]
    best = best_fit(candidates, sig)
    if best:
        return signature, best, "ready"
    return signature, taxonomy.family_default[family], "review"


# ---------------------------------------------------------------------------
# Row generation
# ---------------------------------------------------------------------------

def generate_rows(data_dir: Path, taxonomy) -> list[dict]:
    rows: list[dict] = []

    for work_cts in sorted(data_dir.rglob("__cts__.xml")):
        if not _is_work_level(work_cts, data_dir):
            continue

        work_dir = work_cts.parent
        textgroup_cts = work_dir.parent / "__cts__.xml"

        author = _read_groupname(textgroup_cts)
        title = _read_work_title(work_cts)
        suggested_genre, confidence = _read_genre_annotation(work_cts)
        family = family_of(suggested_genre, taxonomy)

        tei_files = sorted(f for f in work_dir.glob("*.xml") if f.name != "__cts__.xml")
        for tei_file in tei_files:
            signature, proposed, match = verify_structure(tei_file, family, taxonomy)
            needs_review = match != "ready"
            rows.append({
                "urn": _get_urn(tei_file),
                "path": str(tei_file.relative_to(data_dir)),
                "author": author,
                "title": title,
                "suggested_genre": suggested_genre,
                "confidence": confidence,
                "family": family,
                "proposed_subclass": proposed,
                "structure_signature": signature,
                "match": match,
                "needs_review": "true" if needs_review else "false",
                "recommended_genre": proposed,
                "notes": "",
            })

    return rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="generate-genre-map",
        description=(
            "Generate a CSV of CTS texts mapping each prior <ti:genre> suggestion to a "
            "proposed structural subclass, and verifying it against the document's "
            "actual citation structure (ready vs. review). Review rows are the worklist "
            "for new subclasses. Run annotate-genres first to populate <ti:genre>."
        ),
    )
    parser.add_argument(
        "data_dir", type=Path, metavar="DATA_DIR",
        help="Root data directory (e.g. canonical-greekLit/data).",
    )
    parser.add_argument(
        "output_csv", type=Path, metavar="OUTPUT_CSV",
        help="Path for the output CSV file.",
    )
    parser.add_argument(
        "--odd", required=True, type=Path, metavar="ODD",
        help="Path to perseus_base.odd (authoritative genre taxonomy).",
    )
    args = parser.parse_args()

    taxonomy = load_genres(args.odd)
    rows = generate_rows(args.data_dir, taxonomy)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    ready = sum(1 for r in rows if r["match"] == "ready")
    review = sum(1 for r in rows if r["needs_review"] == "true")
    print(
        f"Wrote {len(rows)} rows to {args.output_csv} "
        f"({ready} ready, {review} need review).",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
