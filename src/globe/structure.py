"""The play's structure around its lined body: what is a division of what kind,
where the Dramatis Personae goes, and who speaks.

Run at the end of emit_tei.emit(), after the Globe milestones are placed: the
lineation reads the P4's divisions as acts and scenes (div1, div2) and is not
touched. Here, following the Folger and DraCor (canonical-engLit doc/forum.org):

- a division is typed by what it is: an act or a scene by its number; an
  Induction, a Prologue, an Epilogue or a Chorus by its @n (Henry V's choruses
  are headed PROLOGUE in the Globe, so they are prologues; Gower's are
  choruses). @n is unchanged, so no CTS URN changes;
- the Dramatis Personae is the <castList> in <front>, with the setting after
  it in <set>, taken from wherever the P4 has them: its <front> (ten plays,
  whose cast lists the 2025 conversion lost), or the cast division in its
  body, which goes;
- the speakers are a <particDesc>/<listPerson> in <profileDesc>, from
  data/globe/speakers.tsv (src/globe/speakers.py); <sp who> points to them
  ("#ham."), and each printed <role> points to its speaker with @corresp. The
  P4's empty placeholder roles (ids for speakers, beside a printed list
  without them) go.
"""

from __future__ import annotations

from lxml import etree

from globe import p4_convert, speakers, speech_fixes

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

TOP = {"induction": "induction", "ind": "induction", "prologue": "prologue",
       "epilogue": "epilogue"}


class StructureError(Exception):
    """The play's structure is not what this module knows how to type."""


def division_type(n: str, top: bool) -> str:
    """The @type of a division by its @n: at the top level an act (a number)
    or an induction, prologue or epilogue; within one, a scene (a number), a
    prologue (Henry V, Romeo II) or a chorus (Gower's, chorus and chorus1)."""
    if n.isdigit():
        return "act" if top else "scene"
    if top and n in TOP:
        return TOP[n]
    if not top and n == "prologue":
        return "prologue"
    if not top and n.startswith("chorus"):
        return "chorus"
    raise StructureError(f"a {'top-level' if top else 'nested'} division n={n!r}: no type for it")


def retype(body) -> None:
    for div in body.findall(f"{TEI}div"):
        div.set("type", division_type(div.get("n"), True))
        for sub in div.findall(f"{TEI}div"):
            sub.set("type", division_type(sub.get("n"), False))


def front_from_p4(p4_root):
    """<front>: the P4's cast list, its head as the castList's head, then the
    setting as <set> (the P4's <set>, or the <stage> its cast division ends
    with: "SCENE: Messina.")."""
    cast = speakers.p4_cast(p4_root)
    stats = p4_convert.ConversionStats()
    front = etree.Element(f"{TEI}front")
    cast_list = p4_convert.convert_element(cast.find("castList"), stats, "cast list")
    head = cast.find("head")
    if head is not None:
        cast_list.insert(0, p4_convert.convert_element(head, stats, "cast list"))
    front.append(cast_list)
    for el in cast:
        if el.tag in ("head", "castList"):
            continue
        if el.tag != "stage":
            raise StructureError(f"<{el.tag}> in the P4's cast division")
        set_el = etree.SubElement(front, f"{TEI}set")
        set_el.append(p4_convert.convert_element(el, stats, "cast list"))
    p4_front = p4_root.find("text/front")
    if p4_front is not None:
        for el in p4_front:
            if el.tag == "set":
                front.append(p4_convert.convert_element(el, stats, "front"))
            elif el is not cast:
                raise StructureError(f"<{el.tag}> in the P4's front")
    # whitespace only, so that indenting lays it out afresh; a castItem's own
    # words between roles ("Messengers and other Attendants") are kept
    for el in front.iter():
        if el.tail is not None and not el.tail.strip():
            el.tail = None
        if len(el) and el.text and not el.text.strip():
            el.text = None
    return front


def link_roles(cast_list, rows: list[speakers.Row]) -> None:
    """Each printed role points to its speaker (@corresp), by the table's role
    and role_n; its xml:id, now the speaker's, goes. An empty role (a P4
    placeholder) goes with its castItem."""
    # several speakers may be one printed role (JC's First and Second Commoner,
    # "A Commoner"): its @corresp points to each. An empty role_n: the first.
    wanted: dict[tuple[str, int], list[speakers.Row]] = {}
    for r in rows:
        if r.role:
            wanted.setdefault((r.role, int(r.role_n or 1)), []).append(r)
    seen: dict[str, int] = {}
    for role in list(cast_list.iter(f"{TEI}role")):
        t = speakers.text(role)
        role.attrib.pop(XML_ID, None)
        if not t:
            item = role.getparent()
            parent = item.getparent()
            if item.tag != f"{TEI}castItem" or len(item) != 1 or speakers.text(item):
                raise StructureError("an empty <role> that is not alone in its castItem")
            parent.remove(item)
            continue
        seen[t] = seen.get(t, 0) + 1
        linked = wanted.pop((t, seen[t]), None)
        if linked:
            role.set("corresp", " ".join(f"#{r.id}" for r in linked))
    if wanted:
        missing = ", ".join(f"{r.id} ({r.role!r} {r.role_n or 1})" for rs in wanted.values()
                            for r in rs)
        raise StructureError(f"speakers.tsv names printed roles the cast list does not have: {missing}")


def point_who(body, rows: list[speakers.Row]) -> None:
    ids = {r.id for r in rows}
    for sp in body.iter(f"{TEI}sp"):
        who = (sp.get("who") or "").split()
        unknown = [w for w in who if w not in ids]
        if unknown:
            raise StructureError(f"<sp who> names speakers speakers.tsv does not have: {unknown}")
        if who:
            sp.set("who", " ".join(f"#{w}" for w in who))


def restructure(root, p4_root, rows: list[speakers.Row], fixes=()) -> None:
    """Rebuild the play's structure (module docstring). `root` is the TEI
    document with its new body in place; `rows` the play's speakers;
    `fixes` its rows of speech-fixes.tsv (src/globe/speech_fixes.py)."""
    if not rows:
        raise StructureError("no speakers.tsv rows for this play")
    text_el = root.find(f"{TEI}text")
    body = text_el.find(f"{TEI}body")
    for div in body.findall(f"{TEI}div"):
        if div.get("n") == "cast":
            body.remove(div)
    retype(body)
    front = front_from_p4(p4_root)
    link_roles(front.find(f"{TEI}castList"), rows)
    old = text_el.find(f"{TEI}front")
    if old is not None:
        text_el.remove(old)
    text_el.insert(list(text_el).index(body), front)
    speech_fixes.apply(body, list(fixes))
    point_who(body, rows)
    profile = root.find(f"{TEI}teiHeader/{TEI}profileDesc")
    if profile is None:
        raise StructureError("no <profileDesc> in the shell")
    for old_pd in profile.findall(f"{TEI}particDesc"):
        profile.remove(old_pd)
    profile.append(speakers.particdesc(rows))
