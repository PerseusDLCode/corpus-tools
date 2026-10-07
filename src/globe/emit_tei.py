"""Place Globe milestones and <lb/>s in the P4 text, rewrite the header's
sourceDesc/editorialDecl (src/globe/tei_header.py), and stamp the file.

doc/agenda.org #build/regenerate-lear; conventions from doc/forum.org
#lineation/regenerate-from-witnesses, "Conventions applied".

- a numbered <milestone unit="line" ed="Globe"> begins every Globe line the
  witness shows, with @n on every one, and no @source or @type: the Globe's
  line numbering is an abstraction that outlived any one printing, so the
  edition records only the number, not which witness a page happened to
  print it on;
- <lb/> begins every other printed row: a turnover, a shared line's second
  half, a heading, a stage direction;
- a milestone precedes the content it numbers, so a speech-initial one is
  the first child of its <p> or <l>, after <speaker>, and one whose line
  opens with a stage direction precedes the <stage>;
- a row break inside a hyphenated word puts the milestone before the whole
  word (the word is one token, so this follows).

The review build adds <!-- REVIEW kind: detail --> comments at the point each
concerns. Removing them yields the canonical build byte for byte.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from globe.p4_convert import q
from globe import tei_header
from globe.tokens import Token

TEI = "{http://www.tei-c.org/ns/1.0}"
CONTAINERS = ("p", "l")  # a milestone inside these is the first child, never before them
REVIEW_RE = re.compile(r"^ REVIEW ")


@dataclass
class Mark:
    """Something to insert before token `at`."""
    at: int
    kind: str  # "milestone" | "lb" | "review"
    n: int | None = None
    text: str = ""  # review comments
    order: int = 0  # ties at one token: lower first


def _local(el) -> str:
    return etree.QName(el).localname


def _hoistable(el) -> bool:
    return (el.getparent() is not None and _local(el) not in CONTAINERS
            and _local(el) not in ("body", "div", "sp"))


def insert_before(new, tok: Token) -> None:
    """Insert `new` immediately before the token's word, hoisting out of any
    inline element the word opens (a <stage>, a <head>)."""
    node, slot, off = tok.node, tok.slot, tok.offset
    if slot == "text":
        text = node.text or ""
        if text[:off].strip() or not _hoistable(node):
            node.text = text[:off]
            new.tail = text[off:]
            node.insert(0, new)
            return
        # the word opens this element, so the marker belongs before it -- and
        # before its parent too, where the element opens that in turn
        while True:
            parent = node.getparent()
            opens_parent = node.getprevious() is None and not (parent.text or "").strip()
            if opens_parent and _hoistable(parent):
                node = parent
                continue
            parent.insert(parent.index(node), new)
            return
    tail = node.tail or ""
    parent = node.getparent()
    node.tail = tail[:off]
    new.tail = tail[off:]
    parent.insert(parent.index(node) + 1, new)


def review_marks(reviews) -> list[Mark]:
    return [Mark(at, "review", text=text, order=-1) for at, text in reviews]


def build_marks(lines, rows_in_order) -> list[Mark]:
    """Milestones for every line, <lb/> for every other printed row, and the
    review comments. `rows_in_order` is every aligned row of the play, in
    reading order; rows that start a line are skipped (they carry the
    milestone instead)."""
    marks: list[Mark] = []
    line_start = set()
    for ln in lines:
        marks.append(Mark(ln.start, "milestone", ln.n, order=0))
        line_start.add(id(ln.rows[0]))
    for r in rows_in_order:
        if r.start is None or id(r) in line_start:
            continue
        marks.append(Mark(r.start, "lb", order=1))
    return marks


def _target(toks: list[Token], at: int) -> Token:
    """The token a mark attaches to: never a speaker name, which the page
    prints as a row prefix but the TEI keeps in its own element."""
    at = min(at, len(toks) - 1)
    while at + 1 < len(toks) and toks[at].kind == "speaker":
        at += 1
    return toks[at]


def apply_marks(toks: list[Token], marks: list[Mark]) -> None:
    """Insert every mark. Later tokens first, so earlier offsets stay valid."""
    for m in sorted(marks, key=lambda m: (-m.at, -m.order)):
        if m.kind == "milestone":
            el = etree.Element(q("milestone"))
            el.set("unit", "line")
            el.set("ed", "Globe")
            el.set("n", str(m.n))
        elif m.kind == "lb":
            el = etree.Element(q("lb"))
        else:
            el = etree.Comment(f" REVIEW {m.text} ")
        insert_before(el, _target(toks, m.at))


def review_comment(kind: str, detail: str) -> str:
    """One line, grep-able, and never containing "--" (illegal in a comment)."""
    text = f"{kind}: {' '.join(detail.split())}"
    while "--" in text:
        text = text.replace("--", "-")
    return text


def strip_reviews(xml: bytes) -> bytes:
    """The canonical bytes of a review build: its REVIEW comments removed.

    Review comments are inserted after the body is indented (see emit), so
    merging each comment's tail back restores the canonical text exactly."""
    root = etree.fromstring(xml)
    for c in root.xpath("//comment()"):
        if REVIEW_RE.match(c.text or ""):
            parent = c.getparent()
            tail = c.tail or ""
            prev = c.getprevious()
            if prev is not None:
                prev.tail = (prev.tail or "") + tail
            else:
                parent.text = (parent.text or "") + tail
            parent.remove(c)
    return serialize(root.getroottree())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def workshop_commit(repo: Path) -> str:
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                         check=True, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           check=True, capture_output=True, text=True).stdout.strip()
    return out + ("-DIRTY" if dirty else "")


