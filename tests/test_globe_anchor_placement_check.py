"""A small, hand-verified Globe-anchor PLACEMENT check for King Lear --
does a given transcribed anchor actually lead the text the printed page
says it should?

This is deliberately a down payment on phase1/globe-anchor-fixture (see
doc/agenda.org), not a replacement for it: that task will read the Globe
page images at scale and build the real fixture; this one seeds the same
data file (tests/data/lear_globe_placement.csv) with six triples read
directly off the page images already present locally at
PerseusDLCode/globe_edition/works/lr/, so the fuller fixture extends this
file rather than starting over.

Why this check exists at all, separate from test_globe_anchor_value_fidelity.py
and the interval-closure audit: both of those are placement-independent by
construction (doc/agenda.org phase1/fix-globe-anchor-placement, review
[2026-09-12]) -- a uniform one-line displacement changes no anchor VALUE and
no interval GAP, so neither check can tell a correctly-placed anchor from
one that is off by one line. Only reading the actual page (or, here,
comparing against triples someone already read off the page) can catch
that class of bug -- which is exactly the bug this file's own git history
records: Claude Chat's review caught it after the value/interval checks
both passed clean.

106 and 108 in the data file are recorded but not asserted here: both are
confirmed by counting forward from the visible decade marks (100, 110) on
the same page, but neither is itself a printed marginal number (Globe only
prints decade marks) and neither is transcribed anywhere in the P4 source
as a numbered <lb ed="G">. This pipeline only ever emits @n where P4
transcribed one, so there is nothing in the regenerated file yet for these
two rows to check against -- they're left as a documented starting point
for phase1/globe-anchor-fixture or the alignment-oracle work, not asserted
here.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest
from lxml import etree

LEAR_P5 = (
    Path(__file__).parent.parent.parent
    / "canonical-engLit" / "data" / "shakespeare" / "lr" / "shakespeare.lr.globe.xml"
)
FIXTURE_CSV = Path(__file__).parent / "data" / "lear_globe_placement.csv"

TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}


def _load_rows():
    with FIXTURE_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _leads_text(p5_root, act: str, scene: str, n: str) -> str:
    matches = p5_root.xpath(
        f".//tei:div[@type='act'][@n='{act}']"
        f"//tei:div[@type='scene'][@n='{scene}']"
        f"//tei:milestone[@ed='Globe'][@n='{n}']",
        namespaces=NS,
    )
    assert len(matches) == 1, (
        f"expected exactly one Globe milestone n={n!r} in Act {act} Scene {scene}, "
        f"found {len(matches)}"
    )
    ms = matches[0]
    # Mirror _forward_text's own back-to-back-milestone skip (Globe and F1
    # markers routinely sit adjacent with nothing between them).
    node = ms
    while True:
        if node.tail and node.tail.strip():
            return " ".join(node.tail.split())
        nxt = node.getnext()
        if nxt is None:
            return ""
        if etree.QName(nxt.tag).localname != "milestone":
            return " ".join("".join(nxt.itertext()).split())
        node = nxt


@pytest.mark.skipif(not LEAR_P5.exists(), reason="canonical-engLit sibling repo not found")
def test_hand_verified_anchors_lead_the_printed_text():
    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_root = etree.parse(str(LEAR_P5), p5_parser).getroot()

    checked = 0
    for row in _load_rows():
        if not row["n"]:
            continue  # documented but not yet assertable -- see module docstring
        actual = _leads_text(p5_root, row["act"], row["scene"], row["n"])
        # actual is only the text up to the next embedded marker (e.g. an F1
        # milestone mid-line), which may be a strict prefix of the full
        # printed line recorded in the fixture -- either containing the
        # other is a match.
        expected = row["leads_into"].split(" / ")[0]
        assert actual.startswith(expected) or expected.startswith(actual), (
            f"Globe {row['n']} (Act {row['act']}, Scene {row['scene']}) leads "
            f"{actual!r}, expected {expected!r} (see {row['source_image']})"
        )
        checked += 1
    assert checked == 6, f"expected 6 asserted triples, checked {checked}"
