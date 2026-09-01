from __future__ import annotations

from schmidt_cit_merge import merge_orphaned_citations


# "an hundred"-style: first citation captured in <cit>, further citations
# for the same quote left as bare orphaned <ref> siblings, up to the next
# <cit> (a genuinely new sense, which itself has no trailing orphans here
# and so is left untouched). All gaps here are pure punctuation, so every
# orphan is absorbed and every internal separator dropped -- except the
# final one, which stays outside the merged <cit>.
ORPHANED = (
    "<entryFree><orth>Abatement,</orth> <cit>\n"
    "  <quote>an hundred,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.lll:4.2.63">LLL IV, 2, 63</ref>\n'
    "</cit>. "
    '<ref target="urn:cts:engLit:shakespeare.r2:4.1.16">R2 IV, 16</ref>. '
    '<ref target="urn:cts:engLit:shakespeare.2h6:4.8.59">H6B IV, 8, 59</ref>. <cit>\n'
    "  <quote>an hypocrite,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.mm:5.1.41">Meas. V, 41</ref>\n'
    "</cit>. </entryFree>"
)

ORPHANED_EXPECTED = (
    "<entryFree><orth>Abatement,</orth> <cit>\n"
    "  <quote>an hundred,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.lll:4.2.63">LLL IV, 2, 63</ref>\n'
    '<ref target="urn:cts:engLit:shakespeare.r2:4.1.16">R2 IV, 16</ref>'
    '<ref target="urn:cts:engLit:shakespeare.2h6:4.8.59">H6B IV, 8, 59</ref></cit>. '
    "<cit>\n"
    "  <quote>an hypocrite,</quote>\n"
    '  <ref target="urn:cts:engLit:shakespeare.mm:5.1.41">Meas. V, 41</ref>\n'
    "</cit>. </entryFree>"
)


def test_orphaned_refs_absorbed_dropping_internal_punctuation():
    result, stats = merge_orphaned_citations(ORPHANED)
    assert result == ORPHANED_EXPECTED
    assert stats.cits_merged == 1
    assert stats.refs_absorbed == 2
    assert stats.full_merges == 1
    assert stats.partial_merges == 0


def test_cit_with_no_trailing_refs_is_untouched():
    text = (
        "<cit>\n"
        "  <quote>an host,</quote>\n"
        '  <ref target="urn:cts:engLit:shakespeare.2h6:3.1.342">H6B III, 1, 342</ref>\n'
        "</cit>. <cit>\n"
        "  <quote>an hostess,</quote>\n"
        '  <ref target="urn:cts:engLit:shakespeare.tro:3.3.253">Troil. III, 3, 253</ref>\n'
        "</cit>."
    )
    result, stats = merge_orphaned_citations(text)
    assert result == text
    assert stats.cits_merged == 0
    assert stats.refs_absorbed == 0


def test_orphans_absorbed_up_to_entryFree_boundary():
    # "Presently"-style: the final <cit> in an entry absorbs every
    # remaining orphaned ref up to </entryFree>, not just up to the next
    # <cit> (there is none). Final separator (". ") stays outside.
    text = (
        "<entryFree><orth>Presently,</orth> <cit>\n"
        "  <quote>and then I'll p. attend you,</quote>\n"
        '  <ref target="urn:cts:engLit:shakespeare.wt:1.2.451">Wint. I, 2, 451</ref>\n'
        "</cit>. "
        '<ref target="urn:cts:engLit:shakespeare.oth:1.3.11">Oth. I, 3, 11</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.lr:1.5.1">Lr. I, 5, 1</ref>. '
        "</entryFree>"
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<entryFree><orth>Presently,</orth> <cit>\n"
        "  <quote>and then I'll p. attend you,</quote>\n"
        '  <ref target="urn:cts:engLit:shakespeare.wt:1.2.451">Wint. I, 2, 451</ref>\n'
        '<ref target="urn:cts:engLit:shakespeare.oth:1.3.11">Oth. I, 3, 11</ref>'
        '<ref target="urn:cts:engLit:shakespeare.lr:1.5.1">Lr. I, 5, 1</ref></cit>. '
        "</entryFree>"
    )
    assert result == expected
    assert stats.cits_merged == 1
    assert stats.refs_absorbed == 2
    assert stats.full_merges == 1


