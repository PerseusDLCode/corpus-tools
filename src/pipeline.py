from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree
from transformer import transform


@dataclass
class Step:
    stylesheet: str
    params: dict[str, str] = field(default_factory=dict)


_TEI_NS = "http://www.tei-c.org/ns/1.0"

_DRAMA_GENRES = frozenset({
    "attic-tragedy", "attic-comedy", "roman-comedy", "roman-tragedy", "early-modern-drama",
})
_VERSE_GENRES = frozenset({
    "verse-epic", "verse-didactic", "verse-elegiac",
    "verse-lyric-choral", "verse-lyric-pindaric", "verse-lyric-monodic",
    "verse-satiric", "verse-epigram", "verse-iambic",
})
_PROSE_GENRES = frozenset({
    "prose-historiography", "prose-philosophy", "prose-dialogue",
    "prose-oratory", "prose-biography", "prose-epistolary", "prose-geography",
})

ALL_GENRES: frozenset[str] = _DRAMA_GENRES | _VERSE_GENRES | _PROSE_GENRES

_CTS_URN_STEP = {"cts-base": "", "source-uri": ""}

# Internal pipeline definitions keyed by genre family.
PIPELINES: dict[str, list[Step]] = {
    "prose": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_prose"}),
    ],
    "verse": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("fix-verse.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_verse"}),
    ],
    "drama": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_drama"}),
    ],
}


def read_genre(source: Path) -> str:
    """Return the bare genre id from the document's catRef, or '' if absent."""
    tree = etree.parse(str(source))
    targets = tree.xpath(
        "//tei:catRef[@scheme='#perseus-genre']/@target",
        namespaces={"tei": _TEI_NS},
    )
    return str(targets[0]).lstrip("#") if targets else ""


def genre_family(genre: str) -> str:
    """Map a genre id to its pipeline family (prose/verse/drama)."""
    if genre in _DRAMA_GENRES:
        return "drama"
    if genre in _VERSE_GENRES:
        return "verse"
    if genre in _PROSE_GENRES:
        return "prose"
    raise ValueError(f"Unknown genre {genre!r}. Valid genres: {sorted(ALL_GENRES)}")


def compute_cts_urn(source_path: Path) -> str:
    """Derive CTS URN from filesystem path, mirroring the logic in set-cts-urn.xsl."""
    uri = source_path.resolve().as_uri()
    ns_match = re.search(r"canonical[-_]([^/]+)/data/", uri)
    namespace = ns_match.group(1) if ns_match else ""
    work_id = source_path.stem
    if namespace and work_id:
        return f"urn:cts:{namespace}:{work_id}"
    return ""


def read_existing_cts_urn(source_path: Path) -> str:
    """Return the CTS URN already on body/@xml:base, or '' if absent or invalid.

    normalize-cts.xsl strips @xml:base, so this must be read from the original
    source file before the pipeline starts.
    """
    tree = etree.parse(str(source_path))
    attrs = tree.xpath(
        "//tei:body/@xml:base",
        namespaces={"tei": _TEI_NS},
    )
    urn = str(attrs[0]) if attrs else ""
    return urn if urn.startswith("urn:cts:") else ""


def _step_params(step: Step, overrides: dict[str, str]) -> dict[str, str]:
    return {**step.params, **{k: v for k, v in overrides.items() if k in step.params}}


