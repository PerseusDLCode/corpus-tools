from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

from auditors import StructureAuditor
from tei import TEIDocument, NS, CTS_NS

# Attribute names (namespace-stripped) whose value vocabulary is worth capturing.
_VALUE_ATTRS = {
    "type", "subtype", "unit", "met", "rend", "place",
    "role", "ident", "ed", "lang",
}

# Maximum distinct values to record per (element, attribute, genre) triple.
_MAX_VALUES = 30


def _genre_from_tei(root: etree._Element) -> str:
    refs = root.xpath(
        "//tei:profileDesc/tei:textClass/tei:catRef[@scheme='#perseus-genre']/@target",
        namespaces=NS,
    )
    return str(refs[0]).lstrip("#") if refs else ""


def _genre_from_cts(xml_path: Path) -> str:
    work_cts = xml_path.parent / "__cts__.xml"
    if not work_cts.exists():
        return ""
    try:
        genres = etree.parse(str(work_cts)).xpath("//ti:genre", namespaces={"ti": CTS_NS})
        if genres:
            return (genres[0].text or "").strip()
    except Exception:
        pass
    return ""


def survey_file(
    xml_path: Path,
    element_counts: dict[tuple[str, str], int],
    file_sets: dict[tuple[str, str], set[Path]],
    attr_values: dict[tuple[str, str, str, str], int],
    structure_rows: list[dict],
) -> None:
    try:
        doc = TEIDocument(xml_path)
    except Exception as exc:
        print(f"WARNING: cannot parse {xml_path.name}: {exc}", file=sys.stderr)
        return

    root = doc.root
    genre = _genre_from_tei(root) or _genre_from_cts(xml_path) or "unknown"

    for el in root.iter():
        tag = el.tag
        if not isinstance(tag, str):
            continue
        localname = tag.split("}", 1)[1] if "{" in tag else tag
        key: tuple[str, str] = (localname, genre)
        element_counts[key] = element_counts.get(key, 0) + 1
        file_sets.setdefault(key, set()).add(xml_path)

        for attr_name, attr_val in el.attrib.items():
            attr_local = attr_name.split("}", 1)[1] if "{" in attr_name else attr_name
            if attr_local in _VALUE_ATTRS:
                vkey: tuple[str, str, str, str] = (localname, attr_local, genre, str(attr_val)[:200])
                attr_values[vkey] = attr_values.get(vkey, 0) + 1

    try:
        report = StructureAuditor(doc).audit()
        structure_rows.append({
            "urn": doc.base_urn or xml_path.stem,
            "path": str(xml_path),
            "genre": genre,
            "structural_type": report.structural_type,
            "div_subtypes": "|".join(lv.subtype for lv in report.citation_levels),
            "milestone_units": "|".join(ms.unit for ms in report.milestones),
            "issues": "; ".join(report.issues),
        })
    except Exception:
        pass


def write_elements_csv(
    path: Path,
    element_counts: dict[tuple[str, str], int],
    file_sets: dict[tuple[str, str], set[Path]],
) -> int:
    rows = [
        {
            "element": k[0],
            "genre": k[1],
            "file_count": len(file_sets.get(k, set())),
            "instance_count": v,
        }
        for k, v in element_counts.items()
    ]
    rows.sort(key=lambda r: (-r["instance_count"], r["element"]))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["element", "genre", "file_count", "instance_count"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_attributes_csv(
    path: Path,
    attr_values: dict[tuple[str, str, str, str], int],
) -> int:
    grouped: dict[tuple[str, str, str], list[tuple[int, str]]] = defaultdict(list)
    for (localname, attr, genre, val), count in attr_values.items():
        grouped[(localname, attr, genre)].append((count, val))

    rows = []
    for (localname, attr, genre), value_counts in sorted(grouped.items()):
        for count, val in sorted(value_counts, reverse=True)[:_MAX_VALUES]:
            rows.append({
                "element": localname,
                "attribute": attr,
                "genre": genre,
                "value": val,
                "count": count,
            })
    rows.sort(key=lambda r: (-r["count"], r["element"], r["attribute"]))

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["element", "attribute", "genre", "value", "count"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_structure_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = ["urn", "path", "genre", "structural_type", "div_subtypes", "milestone_units", "issues"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="survey-corpus",
        description=(
            "Analyse element/attribute vocabulary and citation structure across "
            "the corpus. Outputs elements.csv, attributes.csv, and structure.csv "
            "to --output-dir."
        ),
    )
    parser.add_argument("data_dir", type=Path, metavar="DATA_DIR",
                        help="Root data directory (e.g. canonical-greekLit/data).")
    parser.add_argument("--output-dir", type=Path, default=Path("survey"), metavar="DIR")
    parser.add_argument("--genre", metavar="GENRE",
                        help="Restrict output to a single genre leaf (applied post-scan).")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    element_counts: dict[tuple[str, str], int] = {}
    file_sets: dict[tuple[str, str], set[Path]] = {}
    attr_values: dict[tuple[str, str, str, str], int] = {}
    structure_rows: list[dict] = []

    tei_files = sorted(f for f in args.data_dir.rglob("*.xml") if f.name != "__cts__.xml")
    total = len(tei_files)
    print(f"Scanning {total} files...", file=sys.stderr)

    for i, xml_path in enumerate(tei_files, 1):
        if i % 50 == 0 or i == total:
            print(f"  {i}/{total}", file=sys.stderr)
        survey_file(xml_path, element_counts, file_sets, attr_values, structure_rows)

    if args.genre:
        element_counts = {k: v for k, v in element_counts.items() if k[1] == args.genre}
        file_sets = {k: v for k, v in file_sets.items() if k[1] == args.genre}
        attr_values = {k: v for k, v in attr_values.items() if k[2] == args.genre}
        structure_rows = [r for r in structure_rows if r["genre"] == args.genre]

    n = write_elements_csv(args.output_dir / "elements.csv", element_counts, file_sets)
    print(f"Wrote elements.csv ({n} rows)", file=sys.stderr)

    n = write_attributes_csv(args.output_dir / "attributes.csv", attr_values)
    print(f"Wrote attributes.csv ({n} rows)", file=sys.stderr)

    write_structure_csv(args.output_dir / "structure.csv", structure_rows)
    print(f"Wrote structure.csv ({len(structure_rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
