"""Schematron validation using schxslt."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from lxml import etree
from saxonche import PySaxonProcessor

SCHEMATRON_DIR = Path(__file__).parent.parent / "schematron"

_SCHXSLT = (
    Path(__file__).parent.parent
    / "vendor" / "schxslt"
    / "src" / "main" / "resources" / "xslt" / "2.0"
    / "compile-for-svrl.xsl"
)

_SVRL_NS = "http://purl.oclc.org/dsdl/svrl"


_XSL_NS = "http://www.w3.org/1999/XSL/Transform"


def _compile(sch_path: Path) -> Path:
    """Compile a .sch to a validator XSLT; caller is responsible for unlinking."""
    if not _SCHXSLT.exists():
        raise FileNotFoundError(
            f"schxslt not found at {_SCHXSLT}. "
            "Run: git submodule update --init vendor/schxslt"
        )
    proc = PySaxonProcessor(license=False)
    xslt = proc.new_xslt30_processor()
    result = xslt.transform_to_string(
        source_file=str(sch_path),
        stylesheet_file=str(_SCHXSLT),
    )
    if not result:
        raise RuntimeError(f"schxslt produced no output compiling {sch_path.name}")

    # schxslt uses use-when="$schxslt-is-master" but omits the static param
    # declaration — a bug in the Arithmeticus fork. Inject it before Saxon rejects it.
    root = etree.fromstring(result.encode("utf-8"))
    static_param = etree.Element(f"{{{_XSL_NS}}}param")
    static_param.set("name", "schxslt-is-master")
    static_param.set("select", "true()")
    static_param.set("static", "yes")
    root.insert(0, static_param)
    patched = etree.tostring(root, encoding="unicode")

    fd, tmp = tempfile.mkstemp(suffix=".xsl")
    os.close(fd)
    tmp_path = Path(tmp)
    tmp_path.write_text(patched, encoding="utf-8")
    return tmp_path


def _run(validator_xsl: Path, doc_path: Path) -> str:
    proc = PySaxonProcessor(license=False)
    xslt = proc.new_xslt30_processor()
    result = xslt.transform_to_string(
        source_file=str(doc_path),
        stylesheet_file=str(validator_xsl),
    )
    return result or ""


def _parse_svrl(svrl: str) -> list[dict[str, str]]:
    root = etree.fromstring(svrl.encode("utf-8"))
    ns = {"svrl": _SVRL_NS}
    failures = []
    for el in root.xpath("//svrl:failed-assert | //svrl:successful-report[@role='error']",
                         namespaces=ns):
        text_el = el.find(f"{{{_SVRL_NS}}}text")
        failures.append({
            "type": el.tag.split("}")[-1],
            "location": el.get("location", ""),
            "test": el.get("test", ""),
            "message": " ".join((text_el.text or "").split()) if text_el is not None else "",
        })
    return failures


def validate_file(doc_path: Path, sch_path: Path) -> list[dict[str, str]]:
    """Compile sch_path and validate doc_path; return list of failure dicts."""
    validator_xsl = _compile(sch_path)
    try:
        svrl = _run(validator_xsl, doc_path)
        return _parse_svrl(svrl)
    finally:
        validator_xsl.unlink(missing_ok=True)
