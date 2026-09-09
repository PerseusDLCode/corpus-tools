"""Audit closure of the transcribed Globe anchor intervals in a re-derived play.

Per doc/alignment-oracles.org: the P4 source's transcribed Globe line numbers
(<milestone ed="Globe" n="...">, after re-derivation) bound the numbering
problem to individual intervals. Within a scene, consecutive numbered
anchors define an interval; if the number of Globe milestones (numbered or
not) actually falling in that interval doesn't match the arithmetic gap
between the two anchor values, the interval doesn't close -- some boundary
in it is spurious or missing, most often because a shared/split verse line
was given two Globe boundaries where the printed page has one.

This does not resolve non-closing intervals (that's the alignment-oracle
task) -- it reports them, with enough context (the boundaries in between and
the text each one leads into) for that task to adjudicate.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from lxml import etree

from tei import NS


@dataclass
class Boundary:
    position: int  # 1-based position among this scene's Globe milestones
    n: str | None  # transcribed number, if any
    leads_into: str  # start of the text this boundary marks the beginning of


@dataclass
class Interval:
    act: str
    scene: str
    anchor_a: int
    anchor_b: int
    boundaries_between: int  # count of Globe milestones from just after anchor_a through anchor_b
    gap: int  # anchor_b - anchor_a
    boundaries: list[Boundary] = field(default_factory=list)

    @property
    def excess(self) -> int:
        return self.boundaries_between - self.gap

    @property
    def closes(self) -> bool:
        return self.excess == 0


def _following_text(milestone) -> str:
    """Text that begins the line/content a (start-forward) milestone leads --
    its own .tail, or, if it's immediately followed by another milestone with
    nothing between them (Globe/F1 markers routinely sit back-to-back), the
    next non-milestone content's text instead."""
    node = milestone
    while True:
        if node.tail and node.tail.strip():
            return " ".join(node.tail.split())[:60]
        nxt = node.getnext()
        if nxt is None:
            return ""
        if etree.QName(nxt.tag).localname != "milestone":
            return " ".join("".join(nxt.itertext()).split())[:60]
        node = nxt


def compute_scene_intervals(scene_div) -> list[Interval]:
    milestones = scene_div.xpath(".//tei:milestone[@ed='Globe']", namespaces=NS)
    act_n_vals = scene_div.xpath("ancestor::tei:div[@type='act'][1]/@n", namespaces=NS)
    act_n = str(act_n_vals[0]) if act_n_vals else "?"
    scene_n = scene_div.get("n", "?")

    numbered_positions = [
        (i, int(m.get("n"))) for i, m in enumerate(milestones) if m.get("n") is not None
    ]

    intervals: list[Interval] = []
    for (i, a), (j, b) in zip(numbered_positions, numbered_positions[1:]):
        boundaries = [
            Boundary(position=k - i, n=milestones[k].get("n"), leads_into=_following_text(milestones[k]))
            for k in range(i + 1, j + 1)
        ]
        intervals.append(
            Interval(
                act=act_n, scene=scene_n, anchor_a=a, anchor_b=b,
                boundaries_between=j - i, gap=b - a, boundaries=boundaries,
            )
        )
    return intervals


def compute_document_intervals(root) -> list[Interval]:
    intervals: list[Interval] = []
    for scene in root.xpath("//tei:div[@type='scene']", namespaces=NS):
        intervals.extend(compute_scene_intervals(scene))
    return intervals


def excess_histogram(intervals: list[Interval]) -> dict[int, int]:
    hist: dict[int, int] = {}
    for iv in intervals:
        if not iv.closes:
            hist[iv.excess] = hist.get(iv.excess, 0) + 1
    return hist
