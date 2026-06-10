"""Tests for genres.py — ODD parsing, family/subclass mapping, error handling."""
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
                <category xml:id="drama-line"/>
                <category xml:id="drama-act-scene-line"/>
              </category>
              <category xml:id="verse">
                <category xml:id="verse-stichic"/>
                <category xml:id="verse-book-line"/>
              </category>
              <category xml:id="prose">
                <category xml:id="prose-standard"/>
              </category>
            </taxonomy>
          </classDecl>
        </encodingDesc>
      </teiHeader>
      <text><body><p/></body></text>
    </TEI>
""")

_SUBCLASSES = {
    "drama-line", "drama-act-scene-line",
    "verse-stichic", "verse-book-line",
    "prose-standard",
}
_FAMILIES = {"drama", "verse", "prose"}


@pytest.fixture
def minimal_odd(tmp_path) -> Path:
    p = tmp_path / "test.odd"
    p.write_text(_MINIMAL_ODD, encoding="utf-8")
    return p


class TestLoad:
    def test_returns_genre_taxonomy(self, minimal_odd):
        tax = load(minimal_odd)
        assert isinstance(tax, GenreTaxonomy)

    def test_subclasses(self, minimal_odd):
        assert load(minimal_odd).subclasses == _SUBCLASSES

    def test_families(self, minimal_odd):
        assert load(minimal_odd).families == _FAMILIES

    def test_valid_is_subclasses_plus_families(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.valid == _SUBCLASSES | _FAMILIES

    def test_family_defaults(self, minimal_odd):
        assert load(minimal_odd).family_default == {
            "drama": "drama-line",
            "verse": "verse-stichic",
            "prose": "prose-standard",
        }

    def test_missing_taxonomy_raises(self, tmp_path):
        p = tmp_path / "empty.odd"
        p.write_text(
            '<?xml version="1.0"?>'
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p/></body></text></TEI>',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="No <taxonomy"):
            load(p)

    def test_missing_family_default_raises(self, tmp_path):
        # verse family present but its default subclass (verse-stichic) absent
        odd = _MINIMAL_ODD.replace('<category xml:id="verse-stichic"/>', "")
        p = tmp_path / "bad.odd"
        p.write_text(odd, encoding="utf-8")
        with pytest.raises(ValueError, match="verse-stichic"):
            load(p)


class TestFamily:
    def test_subclass_maps_to_family(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.family("verse-book-line") == "verse"
        assert tax.family("drama-act-scene-line") == "drama"
        assert tax.family("prose-standard") == "prose"

    def test_family_id_maps_to_itself(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.family("verse") == "verse"
        assert tax.family("drama") == "drama"

    def test_unknown_target_raises_value_error(self, minimal_odd):
        tax = load(minimal_odd)
        with pytest.raises(ValueError, match="Unknown genre target"):
            tax.family("not-a-genre")

    def test_error_message_includes_valid_targets(self, minimal_odd):
        tax = load(minimal_odd)
        with pytest.raises(ValueError, match="verse-stichic"):
            tax.family("not-a-genre")


class TestIsFamily:
    def test_bare_family_is_family(self, minimal_odd):
        assert load(minimal_odd).is_family("verse") is True

    def test_subclass_is_not_family(self, minimal_odd):
        assert load(minimal_odd).is_family("verse-stichic") is False


class TestSubclassFor:
    def test_subclass_returns_itself(self, minimal_odd):
        assert load(minimal_odd).subclass_for("verse-book-line") == "verse-book-line"

    def test_family_returns_default(self, minimal_odd):
        tax = load(minimal_odd)
        assert tax.subclass_for("verse") == "verse-stichic"
        assert tax.subclass_for("drama") == "drama-line"
        assert tax.subclass_for("prose") == "prose-standard"

    def test_unknown_raises(self, minimal_odd):
        with pytest.raises(ValueError):
            load(minimal_odd).subclass_for("not-a-genre")


class TestLoadFullOdd:
    """Smoke-test against the real perseus_base.odd when available."""

    def test_full_taxonomy_has_expected_subclasses(self, genre_taxonomy):
        expected = {
            "drama-line", "drama-act-scene-line",
            "verse-stichic", "verse-book-line", "prose-standard",
        }
        assert expected <= genre_taxonomy.valid

    def test_all_subclasses_have_known_family(self, genre_taxonomy):
        for g in genre_taxonomy.subclasses:
            assert genre_taxonomy.family(g) in {"drama", "verse", "prose"}
