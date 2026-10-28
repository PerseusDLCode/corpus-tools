"""A `stage` row: a stage direction whose rows the Globe numbers as lines.
The Tempest I.1's cries within are five rows, two of them turnovers, and
three Globe lines, 64-66; Antonio's 'Let's all sink with the king' is 67."""
from __future__ import annotations

from globe import regenerate


def test_the_cries_within_are_three_lines():
    *_, lines, _ = regenerate.build("tmp")
    i1 = {ln.n: ln for ln in lines if ln.div == "1.1"}
    assert [len(i1[n].rows) for n in (64, 65, 66)] == [1, 2, 2]
    assert i1[67].rows[0].text.startswith("Ant.")
    assert max(i1) == 72
