from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from tei import NS, TEIDocument
from tln_globe_map import CorpusMap

CITATION_RE = re.compile(r"^shak\. ([a-z0-9]+) (\d+)\.(\d+)\.(\d+)$")
BARE_ROMAN_DISPLAY_RE = re.compile(r"^\s*([IVXLCDM]+)\s*,\s*(\d+)\s*\.?\s*$")


def scenes_per_act(tei_dir: Path | str, corpus_data: dict, play: str) -> dict[str, int]:
    """Scene count per Act for `play`, from its ShakeDraCor source file's own
    <div type="scene"> structure (the same structure tln_globe_map.build_corpus_map
    walks to build line records)."""
    source_file = corpus_data["plays"][play]["source_file"]
    doc = TEIDocument(Path(tei_dir) / source_file)
    counts: dict[str, int] = {}
    for scene_div in doc.root.xpath("//tei:div[@type='scene']", namespaces=NS):
        act_n = scene_div.getparent().get("n")
        counts[act_n] = counts.get(act_n, 0) + 1
    return counts


@dataclass
class CitationFix:
    element: etree._Element
    play: str
    old_n: str
    new_n: str
    tln: int


def find_collapsed_citations(
    lexicon_root: etree._Element,
    corpus_map: CorpusMap,
    scenes_per_act_by_play: dict[str, dict[str, int]],
) -> list[CitationFix]:
    """Find Schmidt <bibl> citations mangled by the single-scene-Act collapse
    bug: an Act with exactly one ShakeDraCor scene, cited by Schmidt as a bare
    "Roman numeral, line" pair (no scene to disambiguate), whose n= attribute
    was nonetheless forced into a bogus act.scene.line triple. Only returns a
    fix when the reconstructed act.1.line reference actually resolves to a
    TLN -- never emits an unverified guess.
    """
    fixes: list[CitationFix] = []
    for bibl in lexicon_root.iter("{http://www.tei-c.org/ns/1.0}bibl"):
        old_n = bibl.get("n")
        if old_n is None:
            continue
        m = CITATION_RE.match(old_n)
        if not m:
            continue
        play, act, scene, line = m.group(1), m.group(2), m.group(3), int(m.group(4))

        if corpus_map.line_number_map(play, globe=f"{act}.{scene}.{line}") is not None:
            continue  # already resolves; not broken

        if scenes_per_act_by_play.get(play, {}).get(act) != 1:
            continue  # not a single-scene Act; different (or no) problem

        display = "".join(bibl.itertext())
        rm = BARE_ROMAN_DISPLAY_RE.match(display)
        if not rm:
            continue  # display isn't a bare "Roman, line" pair

        true_line = int(rm.group(2))
        new_n = f"shak. {play} {act}.1.{true_line}"
        rec = corpus_map.line_number_map(play, globe=f"{act}.1.{true_line}")
        if rec is None:
            continue  # reconstructed ref still doesn't resolve; leave it alone

        fixes.append(CitationFix(element=bibl, play=play, old_n=old_n, new_n=new_n, tln=rec["tln"]))
    return fixes


def apply_fixes(fixes: list[CitationFix]) -> None:
    for fix in fixes:
        fix.element.set("n", fix.new_n)


def apply_fixes_to_text(text: str, fixes: list[CitationFix]) -> str:
    """Apply `fixes` as surgical string substitutions on the lexicon's raw
    XML text, rather than mutating and re-serializing the parsed tree.

    lexicon.xml hand-wraps long attribute lists and mixed content across
    lines for readability; lxml's serializer doesn't preserve that
    formatting on a round trip (attribute wrapping isn't represented as
    text nodes at all), so writing back a mutated tree rewrites the whole
    file's whitespace, not just the ~2,600 changed attributes. Every
    fixed citation's old n= value is unique and collision-free as a raw
    substring anchor (verified: n="{old_n}" occurs in the file exactly as
    many times as find_collapsed_citations found it for that old_n), so a
    plain string replacement keeps the diff to just the changed attribute
    values.
    """
    mapping: dict[str, str] = {}
    for fix in fixes:
        mapping[fix.old_n] = fix.new_n
    for old_n, new_n in mapping.items():
        text = text.replace(f'n="{old_n}"', f'n="{new_n}"')
    return text


def find_unresolved_citations(
    lexicon_root: etree._Element,
    corpus_map: CorpusMap,
    fixed_elements: set[etree._Element],
) -> list[tuple[str, str, str]]:
    """Every clean act.scene.line <bibl> citation that still doesn't resolve
    to a TLN after `fixed_elements` (the elements find_collapsed_citations
    fixed) are excluded. Returns (play, n, display) tuples for a follow-up
    worklist -- this pass does not attempt to fix these."""
    unresolved: list[tuple[str, str, str]] = []
    for bibl in lexicon_root.iter("{http://www.tei-c.org/ns/1.0}bibl"):
        if bibl in fixed_elements:
            continue
        n = bibl.get("n")
        if n is None:
            continue
        m = CITATION_RE.match(n)
        if not m:
            continue
        play, act, scene, line = m.group(1), m.group(2), m.group(3), int(m.group(4))
        if corpus_map.line_number_map(play, globe=f"{act}.{scene}.{line}") is not None:
            continue
        display = "".join(bibl.itertext())
        unresolved.append((play, n, display))
    return unresolved
