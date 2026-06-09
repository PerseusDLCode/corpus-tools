from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lxml import etree

from pipeline import compute_cts_urn, read_existing_cts_urn

_CTS_NS = "http://chs.harvard.edu/xmlns/cts"
_CTS = {"ti": _CTS_NS}

FIELDNAMES = [
    "urn",
    "path",
    "author",
    "title",
    "suggested_genre",
    "confidence",
    "recommended_genre",
    "notes",
]


# ---------------------------------------------------------------------------
# Metadata readers
# ---------------------------------------------------------------------------

def _read_groupname(textgroup_cts: Path) -> str:
    try:
        names = etree.parse(str(textgroup_cts)).xpath("//ti:groupname", namespaces=_CTS)
        return names[0].text.strip() if names and names[0].text else ""
    except Exception:
        return ""


def _read_work_title(work_cts: Path) -> str:
    try:
        titles = etree.parse(str(work_cts)).xpath("//ti:title", namespaces=_CTS)
        return titles[0].text.strip() if titles and titles[0].text else ""
    except Exception:
        return ""


def _read_genre_annotation(work_cts: Path) -> tuple[str, str]:
    """Return (genre_id, confidence) from <ti:genre>, or ('', '') if absent."""
    try:
        genres = etree.parse(str(work_cts)).xpath("//ti:genre", namespaces=_CTS)
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
# Row generation
# ---------------------------------------------------------------------------

def generate_rows(data_dir: Path) -> list[dict]:
    rows: list[dict] = []

    for work_cts in sorted(data_dir.rglob("__cts__.xml")):
        if not _is_work_level(work_cts, data_dir):
            continue

        work_dir = work_cts.parent
        textgroup_cts = work_dir.parent / "__cts__.xml"

        author = _read_groupname(textgroup_cts)
        title = _read_work_title(work_cts)
        suggested_genre, confidence = _read_genre_annotation(work_cts)

        tei_files = sorted(f for f in work_dir.glob("*.xml") if f.name != "__cts__.xml")
        for tei_file in tei_files:
            rows.append({
                "urn": _get_urn(tei_file),
                "path": str(tei_file.relative_to(data_dir)),
                "author": author,
                "title": title,
                "suggested_genre": suggested_genre,
                "confidence": confidence,
                "recommended_genre": suggested_genre,
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
            "Generate a CSV of CTS texts with suggested genres for classicist review. "
            "Run annotate-genres first to populate <ti:genre> in __cts__.xml files."
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
    args = parser.parse_args()

    rows = generate_rows(args.data_dir)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output_csv}.", file=sys.stderr)


if __name__ == "__main__":
    main()
