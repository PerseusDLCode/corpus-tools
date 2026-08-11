from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from tei import NS

TEI_L = f"{{{NS['tei']}}}l"
TEI_STAGE = f"{{{NS['tei']}}}stage"
TEI_DIV = f"{{{NS['tei']}}}div"

NEW_LINE_PARTS = (None, "N", "I", "Y")
CONTINUATION_PARTS = ("F", "M")


@dataclass
class NumberingWarning:
    play: str
    act: str
    scene: str
    message: str

    def __str__(self) -> str:
        return f"{self.play}: act {self.act} scene {self.scene}: {self.message}"


@dataclass
class CollisionReport:
    play: str
    act: str
    scene: str
    anchor_a: int
    anchor_b: int
    lines_between: int
    gap: int
    collision: bool


def _normalized_part(line: etree._Element) -> str | None:
    """@part='N' and absent @part are equivalent (CLAUDE.md convention)."""
    part = line.get("part")
    return None if part == "N" else part


def _is_new_line(line: etree._Element) -> bool:
    return _normalized_part(line) in NEW_LINE_PARTS


def _is_continuation(line: etree._Element) -> bool:
    return _normalized_part(line) in CONTINUATION_PARTS


def _has_stage_ancestor(line: etree._Element, boundary: etree._Element) -> bool:
    node = line.getparent()
    while node is not None and node is not boundary:
        if node.tag == TEI_STAGE:
            return True
        node = node.getparent()
    return False


def collect_scene_lines(scene: etree._Element) -> list[etree._Element]:
    """<l> elements within a scene, in document order, excluding those inside <stage>."""
    return [line for line in scene.iter(TEI_L) if not _has_stage_ancestor(line, scene)]


def collect_act_direct_lines(act: etree._Element) -> list[etree._Element]:
    """<l> descendants of an act not already inside a nested scene div or <stage>.

    Covers Chorus/Prologue/Epilogue speeches encoded directly under
    <div type="act" n="prologue"/"epilogue"> with no scene wrapper (e.g. h5,
    h8, tro), which would otherwise be silently skipped entirely.
    """
    lines = []
    for line in act.iter(TEI_L):
        node = line.getparent()
        in_nested_scene = False
        while node is not None and node is not act:
            if node.tag == TEI_DIV and node.get("type") == "scene":
                in_nested_scene = True
                break
            node = node.getparent()
        if not in_nested_scene and not _has_stage_ancestor(line, act):
            lines.append(line)
    return lines


def scene_label(scene: etree._Element) -> tuple[str, str]:
    act_n = scene.xpath("ancestor::tei:div[@type='act'][1]/@n", namespaces=NS)
    return (str(act_n[0]) if act_n else "?", scene.get("n", "?"))


