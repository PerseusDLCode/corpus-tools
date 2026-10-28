"""A column whose flush rows are almost all speech prefixes takes its margin
from the rows that hang into the fitted one (3 Henry VI p.540 col.1: speeches
and their turnovers, 'K. Edw.' and 'L. Grey.' among the prefixes, one row at
the margin), and The Taming of the Shrew's V.2 ends as Schmidt cites it
(p.253 col.2: 'toward.' and 'froward.' had read as lines after the scene's
last numeral)."""
from __future__ import annotations

from globe import regenerate


def test_the_shrew_ends_as_schmidt_cites_it():
    *_, lines, _ = regenerate.build("shr")
    v2 = {ln.n: ln for ln in lines if ln.div == "5.2"}
    assert v2[182].rows[0].text.startswith("Vin.") and v2[182].rows[-1].text.startswith("toward.")
    assert "harsh" in v2[183].rows[0].text
