import pytest

from structure import (
    StructureSignature,
    best_fit,
    classify_structure,
    matches,
    signature_from_xml,
)

_PROSE_FAMILY = ["prose-standard", "prose-chapter-section", "prose-book-section",
                 "prose-book-chapter", "prose-chapter", "prose-section"]
_VERSE_FAMILY = ["verse-stichic", "verse-book-line"]


def _doc(body_inner: str) -> str:
    """Wrap canonical body markup in a minimal TEI document."""
    return (
        '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text>'
        f'<body xml:base="urn:cts:test">{body_inner}</body>'
        "</text></TEI>"
    )


# Canonical (post-normalize-cts) fixtures: every citation div is <div type="x">.
EPIC = _doc('<div type="book" n="1"><l n="1">a</l><l n="2">b</l></div>')
STICHIC = _doc('<l n="1">a</l><l n="2">b</l>')
PROSE_STANDARD = _doc(
    '<div type="book" n="1"><div type="chapter" n="1">'
    '<div type="section" n="1"><p>x</p></div></div></div>'
)
PROSE_SECTION_ONLY = _doc('<div type="section" n="309"><p>x</p></div>')
PROSE_CHAPTER_SECTION = _doc(
    '<div type="chapter" n="1"><div type="section" n="1"><p>x</p></div></div>'
)
PROSE_BOOK_SECTION = _doc(
    '<div type="book" n="1"><div type="section" n="1"><p>x</p></div></div>'
)
PROSE_BOOK_CHAPTER = _doc(
    '<div type="book" n="1"><div type="chapter" n="1"><p>x</p></div></div>'
)
PROSE_CHAPTER_ONLY = _doc('<div type="chapter" n="1"><p>x</p></div>')
DRAMA_LINE = _doc('<div type="episode"><sp><speaker>A</speaker><l n="1">x</l></sp></div>')
DRAMA_ACT_SCENE = _doc(
    '<div type="act" n="1"><div type="scene" n="1"><l n="1">x</l></div></div>'
)

# Raw EpiDoc form (pre-normalization): textpart/@subtype under an edition wrapper,
# with a capitalized subtype as Homer encodes it.
EPIC_EPIDOC = _doc(
    '<div type="edition">'
    '<div type="textpart" subtype="Book" n="1"><l n="1">a</l></div>'
    "</div>"
)
PROSE_EPIDOC = _doc(
    '<div type="edition">'
    '<div type="textpart" subtype="book" n="1">'
    '<div type="textpart" subtype="chapter" n="1">'
    '<div type="textpart" subtype="section" n="1"><p>x</p></div>'
    "</div></div></div>"
)


class TestClassifyStructure:
    def test_epic_signature(self):
        sig = signature_from_xml(EPIC)
        assert sig.div_types == {"book"}
        assert sig.has_lines is True
        assert "book" in sig.lines_under

    def test_stichic_signature(self):
        sig = signature_from_xml(STICHIC)
        assert sig.div_types == frozenset()
        assert sig.has_lines is True

    def test_prose_standard_nesting(self):
        sig = signature_from_xml(PROSE_STANDARD)
        assert sig.div_types == {"book", "chapter", "section"}
        # transitive reachability
        assert ("book", "chapter") in sig.contains
        assert ("book", "section") in sig.contains
        assert ("chapter", "section") in sig.contains
        assert sig.has_lines is False

    def test_section_only_signature(self):
        sig = signature_from_xml(PROSE_SECTION_ONLY)
        assert sig.div_types == {"section"}
        assert sig.has_lines is False

    def test_drama_line_signature(self):
        # episode/sp are transparent; lines are present
        sig = signature_from_xml(DRAMA_LINE)
        assert sig.has_lines is True
        assert sig.div_types == {"episode"}

    def test_returns_signature(self):
        assert isinstance(classify_structure(_to_root(STICHIC)), StructureSignature)

    def test_epidoc_capitalized_subtype_equals_canonical(self):
        # raw EpiDoc subtype="Book" under an edition wrapper -> same as type="book"
        sig = signature_from_xml(EPIC_EPIDOC)
        assert sig.div_types == {"book"}
        assert "book" in sig.lines_under
        assert "edition" not in sig.div_types

    def test_epidoc_prose_nesting(self):
        sig = signature_from_xml(PROSE_EPIDOC)
        assert sig.div_types == {"book", "chapter", "section"}
        assert ("book", "section") in sig.contains


