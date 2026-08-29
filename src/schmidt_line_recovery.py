from __future__ import annotations

import re

REF_RE = re.compile(
    r'<ref target="urn:cts:engLit:shakespeare\.([a-z0-9]+):([^"]+)">([^<]*)</ref>'
)
# Digits not glued to a preceding letter, so play abbreviations like H5/1H4/2H6
# don't get misread as a citation number.
DIGIT_RE = re.compile(r"(?<![A-Za-z])\d+")

# Non-dramatic works: already-correct "poem.line" 2-segment citations, out of
# MVP scope (see CLAUDE.md).
NON_DRAMATIC = frozenset({"son", "ven", "luc", "lc", "pp", "pht"})


def _candidate_line(display_text: str) -> str | None:
    digits = DIGIT_RE.findall(display_text)
    return digits[-1] if digits else None


def recover_line_numbers(
    text: str, locator_index: dict[str, set[str]]
) -> tuple[str, int, list[dict]]:
    """Recover a missing line-number segment in Schmidt <ref target> CTS URNs
    of the form urn:cts:engLit:shakespeare.{play}:{act}.{scene} (edition
    token already stripped -- see schmidt_urn_edition.strip_edition),
    verifying every reconstruction against `locator_index`
    (f1_locator_index.build_f1_locator_index's output) rather than guessing.

    Only attempts a fix when the locator is exactly two digit-only segments
    (act.scene) -- the well-understood "line number dropped" shape. For each
    such ref, extracts a candidate line number from the display text (its
    last non-play-abbreviation digit run) and searches locator_index[play]
    for a unique "{act}.*.{candidate}" match. Rewrites only on an exactly-one
    match; everything else -- no candidate digit, unknown play, zero or
    multiple matches -- is left untouched and reported.

    Position-based replacement (not a target-value string .replace()):
    distinct citations can share an identical incomplete target string while
    needing different reconstructed lines (the display text, not just the
    target, determines the fix), so each match is resolved and rewritten
    independently by its own span in the original text.

    Returns (new_text, fixed_count, unresolved), where `unresolved` is a
    list of {play, locator, text, reason} dicts for reporting.
    """
    replacements: list[tuple[int, int, str]] = []
    unresolved: list[dict] = []
    fixed = 0

    for m in REF_RE.finditer(text):
        play, locator, display = m.group(1), m.group(2), m.group(3)
        if play in NON_DRAMATIC:
            continue

        segments = locator.split(".")
        if len(segments) != 2 or not all(s.isdigit() for s in segments):
            continue  # not the "act.scene, missing line" shape -- out of scope

        act = segments[0]
        candidate = _candidate_line(display)
        if candidate is None:
            unresolved.append({
                "play": play, "locator": locator, "text": display,
                "reason": "no recoverable digit in display text",
            })
            continue

        play_locators = locator_index.get(play)
        if play_locators is None:
            unresolved.append({
                "play": play, "locator": locator, "text": display,
                "reason": f"no locator index for play {play!r}",
            })
            continue

        # Try the locator's existing second segment as the real scene first
        # (it usually already is, e.g. "1.2" + line "30" -> "1.2.30") --
        # only fall back to searching every scene in the act when that
        # exact hypothesis doesn't hold (the "digit landed in the scene
        # slot" case, where the second segment is actually the line, not a
        # real scene, so this lookup correctly misses).
        existing_scene = segments[1]
        exact = f"{act}.{existing_scene}.{candidate}"
        if exact in play_locators:
            replacements.append((m.start(2), m.end(2), exact))
            fixed += 1
            continue

        prefix, suffix = f"{act}.", f".{candidate}"
        matches = [
            loc for loc in play_locators
            if loc.startswith(prefix) and loc.endswith(suffix)
        ]
        if len(matches) != 1:
            unresolved.append({
                "play": play, "locator": locator, "text": display,
                "reason": f"{len(matches)} candidate matches (need exactly 1)",
            })
            continue

        replacements.append((m.start(2), m.end(2), matches[0]))
        fixed += 1

    for start, end, new_locator in sorted(replacements, reverse=True):
        text = text[:start] + new_locator + text[end:]

    return text, fixed, unresolved
