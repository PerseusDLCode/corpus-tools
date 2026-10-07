"""Schmidt's Lear citations against the regenerated edition.

doc/agenda.org #validate/schmidt-smoke. The only validation that comes from
outside the page: does the line Schmidt cites contain what he quotes, or, for a
citation without a quotation, his headword?

This module reports, it never fixes. A failure can come from our numbering,
Schmidt's citation, a printing he used that differs, or a word the P4 has
wrong, and telling them apart is the point of looking.

Usage (from the repo root):

    pdm run python -m globe.schmidt_smoke [OUT_DIR]

Reads out/globe/lr/shakespeare.lr.globe.xml and the sibling
schmidt-lexicon-workshop's out/citations.tsv and out/citation_quotes.tsv;
writes schmidt-smoke-lr.tsv (every citation) and schmidt-smoke-lr.md
(the summary and every failure) to OUT_DIR, default reports/globe/.
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from globe.tokens import norm

REPO = Path(__file__).resolve().parent.parent.parent
EDITION = REPO / "out" / "globe" / "lr" / "shakespeare.lr.globe.xml"
SCHMIDT = REPO.parent / "schmidt-lexicon-workshop" / "out"
TEI = "{http://www.tei-c.org/ns/1.0}"
SKIP = {f"{TEI}speaker", f"{TEI}stage", f"{TEI}head", f"{TEI}castList", f"{TEI}note"}
NEAR = 3  # a quotation this many lines from the cited one is "off by k", not missing
FUZZY = 0.6  # share of a quotation's words that must align, in order, for a match with differences
DASH = re.compile(r"--+|[\u2013\u2014]")
ELLIPSIS = re.compile(r"(?:\.\s*){3,}")
SUFFIXES = ("", "s", "es", "d", "ed", "ing", "st", "est", "th", "eth", "n", "en", "er")
OTHER_PLAY = re.compile(r"^\s*(?!Lr\.)[A-Z][a-z]+\.")  # a display naming a play other than Lear


def words(text: str) -> list[str]:
    """Normalised words. Accents are folded first ("compáct" -> "compact"),
    which tokens.norm alone would drop as non-letters, and a dash separates
    words even with no space around it."""
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = DASH.sub(" ", folded)  # "this,--a" is two words, not "thisa"
    return [canon(w) for w in (norm(t) for t in folded.split()) if w]


def canon(w: str) -> str:
    """One spelling for the elisions that differ between Schmidt and the P4:
    "stranger'd" and "strangered" alike become "strangered", and apostrophes
    go ("death'sman" -> "deathsman")."""
    if w.endswith("'d"):
        w = w[:-2] + "ed"
    return w.replace("'", "")


@dataclass
class Scene:
    words: list[str]
    line_of: list[int]  # Globe line number of each word
    lines: dict[int, list[str]]
    prose: set[int]  # Globe lines that begin inside a <p>


def read_edition(path: Path) -> dict[str, Scene]:
    """Each scene's spoken words, each word tagged with its Globe line: the
    text from one Globe milestone to the next, speaker names and stage
    directions left out (Schmidt quotes neither)."""
    root = etree.parse(str(path)).getroot()
    body = root.find(f"{TEI}text/{TEI}body")
    scenes: dict[str, Scene] = {}
    state = {"scene": None, "line": None}

    def add(text):
        s, n = state["scene"], state["line"]
        if not text or s is None or n is None:
            return
        for w in words(text):
            s.words.append(w)
            s.line_of.append(n)
            s.lines.setdefault(n, []).append(w)

    def walk(el, act):
        if el.tag in SKIP:
            # its words are not spoken text, but a Globe line can begin inside
            # it: "[To Ed- | gar] You, sir" (III.6.83) puts the milestone
            # before "Edgar]", within the <stage>
            for m in el.iter(f"{TEI}milestone"):
                if m.get("ed") == "Globe":
                    state["line"] = int(m.get("n"))
            return
        if el.tag == f"{TEI}div":
            if el.get("type") == "act":
                act = el.get("n")
            elif el.get("type") == "scene":
                state["scene"] = scenes.setdefault(f"{act}.{el.get('n')}", Scene([], [], {}, set()))
                state["line"] = None
        if el.tag == f"{TEI}milestone" and el.get("ed") == "Globe":
            state["line"] = int(el.get("n"))
            if state["scene"] is not None and any(a.tag == f"{TEI}p" for a in el.iterancestors()):
                state["scene"].prose.add(state["line"])
        add(el.text)
        for child in el:
            if isinstance(child.tag, str):
                walk(child, act)
            add(child.tail)

    walk(body, None)
    return scenes


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"))


def find(seq: list[str], hay: list[str]) -> list[int]:
    """Every start index of seq as a contiguous run in hay."""
    if not seq:
        return []
    k = len(seq)
    return [i for i in range(len(hay) - k + 1) if hay[i] == seq[0] and hay[i:i + k] == seq]


def headword_match(headword: str):
    """Schmidt's lemma ("Deprive,") against an inflected form in the text
    ("deprived"). A word of four letters or fewer matches whole or with a
    common suffix ("bag" -> "bags", "trip" -> "tripped", "spy" -> "spies"), so
    "a" does not match everything; a longer one matches on all but its last
    three letters ("touching" -> "touches"), at the start of a word; a
    compound anywhere in the line with its spaces removed. Irregular forms
    ("bespeak" / "bespoke") are not found, and are reported."""
    w = "".join(words(headword))
    if len(w) <= 4:
        bases = {w, w + w[-1:]}  # "trip" -> "tripped", "mad" -> "madded"
        if w.endswith("y"):
            bases.add(w[:-1] + "i")  # "spy" -> "spies"
        if w.endswith("e"):
            bases.add(w[:-1])  # "bite" -> "biting"
        forms = {b + suf for b in bases for suf in SUFFIXES}
        return lambda line: any(t in forms for t in line)
    stem = w[:max(4, len(w) - 3)]  # "touching" -> "touch", "inclining" -> "inclin"
    if re.search(r"[\w'][-\s][\w']", headword.strip(" ,.;:")):
        # a compound finds its parts in the joined line: "better-spoken" in
        # "better spoken"; a simple word must begin a word, or "ache" (from
        # "Acheron") would be found in "breaches"
        return lambda line: stem in "".join(line)
    return lambda line: any(t.startswith(stem) for t in line)


def on_line(match, line: list[str]) -> bool:
    return match(line)


def fragments(quote: str, headword: str) -> list[list[str]]:
    """A quotation split at Schmidt's ellipses (". . ."), each piece's words.
    A single letter with a full stop that the expansion left standing ("a
    sectary a.") is his abbreviation of the headword, and is written out."""
    head = "".join(words(headword))
    quote = re.sub(r"(?<![\w'])([A-Za-z])\.(?=[\s,;:?!).]|$)",
                   lambda m: head if head[:1] == m.group(1).lower() else m.group(0), quote)
    return [ws for ws in (words(part) for part in ELLIPSIS.split(quote)) if ws]


def joined_spans(q: list[str], scene: "Scene") -> list[tuple[int, int]]:
    """Where the quotation occurs with the spaces taken out on both sides: the
    same letters with a different word division ("in a door" / "inadoor",
    "half hour" / "halfhour"). Returns (first line, last line) of each."""
    needle = "".join(q)
    if len(needle) < 6:
        return []
    hay, owner = [], []
    for w, n in zip(scene.words, scene.line_of):
        hay.append(w)
        owner.extend([n] * len(w))
    hay = "".join(hay)
    spans, i = [], hay.find(needle)
    while i != -1:
        spans.append((owner[i], owner[i + len(needle) - 1]))
        i = hay.find(needle, i + 1)
    return spans


def fuzzy(q: list[str], scene: "Scene", n: int):
    """The window of lines that best contains the quotation's words in order,
    allowing differences of spelling and reading. Returns (share of q aligned,
    lines holding the aligned words, q's words not found, our words in between
    not in q), or None if no window reaches FUZZY. Ties go to the window nearest
    the cited line."""
    span = max(1, len(q) // 6 + 1)
    best = None
    for m in sorted(scene.lines, key=lambda m: abs(m - n)):
        window, line_of = [], []
        for k in range(m, m + span + 1):
            for w in scene.lines.get(k, []):
                window.append(w)
                line_of.append(k)
        blocks = difflib.SequenceMatcher(None, q, window, autojunk=False).get_matching_blocks()
        got = sum(b.size for b in blocks)
        if best is None or got > best[0]:
            best = (got, blocks, window, line_of)
    if best is None or best[0] / len(q) < FUZZY:
        return None
    got, blocks, window, line_of = best
    hit_q = {b.a + i for b in blocks for i in range(b.size)}
    hit_w = [b.b + i for b in blocks for i in range(b.size)]
    lines = sorted({line_of[i] for i in hit_w})
    missing = [w for i, w in enumerate(q) if i not in hit_q]
    lo, hi = min(hit_w), max(hit_w)
    extra = [window[i] for i in range(lo, hi + 1) if i not in set(hit_w)]
    return got / len(q), lines, missing, extra


def check(cit: dict, quote: dict, scenes: dict[str, Scene]) -> dict:
    ref = cit["p5_ref_target"].rsplit(":", 1)[1]
    out = {"key": quote["key"], "headword": quote["headword"], "cited": ref,
           "display": cit["p4_display_text"], "quote": quote["quote_expanded"],
           "verdict": "", "found_at": "", "offset": "", "match": "", "missing": "", "extra": "",
           "our_line": ""}
    parts = ref.split(".")
    other_play = OTHER_PLAY.match(cit["p4_display_text"])
    if other_play or len(parts) != 3 or not all(p.isdigit() for p in parts) \
            or f"{parts[0]}.{parts[1]}" not in scenes:
        # a citation extracted into Lear's scope that is not Lear's: another
        # play named ("Shr. Ind. 1, 94"), a sonnet ("154, 2"), a Pericles
        # chorus ("IV Prol. 40") -- an extraction question, not a lineation one
        out["verdict"] = "not a Lear citation"
        return out
    scene_id, n = f"{parts[0]}.{parts[1]}", int(parts[2])
    scene = scenes[scene_id]
    out["our_line"] = " ".join(scene.lines.get(n, [])) or "(no such line)"

    frags = fragments(quote["quote_expanded"], quote["headword"]) if quote["has_quote"] == "true" else []
    match = headword_match(quote["headword"])
    located = None  # (first line, last line) of the quotation, if found anywhere near
    if frags:
        spans = [(scene.line_of[i], scene.line_of[i + len(f) - 1]) for f in frags for i in find(f, scene.words)]
        if any(a <= n <= b for a, b in spans):
            out["verdict"] = "quotation on cited line"
            return out
        q = [w for f in frags for w in f]
        loose = [sp for f in frags for sp in joined_spans(f, scene)]
        if any(a <= n <= b for a, b in loose):
            out.update(verdict="quotation on cited line, with differences", match="spacing")
            return out
        near = fuzzy(q, scene, n)
        if near is not None:
            share, lines, missing, extra = near
            out.update(match=f"{share:.0%}", missing=" ".join(missing), extra=" ".join(extra))
            if n in lines:
                out["verdict"] = "quotation on cited line, with differences"
                return out
            located = (lines[0], lines[-1])
        elif spans or loose:
            located = min(spans + loose, key=lambda s: min(abs(s[0] - n), abs(s[1] - n)))
    if on_line(match, scene.lines.get(n, [])):
        out["verdict"] = "headword on cited line"
        if located:
            out["found_at"] = f"{scene_id}.{located[0]}" + (f"-{located[1]}" if located[1] != located[0] else "")
        return out
    if located:
        a, b = located
        off = a - n if a > n else b - n
        out.update(found_at=f"{scene_id}.{a}" + (f"-{b}" if b != a else ""), offset=off)
        out["verdict"] = f"quotation off by {abs(off)}" if abs(off) <= NEAR else "quotation elsewhere in scene"
        if row_break(scene, n, off, match):
            out["verdict"] = "prose row break"
        return out
    if frags:
        other = [(sid, s.line_of[i]) for f in frags if len(f) >= 3
                 for sid, s in scenes.items() for i in find(f, s.words)]
        if other:
            out.update(verdict="quotation in another scene", found_at=f"{other[0][0]}.{other[0][1]}")
            return out
    prefix = "quotation not found; " if frags else ""
    near_hw = sorted((abs(m - n), m) for m, ws in scene.lines.items() if on_line(match, ws))
    if near_hw and near_hw[0][0] <= NEAR:
        m = near_hw[0][1]
        out.update(verdict=f"{prefix}headword off by {abs(m - n)}", found_at=f"{scene_id}.{m}", offset=m - n)
        if row_break(scene, n, m - n, match):
            out["verdict"] = "prose row break"
    else:
        out["verdict"] = f"{prefix}headword not found near cited line"
    return out


def row_break(scene: "Scene", n: int, off: int, match) -> bool:
    """The headword is one line off, in prose, and sits at the edge of our
    line next to the one cited: the first word of the line after, or the last
    of the line before. Prose row breaks are the printing's, not the Globe's
    (CLAUDE.md, "The P4's prose line breaks do not match the printings we
    hold"), so a word there can fall on either line in another printing
    while every line count agrees."""
    if abs(off) != 1 or (n + off) not in scene.prose:
        return False
    line = scene.lines.get(n + off, [])
    edge = line[:1] if off > 0 else line[-1:]
    return bool(edge) and match(edge)


PASS = ("quotation on cited line", "quotation on cited line, with differences", "headword on cited line")


def run(edition: Path = EDITION, schmidt: Path = SCHMIDT) -> tuple[list[dict], dict]:
    scenes = read_edition(edition)
    cits = {(r["key"], r["ordinal"], r["cit_ordinal"]): r for r in read_tsv(schmidt / "citations.tsv")}
    quotes = read_tsv(schmidt / "citation_quotes.tsv")
    rows = [check(cits[(q["key"], q["ordinal"], q["cit_ordinal"])], q, scenes) for q in quotes]
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16]
               for p in (edition, schmidt / "citations.tsv", schmidt / "citation_quotes.tsv")}
    return rows, sources


