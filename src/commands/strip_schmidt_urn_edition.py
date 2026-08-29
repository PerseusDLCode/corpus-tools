from __future__ import annotations

import argparse
import sys
from pathlib import Path

from schmidt_urn_edition import strip_edition


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="strip-schmidt-urn-edition",
        description=(
            "Strip the citation-family/edition token from Schmidt <ref target> CTS URNs: "
            "urn:cts:engLit:shakespeare.{work}.globe:{locator} -> "
            "urn:cts:engLit:shakespeare.{work}:{locator}. Citing to a specific edition is a "
            "separate, still-open problem; citations should resolve to the work."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    args = parser.parse_args()

    original_text = args.lexicon_file.read_text(encoding="utf-8")
    new_text, count = strip_edition(original_text)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(f"Wrote {output} ({count} <ref target> URNs stripped of edition token)", file=sys.stderr)


if __name__ == "__main__":
    main()
