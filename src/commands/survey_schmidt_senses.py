from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from schmidt_sense_survey import survey, summarize


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="survey-schmidt-senses",
        description=(
            "Classify every <entryFree> in the Schmidt lexicon by how reliably its "
            "dictionary senses are signalled by Schmidt's own inline numbering "
            "convention (1)/2)/a)/b)/I)/II)) and by <lb/>, ahead of any future "
            "<sense>-reconstruction work. Read-only: does not modify the lexicon."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "--report", type=Path, metavar="CSV",
        help="Write every classified entry (orth, bucket, lb count, markers) to a CSV.",
    )
    args = parser.parse_args()

    text = args.lexicon_file.read_text(encoding="utf-8")
    entries = survey(text)
    stats = summarize(entries)

    if args.report:
        with args.report.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["orth", "bucket", "lb_count", "marker_count", "markers"])
            for entry in entries:
                marker_repr = ";".join(
                    f"{m.token}{m.level[0]}{'*' if m.entry_start else ('+' if m.lb_aligned else '-')}"
                    for m in entry.markers
                )
                writer.writerow([entry.orth, entry.bucket, entry.lb_count, len(entry.markers), marker_repr])
        print(f"Wrote {len(entries)}-row entry report to {args.report}", file=sys.stderr)

    print(f"{stats.entry_count} entries surveyed", file=sys.stderr)
    for bucket, count in stats.bucket_counts.most_common():
        print(f"  {bucket}: {count}", file=sys.stderr)
    print("marker levels found:", file=sys.stderr)
    for level, count in stats.marker_level_counts.most_common():
        print(f"  {level}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
