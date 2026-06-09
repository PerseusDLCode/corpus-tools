from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

from genres import load as load_genres

_CTS_NS = "http://chs.harvard.edu/xmlns/cts"
_CTS = {"ti": _CTS_NS}
_TEI_NS = "http://www.tei-c.org/ns/1.0"
_NS = {"tei": _TEI_NS}

_FAMILY_SCHEMA = {
    "prose": "perseus_prose.rng",
    "verse": "perseus_verse.rng",
    "drama": "perseus_drama.rng",
}

# Match jing error lines: path:line:col: (error|fatal): message
_JING_RE = re.compile(r'^.+?:(?:\d+:\d+: )?(error|fatal): (.+)$')

# Extract element or attribute name from message for aggregation
_SUBJECT_RE = re.compile(r'(?:element|attribute) "([^"]+)"')

# Trim verbose "expected ..." suffix so similar errors aggregate cleanly
_EXPECTED_RE = re.compile(r';? expected.*$', re.DOTALL)

# Batch size: maximum files per jing invocation (avoids ARG_MAX limits)
_BATCH_SIZE = 500


def _genre_from_tei(xml_path: Path) -> str:
    try:
        root = etree.parse(str(xml_path)).getroot()
        refs = root.xpath(
            "//tei:profileDesc/tei:textClass/tei:catRef[@scheme='#perseus-genre']/@target",
            namespaces=_NS,
        )
        return str(refs[0]).lstrip("#") if refs else ""
    except Exception:
        return ""


def _genre_from_cts(xml_path: Path) -> str:
    work_cts = xml_path.parent / "__cts__.xml"
    if not work_cts.exists():
        return ""
    try:
        genres = etree.parse(str(work_cts)).xpath("//ti:genre", namespaces=_CTS)
        if genres:
            return (genres[0].text or "").strip()
    except Exception:
        pass
    return ""


def _parse_genre_map(csv_path: Path) -> dict[str, str]:
    """Load stem→recommended_genre from a genres.csv-style file."""
    mapping: dict[str, str] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            genre = row.get("recommended_genre") or row.get("suggested_genre", "")
            path = row.get("path", "")
            if path and genre:
                mapping[Path(path).stem] = genre
    return mapping


def _validate_batch(rng_path: Path, xml_files: list[Path]) -> list[str]:
    """Run jing on a batch of files; return stdout lines."""
    result = subprocess.run(
        ["jing", str(rng_path)] + [str(f) for f in xml_files],
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines() if result.stdout else []


def _parse_jing_line(line: str) -> tuple[str, str, str] | None:
    """Return (file_stem, subject, normalized_message) or None if unrecognised."""
    m = _JING_RE.match(line)
    if not m:
        return None
    msg = m.group(2)
    sm = _SUBJECT_RE.search(msg)
    subject = sm.group(1) if sm else ""
    normalized = _EXPECTED_RE.sub("", msg).strip()
    # Extract file stem from the path prefix
    colon_idx = line.index(":")
    file_stem = Path(line[:colon_idx]).stem
    return file_stem, subject, normalized


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="validate-corpus",
        description=(
            "Validate corpus TEI files against their target Perseus RELAX NG schema "
            "(determined by genre) using jing. Writes rng_errors.csv to --output-dir."
        ),
    )
    parser.add_argument("data_dir", type=Path, metavar="DATA_DIR",
                        help="Root data directory (e.g. canonical-greekLit/data).")
    parser.add_argument(
        "--schema-dir", type=Path, default=Path("../perseus-schemas"), metavar="DIR",
        help="Directory containing compiled .rng files (default: ../perseus-schemas).",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("survey"), metavar="DIR")
    parser.add_argument(
        "--genre-map", type=Path, metavar="CSV",
        help="genres.csv mapping file stem → recommended_genre (fallback when no catRef or __cts__.xml genre).",
    )
    parser.add_argument(
        "--odd", type=Path, default=Path("../perseus-schemas/perseus_base.odd"), metavar="ODD",
        help="ODD file for genre taxonomy (default: ../perseus-schemas/perseus_base.odd).",
    )
    args = parser.parse_args()

    # Verify jing is available
    if subprocess.run(["which", "jing"], capture_output=True).returncode != 0:
        print("ERROR: jing not found. Install: brew install jing-trang", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    taxonomy = load_genres(args.odd)
    genre_map = _parse_genre_map(args.genre_map) if args.genre_map else {}

    tei_files = sorted(f for f in args.data_dir.rglob("*.xml") if f.name != "__cts__.xml")
    total = len(tei_files)
    print(f"Determining schemas for {total} files...", file=sys.stderr)

    # Group files by schema family
    by_family: dict[str, list[Path]] = defaultdict(list)
    skipped: list[Path] = []

    for xml_path in tei_files:
        genre = (
            _genre_from_tei(xml_path)
            or _genre_from_cts(xml_path)
            or genre_map.get(xml_path.stem, "")
        )
        if not genre or genre == "unknown":
            skipped.append(xml_path)
            continue
        try:
            family = taxonomy.family(genre)
        except ValueError:
            skipped.append(xml_path)
            continue
        by_family[family].append(xml_path)

    if skipped:
        print(f"  {len(skipped)} files skipped (no determinable genre)", file=sys.stderr)

    # Aggregate: (genre, subject, normalized_message) → {instance_count, file_count}
    error_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    error_files: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    for family, files in sorted(by_family.items()):
        schema_name = _FAMILY_SCHEMA[family]
        rng_path = args.schema_dir / schema_name
        if not rng_path.exists():
            print(f"WARNING: schema not found: {rng_path}", file=sys.stderr)
            continue

        print(f"Validating {len(files)} {family} files against {schema_name}...", file=sys.stderr)

        for batch_start in range(0, len(files), _BATCH_SIZE):
            batch = files[batch_start : batch_start + _BATCH_SIZE]
            lines = _validate_batch(rng_path, batch)
            for line in lines:
                parsed = _parse_jing_line(line)
                if parsed is None:
                    continue
                file_stem, subject, normalized = parsed
                # Recover genre from file stem via the file list
                key: tuple[str, str, str] = (family, subject, normalized)
                error_counts[key] += 1
                error_files[key].add(file_stem)

    # Write rng_errors.csv
    out_path = args.output_dir / "rng_errors.csv"
    rows = [
        {
            "family": k[0],
            "element": k[1],
            "message": k[2],
            "instance_count": error_counts[k],
            "file_count": len(error_files[k]),
        }
        for k in error_counts
    ]
    rows.sort(key=lambda r: (-r["instance_count"], r["family"], r["element"]))

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["family", "element", "message", "instance_count", "file_count"])
        writer.writeheader()
        writer.writerows(rows)

    validated = sum(len(v) for v in by_family.values())
    print(f"Wrote {out_path} ({len(rows)} distinct error types)", file=sys.stderr)
    print(
        f"\nDone. {validated} validated, {len(skipped)} skipped. Total: {total}.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
