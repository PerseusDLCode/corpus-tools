from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tln_globe_map import build_corpus_map, serialize


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="generate-line-map",
        description=(
            "Build a corpus-wide Globe act.scene.line <-> Folger TLN line-number "
            "map from a directory of ShakeDraCor TEI play files."
        ),
    )
    parser.add_argument("tei_dir", type=Path, metavar="TEI_DIR")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, metavar="FILE",
        help="Path to write the combined JSON line-number map to.",
    )
    args = parser.parse_args()

    errors = 0

    def on_error(source: Path, exc: Exception) -> None:
        nonlocal errors
        print(f"ERROR: {source}: {exc}", file=sys.stderr)
        errors += 1

    data = build_corpus_map(args.tei_dir, on_error=on_error)

    serialize(data, args.output)
    print(f"Wrote {len(data['plays'])} plays to {args.output}")

    sys.exit(errors)


if __name__ == "__main__":
    main()
