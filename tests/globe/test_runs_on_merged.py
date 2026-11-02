"""`runs-on` and `merged` rows: Gower's speeches in Pericles Act V.

V.2 ('Now our sands are almost run', p.998) is headed as a scene, but the page
numbers it on from V.1, which ends at 265: 270 beside its 5th line, 280 beside
its 15th. Schmidt cites it from 1 (Pageantry V.2.6).

The epilogue ('In Antiochus and his daughter', p.999) is the P4's scene
"chorus2"; the page prints it inside Scene III and numbers it on (91, 100), as
Schmidt cites it (Descry V.3.91, Ending V.3.102)."""
from __future__ import annotations

import pytest
from lxml import etree

from globe import regenerate, shared_lines


@pytest.fixture(scope="module")
def built():
    _, _, _, lines, results = regenerate.build("per")
    return lines, results


def test_v2_is_counted_from_1_and_checked_from_v1s_count(built):
    lines, results = built
    v1 = [ln for ln in lines if ln.div == "5.1"]
    v2 = {ln.n: ln for ln in lines if ln.div == "5.2"}
    assert v1[-1].n == 265
    assert sorted(v2) == list(range(1, 21))
    assert "Now our sands" in v2[1].rows[0].text
    assert v2[5].num == 270 and v2[15].num == 280
    ivs = [iv for r in results for iv in r.intervals if iv["div"] == "5.2"]
    assert ivs and not any(iv["error"] for iv in ivs)
    assert ivs[0]["frm"] == "scene start, numbered on from 265"


def test_the_epilogue_is_v3_85_to_102(built):
    lines, _ = built
    assert not any(ln.div == "5.chorus2" for ln in lines)
    v3 = {ln.n: ln for ln in lines if ln.div == "5.3"}
    assert "In Antiochus" in v3[85].rows[0].text
    assert "In Helicanus" in v3[91].rows[0].text
    assert "New joy" in v3[102].rows[0].text
    assert max(v3) == 102


def _row(scene: str) -> shared_lines.Row:
    return shared_lines.Row("per", scene, 999, "merged", "in antiochus and", "", "", "image")


def test_merging_moves_the_division_into_the_scene_before():
    body = etree.fromstring(
        '<body><div type="act" n="5"><div type="scene" n="3"><l>a</l></div>'
        '<div type="scene" n="chorus2"><stage>Enter</stage><l>b</l></div></div></body>')
    regenerate.merge_divisions(body, [_row("5.chorus2")])
    scenes = body.findall("div/div")
    assert [s.get("n") for s in scenes] == ["3"]
    assert [c.tag for c in scenes[0]] == ["l", "stage", "l"]


def test_merging_a_division_the_p4_lacks_is_refused():
    body = etree.fromstring('<body><div type="act" n="5"><div type="scene" n="3"/></div></body>')
    with pytest.raises(shared_lines.TableError, match="0 such scenes"):
        regenerate.merge_divisions(body, [_row("5.chorus2")])
