from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from lxml import etree

from genres import load as load_genres
from pipeline import PIPELINES, run_pipeline
from shakedracor_import import convert_play
from transformer import transform

GENRE = "drama-act-scene-line"
TEXTGROUP = "shakespeare"
# Ratified 2026-08-19 (canonical-engLit agenda.org #phase0/cts-urns): Alison
# and Greg confirmed citation-family identifiers (globe, f1) double as the
# file-level edition identifiers -- not the originally-drafted folger-eng1.
EDITION = "f1"

WORK_CTS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:engLit:{textgroup}.{work}" xml:lang="eng" groupUrn="urn:cts:engLit:{textgroup}">
   <ti:title xml:lang="eng">{title}</ti:title>
   <ti:edition xml:lang="eng" workUrn="urn:cts:engLit:{textgroup}.{work}" urn="urn:cts:engLit:{textgroup}.{work}.{edition}">
      <ti:label xml:lang="eng">{title}</ti:label>
      <ti:description xml:lang="eng">The Folger Shakespeare (Folger Digital Texts), ed. Barbara A. Mowat and Paul Werstine, via ShakeDraCor (dracor.org/shake). CC BY-NC 3.0.</ti:description>
   </ti:edition>
</ti:work>
"""


def _write_work_cts(output_dir: Path, work: str, title: str) -> Path:
    path = output_dir / work / "__cts__.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        WORK_CTS_TEMPLATE.format(textgroup=TEXTGROUP, work=work, title=title, edition=EDITION),
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="import-shakedracor",
        description=(
            "Convert ShakeDraCor TEI Simple play files into the Perseus-normalized "
            "TEI P5 shape (data/shakespeare/{work}/shakespeare.{work}.f1.xml), "
            "reusing corpus-tools' set-genre/normalize pipeline for genre, "
            "citeStructure, CTS URN, and schema PI. Also emits a throughline "
            "(Folger TLN) refsDecl alongside the primary act.scene.line one."
        ),
    )
    parser.add_argument("shakedracor_dir", type=Path, metavar="SHAKEDRACOR_TEI_DIR")
    parser.add_argument("output_dir", type=Path, metavar="OUTPUT_DIR",
                         help="e.g. canonical-engLit/data/shakespeare")
    parser.add_argument("--odd", required=True, type=Path, metavar="ODD")
    parser.add_argument(
        "--work", metavar="PLAYID[,PLAYID...]",
        help="Comma-separated playids to convert (default: all plays found).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report anomalies and planned output paths without writing any files.",
    )
    args = parser.parse_args()

    tax = load_genres(args.odd)
    if GENRE not in tax.valid:
        print(f"ERROR: {GENRE!r} is not a valid genre in {args.odd}", file=sys.stderr)
        sys.exit(1)
    family = tax.family(GENRE)

    wanted = set(args.work.split(",")) if args.work else None

    sources = sorted(args.shakedracor_dir.glob("*.xml"))
    errors = 0
    converted = 0
    total_anomalies = 0

    for source in sources:
        try:
            tree, play, anomalies = convert_play(source)
        except Exception as exc:
            print(f"ERROR: {source}: {exc}", file=sys.stderr)
            errors += 1
            continue

        work = play.playid
        if wanted is not None and work not in wanted:
            continue

        total_anomalies += len(anomalies)
        for a in anomalies:
            print(f"ANOMALY: {a.play} <{a.element} xml:id={a.xml_id}> n={a.n!r}: {a.reason}",
                  file=sys.stderr)

        final_output = args.output_dir / work / f"{TEXTGROUP}.{work}.{EDITION}.xml"
        cts_base = f"urn:cts:engLit:{TEXTGROUP}.{work}.{EDITION}"

        if args.dry_run:
            print(f"{work}: would write {final_output} (cts-base={cts_base})")
            converted += 1
            continue

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_adapted = Path(tmpdir) / "adapted.xml"
            tmp_adapted.write_bytes(etree.tostring(tree, xml_declaration=True, encoding="UTF-8"))

            tmp_genred = Path(tmpdir) / "genred.xml"
            xml = transform(tmp_adapted, "set-genre.xsl", target=GENRE, cert="")
            tmp_genred.write_text(xml, encoding="utf-8")

            final_output.parent.mkdir(parents=True, exist_ok=True)
            run_pipeline(
                PIPELINES[family], tmp_genred, final_output,
                **{"cts-base": cts_base, "include-tln-refsdecl": "true"},
            )

        _write_work_cts(args.output_dir, work, play.title or work)
        print(f"{work}: wrote {final_output}", file=sys.stderr)
        converted += 1

    print(
        f"\n{converted} plays {'would be ' if args.dry_run else ''}converted, "
        f"{total_anomalies} anomalies flagged, {errors} errors.",
        file=sys.stderr,
    )
    sys.exit(errors)


if __name__ == "__main__":
    main()
