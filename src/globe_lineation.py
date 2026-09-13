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

from dataclasses import dataclass, field

from lxml import etree

from tei import NS, XML_ID, XML_BASE

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
}


@dataclass
class ConversionStats:
    lb_total: int = 0
    milestone_globe_numbered: int = 0
    milestone_globe_unnumbered: int = 0
    milestone_f1: int = 0
    l_stray_n_stripped: list = field(default_factory=list)
    sp_stray_n_stripped: list = field(default_factory=list)
    reg_collapsed_to_text: list = field(default_factory=list)
    entities_resolved: dict = field(default_factory=dict)
    element_counts_in: dict = field(default_factory=dict)
    element_counts_out: dict = field(default_factory=dict)
    synthesized_leading_milestones: list = field(default_factory=list)
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
            f"{self.milestone_f1} F1 milestones. "
            f"{len(self.l_stray_n_stripped)} stray <l @n> stripped. "
            f"{len(self.sp_stray_n_stripped)} stray <sp @n> stripped. "
            f"{len(self.reg_collapsed_to_text)} <reg @orig> collapsed to plain text. "
            f"entities resolved: {self.entities_resolved or '(none)'}. "
            f"{len(self.synthesized_leading_milestones)} leading milestones synthesized "
            "(start-forward repositioning, no tag at that position in P4). "
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
    ed = old.get("ed")
    n = old.get("n")
    new = etree.Element(q("milestone"))
    new.set("unit", "line")
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


def _local(tag) -> str:
    return etree.QName(tag).localname


def _first_by_tag(scope_el, tag: str):
    for el in scope_el.iter():
        if el is scope_el:
            continue
        if _local(el.tag) == tag:
            return el
    return None


def _is_verse_milestone(m) -> bool:
    """True iff m's direct parent is <l>. P4's verse convention (trailing
    marker, belongs to the *next* line) only ever applies to a milestone
    produced from an <lb> that was nested inside <l> -- everywhere else
    (<p>, or the corpus's rarer shapes: an <lb> sitting directly in <div1>/
    <div2> before any <sp> at all, marking an act/scene's opening boundary;
    an <lb> embedded inside a <stage> direction) already carries P4's prose
    convention (marker leads the text it numbers) or is otherwise already at
    the position P4 itself placed it. Excluding every non-<l> case from the
    shift chain, rather than enumerating each shape, is the same "don't touch
    what P4 already got right" principle Defect 1 states for prose --
    generalized to whatever isn't verse, not just to <p> specifically."""
    parent = m.getparent()
    return parent is not None and _local(parent.tag) == "l"


def _insert_leading(target, new_ms) -> None:
    """Make new_ms the first child of target (an <l>/<p>), ahead of its existing text."""
    new_ms.tail = target.text
    target.text = None
    target.insert(0, new_ms)


def _has_content_after(m) -> bool:
    """True if real (non-whitespace) content remains in m's parent after m's own
    position -- looking past any immediately-adjacent sibling milestones (of
    whichever @ed) that carry no text of their own. Needed because Globe and F1
    markers routinely sit back-to-back in the P4 source (<lb ed="G"/><lb n="311"
    ed="F1"/>of what...) -- a Globe marker's own .tail is empty there even though
    real prose immediately follows its F1 neighbor, which would otherwise cause a
    genuinely mid-paragraph boundary to be misclassified as terminal and moved."""
    node = m
    while True:
        if node.tail and node.tail.strip():
            return True
        nxt = node.getnext()
        if nxt is None:
            return False
        if _local(nxt.tag) != "milestone":
            return True
        node = nxt


def _next_content_element(node, scope_el, tag: str):
    """First element with local name tag in document order strictly after node,
    within scope_el. Restricted to a single tag (not "<l>/<p>") because a
    verse-chain milestone must never be relocated onto a <p> -- P4's prose
    convention already places its own markers correctly (Defect 1), and
    injecting a moved-in verse boundary into an already-correct paragraph
    would fabricate a spurious extra one there."""
    found_self = False
    for el in scope_el.iter():
        if el is node:
            found_self = True
            continue
        if found_self and _local(el.tag) == tag:
            return el
    return None


