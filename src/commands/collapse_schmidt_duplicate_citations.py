from __future__ import annotations

import argparse
import sys
from pathlib import Path

from schmidt_dup_citations import collapse_duplicate_citations


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="collapse-schmidt-duplicate-citations",
        description=(
            "Collapse runs of byte-identical adjacent <ref> citations in the Schmidt "
            "Shakespeare Lexicon, an automatic-tagging artifact, down to a single citation "
            "each. A run that merely repeats the citation already captured inside the "
            "immediately preceding <cit> is deleted outright rather than collapsed."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    args = parser.parse_args()

    original_text = args.lexicon_file.read_text(encoding="utf-8")
    new_text, dup_of_cit, collapsed = collapse_duplicate_citations(original_text)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(
        f"Wrote {output} ({dup_of_cit} runs deleted as duplicates of their enclosing <cit>, "
        f"{collapsed} runs collapsed to a single citation)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
