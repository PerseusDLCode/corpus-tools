from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lexicon_sections import LexiconStructureError, flatten_lexicon_sections


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="flatten-lexicon-sections",
        description=(
            "Remove the leftover EpiDoc <div type=\"edition\"> wrapper from a Perseus "
            "lexicon/glossary file, and rename its <div type=\"textpart\" subtype=\"...\"> "
            "children to <div type=\"section\">, keeping @n and adding @xml:id=\"section-{n}\"."
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
        new_text, count = flatten_lexicon_sections(original_text)
    except LexiconStructureError as e:
        print(f"ERROR: {e} -- aborting", file=sys.stderr)
        raise SystemExit(1)

    output = args.output if args.output else args.lexicon_file
    output.write_text(new_text, encoding="utf-8")
    print(f"Wrote {output} (edition wrapper removed, {count} section divs renamed)", file=sys.stderr)


if __name__ == "__main__":
    main()
