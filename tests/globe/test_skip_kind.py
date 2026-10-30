"""A `skip` row: a number the Globe passes over between two lines. All's
Well II.3 p.262 prints three prose rows from 'Lustig, as the Dutchman says'
(Schmidt's 46) to 'head: why, he's able to lead her a coranto' (Schmidt's
49), and 50 beside 'Mort du vinaigre!'; no 48 is given to any line."""
from __future__ import annotations

from globe import regenerate


def test_the_globe_passes_over_48():
    *_, lines, _ = regenerate.build("aww")
    ii3 = {ln.n: ln for ln in lines if ln.div == "2.3"}
    assert 48 not in ii3
    assert ii3[46].rows[0].text.startswith("Laf. Lustig")
    assert ii3[49].rows[0].text.startswith("head")
    assert ii3[50].num == 50
