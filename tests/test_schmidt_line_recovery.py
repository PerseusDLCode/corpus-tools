from __future__ import annotations

from schmidt_line_recovery import recover_line_numbers

LOCATOR_INDEX = {
    "tmp": {"4.1.267", "4.1.51", "1.2.1"},
    "tn": {"2.5.118"},
    "r2": {"4.1.16", "4.1.104"},
}


def test_digit_landed_in_scene_slot_is_recovered():
    text = '<ref target="urn:cts:engLit:shakespeare.tmp:4.267">Tp. IV, 267</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == '<ref target="urn:cts:engLit:shakespeare.tmp:4.1.267">Tp. IV, 267</ref>'
    assert fixed == 1
    assert unresolved == []


def test_straightforward_missing_line_is_recovered():
    text = '<ref target="urn:cts:engLit:shakespeare.tn:2.5">Tw. II, 5, 118</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == '<ref target="urn:cts:engLit:shakespeare.tn:2.5.118">Tw. II, 5, 118</ref>'
    assert fixed == 1


def test_scene_defaulted_line_dropped_is_recovered():
    text = '<ref target="urn:cts:engLit:shakespeare.r2:4.1">R2 IV, 16</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == '<ref target="urn:cts:engLit:shakespeare.r2:4.1.16">R2 IV, 16</ref>'
    assert fixed == 1


def test_identical_incomplete_target_resolves_independently_per_citation():
    # Two distinct citations sharing the same broken 2-segment target must
    # each resolve to their own correct line, not both get the same fix.
    text = (
        '<ref target="urn:cts:engLit:shakespeare.r2:4.1">R2 IV, 16</ref> '
        '<ref target="urn:cts:engLit:shakespeare.r2:4.1">R2 IV, 104</ref>'
    )
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == (
        '<ref target="urn:cts:engLit:shakespeare.r2:4.1.16">R2 IV, 16</ref> '
        '<ref target="urn:cts:engLit:shakespeare.r2:4.1.104">R2 IV, 104</ref>'
    )
    assert fixed == 2


def test_no_digit_in_display_text_is_unresolved():
    text = '<ref target="urn:cts:engLit:shakespeare.h5:2.0">H5 II Chor.</ref>'
    index = {"h5": {"2.0.1"}}
    result, fixed, unresolved = recover_line_numbers(text, index)
    assert result == text
    assert fixed == 0
    assert unresolved == [{
        "play": "h5", "locator": "2.0", "text": "H5 II Chor.",
        "reason": "no recoverable digit in display text",
    }]


def test_h5_glued_digit_not_mistaken_for_line_number():
    # "H5" contains a digit that must not be read as the citation's line.
    text = '<ref target="urn:cts:engLit:shakespeare.h5:2.0">H5 Chor.</ref>'
    index = {"h5": {"2.0.5"}}
    result, fixed, unresolved = recover_line_numbers(text, index)
    assert fixed == 0
    assert unresolved[0]["reason"] == "no recoverable digit in display text"


def test_existing_scene_segment_preferred_over_ambiguous_broad_search():
    # "1.2" + line "30" should resolve to "1.2.30" directly (the locator's
    # own scene segment is already correct), even though a broad search
    # across every scene in act 1 would also match "1.1.30" and be
    # ambiguous. Real case: Tempest's "an hair, Tp. I, 2, 30".
    text = '<ref target="urn:cts:engLit:shakespeare.tmp:1.2">Tp. I, 2, 30</ref>'
    index = {"tmp": {"1.1.30", "1.2.30"}}
    result, fixed, unresolved = recover_line_numbers(text, index)
    assert result == '<ref target="urn:cts:engLit:shakespeare.tmp:1.2.30">Tp. I, 2, 30</ref>'
    assert fixed == 1
    assert unresolved == []


def test_ambiguous_multiple_matches_is_unresolved():
    text = '<ref target="urn:cts:engLit:shakespeare.tmp:4.51">Tp. IV, 51</ref>'
    index = {"tmp": {"4.1.51", "4.2.51"}}
    result, fixed, unresolved = recover_line_numbers(text, index)
    assert result == text
    assert fixed == 0
    assert unresolved[0]["reason"] == "2 candidate matches (need exactly 1)"


def test_no_match_is_unresolved():
    text = '<ref target="urn:cts:engLit:shakespeare.tmp:4.999">Tp. IV, 999</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == text
    assert fixed == 0
    assert unresolved[0]["reason"] == "0 candidate matches (need exactly 1)"


def test_unknown_play_is_unresolved():
    text = '<ref target="urn:cts:engLit:shakespeare.e3:1.2">E3 I, 2, 29</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert fixed == 0
    assert unresolved[0]["reason"] == "no locator index for play 'e3'"


def test_non_dramatic_work_is_skipped_entirely():
    text = '<ref target="urn:cts:engLit:shakespeare.ven:200">Ven. 200</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == text
    assert fixed == 0
    assert unresolved == []


def test_already_complete_target_is_untouched():
    text = '<ref target="urn:cts:engLit:shakespeare.tmp:1.2.1">Tp. I, 2, 1</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == text
    assert fixed == 0
    assert unresolved == []


def test_non_numeric_locator_out_of_scope_not_reported():
    # e.g. a Chorus-shaped locator that already has a non-digit segment --
    # out of scope for this fix, silently skipped rather than reported.
    text = '<ref target="urn:cts:engLit:shakespeare.h5:2.CHO">H5 Chor. 9</ref>'
    result, fixed, unresolved = recover_line_numbers(text, LOCATOR_INDEX)
    assert result == text
    assert fixed == 0
    assert unresolved == []
