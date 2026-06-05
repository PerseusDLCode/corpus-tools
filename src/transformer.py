from __future__ import annotations

from pathlib import Path

from saxonche import PySaxonProcessor

XSLT_DIR = Path(__file__).parent.parent / "xslt"


def transform(source: Path, stylesheet: str, **params: str) -> str:
    xsl_path = XSLT_DIR / stylesheet
    proc = PySaxonProcessor(license=False)
    xslt = proc.new_xslt30_processor()
    for k, v in params.items():
        xslt.set_parameter(k, proc.make_string_value(v))
    result = xslt.transform_to_string(
        source_file=str(source), stylesheet_file=str(xsl_path)
    )
    return result or ""
