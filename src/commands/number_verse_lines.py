from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tei import TEIDocument
from verse_numbering import number_document, render_collision_table


def _resolve_output(source: Path, output_arg: str | None, batch: bool) -> Path:
    if output_arg is None:
        return source
    out = Path(output_arg)
    if batch or out.is_dir():
        out.mkdir(parents=True, exist_ok=True)
        return out / source.name
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="number-verse-lines",
        description=(
            "Interpolate Globe scene-relative line numbers onto <l> elements "
            "in TEI P5 Shakespeare plays, using existing @n anchors as constraints."
        ),
    )
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run the full algorithm and report collisions without writing any output.",
    )
    parser.add_argument(
        "-o", "--output", metavar="PATH",
        help="Output file (single input) or directory (batch). Default: overwrite in-place.",
    )
    args = parser.parse_args()

    files: list[Path] = args.files
    batch = len(files) > 1

    all_collisions = []
    errors = 0

    for source in files:
        try:
            doc = TEIDocument(source)
            warnings, collisions = number_document(doc.root, play=source.name)
            for w in warnings:
                print(w, file=sys.stderr)
            all_collisions.extend(collisions)

            if not args.dry_run:
                output = _resolve_output(source, args.output, batch)
                doc.tree.write(
                    str(output), xml_declaration=True, encoding="UTF-8", pretty_print=True,
                )
        except Exception as exc:
            print(f"ERROR: {source}: {exc}", file=sys.stderr)
            errors += 1

    if args.dry_run:
        print(render_collision_table(all_collisions))
        has_collision = any(c.collision for c in all_collisions)
        sys.exit(1 if (has_collision or errors) else 0)

    sys.exit(errors)


if __name__ == "__main__":
    main()
