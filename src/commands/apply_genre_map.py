from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from genres import load as load_genres
from transformer import transform


def apply_genre_to_file(tei_path: Path, genre: str, cert: str = "") -> None:
    xml = transform(tei_path, "set-genre.xsl", target=genre, cert=cert)
    tei_path.write_text(xml, encoding="utf-8")


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="apply-genre-map",
        description=(
            "Apply reviewed genre assignments from a CSV to TEI files in-place. "
            "All genres are validated before any file is touched. "
            "Run on a working branch so changes can be rolled back."
        ),
    )
    parser.add_argument(
        "csv_file", type=Path, metavar="CSV_FILE",
        help="Genre map CSV produced by generate-genre-map and reviewed by classicists.",
    )
    parser.add_argument(
        "data_dir", type=Path, metavar="DATA_DIR",
        help="Root data directory (e.g. canonical-greekLit/data).",
    )
    parser.add_argument(
        "--odd", required=True, type=Path, metavar="ODD",
        help="Path to perseus_base.odd (authoritative genre taxonomy).",
    )
    args = parser.parse_args()

    taxonomy = load_genres(args.odd)

    with args.csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Pre-validation: collect ALL invalid genres before touching any file.
    invalid: list[tuple[str, str]] = []
    for row in rows:
        genre = row.get("recommended_genre", "").strip()
        if genre and genre not in taxonomy.valid:
            invalid.append((row.get("path", "?"), genre))

    if invalid:
        print("ERROR: Invalid genre values — no files were modified.", file=sys.stderr)
        for path, genre in invalid:
            print(f"  {path}: {genre!r}", file=sys.stderr)
        print(f"\nValid genres: {', '.join(sorted(taxonomy.valid))}", file=sys.stderr)
        sys.exit(1)

    applied = skipped = errors = 0

    for row in rows:
        genre = row.get("recommended_genre", "").strip()
        if not genre:
            skipped += 1
            continue

        tei_path = args.data_dir / row["path"]
        if not tei_path.exists():
            print(f"ERROR: {tei_path}: file not found", file=sys.stderr)
            errors += 1
            continue

        # Flag needs-review classifications: a bare family target (family default
        # applied) or a row the verification step marked for review.
        cert = "low" if (taxonomy.is_family(genre) or _truthy(row.get("needs_review", ""))) else ""

        try:
            apply_genre_to_file(tei_path, genre, cert)
            suffix = "  [needs review]" if cert else ""
            print(f"{row['path']} → {genre}{suffix}")
            applied += 1
        except Exception as exc:
            print(f"ERROR: {tei_path}: {exc}", file=sys.stderr)
            errors += 1

    print(
        f"\nDone. {applied} applied, {skipped} skipped (blank), {errors} errors.",
        file=sys.stderr,
    )
    sys.exit(errors)


if __name__ == "__main__":
    main()
