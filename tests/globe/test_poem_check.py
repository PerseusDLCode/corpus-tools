"""globe.poem_check: a published poem's line numbers against the page numerals.

A Lover's Complaint (pp.1047-1049) prints a numeral every ten lines to 329.
The published file once numbered two empty <l> elements, P4's marks for
stanza breaks (as 99 and 212), and so ran two lines over from 213."""
from __future__ import annotations

from globe import page_rows, poem_check


def test_lovers_complaint_agrees_with_every_numeral():
    res = poem_check.check("lc")
    assert len(res.lines) == res.published == 329
    assert not res.failing
    assert not res.differing
    nums = [n for _, _, _, ns, _ in res.pages for n in ns]
    assert nums[-1] == 329


def test_four_digit_numerals_are_local_to_the_check():
    before = page_rows.NUMERAL.pattern
    with poem_check.four_digit_numerals():
        assert page_rows.NUMERAL.fullmatch("1189")
    assert page_rows.NUMERAL.pattern == before
    assert not page_rows.NUMERAL.fullmatch("1189")