def _move_milestone_forward(m, scope_el, tag: str) -> None:
    """Relocate a terminal boundary marker (nothing meaningful follows it within its
    current parent) to lead the next element of the given tag in the scope, so it's
    structurally, not just positionally, the start of the content it now describes.
    A milestone embedded mid-sentence in running prose (real text in its .tail) is
    left untouched -- it already sits at the exact character offset that begins the
    content it describes; there is no separate element to relocate it into."""
    target = _next_content_element(m, scope_el, tag)
    parent = m.getparent()
    parent.remove(m)
    if target is None:
        # Nothing of this tag follows within scope (the scene's/play's final
        # boundary, or -- for a verse milestone -- nothing but a trailing prose
        # paragraph) -- put it back where it was; there is nowhere forward to
        # move it to that this chain is allowed to touch.
        parent.append(m)
        m.tail = None
        return
    _insert_leading(target, m)


def _shift_scope_to_start_forward(scope_el, ed: str, scope_label: str, stats: ConversionStats) -> None:
    """Shift ed's milestone @n values back by one boundary-slot within scope_el, so a
    milestone marks the start of the span it describes rather than the end -- matching
    TEI P5's own <lb> "beginning of the line" convention (already settled corpus-wide,
    see canonical-engLit/CLAUDE.md) and perseus_cts's resolver, which walks *forward*
    from a matched milestone to the next one to build its cited span.

    Mode-aware (doc/agenda.org phase1/fix-globe-anchor-placement, Defect 1): only
    milestones whose direct parent is <l> (verse) enter the shift chain. P4's verse
    convention trails a boundary marker at the *end* of the line it labels (the
    marginal number belongs to the line that follows); its prose convention already
    places the marker immediately before the text it numbers -- correct as it stands,
    no shift, no move. Applying the verse rule to prose (or the reverse) is exactly
    the historical bug: a marker's value/position shifted uniformly regardless of
    which P4 convention actually placed it. A scope with no verse-parented milestones
    of this @ed (e.g. Antony's currently all-<p> scenes) is therefore a no-op here.

    Relabeling @n alone would be document-order-correct but leave each marker nested
    inside the *previous* line's element -- not what "beginning of the line it labels"
    means structurally. So a terminal boundary (nothing meaningful after it within its
    current parent -- the normal shape for every verse-line-ending marker) is also
    physically relocated to lead the next <l>. A boundary embedded mid-sentence within
    a verse line is relabeled in place only, since it already sits at the exact
    character offset where the content it now describes begins.

    Only the scope's leading boundary (the P4 source never marks one at the true start
    of a scene/the play) needs a brand new milestone inserted, when that boundary was
    itself transcribed.

    @source travels with the @n value, not with the element: it is captured and
    shifted in lockstep with @n below. Setting @source in _convert_lb and then
    leaving it on the element here would strand it one boundary-slot behind every
    shifted @n -- the identical failure the historical Lear anchor displacement
    had, just for a different attribute. (F1 milestones never carry @source in
    the first place, so this shifting is a no-op for F1 scopes -- nothing special
    needs to gate that off.)
    """
    all_ed_milestones = [m for m in scope_el.iter(q("milestone")) if m.get("ed") == ed]
    milestones = [m for m in all_ed_milestones if _is_verse_milestone(m)]
    if not milestones:
        return
    original_values = [m.get("n") for m in milestones]
    original_sources = [m.get("source") for m in milestones]
    shifted_values = original_values[1:] + [None]
    shifted_sources = original_sources[1:] + [None]
    for m, new_n, new_source in zip(milestones, shifted_values, shifted_sources):
        has_content_after = _has_content_after(m)
        if new_n is not None:
            m.set("n", new_n)
        elif "n" in m.attrib:
            del m.attrib["n"]
        if new_source is not None:
            m.set("source", new_source)
        elif "source" in m.attrib:
            del m.attrib["source"]
        if not has_content_after:
            _move_milestone_forward(m, scope_el, "l")
    leading_value = original_values[0]
    leading_source = original_sources[0]
    if leading_value is not None:
        new_ms = etree.Element(q("milestone"))
        new_ms.set("unit", "line")
        new_ms.set("ed", ed)
        new_ms.set("n", leading_value)
        if leading_source is not None:
            new_ms.set("source", leading_source)
        target = _first_by_tag(scope_el, "l")
        if target is None:
            raise ConversionError(f"no <l> found to anchor a leading milestone in {scope_label}")
        _insert_leading(target, new_ms)
        stats.synthesized_leading_milestones.append((ed, scope_label, leading_value))