def commit_date(repo: Path) -> str:
    """The stamped commit's own committer date (ISO, date only) -- looked up
    against HEAD directly, never against workshop_commit()'s return value,
    which can carry a "-DIRTY" suffix in a --scratch=DIR dev build and would
    make `git show` fail on it."""
    return subprocess.run(["git", "-C", str(repo), "show", "-s", "--format=%cd", "--date=short", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


STAMP_PREFIX = "Globe lineation regenerated from the witness pages"


def stamp(root, tool: str, version: str, commit: str, when: str, sources: dict[str, str]) -> None:
    """Provenance, in <revisionDesc>/<change>.

    CLAUDE.md's output contract says <encodingDesc>/<appInfo>, but
    perseus-schemas/perseus_drama.rng -- the schema this file declares -- has
    no appInfo; a <change> carries the same facts and validates. Flagged for
    Cliff in doc/agenda.org."""
    rev = root.find(f"{TEI}teiHeader/{TEI}revisionDesc")
    if rev is None:
        raise ValueError("no <revisionDesc> in the header to stamp")
    # A published edition is the shell of its next build, so an earlier
    # regeneration stamp would otherwise pile up: this build's stamp replaces
    # it. Older history (the 2025 conversion) is kept.
    for old in rev.findall(q("change")):
        if (old.findtext(q("ab")) or "").startswith(STAMP_PREFIX):
            rev.remove(old)
    change = etree.SubElement(rev, q("change"))
    change.set("when", when)
    ab = etree.SubElement(change, q("ab"))
    srcs = "; ".join(f"{k} sha256 {v}" for k, v in sources.items())
    ab.text = (f"{STAMP_PREFIX} by {tool} {version} "
               f"at corpus-tools commit {commit}; sources: {srcs}. Generated file: DO NOT EDIT.")
    rev.insert(0, change)  # newest first


def serialize(tree) -> bytes:
    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8")


def emit(p5_path: Path, body, toks, marks, tool: str, version: str, commit: str, when: str,
         sources: dict[str, str], play: str, table: list,
         reviews: list[Mark] | None = None) -> bytes:
    """The existing P5 header, its sourceDesc/publicationStmt/editorialDecl
    rewritten, with a freshly marked body under it.

    Review comments go in after the body is indented, so that removing them
    gives back the canonical bytes: indenting a tree that already holds them
    would leave their line breaks behind."""
    apply_marks(toks, marks)
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    tree = etree.parse(str(p5_path), parser)
    root = tree.getroot()
    old_body = root.find(f"{TEI}text/{TEI}body")
    if old_body is None:
        raise ValueError(f"no <body> in {p5_path}")
    xml_base = old_body.get("{http://www.w3.org/XML/1998/namespace}base")
    if xml_base:
        body.set("{http://www.w3.org/XML/1998/namespace}base", xml_base)
    old_body.getparent().replace(old_body, body)
    tei_header.rewrite(root, play, table)
    stamp(root, tool, version, commit, when, sources)
    etree.indent(body, space="  ")
    if reviews:
        apply_marks(toks, reviews)
    return serialize(tree)
