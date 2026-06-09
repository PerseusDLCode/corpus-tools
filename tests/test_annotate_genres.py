"""Tests for commands/annotate_genres.py."""
from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from lxml import etree

from commands.annotate_genres import (
    StructuralSignals,
    annotate_work,
    build_prompt,
    compute_confidence,
    gather_signals,
    load_genre_descriptions,
    read_groupname,
    read_work_metadata,
    write_genre,
    _is_work_level,
)
from genres import load as load_genres

# ---------------------------------------------------------------------------
# ODD fixture (minimal, with catDesc for descriptions)
# ---------------------------------------------------------------------------

_MINIMAL_ODD = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <encodingDesc>
          <classDecl>
            <taxonomy xml:id="perseus-genre">
              <category xml:id="drama">
                <category xml:id="attic-tragedy">
                  <catDesc>Attic tragedy (Aeschylus, Sophocles, Euripides).</catDesc>
                </category>
                <category xml:id="attic-comedy">
                  <catDesc>Attic comedy (Aristophanes, Menander).</catDesc>
                </category>
              </category>
              <category xml:id="verse">
                <category xml:id="verse-epic">
                  <catDesc>Epic verse (Homer, Virgil).</catDesc>
                </category>
              </category>
              <category xml:id="prose">
                <category xml:id="prose-historiography">
                  <catDesc>Historiography (Thucydides, Herodotus).</catDesc>
                </category>
                <category xml:id="prose-dialogue">
                  <catDesc>Platonic dialogue.</catDesc>
                </category>
              </category>
            </taxonomy>
          </classDecl>
        </encodingDesc>
      </teiHeader>
      <text><body><p/></body></text>
    </TEI>
""")

_TEXTGROUP_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts"
                  urn="urn:cts:greekLit:tlg0003">
      <ti:groupname xml:lang="en">Thucydides</ti:groupname>
    </ti:textgroup>
""")

_WORK_CTS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
      <ti:title xml:lang="eng">History of the Peloponnesian War</ti:title>
      <ti:edition urn="urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"
                  workUrn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
        <ti:label xml:lang="grc">Ἱστορίαι</ti:label>
        <ti:description xml:lang="eng">Thucydides. Historiae. Jones, editor. Oxford, 1910.</ti:description>
      </ti:edition>
    </ti:work>
""")

_WORK_CTS_WITH_GENRE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts"
             urn="urn:cts:greekLit:tlg0011.tlg001" xml:lang="grc">
      <ti:title xml:lang="eng">Medea</ti:title>
      <ti:genre confidence="high">attic-tragedy</ti:genre>
    </ti:work>
""")

_PROSE_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>Test</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body>
        <div type="edition"><div type="textpart" subtype="book" n="1">
          <p>Paragraph one.</p><p>Paragraph two.</p>
        </div></div>
      </body></text>
    </TEI>
""")

_DRAMA_TEI = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc><titleStmt><title>Test</title></titleStmt>
        <publicationStmt><p/></publicationStmt><sourceDesc><p/></sourceDesc>
      </fileDesc></teiHeader>
      <text><body>
        <div type="edition">
          <sp><speaker>Actor</speaker><p>Speech text.</p></sp>
          <sp><speaker>Actor</speaker><p>More speech.</p></sp>
        </div>
      </body></text>
    </TEI>
""")


# ---------------------------------------------------------------------------
# Directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def odd_file(tmp_path) -> Path:
    p = tmp_path / "perseus_base.odd"
    p.write_text(_MINIMAL_ODD, encoding="utf-8")
    return p


@pytest.fixture
def prose_work_dir(tmp_path) -> tuple[Path, Path]:
    """Returns (data_dir, work_cts_path) for an unannotated prose work."""
    data = tmp_path / "data"
    tg_dir = data / "tlg0003"
    work_dir = tg_dir / "tlg001"
    work_dir.mkdir(parents=True)

    (tg_dir / "__cts__.xml").write_text(_TEXTGROUP_CTS, encoding="utf-8")
    work_cts = work_dir / "__cts__.xml"
    work_cts.write_text(_WORK_CTS, encoding="utf-8")
    (work_dir / "tlg0003.tlg001.test.xml").write_text(_PROSE_TEI, encoding="utf-8")
    return data, work_cts


@pytest.fixture
def drama_work_dir(tmp_path) -> tuple[Path, Path]:
    """Returns (data_dir, work_cts_path) for an unannotated drama work."""
    data = tmp_path / "data"
    tg_dir = data / "tlg0011"
    work_dir = tg_dir / "tlg001"
    work_dir.mkdir(parents=True)

    (tg_dir / "__cts__.xml").write_text(
        _TEXTGROUP_CTS.replace("tlg0003", "tlg0011").replace("Thucydides", "Euripides"),
        encoding="utf-8",
    )
    work_cts = work_dir / "__cts__.xml"
    work_cts.write_text(
        _WORK_CTS.replace("tlg0003", "tlg0011"),
        encoding="utf-8",
    )
    (work_dir / "tlg0011.tlg001.test.xml").write_text(_DRAMA_TEI, encoding="utf-8")
    return data, work_cts


