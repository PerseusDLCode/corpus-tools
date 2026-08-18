from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from schmidt_citations import (
    apply_fixes_to_text,
    find_collapsed_citations,
    find_unresolved_citations,
    scenes_per_act,
)
from tei import TEIDocument
from tln_globe_map import CorpusMap, build_corpus_map


def _write_report(report_path: Path, unresolved: list[tuple[str, str, str]]) -> None:
    with report_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["play", "n", "display"])
        writer.writerows(unresolved)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="repair-schmidt-citations",
        description=(
            "Fix Schmidt Shakespeare Lexicon <bibl n=...> citations mangled by the "
            "single-scene-Act collapse bug: an Act with exactly one ShakeDraCor scene, "
            "cited by Schmidt as a bare 'Roman numeral, line' pair, whose n= attribute "
            "was forced into a bogus act.scene.line triple anyway. Only rewrites a "
            "citation when the reconstructed act.1.line reference actually resolves to "
            "a Folger TLN."
        ),
    )
    parser.add_argument("lexicon_file", type=Path, metavar="LEXICON_XML")
    parser.add_argument(
        "--shakedracor-dir", required=True, type=Path, metavar="TEI_DIR",
        help="Directory of ShakeDraCor TEI play files (see generate-line-map).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report fixes without writing any output.",
    )
    parser.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="Output file. Default: overwrite the input in place.",
    )
    parser.add_argument(
        "--report", type=Path, metavar="CSV",
        help="Write every clean citation still unresolved after this pass's fixes "
             "to a CSV worklist (play, n, display), for follow-up investigation.",
    )
    args = parser.parse_args()

    corpus_data = build_corpus_map(args.shakedracor_dir)
    corpus_map = CorpusMap(corpus_data)
    scenes_per_act_by_play = {
        play: scenes_per_act(args.shakedracor_dir, corpus_data, play)
        for play in corpus_data["plays"]
    }

    doc = TEIDocument(args.lexicon_file)
    fixes = find_collapsed_citations(doc.root, corpus_map, scenes_per_act_by_play)

    by_play: dict[str, int] = {}
    for fix in fixes:
        by_play[fix.play] = by_play.get(fix.play, 0) + 1

    print(f"{len(fixes)} single-scene-Act collapse fixes found:", file=sys.stderr)
    for play, count in sorted(by_play.items(), key=lambda kv: -kv[1]):
        print(f"  {play:6s} {count}", file=sys.stderr)

    if args.report:
        fixed_elements = {fix.element for fix in fixes}
        unresolved = find_unresolved_citations(doc.root, corpus_map, fixed_elements)
        _write_report(args.report, unresolved)
        print(f"Wrote {len(unresolved)}-row worklist to {args.report}", file=sys.stderr)

    if args.dry_run:
        for fix in fixes:
            print(f"{fix.play}\t{fix.old_n}\t->\t{fix.new_n}\t(TLN {fix.tln})")
        return

    # Fixes are applied as raw-text substitutions, not by re-serializing the
    # parsed tree -- see apply_fixes_to_text's docstring for why a tree
    # round-trip would rewrite the file's hand-wrapped formatting wholesale.
    original_text = args.lexicon_file.read_text(encoding="utf-8")
    fixed_text = apply_fixes_to_text(original_text, fixes)
    output = args.output if args.output else args.lexicon_file
    output.write_text(fixed_text, encoding="utf-8")
    print(f"Wrote {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
