from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from schmidt_cit_merge import merge_orphaned_citations


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="merge-schmidt-orphaned-citations",
        description=(
            "Absorb bare <ref> citations trailing a <cit> into that <cit>, up to the "
            "next <cit>, </entryFree>, or <lb/> -- an automatic-tagging artifact where "
            "<cit> only ever captured the first citation after a <quote>, leaving every "
            "further citation for that quote as an orphaned sibling. Partial merge: stops "
            "at the first gap that isn't pure separator punctuation or a recognized "
            "apparatus pattern, rather than guessing."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    parser.add_argument(
        "--report", type=Path, metavar="CSV",
        help="Write every unrecognized (stopping) gap, with its frequency, to a CSV.",
    )
    args = parser.parse_args()

    original_text = args.lexicon_file.read_text(encoding="utf-8")
    new_text, stats = merge_orphaned_citations(original_text)

    if args.report:
        with args.report.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["gap_text", "count"])
            for gap_text, count in stats.residual_gaps.most_common():
                writer.writerow([gap_text, count])
        print(f"Wrote {len(stats.residual_gaps)}-row residual-gap report to {args.report}", file=sys.stderr)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(
        f"Wrote {output} ({stats.cits_merged} <cit> elements merged -- "
        f"{stats.full_merges} full, {stats.partial_merges} partial -- "
        f"{stats.refs_absorbed} orphaned refs absorbed, {stats.notes_wrapped} "
        f"wrapped in <note>, {len(stats.residual_gaps)} distinct residual gap "
        f"shapes left unmerged)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
