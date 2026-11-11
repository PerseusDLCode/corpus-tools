"""Corrections to who speaks: data/globe/speech-fixes.tsv.

The P4 is the build's source and is not edited (canonical-engLit AGENTS.md);
where it gives a speech to the wrong speaker, a row here says so, and the
build applies it (src/globe/structure.py), to the P4's text as well as to the
edition, so that check_words still compares like with like.

A row picks speeches by play, the speaker label and id the P4 gives them,
and optionally the scene ("4.1") and the speech's first words; it gives them
a new id (`who_to`, a row of speakers.tsv) and, if the label is wrong too, a
new label (`label_to`). With no first words, every speech that matches
changes ("Sec. Gent." under the First Gentleman's id, in All's Well). A row
that matches nothing, or one with first words that matches more than one
speech, stops the build. `checked` is Cliff's.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"
TABLE = Path(__file__).resolve().parent.parent.parent / "data/globe/speech-fixes.tsv"
COLUMNS = ["play", "scene", "label", "first_words", "who_from", "who_to", "label_to", "checked",
           "note"]


class SpeechFixError(Exception):
    """A row that does not apply."""


@dataclass
class Fix:
    play: str
    scene: str
    label: str
    first_words: str
    who_from: str
    who_to: str
    label_to: str
    checked: str = ""
    note: str = ""

    @property
    def pending(self) -> bool:
        return not self.checked.strip()


def read_table(path: Path = TABLE) -> list[Fix]:
    """The table, read like plays.tsv: comments and rows of bare tabs (from a
    spreadsheet) are recognised after parsing."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        raw = [[c.strip() for c in r] for r in csv.reader(fh, delimiter="\t")
               if any(c.strip() for c in r) and not r[0].lstrip().startswith("#")]
    if not raw:
        return []
    header = raw[0]
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise SpeechFixError(f"{path.name}: header lacks {', '.join(missing)}")
    return [Fix(**{k: dict(zip(header, cells)).get(k, "") for k in COLUMNS}) for cells in raw[1:]]


def for_play(rows: list[Fix], play: str) -> list[Fix]:
    return [r for r in rows if r.play == play]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def _scene(sp) -> str:
    divs = [d.get("n") for d in sp.iterancestors(f"{TEI}div")][::-1]
    return ".".join(divs)


def apply(body, fixes: list[Fix]) -> None:
    """Apply a play's fixes to a TEI body, before its @who are made pointers."""
    for f in fixes:
        hits = []
        for sp in body.iter(f"{TEI}sp"):
            if (sp.get("who") or "").split() != [f.who_from]:
                continue
            spk = sp.find(f"{TEI}speaker")
            if spk is None or " ".join("".join(spk.itertext()).split()) != f.label:
                continue
            if f.scene and _scene(sp) != f.scene:
                continue
            if f.first_words:
                said = _words(" ".join(t for el in sp if el.tag != f"{TEI}speaker"
                                       for t in el.itertext()))
                want = _words(f.first_words)
                if said[:len(want)] != want:
                    continue
            hits.append(sp)
        if not hits or (f.first_words and len(hits) > 1):
            raise SpeechFixError(f"speech-fixes.tsv: {f.play} {f.scene or '*'} {f.label!r} "
                                 f"{f.first_words!r}: {len(hits)} speeches match")
        for sp in hits:
            sp.set("who", f.who_to)
            if f.label_to:
                spk = sp.find(f"{TEI}speaker")
                for child in list(spk):
                    spk.remove(child)
                spk.text = f.label_to
