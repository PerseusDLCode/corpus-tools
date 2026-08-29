from __future__ import annotations

from schmidt_dup_citations import collapse_duplicate_citations

# "Abbess"-style: a standalone run of identical bare refs with no <cit> involved.
STANDALONE_RUN = (
    '<entryFree><orth>Abbess,</orth> the governess of a nunnery: '
    '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.117">Err. V, 117</ref>. '
    '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.117">Err. V, 117</ref>\n'
    '            <ref target="urn:cts:engLit:shakespeare.err.globe:5.1.117">Err. V, 117</ref>\n'
    '          </entryFree>'
)

STANDALONE_RUN_EXPECTED = (
    '<entryFree><orth>Abbess,</orth> the governess of a nunnery: '
    '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.117">Err. V, 117</ref>\n'
    '          </entryFree>'
)

# A run that duplicates the citation already inside the preceding <cit> --
# should vanish entirely, not collapse to a leftover single ref.
DUP_OF_CIT = (
    "<cit>\n"
    "  <quote>foo bar,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.shr.globe:5.2.69">Shr. V, 2, 69</ref>\n'
    "</cit>. "
    '<ref target="urn:cts:engLit:shakespeare.shr.globe:5.2.69">Shr. V, 2, 69</ref> '
    '<ref target="urn:cts:engLit:shakespeare.shr.globe:5.2.69">Shr. V, 2, 69</ref> '
    "<cit>\n"
    "  <quote>next sense,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.oth.globe:1.1.1">Oth. I, 1, 1</ref>\n'
    "</cit>."
)

DUP_OF_CIT_EXPECTED = (
    "<cit>\n"
    "  <quote>foo bar,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.shr.globe:5.2.69">Shr. V, 2, 69</ref>\n'
    "</cit>. "
    "<cit>\n"
    "  <quote>next sense,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.oth.globe:1.1.1">Oth. I, 1, 1</ref>\n'
    "</cit>."
)

# A run right after a <cit>, but citing something DIFFERENT from that
# <cit>'s own reference -- must collapse to one, not be deleted.
DIFFERENT_FROM_CIT = (
    "<cit>\n"
    "  <quote>an hundred,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.lll.globe:4.2.63">LLL IV, 2, 63</ref>\n'
    "</cit>. "
    '<ref target="urn:cts:engLit:shakespeare.r2.globe:4.1.16">R2 IV, 16</ref>. '
    '<ref target="urn:cts:engLit:shakespeare.r2.globe:4.1.16">R2 IV, 16</ref>. '
    '<ref target="urn:cts:engLit:shakespeare.2h6.globe:4.8.59">H6B IV, 8, 59</ref>.'
)

DIFFERENT_FROM_CIT_EXPECTED = (
    "<cit>\n"
    "  <quote>an hundred,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.lll.globe:4.2.63">LLL IV, 2, 63</ref>\n'
    "</cit>. "
    '<ref target="urn:cts:engLit:shakespeare.r2.globe:4.1.16">R2 IV, 16</ref>. '
    '<ref target="urn:cts:engLit:shakespeare.2h6.globe:4.8.59">H6B IV, 8, 59</ref>.'
)


def test_standalone_run_collapses_to_one():
    result, dup_of_cit, collapsed = collapse_duplicate_citations(STANDALONE_RUN)
    assert result == STANDALONE_RUN_EXPECTED
    assert dup_of_cit == 0
    assert collapsed == 1


def test_run_duplicating_enclosing_cit_is_deleted_entirely():
    result, dup_of_cit, collapsed = collapse_duplicate_citations(DUP_OF_CIT)
    assert result == DUP_OF_CIT_EXPECTED
    assert dup_of_cit == 1
    assert collapsed == 0


def test_run_differing_from_preceding_cit_collapses_not_deletes():
    result, dup_of_cit, collapsed = collapse_duplicate_citations(DIFFERENT_FROM_CIT)
    assert result == DIFFERENT_FROM_CIT_EXPECTED
    assert dup_of_cit == 0
    assert collapsed == 1


def test_no_duplicates_is_a_no_op():
    text = (
        '<ref target="urn:cts:engLit:shakespeare.oth.globe:1.1.1">Oth. I, 1, 1</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.ham.globe:1.1.1">Hml. I, 1, 1</ref>.'
    )
    result, dup_of_cit, collapsed = collapse_duplicate_citations(text)
    assert result == text
    assert dup_of_cit == 0
    assert collapsed == 0


def test_duplicate_wrapped_differently_still_collapses():
    # "Abbey"-style: the same citation repeated, but one instance happens
    # to be print-line-wrapped across the ref's own text content.
    text = (
        '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.122">Err. V, 122</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.122">Err. V,\n'
        '              122</ref>\n'
        '            <ref target="urn:cts:engLit:shakespeare.err.globe:5.1.122">Err. V, 122</ref>\n'
        '            <ref target="urn:cts:engLit:shakespeare.jn.globe:1.1">John I, 48</ref>.'
    )
    expected = (
        '<ref target="urn:cts:engLit:shakespeare.err.globe:5.1.122">Err. V, 122</ref>\n'
        '            <ref target="urn:cts:engLit:shakespeare.jn.globe:1.1">John I, 48</ref>.'
    )
    result, dup_of_cit, collapsed = collapse_duplicate_citations(text)
    assert result == expected
    assert dup_of_cit == 0
    assert collapsed == 1


def test_different_text_same_target_is_not_collapsed():
    # Same play/line target but different display text (e.g. line-wrap
    # variants) should not be treated as a duplicate.
    text = (
        '<ref target="urn:cts:engLit:shakespeare.oth.globe:1.1.1">Oth. I, 1, 1</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.oth.globe:1.1.1">I, 1, 1</ref>.'
    )
    result, dup_of_cit, collapsed = collapse_duplicate_citations(text)
    assert result == text
    assert dup_of_cit == 0
    assert collapsed == 0
