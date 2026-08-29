from __future__ import annotations

from schmidt_urn_edition import strip_edition


def test_strips_globe_edition_token():
    text = '<ref target="urn:cts:engLit:shakespeare.lr.globe:2.1.1">Lr. II, 1, 1</ref>'
    expected = '<ref target="urn:cts:engLit:shakespeare.lr:2.1.1">Lr. II, 1, 1</ref>'
    result, count = strip_edition(text)
    assert result == expected
    assert count == 1


def test_strips_incomplete_locator_too():
    text = '<ref target="urn:cts:engLit:shakespeare.tn.globe:2.5">Tw. II, 5, 118</ref>'
    expected = '<ref target="urn:cts:engLit:shakespeare.tn:2.5">Tw. II, 5, 118</ref>'
    result, count = strip_edition(text)
    assert result == expected
    assert count == 1


def test_leaves_unrelated_target_attributes_alone():
    text = '<licence target="https://creativecommons.org/licenses/by-sa/4.0/">CC</licence>'
    result, count = strip_edition(text)
    assert result == text
    assert count == 0


def test_counts_multiple():
    text = (
        '<ref target="urn:cts:engLit:shakespeare.h5.globe:1.1.1">a</ref> '
        '<ref target="urn:cts:engLit:shakespeare.h5.globe:2.1.5">b</ref>'
    )
    result, count = strip_edition(text)
    assert count == 2
    assert ".globe:" not in result
