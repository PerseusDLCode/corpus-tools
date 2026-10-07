"""Build the header content this repo controls: doc/agenda.org #build/tei-header,
#build/header-fixes.

Everything else in the header -- titleStmt, profileDesc -- is untouched.
This module replaces sourceDesc, publicationStmt, the CTS refsDecl, and
encodingDesc's editorialDecl (plus its two new convention <p>s) because
lineation now comes from the witnesses, not the P4's own boundaries or
First Folio TLNs.

sourceDesc's copy-text facts beyond OCLC 08687211 are per-play (which
Doubleday volume, its pages) and go in COPY_TEXT -- a future play needs its
own entry there, the same way PLAYS (src/globe/regenerate.py) and
data/globe/shared-lines.tsv do. The witness bibls are built from the registry
(src/globe/witnesses.py), not hand-duplicated, so they can't drift from what the
rest of the pipeline trusts. publicationStmt's filename and CTS idno are
derived (canonical_filename(), and the body's own @xml:base), never typed,
so the header can't disagree with the file it describes or the refsDecl
that resolves citations against that same attribute.
"""
from __future__ import annotations

from lxml import etree

from globe import shared_lines
from globe import witnesses

TEI_XMLNS = "http://www.tei-c.org/ns/1.0"

PLAY_TITLES = {
    "lr": "King Lear",
}

# Established in doc/agenda.org #compare/doubleday (reports/doubleday-comparison.md):
# the 2-volume Nelson Doubleday set is OCLC 08687211, held at Tufts's Tisch
# Library under two catalog records, neither dated more specifically than
# "19--". Which volume and pages hold a given play varies per play; the
# forensic detail behind "date of printing not confirmed" (Internet
# Archive's own inconsistent 1893/1853 readings for this volume) belongs in
# reports/doubleday-comparison.md, not the header (#build/header-fixes).
COPY_TEXT = {
    "lr": dict(volume="volume 2", ia_id="bwb_S0-ATQ-198", pages="758-791"),
}

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen", "twenty"]


def _spell(n: int) -> str:
    """0-20 spelled out (all a play's junction count is realistically going
    to be); digits beyond that rather than guess at a scheme nothing needs yet."""
    return _ONES[n] if 0 <= n <= 20 else str(n)


def canonical_filename(play: str) -> str:
    return f"shakespeare.{play}.globe.xml"


def review_filename(play: str) -> str:
    return f"shakespeare.{play}.globe.review.xml"


def _fragment(xml: str) -> etree.Element:
    """Parse a snippet of header content, wrapped so it can carry the TEI
    namespace without repeating it on every element."""
    wrapper = etree.fromstring(f'<x xmlns="{TEI_XMLNS}">{xml}</x>')
    child = wrapper[0]
    wrapper.remove(child)
    return child


def count_junctions(table: list[shared_lines.Row]) -> int:
    """Shared-line and turnover rows -- not a `numeral` row, which corrects a
    misread marginal number, not a shared-line decision."""
    return sum(1 for r in table if r.kind != "numeral")


def build_source_desc(play: str, catalogs: dict[str, dict]) -> etree.Element:
    title = PLAY_TITLES[play]
    ct = COPY_TEXT[play]
    miun, trent = catalogs["miun"], catalogs["trent"]
    xml = f"""
    <sourceDesc>
      <p>The text of this edition is the Perseus Project's double-keyboarded
      transcription (c. 2003) of <bibl xml:id="copy-text">The Complete Works of
      William Shakespeare, ed. William George Clark and William Aldis Wright
      (Garden City, New York: Nelson Doubleday, Inc.), 2 vols. (OCLC 08687211;
      Tufts University's Tisch Library holds two catalog records for this set,
      both giving the date only as "19--")</bibl>. {title} is in {ct['volume']},
      consulted in the Internet Archive copy {ct['ia_id']} (pp. {ct['pages']});
      its date of printing is not confirmed.
      That edition reprints the Globe text in a setting of its own, with
      American spellings, which the transcription keeps. In some readings the
      transcription departs from both the copy-text and the Globe; the cause
      has not been established.</p>
      <p>The Globe line numbering is not taken from the copy-text. It is read
      from two page-image witnesses to the Globe itself, printed from the same
      plates two decades apart:
      <bibl xml:id="witness-miun">The Works of William Shakespeare, Cambridge
      and London: Macmillan, 1866 (HathiTrust {miun['hathitrust']}, University
      of Michigan copy, catalog record {miun['record']})</bibl> and
      <bibl xml:id="witness-trent">The Works of William Shakespeare, London:
      Macmillan, 1887 (Internet Archive {trent['ia']}, Trent University copy,
      OCLC 1158473505)</bibl>.</p>
    </sourceDesc>"""
    return _fragment(xml)


