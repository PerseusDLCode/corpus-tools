from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from transformer import transform


@dataclass
class Step:
    stylesheet: str
    params: dict[str, str] = field(default_factory=dict)


_CTS_URN_STEP = {"cts-base": "", "source-uri": ""}

PIPELINES: dict[str, list[Step]] = {
    "normalize-prose": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_prose"}),
    ],
    "normalize-verse": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("fix-verse.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_verse"}),
    ],
    "normalize-drama": [
        Step("normalize-cts.xsl"),
        Step("set-cts-urn.xsl", dict(_CTS_URN_STEP)),
        Step("add-citeStructure.xsl"),
        Step("set-schema.xsl", {"tei-schema": "perseus_drama"}),
    ],
}


def compute_cts_urn(source_path: Path) -> str:
    """Derive CTS URN from filesystem path, mirroring the logic in set-cts-urn.xsl."""
    uri = source_path.resolve().as_uri()
    ns_match = re.search(r"canonical[-_]([^/]+)/data/", uri)
    namespace = ns_match.group(1) if ns_match else ""
    work_id = source_path.stem
    if namespace and work_id:
        return f"urn:cts:{namespace}:{work_id}"
    return ""


def _step_params(step: Step, overrides: dict[str, str]) -> dict[str, str]:
    return {**step.params, **{k: v for k, v in overrides.items() if k in step.params}}


def run_pipeline(
    pipeline: list[Step],
    source_path: Path,
    output_path: Path,
    **overrides: str,
) -> None:
    """Run a named pipeline, writing each step's output to a temp file for the next step.

    set-cts-urn.xsl uses base-uri() to derive the CTS URN, which fails when reading
    from a temp file. The URN is therefore pre-computed from source_path here and
    injected as an explicit parameter so the XSLT never needs to call base-uri().
    """
    effective = dict(overrides)
    effective.setdefault("source-uri", source_path.resolve().as_uri())
    if not effective.get("cts-base"):
        urn = compute_cts_urn(source_path)
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
        description="Run a Perseus corpus normalization pipeline.",
    )
    subparsers = parser.add_subparsers(dest="pipeline", required=True)

    for name in PIPELINES:
        sub = subparsers.add_parser(name, help=f"Run the {name} pipeline.")
        sub.add_argument("files", nargs="+", type=Path, metavar="FILE")
        sub.add_argument(
            "-o", "--output", metavar="PATH",
            help="Output file (single input) or directory (batch). Default: overwrite in-place.",
        )
        sub.add_argument(
            "--cts-base", metavar="URN",
            help="Override auto-computed CTS URN (e.g. for pdlrefwk texts).",
        )
        sub.add_argument(
            "--tei-schema", metavar="NAME",
            help="Override the schema name written into the xml-model PI.",
        )

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

    if args.pipeline == "validate":
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

    pipeline = PIPELINES[args.pipeline]
    files: list[Path] = args.files
    batch = len(files) > 1

    overrides: dict[str, str] = {}
    if args.cts_base:
        overrides["cts-base"] = args.cts_base
    if args.tei_schema:
        overrides["tei-schema"] = args.tei_schema

    errors = 0
    for source in files:
        output = _resolve_output(source, args.output, batch)
        try:
            run_pipeline(pipeline, source, output, **overrides)
        except Exception as exc:
            print(f"ERROR: {source}: {exc}", file=sys.stderr)
            errors += 1

    sys.exit(errors)


if __name__ == "__main__":
    main()
