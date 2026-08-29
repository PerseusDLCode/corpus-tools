from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from f1_locator_index import build_f1_locator_index
from schmidt_line_recovery import recover_line_numbers


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="recover-schmidt-line-numbers",
        description=(
            "Recover a missing line-number segment in Schmidt <ref target> CTS URNs "
            "(urn:cts:engLit:shakespeare.{play}:{act}.{scene}, edition token already "
            "stripped), verifying every reconstruction against the real ShakeDraCor "
            "act/scene/line structure rather than guessing."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "--shakespeare-dir", required=True, type=Path, metavar="DIR",
        help="Directory of per-play shakespeare.{play}.f1.xml files (e.g. data/shakespeare).",
    )
    parser.add_argument(
        "--report", type=Path, metavar="CSV",
        help="Write every unresolved citation (play, locator, text, reason) to a CSV.",
    )
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    args = parser.parse_args()

    locator_index = build_f1_locator_index(args.shakespeare_dir)
    print(f"Indexed {len(locator_index)} plays from {args.shakespeare_dir}", file=sys.stderr)

    original_text = args.lexicon_file.read_text(encoding="utf-8")
    new_text, fixed, unresolved = recover_line_numbers(original_text, locator_index)

    if args.report:
        with args.report.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["play", "locator", "text", "reason"])
            writer.writeheader()
            writer.writerows(unresolved)
        print(f"Wrote {len(unresolved)}-row unresolved report to {args.report}", file=sys.stderr)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(
        f"Wrote {output} ({fixed} line numbers recovered, {len(unresolved)} left unresolved)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