def build_editorial_decl(play: str, junction_count: int) -> etree.Element:
    count_word = _spell(junction_count).capitalize()
    xml = f"""
    <editorialDecl>
      <p>Words and structure -- divisions, speakers, speeches, stage
      directions, and verse lines where the copy-text sets verse -- are the
      double-keyboarded text, unaltered. Where a witness page disagrees with
      it over a word, the transcription stands and the disagreement is
      recorded in the project's reports.</p>
      <p>The Globe lineation was regenerated from the witnesses in 2026. Each
      printed row of the witness page was classified by its typography, Globe
      lines were assembled from those rows, and the resulting count was
      checked on every page against every line number printed in that page's
      margins; a page whose count disagreed with any printed number was not
      accepted. {count_word} junctions in this play, where two speeches
      may share a verse line but the page's typography does not show whether
      they do, were decided individually, from the page images and, where the
      page is silent, from the line division of the Folger edition,
      <bibl xml:id="folger-dracor">King Lear, ed. Barbara A. Mowat and Paul
      Werstine, Folger Digital Texts, version 0.5 (Washington, DC: Folger
      Shakespeare Library, 2015), as distributed in the Shakespeare Drama
      Corpus (ShakeDraCor, play shake000033; github.com/dracor-org/shakedracor,
      commit c34c2d4)</bibl>. The Folger was consulted only for its division
      of shared lines, never for words or numbers. Each decision is recorded
      in the project's data tables.</p>
      <p>The Globe line numbers previously carried by the Perseus edition were
      transcribed from the copy-text and are not retained. They are consistent
      with the numbering below, but were placed by a different convention.</p>
      <p>First Folio through-line numbers are not carried by this edition.
      They remain in the Perseus P4 edition.</p>
    </editorialDecl>"""
    return _fragment(xml)


def build_publication_stmt(play: str, xml_base: str) -> etree.Element:
    """Cliff's wording, modelled on the Greek texts' (e.g.
    canonical-engLit/data/james1/basilikon/james1.basilikon.perseus-eng1.xml).
    No <date>: that's not yet settled, and the schema doesn't require one.

    filename and xml_base come in as plain values so this stays testable
    without a tree; rewrite() derives both from single sources of truth
    (canonical_filename(), and the body's own @xml:base) rather than typing
    them here."""
    xml = f"""
    <publicationStmt>
       <publisher>Trustees of Tufts University</publisher>
       <pubPlace>Medford, MA</pubPlace>
       <authority>Perseus Project</authority>
       <idno type="filename">{canonical_filename(play)}</idno>
       <idno type="CTS">{xml_base}</idno>
       <availability>
          <licence target="https://creativecommons.org/licenses/by-sa/4.0/">Available under a
             Creative Commons Attribution-ShareAlike 4.0 International License</licence>
       </availability>
    </publicationStmt>"""
    return _fragment(xml)


def build_encoding_ps() -> list[etree.Element]:
    """No <gi>/<att> here (the P5 tagdocs module the draft assumed isn't in
    perseus_drama.rng, confirmed by jing) -- plain escaped angle brackets,
    matching how this same file's own editorialDecl already names elements
    (e.g. its old F1 paragraph's "&lt;milestone unit="line" ed="F1"&gt;")."""
    xml = """
    <p>&lt;milestone unit="line" ed="Globe"&gt; marks the first word of a
    Globe line, and every Globe line carries one, numbered. A Globe line may
    occupy more than one printed row: a verse line too long for the column,
    or a line shared between two speakers. &lt;lb/&gt; marks each printed row
    that begins no Globe line. A Globe milestone therefore also marks the
    start of a printed row, and reconstructing the page's rows requires
    reading both elements.</p>
    <p>The @part attribute, which marks the parts of a verse line shared
    between speakers, is retained from the Perseus P4 edition and was not
    regenerated. It does not always agree with the Globe's division of
    shared lines; where the two differ, the Globe milestones govern the
    numbering.</p>"""
    wrapper = etree.fromstring(f'<x xmlns="{TEI_XMLNS}">{xml}</x>')
    return list(wrapper)


GLOBE_LINE = "milestone[@unit='line'][@ed='Globe']"


