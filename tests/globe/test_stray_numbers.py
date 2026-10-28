"""A printed number on a row that is no line's numbers the line above it, so
the count is checked there: without their table rows, the Shrew's Induction 2
fails at 141 ('tumbling-trick?', a row Kraken read as one word) and As You
Like It's III.3 at 109 (beside '[Exit.', below the song Touchstone sings)."""
from __future__ import annotations

from globe import regenerate, shared_lines


def _failing_without(play: str, page: int):
    table = [r for r in shared_lines.read_table() if not (r.play == play and int(r.page) == page)]
    *_, results = regenerate.build(play, table)
    return [(iv["page"], iv["div"], iv["error"]) for r in results for iv in r.failing]


def test_the_shrews_141_beside_an_unaligned_row_is_checked():
    assert _failing_without("shr", 231) == [(231, "ind.2", -1)]


def test_as_you_like_its_109_beside_an_exit_is_checked():
    assert _failing_without("ayl", 219) == [(219, "3.3", -4)]
