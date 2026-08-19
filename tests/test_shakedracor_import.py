from __future__ import annotations

from lxml import etree

from shakedracor_import import build_header, convert_play, strip_line_number_prefixes
from tei import NS, TEI_NS


PLAY_TEI = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="shake000099">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Test Play</title>
      </titleStmt>
      <publicationStmt>
        <publisher>Folger Digital Texts</publisher>
        <idno>Tst</idno>
      </publicationStmt>
    </fileDesc>
  </teiHeader>
  <standOff>
    <listEvent>
      <event type="written" when="1600"><desc/></event>
    </listEvent>
  </standOff>
  <text>
    <body>
      <div type="act" n="1">
        <div type="scene" n="1">
          <sp>
            <l xml:id="ftln-0001" n="1.1.1">First line. </l>
            <l xml:id="ftln-0002" n="1.1.2" part="I">Split line, </l>
            <l xml:id="ftln-0003" n="1.1.2" part="F">continued. </l>
          </sp>
        </div>
        <div type="scene" n="2">
          <p>
            <lb xml:id="ftln-0004" n="1.2.1"/>Prose opening.
            <lb xml:id="ftln-0005" n="1.2.gap"/>Anomalous milestone.
          </p>
        </div>
      </div>
      <div type="chorus" n="2.CHO">
        <sp>
          <l xml:id="ftln-0006" n="2.CHO.9">Chorus line, a compound div-path. </l>
        </sp>
      </div>
    </body>
  </text>
</TEI>
"""


def _write(tmp_path, name="test-play.xml"):
    p = tmp_path / name
    p.write_text(PLAY_TEI)
    return p


def test_strip_line_number_prefixes_rewrites_clean_triples(tmp_path):
    root = etree.fromstring(PLAY_TEI.encode())
    body = root.find(f".//{{{TEI_NS}}}body")
    anomalies = strip_line_number_prefixes(body, "tst")

    ls = root.xpath("//tei:l", namespaces=NS)
    assert [l.get("n") for l in ls] == ["1", "2", "2", "9"]

    lbs = root.xpath("//tei:lb", namespaces=NS)
    assert lbs[0].get("n") == "1"
    # anomalous milestone left untouched
    assert lbs[1].get("n") == "1.2.gap"


def test_strip_line_number_prefixes_handles_compound_div_paths(tmp_path):
    # A chorus div's own @n is itself compound ("2.CHO"), so a line inside it
    # reads "2.CHO.9" -- the last-segment rule must still extract "9", not
    # get confused by the extra dot.
    root = etree.fromstring(PLAY_TEI.encode())
    body = root.find(f".//{{{TEI_NS}}}body")
    strip_line_number_prefixes(body, "tst")

    chorus_l = root.xpath("//tei:div[@type='chorus']//tei:l", namespaces=NS)[0]
    assert chorus_l.get("n") == "9"


def test_strip_line_number_prefixes_reports_anomaly(tmp_path):
    root = etree.fromstring(PLAY_TEI.encode())
    body = root.find(f".//{{{TEI_NS}}}body")
    anomalies = strip_line_number_prefixes(body, "tst")

    assert len(anomalies) == 1
    a = anomalies[0]
    assert a.play == "tst"
    assert a.element == "lb"
    assert a.xml_id == "ftln-0005"
    assert a.n == "1.2.gap"


def test_build_header_shape():
    header = build_header("Test Play")
    ns = {"tei": TEI_NS}

    assert header.tag == f"{{{TEI_NS}}}teiHeader"
    assert header.xpath("string(.//tei:titleStmt/tei:title)", namespaces=ns) == "Test Play"
    assert header.xpath("string(.//tei:titleStmt/tei:author)", namespaces=ns) == "William Shakespeare"
    editors = header.xpath(".//tei:titleStmt/tei:editor/text()", namespaces=ns)
    assert editors == ["Barbara A. Mowat", "Paul Werstine"]
    # encodingDesc must be present (empty) for add-citeStructure.xsl to inject into later
    assert header.find(f"{{{TEI_NS}}}encodingDesc") is not None

    # perseus_drama.rng: publicationStmt is either free-text (p/ab) or
    # structured bibliographic elements, never both -- set-cts-urn.xsl
    # appends <idno type="CTS"> later, so no <p> here.
    assert header.find(f".//{{{TEI_NS}}}publicationStmt/{{{TEI_NS}}}p") is None
    # perseus_drama.rng: sourceDesc content is (bibl|biblStruct|list|listBibl)+,
    # no <note>.
    assert header.find(f".//{{{TEI_NS}}}sourceDesc/{{{TEI_NS}}}note") is None


def test_convert_play_replaces_header_and_strips_line_numbers(tmp_path):
    source = _write(tmp_path)
    tree, mapper, anomalies = convert_play(source)
    root = tree.getroot()
    ns = {"tei": TEI_NS}

    assert mapper.playid == "tst"
    assert mapper.title == "Test Play"

    assert root.xpath("string(.//tei:titleStmt/tei:title)", namespaces=ns) == "Test Play"
    assert root.xpath("string(.//tei:titleStmt/tei:author)", namespaces=ns) == "William Shakespeare"

    ls = root.xpath("//tei:l", namespaces=ns)
    assert [l.get("n") for l in ls] == ["1", "2", "2", "9"]

    assert len(anomalies) == 1
    assert anomalies[0].n == "1.2.gap"


def test_convert_play_strips_standoff(tmp_path):
    # ShakeDraCor's standOff (Wikidata event/relation links) isn't modeled by
    # perseus_drama.rng and has no use in Perseus -- must not survive conversion.
    source = _write(tmp_path)
    tree, _mapper, _anomalies = convert_play(source)
    assert tree.getroot().find(f"{{{TEI_NS}}}standOff") is None


def test_convert_play_does_not_mutate_original_source(tmp_path):
    source = _write(tmp_path)
    convert_play(source)
    # PlayMapper re-reads the file fresh, so this only guards against convert_play
    # writing back to disk -- it shouldn't touch the source file at all.
    assert source.read_text() == PLAY_TEI