def build_refs_decl() -> etree._Element:
    """The Globe edition's one citation scheme: act.scene.line, the line a
    Globe milestone (canonical-engLit doc/forum.org
    #encoding/shakespeare-citestructures). The cast list is not an act. A
    line outside any scene (an act-level prologue, as in Henry V) is cited
    act.line, through the second branch, which reaches only speeches that are
    the act's own children. The scene is the chunk. Paths avoid XPath axes:
    perseus-cts does not namespace-prefix a name after one."""
    xml = f"""<refsDecl n="CTS" xml:id="CTS">
      <citeStructure match="/TEI/text/body" use="@xml:base">
        <citeStructure unit="act" delim=":" match="div[@type='act'][@n != 'cast']" use="@n">
          <citeStructure unit="scene" delim="." match="div[@type='scene']" use="@n" n="chunk">
            <citeStructure unit="line" delim="." match=".//{GLOBE_LINE}" use="@n"/>
          </citeStructure>
          <citeStructure unit="line" delim="." match="sp//{GLOBE_LINE}" use="@n"/>
        </citeStructure>
      </citeStructure>
    </refsDecl>"""
    compact = "".join(part.strip() for part in xml.splitlines())
    refs = etree.fromstring(f'<x xmlns="{TEI_XMLNS}">{compact}</x>')[0]
    refs.tail = "\n    "  # editorialDecl follows on its own line, as it did after the shell's
    return refs


def check_every_line_citable(body) -> None:
    """Each Globe milestone must be reachable exactly once through
    build_refs_decl(): in a scene, or in a speech that is an act's own child.
    One anywhere else (a line directly under an act outside a speech, or in
    the cast list) would be uncitable, so the build stops instead."""
    ns = {"tei": TEI_XMLNS}
    line = "tei:milestone[@unit='line'][@ed='Globe']"
    total = len(body.xpath(f".//{line}", namespaces=ns))
    reached = 0
    for act in body.xpath("tei:div[@type='act'][@n != 'cast']", namespaces=ns):
        reached += len(act.xpath(f"tei:div[@type='scene']//{line}", namespaces=ns))
        reached += len(act.xpath(f"tei:sp//{line}", namespaces=ns))
    if reached != total:
        raise ValueError(f"{total - reached} of {total} Globe line milestones are not citable "
                         f"through the CTS refsDecl (build_refs_decl)")


def rewrite(root, play: str, table: list[shared_lines.Row]) -> None:
    """Replace sourceDesc and publicationStmt wholesale; rebuild encodingDesc
    from a new CTS refsDecl (build_refs_decl), a new editorialDecl, and the
    two new <p>s. The shell's refsDecl is discarded: on mvp it cites lines by
    position among <lb ed="G">, which no longer exist.

    Called after the new <body> (with its @xml:base already copied over from
    the existing P5 file -- see emit_tei.emit()) has replaced the old one, so
    publicationStmt's CTS idno can be read straight off it."""
    reg = witnesses.load(["miun", "trent"])
    catalogs = {wid: reg.witness(wid).catalog for wid in ("miun", "trent")}
    body = root.find(f"{{{TEI_XMLNS}}}text/{{{TEI_XMLNS}}}body")
    xml_base = body.get("{http://www.w3.org/XML/1998/namespace}base")

    file_desc = root.find(f"{{{TEI_XMLNS}}}teiHeader/{{{TEI_XMLNS}}}fileDesc")
    old_pub = file_desc.find(f"{{{TEI_XMLNS}}}publicationStmt")
    if old_pub is None:
        raise ValueError("no <publicationStmt> in the header to replace")
    file_desc.replace(old_pub, build_publication_stmt(play, xml_base))

    old_source = file_desc.find(f"{{{TEI_XMLNS}}}sourceDesc")
    if old_source is None:
        raise ValueError("no <sourceDesc> in the header to replace")
    file_desc.replace(old_source, build_source_desc(play, catalogs))

    encoding_desc = root.find(f"{{{TEI_XMLNS}}}teiHeader/{{{TEI_XMLNS}}}encodingDesc")
    if encoding_desc is None:
        raise ValueError("no <encodingDesc> in the header to rewrite")
    check_every_line_citable(body)
    for child in list(encoding_desc):
        encoding_desc.remove(child)
    encoding_desc.append(build_refs_decl())
    encoding_desc.append(build_editorial_decl(play, count_junctions(table)))
    for p in build_encoding_ps():
        encoding_desc.append(p)