def reposition_milestones_start_forward(new_body, stats: ConversionStats) -> None:
    # F1 first, Globe second: when both end up leading the same <l>/<p> (the common
    # case -- P4 pairs a Globe boundary with an F1 one on nearly every line), whichever
    # runs second becomes the outer/first child via _insert_leading's insert(0), so
    # this order reproduces P4's own Globe-before-F1 tag order in the output.
    _shift_scope_to_start_forward(new_body, "F1", "(whole play)", stats)
    for scene in new_body.iter(q("div")):
        if scene.get("type") != "scene":
            continue
        act_n = scene.xpath("ancestor::tei:div[@type='act'][1]/@n", namespaces=NS)
        label = f"Act {act_n[0] if act_n else '?'}, Scene {scene.get('n')}"
        _shift_scope_to_start_forward(scene, "Globe", label, stats)


def _recover_pending_anchors(stats: ConversionStats) -> None:
    """Apply Defect 2's deferred recoveries: a stray @n found on <l> during
    conversion (staged in stats.pending_anchor_recovery as (ctx, n,
    target_l)) becomes a leading Globe milestone on that same <l>, carrying
    @source since it is by construction a transcribed number. Run after
    repositioning so the recovery is layered onto the shift chain's already-
    settled result, not folded into its arithmetic.

    target_l very often already has its own leading Globe milestone by this
    point -- the ordinary (unnumbered) one the shift chain moved in from the
    previous line -- since a stray @n is data recorded *in addition to*, not
    instead of, the P4 <lb ed="G"/> most such lines also carry (both known
    cases do). Update that milestone's value in place rather than inserting a
    second one, which would otherwise leave the <l> with two Globe milestones
    and its own text stranded between them.

    A recovered anchor may land on the F-half of a shared verse-line split
    (P4 records the compositor's choice, not the model's -- see Defect 3);
    _dedupe_shared_verse_lines, run immediately after this, relocates any
    such value onto the I-half where Defect 3 says the single resulting
    milestone belongs. This function does not need to know about that; it
    only restores the number to the slot where P4 recorded it.
    """
    for ctx, n, target_l in stats.pending_anchor_recovery:
        existing = _leading_milestone(target_l, "Globe")
        if existing is not None:
            existing.set("n", n)
            existing.set("source", GLOBE_EDITION_SOURCE)
        else:
            new_ms = etree.Element(q("milestone"))
            new_ms.set("unit", "line")
            new_ms.set("ed", "Globe")
            new_ms.set("n", n)
            new_ms.set("source", GLOBE_EDITION_SOURCE)
            _insert_leading(target_l, new_ms)
            stats.milestone_globe_numbered += 1
        stats.recovered_transcribed_anchors.append((ctx, n))


def _l_snippet(l_el) -> str:
    return "".join(l_el.itertext()).strip()[:60]


def _leading_milestone(l_el, ed: str):
    """l_el's first child, if it is a <milestone> of the given @ed -- else None."""
    if len(l_el) == 0:
        return None
    first = l_el[0]
    if _local(first.tag) == "milestone" and first.get("ed") == ed:
        return first
    return None


def _remove_leading_milestone(l_el, ms) -> None:
    """Delete ms, l_el's leading (first) child, folding any text it carried
    in its .tail back into l_el's own leading text so nothing is lost."""
    tail = ms.tail or ""
    l_el.remove(ms)
    l_el.text = tail + (l_el.text or "")


