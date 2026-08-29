from __future__ import annotations

import re

REF_TARGET_RE = re.compile(
    r'(<ref target="urn:cts:engLit:shakespeare\.[a-z0-9]+)\.(?:globe|f1)(:[^"]*")'
)


def strip_edition(text: str) -> tuple[str, int]:
    """Strip the citation-family/edition token from Schmidt <ref target> CTS
    URNs: urn:cts:engLit:shakespeare.{work}.globe:{locator} ->
    urn:cts:engLit:shakespeare.{work}:{locator}.

    Resolving a citation to a specific edition (Globe vs. F1/TLN) is a
    separate, still-open problem -- a citation should resolve to the work,
    not commit to an edition, per doc/forum.org
    #citations/cts-urns-and-citation-families. Only touches <ref target>
    attributes (not e.g. the unrelated licence URL also carrying a bare
    target= attribute elsewhere in the file).

    Returns (new_text, count_stripped).
    """
    return REF_TARGET_RE.subn(r"\1\2", text)