def _number_lines(
    all_lines: list[etree._Element], play: str, act: str, scene_n: str
) -> tuple[list[NumberingWarning], list[CollisionReport]]:
    """Assign @n to every <l> in all_lines missing it. Mutates the tree in place."""
    warnings: list[NumberingWarning] = []
    collisions: list[CollisionReport] = []

    if not all_lines:
        warnings.append(NumberingWarning(play, act, scene_n, "no <l> elements (prose-only scene)"))
        return warnings, collisions

    seq = [line for line in all_lines if _is_new_line(line)]
    anchors: list[tuple[int, int]] = []
    for idx, line in enumerate(seq):
        raw = line.get("n")
        if raw is None:
            continue
        try:
            anchors.append((idx, int(raw)))
        except ValueError:
            warnings.append(NumberingWarning(
                play, act, scene_n,
                f"<l> has non-numeric @n={raw!r}; left unmodified and excluded "
                "from interpolation math (fix the source value)",
            ))

    def _set_if_unset(line: etree._Element, value: int) -> None:
        if line.get("n") is None:
            line.set("n", str(value))

    if not anchors:
        for idx, line in enumerate(seq):
            _set_if_unset(line, idx + 1)
    else:
        first_i, first_v = anchors[0]
        for idx in range(first_i):
            _set_if_unset(seq[idx], first_v - (first_i - idx))

        for (i, a), (j, b) in zip(anchors, anchors[1:]):
            lines_between = j - i - 1
            if lines_between <= 0:
                continue
            gap = b - a
            # There are only gap-1 integers strictly between a and b, so
            # lines_between == gap is already oversubscribed by one, not just
            # lines_between > gap (a naive reading of "exceeds b - a").
            collision = lines_between >= gap
            collisions.append(CollisionReport(play, act, scene_n, a, b, lines_between, gap, collision))
            if collision:
                warnings.append(NumberingWarning(
                    play, act, scene_n,
                    f"{lines_between} new-line elements between anchors {a} and {b} "
                    f"(gap {gap}) — numbering collision",
                ))
            prev = a
            for t in range(1, lines_between + 1):
                value = round(a + t * (b - a) / (j - i))
                value = max(value, prev + 1)
                # Leave room for the remaining ties to also land strictly
                # below b; only enforce it while doing so wouldn't itself
                # break monotonicity (i.e. this isn't a collision overflow).
                ceiling = b - (lines_between - t) - 1
                if ceiling >= prev + 1:
                    value = min(value, ceiling)
                _set_if_unset(seq[i + t], value)
                prev = value

        last_i, last_v = anchors[-1]
        for k in range(last_i + 1, len(seq)):
            last_v += 1
            _set_if_unset(seq[k], last_v)

    last_new_line_n: str | None = None
    for line in all_lines:
        if _is_new_line(line):
            last_new_line_n = line.get("n")
        elif _is_continuation(line):
            if last_new_line_n is None:
                warnings.append(NumberingWarning(
                    play, act, scene_n,
                    "continuation <l> (part='F'/'M') precedes any new-line element in scene",
                ))
            else:
                line.set("n", last_new_line_n)

    for line in all_lines:
        if not line.get("n"):
            warnings.append(NumberingWarning(play, act, scene_n, "<l> still lacks @n after numbering pass"))

    return warnings, collisions


def number_scene(
    scene: etree._Element, play: str
) -> tuple[list[NumberingWarning], list[CollisionReport]]:
    """Assign @n to every <l> in a scene missing it. Mutates the tree in place."""
    act, scene_n = scene_label(scene)
    return _number_lines(collect_scene_lines(scene), play, act, scene_n)


def number_document(
    root: etree._Element, play: str
) -> tuple[list[NumberingWarning], list[CollisionReport]]:
    warnings: list[NumberingWarning] = []
    collisions: list[CollisionReport] = []
    for scene in root.iter(TEI_DIV):
        if scene.get("type") != "scene":
            continue
        w, c = number_scene(scene, play)
        warnings.extend(w)
        collisions.extend(c)

    for act in root.iter(TEI_DIV):
        if act.get("type") != "act":
            continue
        direct_lines = collect_act_direct_lines(act)
        if not direct_lines:
            continue
        w, c = _number_lines(direct_lines, play, act.get("n", "?"), "(act-level, no scene wrapper)")
        warnings.extend(w)
        collisions.extend(c)

    return warnings, collisions


def render_collision_table(collisions: list[CollisionReport]) -> str:
    header = f"{'PLAY':<10}{'ACT':<5}{'SCENE':<7}{'ANCHOR_A':<10}{'ANCHOR_B':<10}{'LINES_BETWEEN':<15}{'GAP':<6}{'COLLISION'}"
    lines = [header]
    for c in collisions:
        lines.append(
            f"{c.play:<10}{c.act:<5}{c.scene:<7}{c.anchor_a:<10}{c.anchor_b:<10}"
            f"{c.lines_between:<15}{c.gap:<6}{'YES' if c.collision else 'no'}"
        )
    n_collisions = sum(1 for c in collisions if c.collision)
    plays = {c.play for c in collisions}
    lines.append("")
    lines.append(
        f"SUMMARY: {len(collisions)} interpolation gap(s) across {len(plays)} play(s), "
        f"{n_collisions} collision(s)"
    )
    return "\n".join(lines)
