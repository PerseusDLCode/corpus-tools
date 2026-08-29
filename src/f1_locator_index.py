from __future__ import annotations

from pathlib import Path

from tei import NS, TEIDocument

TEI_L = "{http://www.tei-c.org/ns/1.0}l"
TEI_LB = "{http://www.tei-c.org/ns/1.0}lb"


def play_locators(f1_path: Path | str) -> set[str]:
    """Every ordinary act.scene.line locator found in `f1_path`'s real
    ShakeDraCor structure (data/shakespeare/{play}/shakespeare.{play}.f1.xml),
    composed from each act/scene div's own @n plus each <l>/<lb>'s own
    (locally-scoped) @n -- prose lines carry their citable @n on a nested
    <lb> milestone, not on the enclosing <p>, so matching l/lb covers both
    verse and prose scenes.

    Deliberately limited to this one unambiguous nesting shape: only
    <div type="scene"> children of <div type="act">. Induction/Prologue/
    Epilogue/Chorus divs are excluded -- composing a correct locator for
    those is an open citeStructure design question (a per-act Chorus div's
    own @n is already self-qualified with the act number, e.g. "2.CHO",
    while a plain scene div's @n is bare, so a uniform composition rule
    would double-prefix one of the two) -- not something to guess at here.
    """
    doc = TEIDocument(f1_path)
    locators: set[str] = set()
    for act in doc.root.xpath(".//tei:body/tei:div[@type='act']", namespaces=NS):
        act_n = act.get("n")
        if act_n is None:
            continue
        for scene in act.xpath("tei:div[@type='scene']", namespaces=NS):
            scene_n = scene.get("n")
            if scene_n is None:
                continue
            for line in scene.iter(TEI_L, TEI_LB):
                line_n = line.get("n")
                if line_n is None:
                    continue
                locators.add(f"{act_n}.{scene_n}.{line_n}")
    return locators


def build_f1_locator_index(shakespeare_dir: Path | str) -> dict[str, set[str]]:
    """{playid: {locator, ...}} for every play under `shakespeare_dir`
    (data/shakespeare), built from each play's shakespeare.{playid}.f1.xml."""
    shakespeare_dir = Path(shakespeare_dir)
    index: dict[str, set[str]] = {}
    for f1_path in sorted(shakespeare_dir.glob("*/shakespeare.*.f1.xml")):
        playid = f1_path.name.split(".")[1]
        index[playid] = play_locators(f1_path)
    return index