def _merge_split_pair(i_half, f_half, stats: ConversionStats) -> None:
    """A verse line split between two speakers is one Globe line (Defect 3):
    the single resulting milestone belongs on the I-half; any Globe milestone
    on the F-half is a duplicate of the same boundary and is deleted, not
    left unnumbered. P4 sometimes records the transcribed number on the
    F-half instead of the I-half (the compositor's choice, not the model's --
    confirmed for both known cases: Lear II.1's 111 sits on the I-half, III.7's
    100 on the F-half) -- if the F-half's milestone is numbered, its value and
    @source transfer onto the I-half's (creating one there if none exists)
    before the F-half's is removed, so the number is preserved rather than
    silently deleted along with the duplicate slot.

    Two numbered milestones with *different* values is a genuine conflict,
    not something to guess about -- raise rather than pick one.
    """
    i_ms = _leading_milestone(i_half, "Globe")
    f_ms = _leading_milestone(f_half, "Globe")
    if f_ms is None:
        stats.split_line_pairs_already_clean.append((_l_snippet(i_half), _l_snippet(f_half)))
        return
    if (
        i_ms is not None
        and i_ms.get("n") is not None
        and f_ms.get("n") is not None
        and i_ms.get("n") != f_ms.get("n")
    ):
        raise ConversionError(
            f"split pair {_l_snippet(i_half)!r} / {_l_snippet(f_half)!r}: conflicting "
            f"numbered Globe boundaries ({i_ms.get('n')!r} on the I-half vs "
            f"{f_ms.get('n')!r} on the F-half) -- needs human review, not a guessed merge"
        )
    if f_ms.get("n") is not None:
        if i_ms is None:
            i_ms = etree.Element(q("milestone"))
            i_ms.set("unit", "line")
            i_ms.set("ed", "Globe")
            _insert_leading(i_half, i_ms)
        i_ms.set("n", f_ms.get("n"))
        if f_ms.get("source") is not None:
            i_ms.set("source", f_ms.get("source"))
    _remove_leading_milestone(f_half, f_ms)
    stats.split_line_boundaries_deleted.append((_l_snippet(i_half), _l_snippet(f_half)))


def _dedupe_shared_verse_lines(new_body, stats: ConversionStats) -> None:
    """Walk <l> elements in document order; an adjacent part="I" -> part="F"
    pair is a shared verse line and gets merged (Defect 3). @part is
    incomplete and sometimes asymmetric in this corpus (Lear: 221 "I" vs 224
    "F", plus splits with no @part at all) -- do not guess at an unpaired or
    asymmetric marker; leave both boundaries in place and record it so the
    interval report can flag it for the alignment-oracle task instead."""
    all_l = list(new_body.iter(q("l")))
    i, n = 0, len(all_l)
    while i < n:
        l = all_l[i]
        part = l.get("part")
        if part == "I" and i + 1 < n and all_l[i + 1].get("part") == "F":
            _merge_split_pair(l, all_l[i + 1], stats)
            i += 2
            continue
        if part in ("I", "F"):
            stats.unpaired_part_markers.append((_l_snippet(l), part))
        i += 1


def rederive(p4_path, existing_p5_path) -> tuple[etree._ElementTree, ConversionStats]:
    """Build a re-derived P5 tree: existing P5 teiHeader (refsDecl leaf level rewritten to
    address Globe milestones) + a body converted fresh from the P4 source."""
    stats = ConversionStats()
    p4_root = parse_p4(p4_path)
    new_body = convert_body(p4_root, stats)
    reposition_milestones_start_forward(new_body, stats)
    _recover_pending_anchors(stats)
    _dedupe_shared_verse_lines(new_body, stats)

    p5_parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    p5_tree = etree.parse(str(existing_p5_path), p5_parser)
    p5_root = p5_tree.getroot()

    old_body = p5_root.find(f"{q('text')}/{q('body')}")
    if old_body is None:
        raise ConversionError(f"no <body> found in existing P5 file {existing_p5_path}")
    xml_base = old_body.get(XML_BASE)
    if xml_base:
        new_body.set(XML_BASE, xml_base)

    old_body.getparent().replace(old_body, new_body)

    _rewrite_line_cite_structure(p5_root)

    etree.indent(new_body, space="  ")

    return p5_tree, stats


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
