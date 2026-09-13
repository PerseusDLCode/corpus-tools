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
    if stats.recovered_transcribed_anchors:
        print(
            f"Recovered transcribed anchors (stray <l @n> restored as Globe milestones -- "
            f"insertions): {len(stats.recovered_transcribed_anchors)}",
            file=sys.stderr,
        )
        for ctx, n in stats.recovered_transcribed_anchors:
            print(f"  {ctx}: n={n!r}", file=sys.stderr)
    if stats.split_line_boundaries_deleted:
        print(
            f"Shared verse-line split boundaries deleted (spurious duplicate removed): "
            f"{len(stats.split_line_boundaries_deleted)}",
            file=sys.stderr,
        )
        for i_snip, f_snip in stats.split_line_boundaries_deleted:
            print(f"  {i_snip!r} / {f_snip!r}", file=sys.stderr)
    if stats.split_line_pairs_already_clean:
        print(
            f"Shared verse-line pairs already clean (no boundary to delete): "
            f"{len(stats.split_line_pairs_already_clean)}",
            file=sys.stderr,
        )
    if stats.unpaired_part_markers:
        print(
            f"Unpaired/asymmetric @part markers left unresolved, flagged for the "
            f"alignment-oracle task: {len(stats.unpaired_part_markers)}",
            file=sys.stderr,
        )
        for snip, part in stats.unpaired_part_markers:
            print(f"  part={part!r}: {snip!r}", file=sys.stderr)

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

    flagged_count = sum(1 for iv in intervals if not iv.closes and iv.has_flagged_boundary)
    if flagged_count:
        print(
            f"  of which {flagged_count} non-closing interval(s) contain an "
            "unpaired/asymmetric @part boundary (flagged for the oracle, not guessed at here)",
            file=sys.stderr,
        )

    if args.intervals_csv:
        with args.intervals_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "act", "scene", "anchor_a", "anchor_b", "gap", "boundaries_between",
                "excess", "closes", "interval_flagged",
                "boundary_position", "boundary_n", "leads_into", "boundary_flagged",
            ])
            for iv in intervals:
                interval_flagged = "yes" if iv.has_flagged_boundary else "no"
                if iv.closes:
                    writer.writerow([iv.act, iv.scene, iv.anchor_a, iv.anchor_b, iv.gap,
                                      iv.boundaries_between, iv.excess, "yes", interval_flagged,
                                      "", "", "", ""])
                else:
                    for b in iv.boundaries:
                        writer.writerow([iv.act, iv.scene, iv.anchor_a, iv.anchor_b, iv.gap,
                                          iv.boundaries_between, iv.excess, "no", interval_flagged,
                                          b.position, b.n or "", b.leads_into,
                                          "yes" if b.flagged else "no"])
        print(f"Wrote {len(intervals)}-interval closure audit to {args.intervals_csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
