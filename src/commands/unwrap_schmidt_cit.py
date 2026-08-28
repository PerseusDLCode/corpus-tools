from __future__ import annotations

import argparse
import sys
from pathlib import Path

from schmidt_cit_unwrap import UnbalancedCitWrapperError, unwrap_doubled_cit


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="unwrap-schmidt-cit",
        description=(
            "Remove the empty outer <cit> that wraps every real <cit><quote>...<ref>...</cit> "
            "in the Schmidt Shakespeare Lexicon, an artifact of automatic tagging."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    args = parser.parse_args()

    original_text = args.lexicon_file.read_text(encoding="utf-8")
    try:
        new_text, count = unwrap_doubled_cit(original_text)
    except UnbalancedCitWrapperError as e:
        print(f"ERROR: {e} -- aborting", file=sys.stderr)
        raise SystemExit(1)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(f"Wrote {output} ({count} outer <cit> wrappers removed)", file=sys.stderr)


if __name__ == "__main__":
    main()
