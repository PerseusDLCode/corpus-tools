from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tei import TEIDocument
from auditors import StructureAuditor


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="audit-structure",
        description="Audit div/milestone citation structure in Perseus TEI documents.",
    )
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "-o", "--output", type=Path, metavar="DIR",
        help="Write one report file per input into DIR instead of printing to stdout.",
    )
    args = parser.parse_args()

    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

    errors = 0
    for source in args.files:
        try:
            doc = TEIDocument(source)
            report = StructureAuditor(doc).audit()
            text = report.to_json() if args.format == "json" else report.render_text()
            if args.output:
                suffix = ".json" if args.format == "json" else ".txt"
                (args.output / (source.stem + "-structure" + suffix)).write_text(text)
            else:
                print(text)
        except Exception as exc:
            print(f"ERROR: {source}: {exc}", file=sys.stderr)
            errors += 1

    sys.exit(errors)


if __name__ == "__main__":
    main()
