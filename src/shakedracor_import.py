from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from tei import NS, TEI_NS
from tln_globe_map import PlayMapper

TEI_L = f"{{{TEI_NS}}}l"
TEI_LB = f"{{{TEI_NS}}}lb"
TEI_BODY = f"{{{TEI_NS}}}body"
TEI_HEADER = f"{{{TEI_NS}}}teiHeader"
TEI_STANDOFF = f"{{{TEI_NS}}}standOff"

# ShakeDraCor's <l>/<lb> @n is always "{div-path}.{line}", where div-path is
# the enclosing citable div's own @n -- which is itself sometimes compound
# (a chorus div's @n is e.g. "2.CHO", so a line inside it reads "2.CHO.9").
# The line number is reliably the *last* dot-segment regardless of how many
# segments precede it; a naive fixed act.scene.line split undercounts these.
LAST_SEGMENT_RE = re.compile(r"^.*\.(\d+)$")

FOLGER_EDITORS = ("Barbara A. Mowat", "Paul Werstine")


@dataclass
class Anomaly:
    play: str
    element: str
    xml_id: str | None
    n: str
    reason: str


def strip_line_number_prefixes(body: etree._Element, play: str) -> list[Anomaly]:
    """Rewrite l/lb @n from ShakeDraCor's full div-path-qualified form to the
    bare per-div line number the citeStructure templates expect (each level
    of nesting -- act, scene, induction, prologue, epilogue, chorus -- is
    already expressed by the enclosing div's own @n; repeating the full path
    on every line would double it once citeStructure nests them).

    Elements whose @n has a non-numeric final segment (e.g. ShakeDraCor's
    placeholder "2.4.gap") are left untouched and reported as an anomaly
    rather than guessed at.
    """
    anomalies: list[Anomaly] = []
    for el in body.iter(TEI_L, TEI_LB):
        n = el.get("n")
        if n is None:
            continue
        m = LAST_SEGMENT_RE.match(n)
        if m:
            el.set("n", m.group(1))
        else:
            anomalies.append(Anomaly(
                play=play,
                element=etree.QName(el).localname,
                xml_id=el.get(f"{{{NS['xml']}}}id"),
                n=n,
                reason="@n's final segment is not a plain line number",
            ))
    return anomalies


def build_header(title: str) -> etree.Element:
    """Perseus-shape teiHeader for a ShakeDraCor-derived edition, modeled on
    the existing Globe files' header shape (see data/shakespeare/tmp.xml)
    but attributing Folger Digital Texts / ShakeDraCor as the source rather
    than the Globe editors."""
    header = etree.Element(TEI_HEADER, nsmap={None: TEI_NS})
    header.set(f"{{{NS['xml']}}}lang", "eng")

    file_desc = etree.SubElement(header, f"{{{TEI_NS}}}fileDesc")
    title_stmt = etree.SubElement(file_desc, f"{{{TEI_NS}}}titleStmt")
    etree.SubElement(title_stmt, f"{{{TEI_NS}}}title").text = title
    etree.SubElement(title_stmt, f"{{{TEI_NS}}}author").text = "William Shakespeare"
    for name in FOLGER_EDITORS:
        etree.SubElement(title_stmt, f"{{{TEI_NS}}}editor").text = name

    # Structured form (publisher/pubPlace/authority, no <p>) -- matches the
    # already-validating Perseus convention (e.g. phi0959.phi010.perseus-lat2.xml).
    # A <p>/<idno> mix here fails perseus_drama.rng; set-cts-urn.xsl appends
    # <idno type="CTS"> as a sibling of these once the pipeline runs.
    pub_stmt = etree.SubElement(file_desc, f"{{{TEI_NS}}}publicationStmt")
    etree.SubElement(pub_stmt, f"{{{TEI_NS}}}publisher").text = "Trustees of Tufts University"
    etree.SubElement(pub_stmt, f"{{{TEI_NS}}}pubPlace").text = "Medford, MA"
    etree.SubElement(pub_stmt, f"{{{TEI_NS}}}authority").text = "Perseus Project"

    source_desc = etree.SubElement(file_desc, f"{{{TEI_NS}}}sourceDesc")
    source_desc.set("default", "false")
    bibl_struct = etree.SubElement(source_desc, f"{{{TEI_NS}}}biblStruct")
    bibl_struct.set("default", "false")
    bibl_struct.set("status", "draft")
    monogr = etree.SubElement(bibl_struct, f"{{{TEI_NS}}}monogr")
    etree.SubElement(monogr, f"{{{TEI_NS}}}author").text = "William Shakespeare"
    for name in FOLGER_EDITORS:
        etree.SubElement(monogr, f"{{{TEI_NS}}}editor").text = name
    etree.SubElement(monogr, f"{{{TEI_NS}}}title").text = (
        "The Folger Shakespeare (Folger Digital Texts)"
    )
    imprint = etree.SubElement(monogr, f"{{{TEI_NS}}}imprint")
    etree.SubElement(imprint, f"{{{TEI_NS}}}pubPlace").text = "Washington, DC"
    etree.SubElement(imprint, f"{{{TEI_NS}}}publisher").text = "Folger Shakespeare Library"
    # sourceDesc's content model is (bibl|biblStruct|list|listBibl)+ -- no
    # <note> sibling -- so the ShakeDraCor attribution is a second <bibl>,
    # not free text.
    provenance = etree.SubElement(source_desc, f"{{{TEI_NS}}}bibl")
    provenance.text = (
        "TEI encoding via ShakeDraCor (dracor.org/shake), derived from Folger "
        "Digital Texts. Distributed under CC BY-NC 3.0."
    )

    etree.SubElement(header, f"{{{TEI_NS}}}encodingDesc")

    profile_desc = etree.SubElement(header, f"{{{TEI_NS}}}profileDesc")
    lang_usage = etree.SubElement(profile_desc, f"{{{TEI_NS}}}langUsage")
    lang_usage.set("default", "false")
    language = etree.SubElement(lang_usage, f"{{{TEI_NS}}}language")
    language.set("ident", "eng")
    language.text = "English"

    revision_desc = etree.SubElement(header, f"{{{TEI_NS}}}revisionDesc")
    change = etree.SubElement(revision_desc, f"{{{TEI_NS}}}change")
    etree.SubElement(change, f"{{{TEI_NS}}}ab").text = (
        "converted from ShakeDraCor TEI via corpus-tools import-shakedracor"
    )

    return header


def convert_play(source_path: Path) -> tuple[etree._ElementTree, PlayMapper, list[Anomaly]]:
    """Convert one ShakeDraCor play file into the Perseus-normalized shape
    (minus genre/citeStructure/schema/CTS-URN, which the existing set-genre
    and normalize pipeline steps add -- see commands/import_shakedracor.py)."""
    mapper = PlayMapper(source_path)
    if mapper.playid is None:
        raise ValueError(f"{source_path}: no Folger idno found; cannot derive playid")

    new_tree = copy.deepcopy(mapper.doc.tree)
    root = new_tree.getroot()

    old_header = root.find(TEI_HEADER)
    new_header = build_header(mapper.title or mapper.playid)
    root.replace(old_header, new_header)

    # ShakeDraCor-specific metadata (Wikidata event/relation links) that
    # perseus_drama.rng doesn't model and Perseus has no use for.
    standoff = root.find(TEI_STANDOFF)
    if standoff is not None:
        root.remove(standoff)

    body = root.find(f".//{TEI_BODY}")
    anomalies = strip_line_number_prefixes(body, mapper.playid)

    return new_tree, mapper, anomalies