def run_pipeline(
    pipeline: list[Step],
    source_path: Path,
    output_path: Path,
    **overrides: str,
) -> None:
    """Run a pipeline, writing each step's output to a temp file for the next step.

    set-cts-urn.xsl uses base-uri() to derive the CTS URN, which fails when reading
    from a temp file. The URN is therefore pre-computed from source_path here and
    injected as an explicit parameter so the XSLT never needs to call base-uri().
    """
    effective = dict(overrides)
    effective.setdefault("source-uri", source_path.resolve().as_uri())
    if not effective.get("cts-base"):
        urn = (compute_cts_urn(source_path)
               or read_existing_cts_urn(source_path))
        if urn:
            effective["cts-base"] = urn

    current = source_path
    tmp_files: list[Path] = []

    try:
        for i, step in enumerate(pipeline):
            xml = transform(current, step.stylesheet, **_step_params(step, effective))
            if i < len(pipeline) - 1:
                fd, tmp = tempfile.mkstemp(suffix=".xml")
                os.close(fd)
                tmp_path = Path(tmp)
                tmp_path.write_text(xml, encoding="utf-8")
                tmp_files.append(tmp_path)
                current = tmp_path
        output_path.write_text(xml, encoding="utf-8")
    finally:
        for tmp_path in tmp_files:
            tmp_path.unlink(missing_ok=True)


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
        prog="corpus-tools",
        description="Prepare Perseus TEI documents for the canonical corpus.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # set-genre ---------------------------------------------------------------
    sg = subparsers.add_parser(
        "set-genre",
        help="Annotate a document with its Perseus genre category.",
    )
    sg.add_argument("files", nargs="+", type=Path, metavar="FILE")
    sg.add_argument(
        "--genre", required=True, metavar="GENRE",
        help=(
            "Genre category id (e.g. prose-historiography, verse-epic, attic-tragedy). "
            f"Valid values: {', '.join(sorted(ALL_GENRES))}"
        ),
    )
    sg.add_argument(
        "-o", "--output", metavar="PATH",
        help="Output file (single input) or directory (batch). Default: overwrite in-place.",
    )

    # normalize ---------------------------------------------------------------
    norm = subparsers.add_parser(
        "normalize",
        help=(
            "Normalize a genre-annotated TEI document. "
            "Run set-genre first if the document has no catRef."
        ),
    )
    norm.add_argument("files", nargs="+", type=Path, metavar="FILE")
    norm.add_argument(
        "-o", "--output", metavar="PATH",
        help="Output file (single input) or directory (batch). Default: overwrite in-place.",
    )
    norm.add_argument(
        "--cts-base", metavar="URN",
        help="Override auto-computed CTS URN (e.g. for pdlrefwk texts).",
    )
    norm.add_argument(
        "--tei-schema", metavar="NAME",
        help="Override the schema name written into the xml-model PI.",
    )

    # validate ----------------------------------------------------------------
    val = subparsers.add_parser(
        "validate",
        help="Validate normalized documents against Schematron rules.",
    )
    val.add_argument("files", nargs="+", type=Path, metavar="FILE")
    val.add_argument(
        "--schema", type=Path, metavar="SCH",
        help="Schematron schema (default: schematron/perseus_normalized.sch).",
    )

    args = parser.parse_args()

    # --- validate ------------------------------------------------------------
    if args.command == "validate":
        from validate import validate_file, SCHEMATRON_DIR
        sch = args.schema or SCHEMATRON_DIR / "perseus_normalized.sch"
        errors = 0
        for source in args.files:
            failures = validate_file(source, sch)
            if failures:
                print(f"INVALID: {source.name}")
                for f in failures:
                    print(f"  [{f['type']}] {f['location']}")
                    print(f"    {f['message']}")
                errors += 1
            else:
                print(f"OK: {source.name}")
        sys.exit(errors)

    # --- set-genre -----------------------------------------------------------
    if args.command == "set-genre":
        genre = args.genre
        if genre not in ALL_GENRES:
            print(
                f"ERROR: {genre!r} is not a valid genre.\n"
                f"Valid genres: {', '.join(sorted(ALL_GENRES))}",
                file=sys.stderr,
            )
            sys.exit(1)
        files: list[Path] = args.files
        batch = len(files) > 1
        errors = 0
        for source in files:
            output = _resolve_output(source, args.output, batch)
            try:
                xml = transform(source, "set-genre.xsl", target=genre)
                output.write_text(xml, encoding="utf-8")
            except Exception as exc:
                print(f"ERROR: {source}: {exc}", file=sys.stderr)
                errors += 1
        sys.exit(errors)

    # --- normalize -----------------------------------------------------------
    if args.command == "normalize":
        files = args.files
        batch = len(files) > 1
        overrides: dict[str, str] = {}
        if args.cts_base:
            overrides["cts-base"] = args.cts_base
        if args.tei_schema:
            overrides["tei-schema"] = args.tei_schema

        errors = 0
        for source in files:
            try:
                genre = read_genre(source)
                if not genre:
                    raise ValueError(
                        "No genre catRef found. "
                        "Run 'corpus-tools set-genre --genre GENRE' first."
                    )
                family = genre_family(genre)
                pipeline = PIPELINES[family]
                output = _resolve_output(source, args.output, batch)
                run_pipeline(pipeline, source, output, **overrides)
            except Exception as exc:
                print(f"ERROR: {source}: {exc}", file=sys.stderr)
                errors += 1

        sys.exit(errors)


if __name__ == "__main__":
    main()
