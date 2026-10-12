# FROM corpus-tools' own src/globe_lineation.py @ 10a6f74
#   file sha256 71eaff1e5fc074f4653c5a239881bce28173cc94a92c8d9b6a5c352bbbfc44c3
#   (tei.py constants inlined from src/tei.py @ 10a6f74,
#    sha256 21ae01e447f29e504a45e35716cdafb9dc0dba17be4787d7c9caf128405ec01b)
#
# globe-lineation-workshop vendored the P4 -> P5 *conversion* from that
# file: lines 1-383 (entities, <reg> collapse, divisions, speakers, stage
# directions, <lb> -> milestone) and _rewrite_line_cite_structure. None of
# its lineation passes: lineation is regenerated from the witness pages
# (doc/agenda.org #build/regenerate-lear). Code below the marker is
# unchanged except for the tei import and the inline elements the other
# plays' P4s use (<gap> as <ellipsis>, <foreign>, <q>, <quote>, <hi>, <seg>, <closer>,
# <signed>: canonical-engLit doc/agenda.org #build/batch-remaining). It came home with the witness-page
# pipeline (doc/globe-lineation.org) unchanged; it is not folded back into
# src/tei.py. The original module, with the failed re-derivation it
# belonged to, is kept under the tag archive/globe-rederive.
# tests/globe/test_regenerate_lear.py checks it against the original.
# ---- vendored below ----
"""Re-derive a P5 Globe-edition body from its P4 source.

The 2025 P4->P5 migration discarded the Globe/F1 <lb> milestones and
replaced them with an interpolated @n on <l>, conflating the heterogeneous
Globe convention (numbers verse lines in verse, printed lines in prose)
and producing real duplicate-number collisions. See
canonical-engLit/doc/alignment-oracles.org for the full diagnosis.

This module re-derives the body from the P4 source directly:

- <l> carries no @n.
- Every Globe <lb ed="G"/> (numbered or not) becomes
  <milestone unit="line" ed="Globe" [n="..."]/> -- @n present only where
  the P4 source actually transcribed a number. Do not invent numbers.
- A Globe milestone whose @n was transcribed from the page also carries
  source="#globe-edition", pointing at the <bibl xml:id="globe-edition">
  in the existing P5 file's <sourceDesc> that describes the Globe edition
  itself (Clark & Wright, Macmillan). A Globe milestone whose @n arose any
  other way (future interpolation/oracle fit), and any Globe milestone
  with no @n at all, carries no @source. @source is the durable marker of
  evidence vs. inference; @n-presence alone stops discriminating the
  moment something starts interpolating numbers. See
  canonical-engLit/doc/forum.org #citations/globe-recap and
  doc/agenda.org phase1/milestone-source-provenance.
- Every F1 <lb ed="F1" n="..."/> becomes
  <milestone unit="line" ed="F1" n="..."/>. F1 milestones never carry
  @source: every one of them is numbered by the same route, so there is
  no discriminating subset -- F1's unidentified provenance is recorded
  once per document, not per milestone (see the play file's <sourceDesc>/
  <encodingDesc>).
- <reg orig="X">Y</reg> (P4's hyphenation-regularization shorthand)
  becomes plain text Y -- the regularized reading P4 itself displays.
  <orig>/<reg> are not in the Perseus P5 schema and the P4-shape @orig
  isn't valid TEI P5 either way; this is corpus-wide practice for
  print-hyphenation noise, not something worth a schema change for.
- Named entities used in the P4 source (DTD loading is deliberately off,
  per canonical-engLit's CLAUDE.md, so entities are not defined by a DTD)
  are resolved via ENTITY_MAP rather than left unexpanded.

Coverage discipline: every element tag encountered in the P4 input must be
handled explicitly (PASSTHROUGH_ATTRS or a dedicated converter) or the
conversion raises -- silently dropping structure is exactly the failure
this task exists to fix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from lxml import etree

NS = {"tei": "http://www.tei-c.org/ns/1.0", "ti": "http://chs.harvard.edu/xmlns/cts", "xml": "http://www.w3.org/XML/1998/namespace"}
XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

TEI_URI = NS["tei"]

# Pointer target for @source on a transcribed Globe milestone: a
# <bibl xml:id="globe-edition"> in the play file's <sourceDesc>, describing
# the Globe edition itself (not a specific digitized copy). See the module
# docstring and canonical-engLit/doc/agenda.org phase1/milestone-source-provenance.
GLOBE_EDITION_SOURCE = "#globe-edition"


def q(tag: str) -> str:
    return f"{{{TEI_URI}}}{tag}"


class ConversionError(Exception):
    pass


# Named entities that appear in the P4 Renaissance sources and must be
# resolved by hand, since DTD loading (and with it, entity definition) is
# deliberately disabled. An entity not listed here raises rather than
# silently emitting an undefined/unresolved reference into P5 output.
ENTITY_MAP = {
    "AElig": "Æ",
    "aelig": "æ",
    "mdash": "—",
    # The other plays' P4s (canonical-engLit doc/agenda.org #build/p4-coverage)
    "lsquo": "\u2018",  # ham, 1h4, cor
    "rsquo": "\u2019",
    "oelig": "œ",  # 2h6
    "agrave": "à",  # 1h6
}

# Elements copied through with tag name preserved and exactly this
# attribute set allowed (missing attributes are fine; anything extra is a
# reported error, not a silent pass-through).
PASSTHROUGH_ATTRS: dict[str, set[str]] = {
    "head": {"rend"},
    "stage": {"type"},
    "sp": {"who"},
    "speaker": set(),
    "p": set(),
    "castList": set(),
    "castGroup": set(),
    "castItem": {"type"},
    "roleDesc": set(),
    # Inline in the other plays' P4s; none starts or ends a row. <lg> and a
    # <text> inside the body (songs, masques, letters) are not here: whether
    # the Globe numbers their rows is undecided (canonical-engLit
    # doc/agenda.org #build/inset-numbering), so they still raise.
    "hi": {"rend"},
    "quote": {"rend"},
    "seg": set(),
    "closer": set(),
    "signed": set(),
}

# The P4's <gap/> is the Globe's lacuna, its row of dots following it as text
# (Titus III.1.36, "And bootless unto them<gap/> . . . . . . . . ."). The
# source marks that omission itself, so it is P5's <ellipsis>, not <gap>
# (which is for what the encoder leaves out); the dots are its <metamark>.
LACUNA_DOTS = re.compile(r"^\s*(?:\.\s*)+")

# P4's <q direct="unspecified"> is its default value, not a reading; P5's <q>
# has no @direct.
Q_DIRECT_DEFAULT = "unspecified"


@dataclass
class ConversionStats:
    lb_total: int = 0
    milestone_globe_numbered: int = 0
    milestone_globe_unnumbered: int = 0
    milestone_f1: int = 0
    # <lb> with no @ed, read as a Globe marker (canonical-engLit doc/agenda.org
    # #build/p4-coverage): Pericles and Troilus mark their Globe rows this way
    # almost throughout, and elsewhere a numbered one falls in the play's
    # ed="G" number sequence (Othello II.3 70, 81, 100; Timon IV.3 299, 319, 350).
    lb_no_ed_read_as_globe: int = 0
    l_stray_n_stripped: list = field(default_factory=list)
    sp_stray_n_stripped: list = field(default_factory=list)
    # A <p @n> is the Globe number of the speech's first row, recorded on the
    # paragraph because the P4 had no marker to carry it: every one of the 78
    # in the plays falls in order in its scene's Globe sequence (canonical-engLit
    # doc/agenda.org #build/p4-coverage). Recovered as a transcribed Globe
    # milestone opening the <p>; entries are (ctx, n, snippet).
    p_n_recovered: list = field(default_factory=list)
    reg_collapsed_to_text: list = field(default_factory=list)
    q_direct_dropped: int = 0
    entities_resolved: dict = field(default_factory=dict)
    element_counts_in: dict = field(default_factory=dict)
    element_counts_out: dict = field(default_factory=dict)
    # Defect 2 (doc/agenda.org phase1/fix-globe-anchor-placement): a stray @n on
    # <l> whose immediately preceding <l> (in document order, crossing <sp>
    # boundaries) lacks its own <lb ed="G"> is a transcribed Globe anchor
    # recorded in the wrong slot, not P4 encoding noise. Recovery is deferred:
    # entries here are (ctx, n, target_l_element), applied by
    # _recover_pending_anchors after repositioning, so a recovered anchor never
    # enters the shift-chain arithmetic.
    pending_anchor_recovery: list = field(default_factory=list)
    recovered_transcribed_anchors: list = field(default_factory=list)
    # Defect 3: a verse line split between two speakers (<l part="I">/<l
    # part="F">) gets one Globe milestone, on the I-half; a spurious duplicate
    # on the F-half is deleted (transferring its value first, if numbered).
    split_line_boundaries_deleted: list = field(default_factory=list)
    split_line_pairs_already_clean: list = field(default_factory=list)
    # An <l> carrying @part="I"/"F" that isn't part of a clean adjacent pair --
    # left unresolved deliberately (see _dedupe_shared_verse_lines), flagged for
    # the alignment-oracle task rather than guessed at here.
    unpaired_part_markers: list = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"lb: {self.lb_total} total -> "
            f"{self.milestone_globe_numbered} numbered Globe milestones, "
            f"{self.milestone_globe_unnumbered} unnumbered Globe milestones, "
            f"{self.milestone_f1} F1 milestones "
            f"({self.lb_no_ed_read_as_globe} <lb> with no @ed read as Globe). "
            f"{len(self.l_stray_n_stripped)} stray <l @n> stripped. "
            f"{len(self.sp_stray_n_stripped)} stray <sp @n> stripped. "
            f"{len(self.p_n_recovered)} <p @n> recovered as Globe anchors. "
            f"{len(self.reg_collapsed_to_text)} <reg @orig> collapsed to plain text. "
            f"entities resolved: {self.entities_resolved or '(none)'}. "
            f"{len(self.recovered_transcribed_anchors)} transcribed anchors recovered "
            "(stray <l @n>, restored rather than stripped). "
            f"{len(self.split_line_boundaries_deleted)} shared verse-line split "
            f"boundaries deleted, {len(self.split_line_pairs_already_clean)} pairs "
            "already clean. "
            f"{len(self.unpaired_part_markers)} unpaired/asymmetric @part markers "
            "flagged, left unresolved."
        )


def _emit_text(new_parent, last_new_child, text) -> object:
    """Append text to the running mixed-content stream; return the (unchanged) last child."""
    if not text:
        return last_new_child
    if last_new_child is None:
        new_parent.text = (new_parent.text or "") + text
    else:
        last_new_child.tail = (last_new_child.tail or "") + text
    return last_new_child


def convert_children(old_el, new_el, stats: ConversionStats, ctx: str) -> None:
    last_new_child = None
    last_new_child = _emit_text(new_el, last_new_child, old_el.text)
    for child in old_el.iterchildren():
        if isinstance(child, etree._Comment):
            new_comment = etree.Comment(child.text)
            new_el.append(new_comment)
            last_new_child = new_comment
            last_new_child = _emit_text(new_el, last_new_child, child.tail)
            continue
        if isinstance(child, etree._Entity):
            name = child.name
            if name not in ENTITY_MAP:
                raise ConversionError(f"Unmapped entity &{name}; at {ctx}")
            stats.entities_resolved[name] = stats.entities_resolved.get(name, 0) + 1
            last_new_child = _emit_text(new_el, last_new_child, ENTITY_MAP[name])
            last_new_child = _emit_text(new_el, last_new_child, child.tail)
            continue
        if isinstance(child, etree._ProcessingInstruction):
            raise ConversionError(f"Unexpected processing instruction in body at {ctx}")
        if child.tag == "gap":
            last_new_child = _convert_gap(child, new_el, stats, ctx)
            continue
        if child.tag == "reg":
            # P4's <reg orig="X">Y</reg> hyphenation-regularization shorthand collapses to
            # plain text Y (the regularized reading P4 itself displays) -- <orig>/<reg> are
            # not in the Perseus P5 schema, so this can't become an element at all.
            reg_text = _reg_text(child, stats, ctx)
            last_new_child = _emit_text(new_el, last_new_child, reg_text)
            last_new_child = _emit_text(new_el, last_new_child, child.tail)
            continue
        converted = convert_element(child, stats, ctx)
        new_el.append(converted)
        last_new_child = converted
        last_new_child = _emit_text(new_el, last_new_child, child.tail)


def convert_element(old, stats: ConversionStats, ctx: str):
    tag = old.tag
    if not isinstance(tag, str):
        raise ConversionError(f"Unexpected non-element node at {ctx}")
    stats.element_counts_in[tag] = stats.element_counts_in.get(tag, 0) + 1

    if tag == "lb":
        new = _convert_lb(old, stats, ctx)
    elif tag == "div1":
        new = _convert_div(old, stats, ctx, "act")
    elif tag == "div2":
        new = _convert_div(old, stats, ctx, "scene")
    elif tag == "l":
        new = _convert_l(old, stats, ctx)
    elif tag == "role":
        new = _convert_role(old, stats, ctx)
    elif tag == "foreign":
        new = _convert_foreign(old, stats, ctx)
    elif tag == "q":
        new = _convert_q(old, stats, ctx)
    elif tag in PASSTHROUGH_ATTRS:
        new = _convert_passthrough(old, stats, ctx, tag)
    else:
        raise ConversionError(f"Unhandled element <{tag}> at {ctx}")

    out_tag = etree.QName(new.tag).localname
    stats.element_counts_out[out_tag] = stats.element_counts_out.get(out_tag, 0) + 1
    return new


def _convert_lb(old, stats: ConversionStats, ctx: str):
    stats.lb_total += 1
    if old.text or len(old) > 0:
        raise ConversionError(f"<lb> unexpectedly has content at {ctx}")
    extra = set(old.attrib.keys()) - {"ed", "n"}
    if extra:
        raise ConversionError(f"<lb> has unexpected attributes {extra} at {ctx}")
    ed = old.get("ed")
    n = old.get("n")
    new = etree.Element(q("milestone"))
    new.set("unit", "line")
    if ed is None:
        stats.lb_no_ed_read_as_globe += 1
        ed = "G"
    if ed == "G":
        new.set("ed", "Globe")
        if n is not None:
            new.set("n", n)
            new.set("source", GLOBE_EDITION_SOURCE)
            stats.milestone_globe_numbered += 1
        else:
            stats.milestone_globe_unnumbered += 1
        return new
    if ed == "F1":
        if n is None:
            raise ConversionError(f"<lb ed='F1'> missing @n at {ctx} (expected all F1 anchors numbered)")
        new.set("ed", "F1")
        new.set("n", n)
        stats.milestone_f1 += 1
        return new
    raise ConversionError(f"<lb> with unexpected @ed={ed!r} at {ctx}")


def _convert_div(old, stats: ConversionStats, ctx: str, expected_type: str):
    dtype = old.get("type")
    if dtype != expected_type:
        raise ConversionError(f"<{old.tag}> has type={dtype!r}, expected {expected_type!r} at {ctx}")
    n = old.get("n")
    if n is None:
        raise ConversionError(f"<{old.tag}> missing @n at {ctx}")
    extra = set(old.attrib.keys()) - {"type", "n"}
    if extra:
        raise ConversionError(f"<{old.tag}> has unexpected attributes {extra} at {ctx}")
    if expected_type == "act":
        child_ctx = "cast list" if n == "cast" else f"Act {n}"
    else:
        child_ctx = f"{ctx}, Scene {n}"
    new = etree.Element(q("div"))
    new.set("type", expected_type)
    new.set("n", n)
    convert_children(old, new, stats, child_ctx)
    return new


def _preceding_l_in_scene(old):
    """The nearest preceding <l> in document order within old's enclosing P4
    scene (<div2>, or <div1> if there's no div2), crossing <sp> boundaries --
    a shared verse line routinely splits across a change of speaker, so the
    "preceding line" a Globe boundary would sit after is not necessarily a
    direct XML sibling. None if old is the scene's first <l>."""
    scope = old.getparent()
    while scope is not None and scope.tag not in ("div2", "div1"):
        scope = scope.getparent()
    if scope is None:
        return None
    siblings = list(scope.iter("l"))
    idx = siblings.index(old)
    return siblings[idx - 1] if idx > 0 else None


def _stray_n_is_recoverable(old) -> bool:
    """A stray @n on <l> is a transcribed Globe anchor recorded in the wrong
    slot -- not P4 encoding noise -- iff the immediately preceding <l> lacks
    the <lb ed="G"/> every ordinary line has (doc/agenda.org
    phase1/fix-globe-anchor-placement, Defect 2). No preceding line (this is
    the scene's first <l>) leaves nothing to corroborate against, so treat
    conservatively as noise -- this is the 2,550-instance ordinary case, not
    the two known real ones."""
    prev = _preceding_l_in_scene(old)
    if prev is None:
        return False
    return not any(c.tag == "lb" and c.get("ed") == "G" for c in prev)


def _convert_l(old, stats: ConversionStats, ctx: str):
    part = old.get("part")
    stray_n = old.get("n")
    extra = set(old.attrib.keys()) - {"part", "n"}
    if extra:
        raise ConversionError(f"<l> has unexpected attributes {extra} at {ctx}")
    new = etree.Element(q("l"))
    if part is not None:
        new.set("part", part)
    convert_children(old, new, stats, ctx)
    _wordless_l_to_ellipsis(new, stats)
    if stray_n is not None:
        if _stray_n_is_recoverable(old):
            stats.pending_anchor_recovery.append((ctx, stray_n, new))
        else:
            snippet = "".join(old.itertext()).strip()[:60]
            stats.l_stray_n_stripped.append((ctx, stray_n, snippet))
    return new


def _convert_role(old, stats: ConversionStats, ctx: str):
    extra = set(old.attrib.keys()) - {"id"}
    if extra:
        raise ConversionError(f"<role> has unexpected attributes {extra} at {ctx}")
    new = etree.Element(q("role"))
    rid = old.get("id")
    if rid is not None:
        new.set(XML_ID, rid)
    convert_children(old, new, stats, ctx)
    return new


def _wordless_l_to_ellipsis(new, stats: ConversionStats) -> None:
    """A verse line that is only the Globe's dots, with no <gap/> before them
    (Richard II II.1.280, "<l>...................</l>"): the whole line is the
    lacuna, so its dots are an <ellipsis> too, as Titus's are."""
    if not new.text or not LACUNA_DOTS.fullmatch(new.text):
        return
    if any(etree.QName(c).localname != "milestone" or (c.tail or "").strip() for c in new):
        return
    ellipsis = etree.Element(q("ellipsis"))
    metamark = etree.SubElement(ellipsis, q("metamark"))
    metamark.set("function", "ellipsis")
    metamark.text, new.text = new.text, None
    new.insert(0, ellipsis)
    stats.element_counts_out["ellipsis"] = stats.element_counts_out.get("ellipsis", 0) + 1


def _convert_gap(old, new_parent, stats: ConversionStats, ctx: str):
    """<gap/> and the dots after it -> <ellipsis><metamark>dots</metamark></ellipsis>;
    whatever follows the dots stays the ellipsis's tail. Returns the ellipsis."""
    if old.attrib or old.text or len(old):
        raise ConversionError(f"<gap> unexpectedly has attributes or content at {ctx}")
    tail = old.tail or ""
    m = LACUNA_DOTS.match(tail)
    if m is None:
        raise ConversionError(f"<gap> at {ctx} is not followed by the Globe's dots")
    stats.element_counts_in["gap"] = stats.element_counts_in.get("gap", 0) + 1
    ellipsis = etree.SubElement(new_parent, q("ellipsis"))
    metamark = etree.SubElement(ellipsis, q("metamark"))
    metamark.set("function", "ellipsis")
    metamark.text = m.group()
    ellipsis.tail = tail[m.end():]
    stats.element_counts_out["ellipsis"] = stats.element_counts_out.get("ellipsis", 0) + 1
    return ellipsis


def _convert_foreign(old, stats: ConversionStats, ctx: str):
    """P4's @lang is P5's @xml:lang."""
    extra = set(old.attrib.keys()) - {"lang"}
    if extra:
        raise ConversionError(f"<foreign> has unexpected attributes {extra} at {ctx}")
    new = etree.Element(q("foreign"))
    lang = old.get("lang")
    if lang is not None:
        new.set(XML_LANG, lang)
    convert_children(old, new, stats, ctx)
    return new


def _convert_q(old, stats: ConversionStats, ctx: str):
    extra = set(old.attrib.keys()) - {"direct"}
    if extra:
        raise ConversionError(f"<q> has unexpected attributes {extra} at {ctx}")
    direct = old.get("direct")
    if direct is not None:
        if direct != Q_DIRECT_DEFAULT:
            raise ConversionError(f"<q direct={direct!r}> at {ctx}: only the default is known")
        stats.q_direct_dropped += 1
    new = etree.Element(q("q"))
    convert_children(old, new, stats, ctx)
    return new


def _reg_text(old, stats: ConversionStats, ctx: str) -> str:
    orig = old.get("orig")
    if orig is None:
        raise ConversionError(f"<reg> missing @orig at {ctx}")
    extra = set(old.attrib.keys()) - {"orig"}
    if extra:
        raise ConversionError(f"<reg> has unexpected attributes {extra} at {ctx}")
    if len(old) > 0:
        raise ConversionError(f"<reg> unexpectedly has child elements at {ctx} (expected plain text only)")
    text = old.text or ""
    stats.element_counts_in["reg"] = stats.element_counts_in.get("reg", 0) + 1
    stats.reg_collapsed_to_text.append((ctx, orig, text))
    return text


def _convert_passthrough(old, stats: ConversionStats, ctx: str, tag: str):
    allowed = PASSTHROUGH_ATTRS[tag]
    attribs = dict(old.attrib)
    if tag == "sp" and "n" in attribs:
        # A single stray @n on <sp> is known to occur in the Antony P4 source
        # (<sp who="ant-1" n="20">) -- not a legal P5 attribute for <sp>, but data,
        # not noise: strip and log it rather than raise, mirroring _convert_l's
        # stray-@n handling.
        stray_n = attribs.pop("n")
        snippet = "".join(old.itertext()).strip()[:60]
        stats.sp_stray_n_stripped.append((ctx, stray_n, snippet))
    p_n = attribs.pop("n") if tag == "p" and "n" in attribs else None
    extra = set(attribs.keys()) - allowed
    if extra:
        raise ConversionError(f"<{tag}> has unexpected attributes {extra} at {ctx}")
    new = etree.Element(q(tag))
    for a in sorted(allowed):
        v = attribs.get(a)
        if v is not None:
            new.set(a, v)
    child_ctx = ctx
    if tag == "sp":
        child_ctx = f"{ctx} sp[@who={old.get('who')!r}]"
    convert_children(old, new, stats, child_ctx)
    if p_n is not None:
        anchor = etree.Element(q("milestone"))
        anchor.set("unit", "line")
        anchor.set("ed", "Globe")
        anchor.set("n", p_n)
        anchor.set("source", GLOBE_EDITION_SOURCE)
        anchor.tail, new.text = new.text, None
        new.insert(0, anchor)
        stats.milestone_globe_numbered += 1
        snippet = "".join(old.itertext()).strip()[:60]
        stats.p_n_recovered.append((ctx, p_n, snippet))
    return new


def parse_p4(path) -> etree._Element:
    """Parse a P4 Renaissance source without DTD loading (canonical-engLit CLAUDE.md gotcha:
    lxml/libxml2 materializes DTD-default attribute values into output otherwise)."""
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True, recover=False)
    tree = etree.parse(str(path), parser)
    return tree.getroot()


def convert_body(p4_root, stats: ConversionStats):
    old_body = p4_root.find("text/body")
    if old_body is None:
        raise ConversionError("no <body> found in P4 source (unexpected document shape)")
    new_body = etree.Element(q("body"))
    convert_children(old_body, new_body, stats, "body")
    return new_body


def _rewrite_line_cite_structure(p5_root) -> None:
    leaf_candidates = p5_root.xpath(
        "//tei:encodingDesc/tei:refsDecl"
        "/tei:citeStructure/tei:citeStructure/tei:citeStructure/tei:citeStructure",
        namespaces=NS,
    )
    if len(leaf_candidates) != 1:
        raise ConversionError(
            f"expected exactly one act->scene->line leaf citeStructure, found {len(leaf_candidates)}"
        )
    leaf = leaf_candidates[0]
    if leaf.get("unit") != "line":
        raise ConversionError(f"leaf citeStructure has unit={leaf.get('unit')!r}, expected 'line'")
    leaf.set("match", ".//milestone[@ed='Globe']")
    leaf.set("use", "@n")
