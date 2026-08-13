from __future__ import annotations

import pytest

from tln_globe_map import (
    CorpusMap,
    DuplicateKeyError,
    LineRecord,
    PlayMapper,
    build_corpus_map,
)


TEI_HEADER = """<?xml version="1.0" encoding="utf-8"?>
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
  <text>
    <body>
      <div type="act" n="1">
        <div type="scene" n="1">
          {body}
        </div>
      </div>
    </body>
  </text>
</TEI>
"""


@pytest.fixture
def hamlet_excerpt(shared_datadir):
    return PlayMapper(shared_datadir / "hamlet-excerpt.xml")


@pytest.fixture
def macbeth_excerpt(shared_datadir):
    return PlayMapper(shared_datadir / "macbeth-excerpt.xml")


def test_records_capture_lb_and_l_elements(hamlet_excerpt):
    records = hamlet_excerpt.records
    assert records == [
        LineRecord(tln=1, globe="1.1.1", part=None, element="lb"),
        LineRecord(tln=2, globe="1.1.2", part=None, element="l"),
        LineRecord(tln=3, globe="1.1.3", part=None, element="lb"),
        LineRecord(tln=8, globe="1.1.8", part=None, element="l"),
        LineRecord(tln=9, globe="1.1.9", part=None, element="l"),
    ]


def test_stage_directions_are_not_captured(hamlet_excerpt):
    globes = {r.globe for r in hamlet_excerpt.records}
    assert "SD 1.1.0" not in globes


def test_globe_map_and_tln_map_are_inverses(hamlet_excerpt):
    assert hamlet_excerpt.globe_map == {
        "1.1.1": 1, "1.1.2": 2, "1.1.3": 3, "1.1.8": 8, "1.1.9": 9,
    }
    assert hamlet_excerpt.tln_map == {
        1: "1.1.1", 2: "1.1.2", 3: "1.1.3", 8: "1.1.8", 9: "1.1.9",
    }


def test_hamlet_metadata(hamlet_excerpt):
    assert hamlet_excerpt.title == "Hamlet"
    assert hamlet_excerpt.dracor_id == "shake000032"
    assert hamlet_excerpt.folger_idno == "Ham"
    assert hamlet_excerpt.playid == "ham"


def test_split_lines_carry_part_attribute(macbeth_excerpt):
    by_tln = {r.tln: r for r in macbeth_excerpt.records}
    assert by_tln[6].part == "I"
    assert by_tln[7].part == "F"
    assert by_tln[1].part is None


def test_macbeth_metadata(macbeth_excerpt):
    assert macbeth_excerpt.title == "Macbeth"
    assert macbeth_excerpt.playid == "mac"


def test_duplicate_globe_reference_fails_loudly(tmp_path):
    body = (
        '<l xml:id="ftln-0001" n="1.1.1">Line one. </l>'
        '<l xml:id="ftln-0002" n="1.1.1">Duplicate globe ref. </l>'
    )
    source = tmp_path / "dup-globe.xml"
    source.write_text(TEI_HEADER.format(body=body))
    mapper = PlayMapper(source)
    with pytest.raises(DuplicateKeyError):
        mapper.globe_map


def test_duplicate_tln_fails_loudly(tmp_path):
    # Different xml:id strings (libxml2 rejects literal xml:id duplicates
    # at parse time) that nonetheless parse to the same integer TLN.
    body = (
        '<l xml:id="ftln-0007" n="1.1.1">Line one. </l>'
        '<l xml:id="ftln-007" n="1.1.2">Duplicate TLN. </l>'
    )
    source = tmp_path / "dup-tln.xml"
    source.write_text(TEI_HEADER.format(body=body))
    mapper = PlayMapper(source)
    with pytest.raises(DuplicateKeyError):
        mapper.tln_map


def test_build_corpus_map_and_query(tmp_path, shared_datadir):
    import shutil

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    shutil.copy(shared_datadir / "hamlet-excerpt.xml", corpus_dir / "hamlet.xml")
    shutil.copy(shared_datadir / "macbeth-excerpt.xml", corpus_dir / "macbeth.xml")

    data = build_corpus_map(corpus_dir)
    assert set(data["plays"]) == {"ham", "mac"}
    assert data["plays"]["ham"]["source_file"] == "hamlet.xml"
    assert data["plays"]["ham"]["title"] == "Hamlet"

    corpus_map = CorpusMap(data)
    assert corpus_map.line_number_map("ham", tln=2) == {
        "tln": 2, "globe": "1.1.2", "part": None, "element": "l",
    }
    assert corpus_map.line_number_map("ham", globe="1.1.2")["tln"] == 2
    assert corpus_map.line_number_map("mac", tln=6)["part"] == "I"
    assert corpus_map.line_number_map("ham", tln=9999) is None
    assert corpus_map.line_number_map("nonexistent-play", tln=1) is None


def test_build_corpus_map_rejects_playid_collision(tmp_path, shared_datadir):
    import shutil

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    shutil.copy(shared_datadir / "hamlet-excerpt.xml", corpus_dir / "hamlet-1.xml")
    shutil.copy(shared_datadir / "hamlet-excerpt.xml", corpus_dir / "hamlet-2.xml")

    with pytest.raises(DuplicateKeyError):
        build_corpus_map(corpus_dir)


def test_line_number_map_requires_exactly_one_lookup_kind():
    corpus_map = CorpusMap({"plays": {}})
    with pytest.raises(ValueError):
        corpus_map.line_number_map("ham")
    with pytest.raises(ValueError):
        corpus_map.line_number_map("ham", globe="1.1.1", tln=1)


def test_playid_matches_canonical_englit_filenames(
    shakedracor_tei_dir, canonical_englit_shakespeare_dir
):
    mismatches = []
    for source in sorted(shakedracor_tei_dir.glob("*.xml")):
        playid = PlayMapper(source).playid
        if playid is None or not (canonical_englit_shakespeare_dir / f"{playid}.xml").exists():
            mismatches.append((source.name, playid))
    assert mismatches == [], (
        f"ShakeDraCor playids with no matching canonical-engLit file: {mismatches}"
    )