COLUMNS = ["key", "headword", "cited", "display", "verdict", "found_at", "offset", "match",
           "missing", "extra", "quote", "our_line"]


def write(rows: list[dict], sources: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = "; ".join(f"{k} sha256 {v}" for k, v in sources.items())
    with (out_dir / "schmidt-smoke-lr.tsv").open("w", newline="", encoding="utf-8") as f:
        f.write(f"# schmidt_smoke.py; sources: {stamp}\n")
        w = csv.DictWriter(f, COLUMNS, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    counts = Counter(r["verdict"] for r in rows)
    quoted = [r for r in rows if r["quote"]]
    bare = [r for r in rows if not r["quote"]]
    ok = lambda rs: sum(r["verdict"] in PASS for r in rs)  # noqa: E731
    lines = [
        "# Schmidt smoke test: King Lear",
        "",
        f"Sources: {stamp}.",
        "",
        "Every Lear citation in Schmidt's *Shakespeare-Lexicon*, checked against the "
        "regenerated edition: does the cited line contain the quotation, or (for a "
        "citation without one) the headword? Report only; nothing is fixed.",
        "",
        f"- **All citations:** {ok(rows)}/{len(rows)} ({ok(rows) / len(rows):.1%}) pass.",
        f"- **With a quotation:** {ok(quoted)}/{len(quoted)} ({ok(quoted) / len(quoted):.1%}) "
        "have it on the cited line.",
        f"- **Headword only:** {ok(bare)}/{len(bare)} ({ok(bare) / len(bare):.1%}) have it on the "
        "cited line.",
        "",
        "| Verdict | Citations |",
        "|---|---|",
        *[f"| {v} | {c} |" for v, c in counts.most_common()],
        "",
        "## Every failure",
        "",
        "| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        if r["verdict"] not in PASS:
            cells = [r["cited"], r["display"], r["headword"].rstrip(","), r["verdict"], r["found_at"],
                     r["quote"], r["our_line"]]
            lines.append("| " + " | ".join(c.replace("|", "/") for c in map(str, cells)) + " |")
    (out_dir / "schmidt-smoke-lr.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "reports" / "globe"
    rows, sources = run()
    write(rows, sources, out)
    counts = Counter(r["verdict"] for r in rows)
    print(f"{sum(r['verdict'] in PASS for r in rows)}/{len(rows)} pass", file=sys.stderr)
    for v, c in counts.most_common():
        print(f"  {c:5d}  {v}", file=sys.stderr)