class TestEncodingEquivalence:
    def test_epidoc_epic_matches_book_line(self):
        assert matches("verse-book-line", signature_from_xml(EPIC_EPIDOC)) is True

    def test_epidoc_prose_matches_standard(self):
        assert matches("prose-standard", signature_from_xml(PROSE_EPIDOC)) is True


class TestMatches:
    def test_epic_matches_book_line(self):
        assert matches("verse-book-line", signature_from_xml(EPIC)) is True

    def test_epic_not_prose_standard(self):
        assert matches("prose-standard", signature_from_xml(EPIC)) is False

    def test_stichic_matches(self):
        assert matches("verse-stichic", signature_from_xml(STICHIC)) is True

    def test_stichic_not_book_line(self):
        assert matches("verse-book-line", signature_from_xml(STICHIC)) is False

    def test_prose_standard_matches(self):
        assert matches("prose-standard", signature_from_xml(PROSE_STANDARD)) is True

    def test_section_only_not_prose_standard(self):
        # Plato-style: only sections -> flagged for review
        assert matches("prose-standard", signature_from_xml(PROSE_SECTION_ONLY)) is False

    def test_drama_line_matches(self):
        assert matches("drama-line", signature_from_xml(DRAMA_LINE)) is True

    def test_drama_line_not_act_scene(self):
        assert matches("drama-act-scene-line", signature_from_xml(DRAMA_LINE)) is False

    def test_act_scene_matches(self):
        assert matches("drama-act-scene-line", signature_from_xml(DRAMA_ACT_SCENE)) is True

    def test_unknown_subclass_raises(self):
        with pytest.raises(ValueError):
            matches("not-a-subclass", signature_from_xml(STICHIC))

    def test_section_only_matches_prose_section(self):
        assert matches("prose-section", signature_from_xml(PROSE_SECTION_ONLY)) is True

    def test_chapter_section_matches(self):
        sig = signature_from_xml(PROSE_CHAPTER_SECTION)
        assert matches("prose-chapter-section", sig) is True
        assert matches("prose-standard", sig) is False  # no book

    def test_book_section_matches(self):
        sig = signature_from_xml(PROSE_BOOK_SECTION)
        assert matches("prose-book-section", sig) is True
        assert matches("prose-chapter-section", sig) is False  # no chapter


class TestBestFit:
    def test_full_nesting_resolves_to_standard(self):
        # book->chapter->section fits every prose subclass; deepest wins
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_STANDARD)) == "prose-standard"

    def test_chapter_section_resolves(self):
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_CHAPTER_SECTION)) == "prose-chapter-section"

    def test_book_section_resolves(self):
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_BOOK_SECTION)) == "prose-book-section"

    def test_section_only_resolves(self):
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_SECTION_ONLY)) == "prose-section"

    def test_flat_verse_resolves_to_stichic(self):
        # an "epic" suggestion on flat lines resolves to stichic, not book-line
        assert best_fit(_VERSE_FAMILY, signature_from_xml(STICHIC)) == "verse-stichic"

    def test_book_line_resolves_to_book_line(self):
        assert best_fit(_VERSE_FAMILY, signature_from_xml(EPIC)) == "verse-book-line"

    def test_no_fit_returns_none(self):
        # structureless prose body fits no prose subclass
        empty = signature_from_xml(_doc("<p>x</p>"))
        assert best_fit(_PROSE_FAMILY, empty) is None

    def test_book_chapter_resolves(self):
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_BOOK_CHAPTER)) == "prose-book-chapter"

    def test_chapter_only_resolves(self):
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_CHAPTER_ONLY)) == "prose-chapter"

    def test_full_nesting_still_resolves_to_standard(self):
        # with the extra subclasses, book->chapter->section must still win as deepest
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_STANDARD)) == "prose-standard"

    def test_chapter_section_still_resolves(self):
        # chapter->section must not be shadowed by the new chapter-only subclass
        assert best_fit(_PROSE_FAMILY, signature_from_xml(PROSE_CHAPTER_SECTION)) == "prose-chapter-section"


class TestDescribe:
    def test_describe_epic(self):
        assert signature_from_xml(EPIC).describe() == "book+l"

    def test_describe_prose(self):
        assert signature_from_xml(PROSE_STANDARD).describe() == "book+chapter+section"

    def test_describe_stichic(self):
        assert signature_from_xml(STICHIC).describe() == "l"


def _to_root(xml: str):
    from lxml import etree
    return etree.fromstring(xml.encode("utf-8"))
