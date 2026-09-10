from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lxml import etree

from globe_lineation import ConversionError, rederive
from globe_anchor_intervals import compute_document_intervals, excess_histogram


def _write(tree: etree._ElementTree, output: Path) -> None:
    body = etree.tostring(tree, xml_declaration=False, encoding="UTF-8", pretty_print=False)
    output.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>' + body)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="rederive-globe-lineation",
        description=(
            "Re-derive a Shakespeare play's P5 Globe-edition body from its P4 "
            "Renaissance source, restoring the Globe/F1 <lb> milestones the "
            "2025 P4->P5 migration discarded (see doc/alignment-oracles.org)."
        ),
    )
    parser.add_argument("p4_source", type=Path, metavar="P4_XML")
    parser.add_argument("existing_p5", type=Path, metavar="P5_XML")
    parser.add_argument("-o", "--output", type=Path, metavar="PATH", help="Default: overwrite existing_p5 in place.")
    parser.add_argument(
        "--intervals-csv", type=Path, metavar="CSV",
        help="Write the per-scene anchor-interval closure audit to this CSV.",
    )
    args = parser.parse_args()

    try:
        tree, stats = rederive(args.p4_source, args.existing_p5)
    except ConversionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(stats.summary(), file=sys.stderr)
    if stats.l_stray_n_stripped:
        print("Stray <l @n> stripped (P4 encoding oddities, not carried into P5):", file=sys.stderr)
        for ctx, n, snippet in stats.l_stray_n_stripped:
            print(f"  {ctx}: n={n!r} ({snippet!r})", file=sys.stderr)
    if stats.sp_stray_n_stripped:
        print("Stray <sp @n> stripped (P4 encoding oddities, not carried into P5):", file=sys.stderr)
        for ctx, n, snippet in stats.sp_stray_n_stripped:
            print(f"  {ctx}: n={n!r} ({snippet!r})", file=sys.stderr)

    in_counts = {t: n for t, n in stats.element_counts_in.items()}
    out_counts = stats.element_counts_out
    print(f"Element tags in P4 input: {sorted(in_counts.items())}", file=sys.stderr)
    print(f"Element tags in P5 output: {sorted(out_counts.items())}", file=sys.stderr)

    output = args.output if args.output else args.existing_p5
    _write(tree, output)
    print(f"Wrote {output}", file=sys.stderr)

    intervals = compute_document_intervals(tree.getroot())
    non_closing = [iv for iv in intervals if not iv.closes]
    print(
        f"Anchor intervals: {len(intervals)} total, {len(non_closing)} non-closing "
        f"({len(intervals) - len(non_closing)} close exactly)",
        file=sys.stderr,
    )
    hist = excess_histogram(intervals)
    for excess, count in sorted(hist.items()):
        print(f"  excess {excess:+d}: {count}", file=sys.stderr)

    if args.intervals_csv:
        with args.intervals_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "act", "scene", "anchor_a", "anchor_b", "gap", "boundaries_between",
                "excess", "closes", "boundary_position", "boundary_n", "leads_into",
            ])
            for iv in intervals:
                if iv.closes:
                    writer.writerow([iv.act, iv.scene, iv.anchor_a, iv.anchor_b, iv.gap,
                                      iv.boundaries_between, iv.excess, "yes", "", "", ""])
                else:
                    for b in iv.boundaries:
                        writer.writerow([iv.act, iv.scene, iv.anchor_a, iv.anchor_b, iv.gap,
                                          iv.boundaries_between, iv.excess, "no",
                                          b.position, b.n or "", b.leads_into])
        print(f"Wrote {len(intervals)}-interval closure audit to {args.intervals_csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
