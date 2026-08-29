from __future__ import annotations

import re

EDITION_OPEN_RE = re.compile(r'<div type="edition"[^>]*>')
TEXTPART_RE = re.compile(r'<div type="textpart" subtype="[^"]*" n="([^"]+)">')
DIV_TAG_RE = re.compile(r'<div\b[^>]*?(/?)>|</div>')


class LexiconStructureError(ValueError):
    """Raised when the file doesn't match the single-edition-wrapper
    structure this module assumes (a leftover from the prior EpiDoc
    encoding: <body> holds exactly one <div type="edition">, itself
    holding a flat run of <div type="textpart" subtype="...">
    sections)."""


def _remove_span_collapsing_blank_line(text: str, start: int, end: int) -> str:
    """Delete text[start:end]. If doing so leaves its line pure whitespace
    (true whenever the tag had its own line, e.g. Schmidt's formatting),
    drop that now-empty line too rather than leaving it stray. If the line
    had other content (e.g. onions/dyce's `<body><div type="edition"...>`
    on one line), only the tag itself is removed."""
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line_without_span = text[line_start:start] + text[end:line_end]
    if line_without_span.strip() == "":
        return text[:line_start] + text[line_end + 1 :] if line_end < len(text) else text[:line_start]
    return text[:start] + text[end:]


def _find_matching_close(text: str, search_from: int) -> tuple[int, int]:
    """Depth-walk div open/close tags from `search_from` (just after an
    edition div's own open tag) to find that div's true matching </div>,
    however deeply its content is nested -- not just the next </div>."""
    depth = 1
    for m in DIV_TAG_RE.finditer(text, search_from):
        if m.group(0) == "</div>":
            depth -= 1
            if depth == 0:
                return m.start(), m.end()
        elif m.group(1) != "/":
            depth += 1
    raise LexiconStructureError("no matching </div> found for edition div")


def flatten_lexicon_sections(text: str) -> tuple[str, int]:
    """Remove the leftover EpiDoc <div type="edition"> wrapper and rename
    each <div type="textpart" subtype="..."> to <div type="section">,
    keeping @n and adding @xml:id="section-{n}".

    Raw-text substitution rather than a parse/reserialize pass, since these
    lexicon files are hand-formatted -- see strip_bibl_wrapper.py and
    schmidt_cit_unwrap.py for the same rationale. Raises
    LexiconStructureError rather than guessing if the file doesn't have
    exactly one <div type="edition">.
    """
    opens = list(EDITION_OPEN_RE.finditer(text))
    if len(opens) != 1:
        raise LexiconStructureError(
            f'expected exactly 1 <div type="edition"> open tag, found {len(opens)}'
        )
    open_match = opens[0]

    close_start, close_end = _find_matching_close(text, open_match.end())

    # Remove the close tag first so the open tag's offsets stay valid.
    text = _remove_span_collapsing_blank_line(text, close_start, close_end)
    text = _remove_span_collapsing_blank_line(text, open_match.start(), open_match.end())

    text, section_count = TEXTPART_RE.subn(
        lambda m: f'<div type="section" n="{m.group(1)}" xml:id="section-{m.group(1)}">',
        text,
    )

    return text, section_count
