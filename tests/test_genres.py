"""Tests for genres.py — ODD parsing, family mapping, error handling."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from genres import GenreTaxonomy, load

_MINIMAL_ODD = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader>
        <encodingDesc>
          <classDecl>
            <taxonomy xml:id="perseus-genre">
              <category xml:id="drama">
                <category xml:id="attic-tragedy"/>
                <category xml:id="attic-comedy"/>
              </category>
              <category xml:id="verse">
                <category xml:id="verse-epic"/>
                <category xml:id="verse-didactic"/>
              </category>
              <category xml:id="prose">
                <category xml:id="prose-historiography"/>
                <category xml:id="prose-dialogue"/>
              </category>
            </taxonomy>
          </classDecl>
        </encodingDesc>
      </teiHeader>
      <text><body><p/></body></text>
    </TEI>
""")


@pytest.fixture
def minimal_odd(tmp_path) -> Path:
    p = tmp_path / "test.odd"
    p.write_text(_MINIMAL_ODD, encoding="utf-8")
    return p


class TestLoad:
    def test_returns_genre_taxonomy(self, minimal_odd):
        tax = load(minimal_odd)
        assert isinstance(tax, GenreTaxonomy)

    def test_valid_contains_leaf_genres(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.valid == {
            "attic-tragedy", "attic-comedy",
            "verse-epic", "verse-didactic",
            "prose-historiography", "prose-dialogue",
        }

    def test_family_categories_not_in_valid(self, minimal_odd):
        tax = load(minimal_odd)
        assert "drama" not in tax.valid
        assert "verse" not in tax.valid
        assert "prose" not in tax.valid

    def test_missing_taxonomy_raises(self, tmp_path):
        p = tmp_path / "empty.odd"
        p.write_text(
            '<?xml version="1.0"?>'
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p/></body></text></TEI>',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="No <taxonomy"):
            load(p)


class TestGenreTaxonomyFamily:
    def test_drama_leaf_maps_to_drama(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.family("attic-tragedy") == "drama"
        assert tax.family("attic-comedy") == "drama"

    def test_verse_leaf_maps_to_verse(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.family("verse-epic") == "verse"
        assert tax.family("verse-didactic") == "verse"

    def test_prose_leaf_maps_to_prose(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.family("prose-historiography") == "prose"
        assert tax.family("prose-dialogue") == "prose"

    def test_unknown_genre_raises_value_error(self, minimal_odd):
        tax = load(minimal_odd)
        with pytest.raises(ValueError, match="Unknown genre"):
            tax.family("not-a-genre")

    def test_error_message_includes_valid_genres(self, minimal_odd):
        tax = load(minimal_odd)
        with pytest.raises(ValueError, match="attic-tragedy"):
            tax.family("not-a-genre")


class TestLoadFullOdd:
    """Smoke-test against the real perseus_base.odd when available."""

    def test_full_taxonomy_has_expected_genres(self, genre_taxonomy):
        expected = {
            "attic-tragedy", "verse-epic", "prose-historiography",
            "prose-dialogue", "attic-comedy", "roman-comedy",
        }
        assert expected <= genre_taxonomy.valid

    def test_all_genres_have_known_family(self, genre_taxonomy):
        for g in genre_taxonomy.valid:
            assert genre_taxonomy.family(g) in {"drama", "verse", "prose"}