@pytest.fixture
def annotated_work_dir(tmp_path) -> tuple[Path, Path]:
    """Returns (data_dir, work_cts_path) for a work that already has <ti:genre>."""
    data = tmp_path / "data"
    work_dir = data / "tlg0011" / "tlg001"
    work_dir.mkdir(parents=True)
    (data / "tlg0011" / "__cts__.xml").write_text(_TEXTGROUP_CTS, encoding="utf-8")
    work_cts = work_dir / "__cts__.xml"
    work_cts.write_text(_WORK_CTS_WITH_GENRE, encoding="utf-8")
    return data, work_cts


def _mock_client(genre_response: str) -> MagicMock:
    content = MagicMock()
    content.text = genre_response
    response = MagicMock()
    response.content = [content]
    client = MagicMock()
    client.messages.create.return_value = response
    return client


# ---------------------------------------------------------------------------
# gather_signals
# ---------------------------------------------------------------------------

class TestGatherSignals:
    def test_prose_file_counts_paragraphs(self, prose_work_dir):
        _, work_cts = prose_work_dir
        signals = gather_signals(work_cts.parent)
        assert signals.p_count == 2
        assert signals.l_count == 0
        assert signals.sp_count == 0

    def test_drama_file_counts_speech_elements(self, drama_work_dir):
        _, work_cts = drama_work_dir
        signals = gather_signals(work_cts.parent)
        assert signals.sp_count == 2
        assert signals.l_count == 0

    def test_div_types_collected(self, prose_work_dir):
        _, work_cts = prose_work_dir
        signals = gather_signals(work_cts.parent)
        assert "edition" in signals.div_types or "textpart" in signals.div_types

    def test_skips_cts_xml(self, prose_work_dir):
        _, work_cts = prose_work_dir
        # __cts__.xml should not be parsed as TEI
        signals = gather_signals(work_cts.parent)
        assert signals.p_count == 2  # only from the TEI file, not __cts__.xml

    def test_skips_unparseable_files(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        (work_dir / "bad.xml").write_text("not valid xml <<<", encoding="utf-8")
        signals = gather_signals(work_dir)
        assert signals.p_count == 0


# ---------------------------------------------------------------------------
# StructuralSignals.inferred_family
# ---------------------------------------------------------------------------

class TestInferredFamily:
    def test_speech_implies_drama(self):
        assert StructuralSignals(sp_count=5).inferred_family() == "drama"

    def test_lines_dominating_implies_verse(self):
        assert StructuralSignals(l_count=100, p_count=2).inferred_family() == "verse"

    def test_paragraphs_dominating_implies_prose(self):
        assert StructuralSignals(p_count=50, l_count=0).inferred_family() == "prose"

    def test_empty_signals_returns_none(self):
        assert StructuralSignals().inferred_family() is None

    def test_drama_overrides_lines(self):
        assert StructuralSignals(sp_count=3, l_count=200).inferred_family() == "drama"


# ---------------------------------------------------------------------------
# read_groupname / read_work_metadata
# ---------------------------------------------------------------------------

class TestReadHelpers:
    def test_reads_groupname(self, prose_work_dir):
        _, work_cts = prose_work_dir
        name = read_groupname(work_cts.parent.parent / "__cts__.xml")
        assert name == "Thucydides"

    def test_reads_title(self, prose_work_dir):
        _, work_cts = prose_work_dir
        title, _ = read_work_metadata(work_cts)
        assert title == "History of the Peloponnesian War"

    def test_reads_description(self, prose_work_dir):
        _, work_cts = prose_work_dir
        _, desc = read_work_metadata(work_cts)
        assert "Thucydides" in desc

    def test_missing_file_returns_empty(self, tmp_path):
        assert read_groupname(tmp_path / "missing.xml") == ""
        assert read_work_metadata(tmp_path / "missing.xml") == ("", "")


# ---------------------------------------------------------------------------
# load_genre_descriptions
# ---------------------------------------------------------------------------

class TestLoadGenreDescriptions:
    def test_returns_descriptions_for_leaf_genres(self, odd_file):
        descs = load_genre_descriptions(odd_file)
        assert "attic-tragedy" in descs
        assert "Aeschylus" in descs["attic-tragedy"]

    def test_does_not_include_family_categories(self, odd_file):
        descs = load_genre_descriptions(odd_file)
        assert "drama" not in descs
        assert "verse" not in descs

    def test_empty_when_no_taxonomy(self, tmp_path):
        p = tmp_path / "empty.odd"
        p.write_text(
            '<?xml version="1.0"?>'
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p/></body></text></TEI>',
            encoding="utf-8",
        )
        assert load_genre_descriptions(p) == {}


# ---------------------------------------------------------------------------
# compute_confidence
# ---------------------------------------------------------------------------

class TestComputeConfidence:
    def test_high_when_structural_and_api_agree(self, odd_file):
        tax = load_genres(odd_file)
        signals = StructuralSignals(p_count=50)
        assert compute_confidence("prose-historiography", signals, tax) == "high"

    def test_medium_when_structural_and_api_disagree(self, odd_file):
        tax = load_genres(odd_file)
        signals = StructuralSignals(p_count=50)
        assert compute_confidence("attic-tragedy", signals, tax) == "medium"

    def test_medium_when_no_structural_signal(self, odd_file):
        tax = load_genres(odd_file)
        signals = StructuralSignals()
        assert compute_confidence("verse-epic", signals, tax) == "medium"

    def test_low_for_unknown_genre(self, odd_file):
        tax = load_genres(odd_file)
        signals = StructuralSignals(p_count=10)
        assert compute_confidence("unknown", signals, tax) == "low"


# ---------------------------------------------------------------------------
# write_genre
# ---------------------------------------------------------------------------

class TestWriteGenre:
    def test_writes_genre_element(self, prose_work_dir):
        _, work_cts = prose_work_dir
        write_genre(work_cts, "prose-historiography", "high")
        tree = etree.parse(str(work_cts))
        genres = tree.xpath(
            "//ti:genre", namespaces={"ti": "http://chs.harvard.edu/xmlns/cts"}
        )
        assert len(genres) == 1
        assert genres[0].text == "prose-historiography"
        assert genres[0].get("confidence") == "high"

    def test_overwrites_existing_genre(self, annotated_work_dir):
        _, work_cts = annotated_work_dir
        write_genre(work_cts, "attic-comedy", "medium")
        tree = etree.parse(str(work_cts))
        genres = tree.xpath(
            "//ti:genre", namespaces={"ti": "http://chs.harvard.edu/xmlns/cts"}
        )
        assert len(genres) == 1
        assert genres[0].text == "attic-comedy"

    def test_preserves_other_elements(self, prose_work_dir):
        _, work_cts = prose_work_dir
        write_genre(work_cts, "prose-historiography", "high")
        tree = etree.parse(str(work_cts))
        titles = tree.xpath(
            "//ti:title", namespaces={"ti": "http://chs.harvard.edu/xmlns/cts"}
        )
        assert titles


# ---------------------------------------------------------------------------
# annotate_work
# ---------------------------------------------------------------------------

class TestAnnotateWork:
    def test_returns_none_when_already_annotated(self, annotated_work_dir, odd_file):
        _, work_cts = annotated_work_dir
        tax = load_genres(odd_file)
        descs = load_genre_descriptions(odd_file)
        client = _mock_client("prose-historiography")
        result = annotate_work(work_cts, client, tax, descs, "test-model", dry_run=False)
        assert result is None
        client.messages.create.assert_not_called()

    def test_calls_api_and_writes_genre(self, prose_work_dir, odd_file):
        _, work_cts = prose_work_dir
        tax = load_genres(odd_file)
        descs = load_genre_descriptions(odd_file)
        client = _mock_client("prose-historiography")

        genre, confidence = annotate_work(
            work_cts, client, tax, descs, "test-model", dry_run=False
        )
        assert genre == "prose-historiography"
        assert confidence in {"high", "medium", "low"}
        client.messages.create.assert_called_once()

        # Verify written to disk
        tree = etree.parse(str(work_cts))
        genres = tree.xpath(
            "//ti:genre", namespaces={"ti": "http://chs.harvard.edu/xmlns/cts"}
        )
        assert genres[0].text == "prose-historiography"

    def test_invalid_api_response_writes_unknown(self, prose_work_dir, odd_file):
        _, work_cts = prose_work_dir
        tax = load_genres(odd_file)
        descs = load_genre_descriptions(odd_file)
        client = _mock_client("not-a-real-genre")

        genre, confidence = annotate_work(
            work_cts, client, tax, descs, "test-model", dry_run=False
        )
        assert genre == "unknown"
        assert confidence == "low"

    def test_dry_run_does_not_write(self, prose_work_dir, odd_file):
        _, work_cts = prose_work_dir
        original = work_cts.read_text()
        tax = load_genres(odd_file)
        descs = load_genre_descriptions(odd_file)
        client = _mock_client("prose-historiography")

        annotate_work(work_cts, client, tax, descs, "test-model", dry_run=True)
        assert work_cts.read_text() == original

    def test_passes_model_to_api(self, prose_work_dir, odd_file):
        _, work_cts = prose_work_dir
        tax = load_genres(odd_file)
        descs = load_genre_descriptions(odd_file)
        client = _mock_client("prose-historiography")

        annotate_work(work_cts, client, tax, descs, "claude-opus-test", dry_run=True)
        call_kwargs = client.messages.create.call_args
        assert call_kwargs.kwargs.get("model") == "claude-opus-test"


# ---------------------------------------------------------------------------
# _is_work_level
# ---------------------------------------------------------------------------

class TestIsWorkLevel:
    def test_work_level_file_returns_true(self, prose_work_dir):
        data_dir, work_cts = prose_work_dir
        assert _is_work_level(work_cts, data_dir) is True

    def test_textgroup_level_file_returns_false(self, prose_work_dir):
        data_dir, work_cts = prose_work_dir
        tg_cts = work_cts.parent.parent / "__cts__.xml"
        assert _is_work_level(tg_cts, data_dir) is False
