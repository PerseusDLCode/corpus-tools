from __future__ import annotations

OPEN_OLD = "<cit>\n              <cit>\n"
OPEN_NEW = "<cit>\n"
CLOSE_OLD = "</cit>\n\n            </cit>"
CLOSE_NEW = "</cit>"


class UnbalancedCitWrapperError(ValueError):
    """Raised when the doubled-<cit> open/close patterns don't occur in equal
    counts, meaning the file doesn't match the uniform wrapping this module
    assumes."""


def unwrap_doubled_cit(text: str) -> tuple[str, int]:
    """Strip the empty outer <cit> that wraps every real <cit>...</cit> in
    the Schmidt lexicon (an artifact of automatic tagging), via raw-text
    substitution rather than a parse/reserialize pass.

    schmidt.lexicon.perseus-eng1.xml is hand-formatted; reserializing the
    parsed tree collapses tag-internal line breaks across the whole file,
    producing a diff far larger than the actual edit. The doubled wrapping
    is uniform throughout the file: the outer <cit> always opens with a
    fixed 14-space indent before the inner <cit>, and the inner </cit> is
    always followed by a blank line and a 12-space-indented outer </cit>,
    so both patterns below are safe as literal substrings.

    Returns the transformed text and the number of wrappers removed.
    Raises UnbalancedCitWrapperError if the open/close pattern counts
    disagree, since that means the file's formatting no longer matches
    what this substitution assumes.
    """
    opens = text.count(OPEN_OLD)
    closes = text.count(CLOSE_OLD)
    if opens != closes:
        raise UnbalancedCitWrapperError(
            f"{opens} occurrences of {OPEN_OLD!r} vs {closes} of {CLOSE_OLD!r} -- not 1:1"
        )

    text = text.replace(OPEN_OLD, OPEN_NEW).replace(CLOSE_OLD, CLOSE_NEW)
    return text, opens