def test_no_cit_at_all_is_a_no_op():
    text = (
        '<entryFree><orth>A,</orth> the first letter: '
        '<ref target="urn:cts:engLit:shakespeare.lll:5.1.50">LLL V, 1, 50</ref>. </entryFree>'
    )
    result, stats = merge_orphaned_citations(text)
    assert result == text
    assert stats.cits_merged == 0
    assert stats.refs_absorbed == 0


def test_consecutive_cits_each_resolved_independently():
    # A run of three <cit>s where the first two each have exactly one
    # orphaned ref, and the third has none -- each decision is independent.
    text = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a</ref></cit>. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>. '
        "<cit><quote>b,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.3">b</ref></cit>. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.4">b2</ref>. '
        "<cit><quote>c,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.5">c</ref></cit>.'
    )
    result, stats = merge_orphaned_citations(text)
    assert stats.cits_merged == 2
    assert stats.refs_absorbed == 2
    assert result.count("<cit>") == 3
    assert result.count("</cit>") == 3


def test_stops_at_first_unrecognized_gap_partial_merge():
    # Two orphans absorbed cleanly (punctuation gaps), then genuinely new
    # prose ("and") introduces a third ref that must NOT be swept in.
    text = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref></cit>. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.3">a3</ref> and '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.4">a4</ref>. <cit><quote>b,</quote>'
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.5">b1</ref></cit>.'
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>'
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>'
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.3">a3</ref></cit> and '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.4">a4</ref>. <cit><quote>b,</quote>'
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.5">b1</ref></cit>.'
    )
    assert result == expected
    assert stats.cits_merged == 1
    assert stats.refs_absorbed == 2
    assert stats.partial_merges == 1
    assert stats.full_merges == 0
    assert stats.residual_gaps["and"] == 1


def test_cf_gap_wrapped_in_note():
    text = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref></cit>; cf. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>. <cit>'
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>'
        "<note>; cf.</note> "
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref></cit>. <cit>'
    )
    assert result == expected
    assert stats.notes_wrapped == 1
    assert stats.refs_absorbed == 1


def test_parenthetical_cf_pair_wrapped_in_matching_notes():
    # The very common "(cf. <ref>...</ref>)." shape: both the opening and
    # closing fragments are recognized and independently note-wrapped,
    # preserving the parenthetical.
    text = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref></cit> (cf. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>). <cit>'
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>'
        " <note>(cf.</note> "
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>'
        "<note>).</note> </cit><cit>"
    )
    assert result == expected
    assert stats.notes_wrapped == 2
    assert stats.refs_absorbed == 1


def test_qqff_parenthetical_wrapped_in_note():
    text = (
        "<cit><quote>a hundred,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref></cit> '
        "(Qq. <mentioned>a hundred</mentioned>). "
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>. <cit>'
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<cit><quote>a hundred,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>'
        " <note>(Qq. <mentioned>a hundred</mentioned>).</note> "
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref></cit>. <cit>'
    )
    assert result == expected
    assert stats.notes_wrapped == 1
    assert stats.refs_absorbed == 1


def test_lb_is_an_absorption_boundary():
    # A sense boundary marked only by <lb/>, not <cit>/</entryFree>, must
    # also stop absorption -- confirmed a corpus finding, not hypothetical.
    text = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref></cit>. '
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref>. '
        '<lb n="2"/><ref target="urn:cts:engLit:shakespeare.x:1.1.3">a3</ref>.'
    )
    result, stats = merge_orphaned_citations(text)
    expected = (
        "<cit><quote>a,</quote>"
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.1">a1</ref>'
        '<ref target="urn:cts:engLit:shakespeare.x:1.1.2">a2</ref></cit>. '
        '<lb n="2"/><ref target="urn:cts:engLit:shakespeare.x:1.1.3">a3</ref>.'
    )
    assert result == expected
    assert stats.refs_absorbed == 1
