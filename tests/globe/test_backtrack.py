"""A page that fails in both witnesses on an interval from a number on the
page before builds that page again from the other witness (The Winter's Tale
p.317: Kraken lost three rows below the page's last number in Michigan, not in
Trent, and the count fell short only at 50 on p.318)."""
from __future__ import annotations

from globe import regenerate, shared_lines


def test_the_page_before_is_built_again_from_the_other_witness():
    table = [r for r in shared_lines.read_table() if not (r.play == "wt" and r.kind == "dropped")]
    *_, results = regenerate.build("wt", table)
    by_page = {r.page: r for r in results}
    assert not [r.page for r in results if r.failing]
    assert by_page[317].witness == "trent/kraken"
    assert by_page[317].tried[0] == ("miun/kraken", "p.318:3")
    assert by_page[318].witness == "miun/kraken"
