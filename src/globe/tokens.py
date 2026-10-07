"""The P4 word stream, each word carrying its address in the converted tree.

doc/agenda.org #build/regenerate-lear. The P4 supplies every word; the page
only says where lines begin. So alignment works on this stream, and the
emitter inserts a milestone or <lb/> before a token by its address:
(node, slot, offset) -- the word starts `offset` characters into
`node.text` (slot "text") or `node.tail` (slot "tail").

A token is one whitespace-delimited word. Speaker names are tokens of kind
"speaker": the page prints them as row prefixes, so they anchor the alignment
(without them, repeated speech such as "A herald, ho!" / "A herald, ho, a
herald!" aligns ambiguously), but nothing is ever inserted before one and they
never make a row a line. Headings and stage directions are tokens, flagged by
`kind`, because they occupy printed rows that get <lb/>. The cast list is not
tokenised.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from lxml import etree

TEI = "{http://www.tei-c.org/ns/1.0}"
WORD = re.compile(r"\S+")


def norm(w: str) -> str:
    w = w.replace("’", "'").replace("‘", "'").lower()
    return re.sub(r"[^a-z0-9']", "", w).strip("'")


@dataclass
class Token:
    i: int
    t: str  # normalised
    raw: str
    kind: str  # "speech" | "stage" | "head" | "speaker"
    node: etree._Element
    slot: str  # "text" | "tail"
    offset: int
    cont: etree._Element | None  # enclosing <p> or <l>
    div: str  # "act.scene"


def _local(el) -> str:
    return etree.QName(el).localname


@dataclass
class Mark:
    """A Globe milestone in an existing encoding, located in the token stream."""
    before: int  # index of the first token after it
    n: str | None
    transcribed: bool  # carries @source (a number read from the page)
    div: str


def tokenize(body: etree._Element, marks: list[Mark] | None = None) -> list[Token]:
    """The token stream. If `marks` is given, Globe milestones met on the way
    are appended to it (for reading an existing encoding)."""
    toks: list[Token] = []

    def add(text, node, slot, kind, cont, div):
        if not text:
            return
        for m in WORD.finditer(text):
            n = norm(m.group())
            if n:
                toks.append(Token(len(toks), n, m.group(), kind, node, slot, m.start(), cont, div))

    def walk(el, kind, cont, div):
        tag = _local(el)
        if tag == "castList":
            return  # tail is handled by the caller
        if tag == "div":
            if el.get("type") == "act":
                if el.get("n") == "cast":
                    return
                div = f"{el.get('n')}.0"
            elif el.get("type") == "scene":
                div = f"{div.split('.')[0]}.{el.get('n')}"
        if tag in ("p", "l"):
            cont = el
        if tag == "milestone" and marks is not None and el.get("ed") == "Globe":
            marks.append(Mark(len(toks), el.get("n"), el.get("source") is not None, div))
        if tag == "stage":
            kind = "stage"
        elif tag == "head":
            kind = "head"
        elif tag == "speaker":
            kind = "speaker"
        add(el.text, el, "text", kind, cont, div)
        for c in el:
            if isinstance(c.tag, str):
                walk(c, kind, cont, div)
            add(c.tail, c, "tail", kind, cont, div)

    walk(body, "speech", None, "0.0")
    return toks


def speaker_names(toks: list[Token]) -> set[str]:
    """Normalised speaker prefixes, whole ("Old Man." -> "oldman")."""
    names: dict[int, str] = {}
    for t in toks:
        if t.kind == "speaker":
            names[id(t.node)] = names.get(id(t.node), "") + t.t
    return set(names.values())


def word_stream(body: etree._Element) -> list[str]:
    """Every word in the body, in order, with an element boundary counting as
    a word break. Regeneration must leave this unchanged.

    The boundary matters: the P4 has adjacent elements with no whitespace
    between them (<stage>Sennet.</stage><stage>Enter KING LEAR...), which
    joining blindly would read as one word "Sennet.Enter", and which
    indenting the output separates."""
    return " ".join(body.itertext()).split()
