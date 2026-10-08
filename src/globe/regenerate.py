"""Regenerate a play's Globe lineation from the witnesses: the gate and its reports.

doc/agenda.org #build/regenerate-lear. Usage (from the repo root):

    pdm run python -m globe.regenerate lr [--scratch=DIR] [--allow-pending] [--any-corpus-branch]

canonical-engLit must have mvp checked out. --scratch=DIR writes the builds and
every report under DIR, and nothing in the repo.

Words and structure come from the P4 (vendored conversion, src/globe/p4_convert.py);
line starts come from the witness pages. Page by page, miun/kraken is tried
first; if the page's printed marginal numbers do not close against the count,
trent/kraken is tried from the same state. The two share plates, so either is
authoritative for line breaks.

The gate: every printed marginal number must equal the count of its line,
counted from the scene start. If any page fails, the play is not written; the
reports are, so the failures can be read. This module writes no TEI.
"""
from __future__ import annotations

import bisect
import csv
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from globe import align_play
from globe import lineate
from globe import manifest
from globe import emit_tei
from globe import folger_check
from globe import page_rows
from globe import plays
from globe import shared_lines
from globe import source_text
from globe import tei_header
from globe import tokens
from globe import witnesses

REPO = Path(__file__).resolve().parent.parent.parent
CORPUS = REPO.parent / "canonical-engLit"
CORPUS_BRANCH = "mvp"  # doc/agenda.org #build/retire-rederive: build only from mvp
ORDER = [("miun", "kraken"), ("trent", "kraken")]
BORDERLINE_SHORT_U = (0.6, 1.4)  # turnover-band rows whose row above is this far short: review


@dataclass
class PageResult:
    page: int
    witness: str
    lines: list[lineate.Line]
    rows: list[page_rows.Row]
    intervals: list[dict]
    joined_previous: bool  # first row continued the previous page's last line
    applied: list[tuple[int, shared_lines.Row]] = field(default_factory=list)  # (line index in page, row)
    leaf: str = ""
    tried: list[tuple[str, int]] = field(default_factory=list)  # (witness, total count error)

    @property
    def failing(self) -> list[dict]:
        return [iv for iv in self.intervals if iv["error"]]

    @property
    def error(self) -> int:
        """Total count error over the page's intervals: how witnesses are compared."""
        return sum(abs(iv["error"]) for iv in self.intervals)


@dataclass
class NumberState:
    div: str | None = None
    n: int = 0  # last line counted
    last_num: int | None = None  # last printed number met in this scene ...
    last_num_n: int | None = None  # ... and the count of its line
    last_num_page: int | None = None


def number_page(lines, toks, state: NumberState, page: int, witness: str, carried: int | None = None,
                alt: dict[int, tuple[str, int]] | None = None):
    """Count this page's lines on from `state`; check every printed number
    against the previous one in the same scene (or the scene start). A number
    printed on a row that continues the previous page's last line is
    `carried`. `alt` gives the other witness's reading of a line's number,
    keyed by the line's first token: where this witness's numeral does not
    close and the other's does, the other's is taken as the reading and the
    interval records it. Returns the intervals and the state after the page.
    Does not mutate `state`."""
    st = NumberState(**vars(state))
    intervals = []
    pending = [(None, carried)] if carried is not None else []
    pending += [(ln, None) for ln in lines]
    for ln, cnum in pending:
        if ln is not None:
            d = toks[ln.start].div
            if d != st.div:
                st = NumberState(div=d)
            st.n += 1
            ln.div, ln.n = d, st.n
            num = ln.num
        else:
            d, num = st.div, cnum
        if num is None:
            continue
        n = st.n
        base, base_n = (0, 0) if st.last_num is None else (st.last_num, st.last_num_n)
        frm = "scene start" if st.last_num is None else f"{st.last_num} (p.{st.last_num_page})"
        reading = ""
        if (n - base_n) != (num - base) and alt and ln is not None and ln.start in alt:
            other_w, other = alt[ln.start]
            if other != num and (n - base_n) == (other - base):
                reading = f"{witness} read {num}; {other_w} read {other}"
                num = other
        intervals.append(dict(page=page, witness=witness, div=d, frm=frm, to=num,
                              printed_gap=num - base, counted_gap=n - base_n,
                              error=(n - base_n) - (num - base), counted_n=n, reading=reading))
        st.last_num, st.last_num_n, st.last_num_page = num, n, page
    return intervals, st


def fold(first, second) -> None:
    """Merge a shared line's second half into its first. A marginal number
    printed beside either half numbers the whole line, so the merged line
    keeps the last one -- the compositor set it where it fit."""
    first.rows += second.rows
    nums = [r.num for r in first.rows if r.num is not None]
    first.num = nums[-1] if nums else None


def apply_table(new, prev_last, toks, table, page: int):
    """Fold the junctions the table records (shared halves and unmarked
    turnovers), and take its numeral readings. Returns the page's lines and
    the rows applied.

    A junction is located by the first spoken words of each half, within the
    page. A junction across a page break (the first half being the previous
    page's last line) is returned in `carry` and applied by the caller, once
    a witness has been chosen for the page, so that trying a witness never
    alters the pages already built. doc/forum.org #lineation/shared-lines-table."""
    rows = [r for r in table if r.page == page]
    applied, carry = [], None
    for r in rows:
        if r.kind == "numeral":
            printed, read = int(r.first_half), int(r.second_half)
            want = tuple(r.line.split())
            hits = [k for k, ln in enumerate(new)
                    if ln.num == read and shared_lines.line_words(new, k, toks, len(want)) == want]
            if len(hits) != 1:
                raise shared_lines.TableError(
                    f"shared-lines.tsv: p.{page} numeral {read} on {r.line!r} matches "
                    f"{len(hits)} lines, expected 1")
            new[hits[0]].num = printed
            applied.append((hits[0], r))
            continue
        want_a, want_b = tuple(r.first_half.split()), tuple(r.second_half.split())
        seq = ([prev_last] if prev_last is not None else []) + new
        off = 1 if prev_last is not None else 0
        hits = [k for k in range(len(seq) - 1)
                if seq[k].div == r.scene or seq[k].div == ""
                if shared_lines.line_words(seq, k, toks, len(want_a)) == want_a
                and shared_lines.line_words(seq, k + 1, toks, len(want_b)) == want_b]
        if len(hits) != 1:
            raise shared_lines.TableError(
                f"shared-lines.tsv: p.{page} {r.first_half!r} / {r.second_half!r} matches "
                f"{len(hits)} junctions on this page, expected 1")
        k = hits[0]
        first, second = seq[k], seq[k + 1]
        if first is prev_last:  # across the page break: the caller applies it
            carry = (second, r)
            new.remove(second)
            continue
        fold(first, second)
        new.remove(second)
        applied.append((k - off, r))
    return new, applied, carry


def build(play: str, table: list[shared_lines.Row] | None = None):
    entry = plays.get(play)  # data/globe/plays.tsv: P4, shell, printed pages, DraCor file
    first, last = entry.first, entry.last
    table = shared_lines.read_table() if table is None else table
    text = source_text.load_p4(CORPUS / entry.p4)
    toks = tokens.tokenize(text.body)
    enc = [t.t for t in toks]
    grams = align_play.trigram_index(enc)
    speakers = tokens.speaker_names(toks)
    reg = witnesses.load(sorted({w for w, _ in ORDER}))
    manifest.verify(play, reg, ORDER, first, last)  # refuse a witness file that is not as pinned

    # every page of every witness, aligned in order
    pages: dict[tuple[str, int], tuple[page_rows.Page, align_play.PageAlignment]] = {}
    for wid, layer in ORDER:
        w = reg.witness(wid)
        L = w.layer(layer)
        floor = 0
        for p in range(first, last + 1):
            leaf = w.leaves.leaf_for_printed(p)
            pg = page_rows.read_page(L.file_for(leaf), p, f"{wid}/{layer}", leaf, speakers)
            al = align_play.align_page(pg, toks, enc, grams, floor, speakers)
            floor = al.last + 1
            pages[(f"{wid}/{layer}", p)] = (pg, al)

    lines: list[lineate.Line] = []
    state = NumberState()
    results: list[PageResult] = []
    for p in range(first, last + 1):
        best = None
        tried = []
        for wid, layer in ORDER:
            key = f"{wid}/{layer}"
            pg, _ = pages[(key, p)]
            new = lineate.globe_lines(pg.rows, p)
            joined = bool(new and lines and lineate.continues(lines[-1].rows[-1], new[0].rows[0]))
            head = new.pop(0) if joined else None
            new, applied, carry = apply_table(new, lines[-1] if lines else None, toks, table, p)
            alt = {}
            for owid, olayer in ORDER:
                okey = f"{owid}/{olayer}"
                if okey != key:
                    for oln in lineate.globe_lines(pages[(okey, p)][0].rows, p):
                        if oln.num is not None and oln.start is not None:
                            alt.setdefault(oln.start, (okey, oln.num))
            ivs, st = number_page(new, toks, state, p, key,
                                  carried=head.num if head is not None else None, alt=alt)
            res = PageResult(p, key, new, pg.rows, ivs, joined, applied, pg.leaf)
            res._carry = carry
            res._head, res._state = head, st
            tried.append((key, res.error))
            if best is None or res.error < best.error:
                best = res
            if not res.failing:
                break
        best.tried = tried
        if best._head is not None:
            lines[-1].rows += best._head.rows
        if best._carry is not None:  # a junction folded across the page break
            second, row = best._carry
            fold(lines[-1], second)
            best.applied.append((-1, row))
        lines += best.lines
        state = best._state
        results.append(best)
    return text, toks, pages, lines, results


# ---------------------------------------------------------------- reports


def write_tsv(path: Path, header: list[str], rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def report_gate(out: Path, results) -> None:
    rows = []
    for r in results:
        printed = [iv["to"] for iv in r.intervals]
        counted = [iv["counted_n"] for iv in r.intervals]
        verdict = "fail" if r.failing else ("pass" if printed else "unchecked")
        rows.append([r.page, r.witness, " ".join(f"{w}:{n}" for w, n in r.tried), len(r.lines),
                     f"{r.lines[0].div}.{r.lines[0].n}" if r.lines else "",
                     f"{r.lines[-1].div}.{r.lines[-1].n}" if r.lines else "",
                     " ".join(map(str, printed)), " ".join(map(str, counted)), verdict])
    write_tsv(out, ["page", "witness_used", "tried(witness:total_error)", "lines_starting_here",
                    "first_line", "last_line", "printed_numbers", "counted_numbers", "verdict"], rows)


def report_intervals(out: Path, results) -> None:
    rows = [[iv["page"], iv["witness"], iv["div"], iv["frm"], iv["to"], iv["printed_gap"],
             iv["counted_gap"], f"{iv['error']:+d}" if iv["error"] else "0", iv["reading"]]
            for r in results for iv in r.intervals]
    write_tsv(out, ["page", "witness", "scene", "from", "to", "printed_gap", "counted_gap", "error",
                    "numeral_reading"], rows)


def report_words(out: Path, pages, results) -> list[tuple[int, str]]:
    used = {r.page: r.witness for r in results}
    rows, reviews = [], []
    for (key, p), (pg, al) in sorted(pages.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if key != used[p]:
            continue
        other = next((pages[(k, p)][1] for k, _ in [(f"{w}/{l}", 0) for w, l in ORDER] if k != key), None)
        for d in al.disagreements:
            other_reading = align_play.witness_reading(other, d.tok_from, d.tok_to) if other else ""
            agree = bool(other_reading) and other_reading == d.witness
            rows.append([d.page, key, d.col, d.seq, d.op, d.p4, d.witness, other_reading,
                         "same" if agree else ""])
            if agree:
                # only where both witnesses read the same thing against the P4:
                # a single witness disagreeing is nearly always OCR noise
                if d.op == "insert":
                    detail = f"both witnesses have {d.witness!r} here; the P4 has nothing"
                elif d.op == "delete":
                    detail = f"the P4 has {d.p4!r} here; neither witness has it"
                else:
                    detail = f"both witnesses read {d.witness!r}; the P4 reads {d.p4!r}"
                reviews.append((d.tok_from, emit_tei.review_comment("words", detail)))
    write_tsv(out, ["page", "witness", "col", "row", "op", "p4", "witness_reading",
                    "other_witness_reading", "witnesses_agree"], rows)
    return reviews


BASELINE = ("baseline: the Globe numbers the P4 transcribed, <lb ed=\"G\" n=\"...\"/> in {p4} "
            "(sha256 {sha}); not the shell's milestones or <l n>")


def report_old_vs_new(out: Path, summary: Path, p4_path: Path, toks, lines, failing_scenes) -> dict:
    """Every number the P4 transcribed, located among the new lines.

    doc/agenda.org #build/old-vs-new-from-p4. A numbered marker labels the P4
    row after it (source_text.Anchor). The convention for reading it is
    doc/forum.org #lineation/regenerate-from-witnesses, amendment 2026-09-24:
    the anchor is the number of the Globe line that begins at the numeral's
    row. Where the row's first spoken word begins a new line, that is
    unambiguous, and the anchor agrees or disagrees with it.

    Where the row begins inside a line, it is not. The amendment's second
    clause ("or the next line to begin") does not hold for the P4's own
    markers: in Lear it gives the P4's number for 24 such rows, and the
    containing line's for 28. Those anchors are reported as unmapped, with
    both candidates, and not scored. An unmapped anchor whose number is
    neither candidate is listed for review."""
    anchors = source_text.p4_anchors(p4_path)
    starts = {ln.start: ln for ln in lines}
    order = sorted(starts)
    rows, listed, reviews = [], [], []
    stats = {"anchors": 0, "mapped": 0, "agree": 0, "clean": 0, "agree_clean": 0,
             "unmapped": 0, "containing": 0, "next": 0, "neither": 0}
    for a in anchors:
        first = next((k for k in range(a.row_start, a.row_end) if toks[k].kind == "speech"), a.row_start)
        i = bisect.bisect_right(order, first) - 1
        containing = starts[order[i]] if i >= 0 else None
        following = starts[order[i + 1]] if i + 1 < len(order) else None
        ctx = " ".join(t.raw for t in toks[a.row_start:a.row_start + 6])
        clean = a.div not in failing_scenes
        stats["anchors"] += 1
        if containing is not None and containing.start == first:
            new_n = containing.n
            verdict = "agree" if int(a.n) == new_n else "disagree"
            stats["mapped"] += 1
            stats["agree"] += verdict == "agree"
            stats["clean"] += clean
            stats["agree_clean"] += clean and verdict == "agree"
            if verdict == "disagree":
                listed.append((a.div, a.n, verdict, new_n, "", "",
                               "" if clean else "scene fails the gate", ctx))
                reviews.append((first, emit_tei.review_comment(
                    "anchor", f"P4 anchor says {a.n}; the page count says {new_n} here")))
            rows.append([a.div, a.n, "row begins a line", new_n, "", "", verdict, ctx])
            continue
        c_n = containing.n if containing else ""
        f_n = following.n if following else ""
        which = ("containing" if str(c_n) == a.n else "next" if str(f_n) == a.n else "neither")
        stats["unmapped"] += 1
        stats[which] += 1
        verdict = f"unmapped (P4 number is the {which} line)" if which != "neither" else "unmapped (neither)"
        if which == "neither":
            listed.append((a.div, a.n, verdict, "", c_n, f_n,
                           "" if clean else "scene fails the gate", ctx))
            reviews.append((first, emit_tei.review_comment(
                "anchor", f"P4 anchor says {a.n}; its row begins inside line {c_n}, before {f_n}")))
        rows.append([a.div, a.n, "row begins inside a line", "", c_n, f_n, verdict, ctx])
    baseline = BASELINE.format(p4=p4_path.name, sha=emit_tei.sha256(p4_path)[:16])
    with out.open("w", newline="", encoding="utf-8") as f:
        f.write(f"# {baseline}\n")
        f.write("# one row per transcribed number; lines the P4 does not number are not listed\n")
    with out.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["scene", "old_n", "row", "new_n", "row_inside_line", "next_line", "verdict", "context"])
        w.writerows(rows)
    with summary.open("w", encoding="utf-8") as f:
        f.write(f"# {baseline}\n")
        f.write(f"# transcribed anchors: {stats['anchors']}; mapped (the row begins a line): "
                f"{stats['mapped']}; of those, carrying the same number: {stats['agree']}\n")
        f.write(f"# in scenes that pass the gate: {stats['clean']} mapped; agreeing: {stats['agree_clean']}\n")
        f.write(f"# unmapped (the row begins inside a line): {stats['unmapped']}; the P4's number is "
                f"the containing line's for {stats['containing']}, the next line's for {stats['next']}, "
                f"neither for {stats['neither']}\n")
        f.write("# listed: every disagreement, and every unmapped anchor whose number is neither\n")
        f.write("scene\told_n\tverdict\tnew_n\trow_inside_line\tnext_line\tnote\tcontext\n")
        for d in listed:
            f.write("\t".join(map(str, d)) + "\n")
    return stats, reviews


def report_verse_prose(out: Path, lines) -> list[tuple[int, str]]:
    rows, reviews = [], []
    seen_l: dict[int, list] = {}
    for ln in lines:
        for r in ln.rows[1:]:
            c = r.extra.get("cont")
            if c is not None and etree.QName(c).localname == "p":
                rows.append([ln.page, ln.div, ln.n, "continuation row inside <p>", r.band, r.text])
                reviews.append((r.start, emit_tei.review_comment(
                    "verse-prose", f"{r.band} row inside a <p>: P4 tags this speech as prose, "
                                   "the page lays it out as verse")))
        c = ln.rows[0].extra.get("cont")
        if c is not None and etree.QName(c).localname == "l":
            seen_l.setdefault(id(c), []).append(ln)
    for group in seen_l.values():
        if len(group) > 1:
            ln = group[0]
            rows.append([ln.page, ln.div, ln.n, f"one <l> holds {len(group)} Globe line starts",
                         "", " | ".join(g.rows[0].text[:40] for g in group)])
            reviews.append((ln.start, emit_tei.review_comment(
                "verse-prose", f"one P4 <l> holds {len(group)} Globe line starts: "
                               "P4 tags this as one verse line, the page prints more")))
    write_tsv(out, ["page", "scene", "line", "finding", "band", "rows"], rows)
    return reviews


def report_borderline(out: Path, lines) -> list[tuple[int, str]]:
    """Rows decided on thin evidence: turnover-band rows whose row above is
    near the full-measure threshold, and every displaced row, with how it was
    decided and what the P4's <l> division says."""
    rows, reviews = [], []
    prev = None
    for ln in lines:
        for k, r in enumerate(ln.rows):
            if prev is not None and r.band == "turnover" and BORDERLINE_SHORT_U[0] <= prev.short_u <= BORDERLINE_SHORT_U[1]:
                same_l = r.extra.get("cont") is prev.extra.get("cont")
                rows.append([ln.page, r.col, ln.div, ln.n, "continues" if k else "new line",
                             f"{prev.short_u:.2f}", "same <l>" if same_l else "different <l>/<p>",
                             prev.text[-30:], r.text[:40]])
                reviews.append((r.start, emit_tei.review_comment(
                    "turnover", f"row above ends {prev.short_u:.2f}u short of the measure, near the "
                                f"1.0u cut: read as {'a turnover' if k else 'a new line'}; "
                                f"P4 has {'the same' if same_l else 'a different'} element")))
            prev = r
    write_tsv(out, ["page", "col", "scene", "line", "decision", "row_above_short_u", "p4",
                    "row_above", "row"], rows)
    return reviews


def build_reviews(results, lines, toks) -> list[tuple[int, str]]:
    """Review comments that come from the build itself: where each page
    begins, where a page came from Trent, and every table row applied."""
    out = []
    for r in results:
        if not r.lines:
            continue
        pg_line = r.lines[0]
        out.append((pg_line.start, emit_tei.review_comment(
            "page", f"p.{r.page} {r.witness} leaf {r.leaf}")))
        if not r.witness.startswith("miun"):
            out.append((pg_line.start, emit_tei.review_comment(
                "witness", f"p.{r.page} taken from {r.witness}: "
                           f"{' '.join(f'{w}:{e}' for w, e in r.tried)} (total count error)")))
        for k, row in r.applied:
            ln = r.lines[k] if 0 <= k < len(r.lines) else r.lines[0]
            state = "checked " + row.checked if row.checked.strip() else "PENDING"
            ids = f" {row.folger_ids}" if row.folger_ids else ""
            if row.kind == "numeral":
                out.append((ln.start, emit_tei.review_comment(
                    "numeral", f"shared-lines.tsv: the page prints {row.first_half}; both witnesses "
                               f"read {row.second_half} ({row.basis}, {state})")))
            elif row.kind == "turnover":
                out.append((ln.start, emit_tei.review_comment(
                    "turnover", f"shared-lines.tsv: this line continues on a row the page sets "
                                f"flush, not at the turnover indent; it begins "
                                f"{row.second_half!r} (basis {row.basis}{ids}, {state})")))
            else:
                out.append((ln.start, emit_tei.review_comment(
                    "shared", f"shared-lines.tsv: this line ends with a half the page cannot show "
                              f"as shared; second half begins {row.second_half!r} "
                              f"(basis {row.basis}{ids}, {state})")))
        for iv in r.intervals:
            if iv["reading"]:  # the numeral was re-read from the other witness
                ln = next((l for l in r.lines if l.n == iv["counted_n"]), None)
                if ln is not None:
                    out.append((ln.start, emit_tei.review_comment("numeral", iv["reading"])))
    return out


def check_words(xml: bytes, source_words: list[str]) -> None:
    """Regeneration moves no words: the output's word stream is the P4's."""
    body = etree.fromstring(xml).find(f"{{http://www.tei-c.org/ns/1.0}}text/"
                                      f"{{http://www.tei-c.org/ns/1.0}}body")
    got = tokens.word_stream(body)
    if got != source_words:
        n = next((i for i, (a, b) in enumerate(zip(got, source_words)) if a != b), 0)
        raise ValueError(f"the output's words differ from the P4's at word {n}: "
                         f"{got[n:n + 5]} against {source_words[n:n + 5]}")


def emit_builds(play: str, lines, results, toks, reviews, out_dir: Path, allow_pending: bool,
                table, commit: str | None = None) -> dict:
    """Write the canonical and review builds. The canonical build is refused
    while any table row it applies is unchecked (doc/forum.org
    #lineation/shared-lines-table)."""
    entry = plays.get(play)
    p4_path, p5_path = CORPUS / entry.p4, CORPUS / entry.shell
    commit = commit or emit_tei.workshop_commit(REPO)  # main() reads it before writing reports
    when = emit_tei.commit_date(REPO)
    sources = {p4_path.name: emit_tei.sha256(p4_path)[:16],
               "shared-lines.tsv": emit_tei.sha256(shared_lines.TABLE)[:16],
               f"shell {entry.shell}": emit_tei.sha256(p5_path)[:16]}
    applied = [row for r in results for _, row in r.applied]
    pending = [row for row in applied if row.pending]

    def one(with_reviews: bool) -> bytes:
        text = source_text.load_p4(p4_path)
        fresh = tokens.tokenize(text.body)
        rows_in_order = [r for res in results for r in res.rows]
        marks = emit_tei.build_marks(lines, rows_in_order)
        return emit_tei.emit(p5_path, text.body, fresh, marks, "regenerate.py", "0.1.0",
                             commit, when, sources, play, table,
                             emit_tei.review_marks(reviews) if with_reviews else None)

    out_dir.mkdir(parents=True, exist_ok=True)
    source_words = tokens.word_stream(source_text.load_p4(p4_path).body)
    review_bytes = one(True)
    check_words(review_bytes, source_words)
    (out_dir / tei_header.review_filename(play)).write_bytes(review_bytes)
    written = {"review": out_dir / tei_header.review_filename(play)}
    if pending and not allow_pending:
        print(f"canonical build refused: {len(pending)} shared-lines.tsv rows are unchecked "
              f"({', '.join(sorted({r.scene for r in pending}))}); review build written",
              file=sys.stderr)
    else:
        canonical = one(False)
        check_words(canonical, source_words)
        if emit_tei.strip_reviews(review_bytes) != canonical:
            raise ValueError("the review build does not reduce to the canonical build")
        (out_dir / tei_header.canonical_filename(play)).write_bytes(canonical)
        written["canonical"] = out_dir / tei_header.canonical_filename(play)
    return written


def write_reports(play: str, rep: Path, pages, lines, results, toks, body=None, table=None) -> tuple[dict, list, dict]:
    """Write every report, and collect the review comments they carry. Used by
    main and by the tests, so the review build a test sees is the real one."""
    rep.mkdir(parents=True, exist_ok=True)
    stem = f"regenerate-{play}"
    entry = plays.get(play)
    report_gate(rep / f"{stem}-gate.tsv", results)
    report_intervals(rep / f"{stem}-intervals.tsv", results)
    reviews = build_reviews(results, lines, toks)
    reviews += report_words(rep / f"{stem}-word-disagreements.tsv", pages, results)
    failing_scenes = {iv["div"] for r in results for iv in r.failing}
    ovn, anchor_reviews = report_old_vs_new(
        rep / f"{stem}-old-vs-new.tsv", rep / f"{stem}-old-vs-new-anchors.tsv",
        CORPUS / entry.p4, toks, lines, failing_scenes)
    reviews += anchor_reviews
    reviews += report_verse_prose(rep / f"{stem}-verse-prose.tsv", lines)
    reviews += report_borderline(rep / f"{stem}-borderline-rows.tsv", lines)
    folger = report_folger(rep / f"{stem}-folger-check.tsv", lines, toks, entry.dracor_path)
    if body is not None:
        report_part_vs_page(rep / f"{stem}-part-vs-page.tsv", lines, toks, body, table)
    return ovn, reviews, folger


def report_part_vs_page(out: Path, lines, toks, body, table) -> list[list]:
    """Where the P4's @part and the page disagree about shared lines.

    @part was added by the P4's encoding process, not by the keyboarders
    (Cliff, 2026-09-22), so it is not part of the double-keyed text's
    authority and is not infallible. The page decides
    (doc/forum.org #witnesses/division-of-authority); this report is the
    evidence for what that costs the markup, and nothing is retagged."""
    folds = folger_check.folds(lines, toks)

    def container(ti):
        return toks[ti].cont

    def from_table(ln):
        for r in table or []:
            if r.kind == "numeral" or r.scene != ln.div:
                continue
            want = tuple(r.first_half.split())
            k = next((i for i, l in enumerate(lines) if l is ln), None)
            if k is not None and shared_lines.line_words(lines, k, toks, len(want)) == want:
                return f"shared-lines.tsv ({r.basis})"
        return "the page's layout"

    rows, inside = [], set()
    for _, ln in folds:
        first = container(ln.start)
        second = None
        for r in ln.rows[1:]:
            if r.start is not None and container(r.start) is not first:
                second = container(r.start)
                break
        for r in ln.rows:
            if r.start is not None:
                inside.add(id(container(r.start)))
        pa = first.get("part") if first is not None else None
        pb = second.get("part") if second is not None else None
        if pa == "I" and pb in ("F", "Y"):
            continue
        finding = ("P4 marks one half only" if (pa or pb) else "P4 marks neither half")
        rows.append([ln.div, ln.n, ln.page, finding, f"{pa or '-'}/{pb or '-'}", from_table(ln),
                     " / ".join(r.text[:44] for r in ln.rows)])
    by_container = {}
    for ln in lines:
        by_container.setdefault(id(container(ln.start)), ln)
    for l in body.iter(f"{{http://www.tei-c.org/ns/1.0}}l"):
        if l.get("part") != "I" or id(l) in inside:
            continue
        ln = by_container.get(id(l))
        nxt = l.getparent().getnext()
        second = "".join(nxt.itertext()).split() if nxt is not None else []
        rows.append([ln.div if ln else "", ln.n if ln else "", ln.page if ln else "",
                     "P4 marks a pair the page does not fold", "I/-", "the page's layout",
                     " / ".join(["".join(l.itertext()).split() and " ".join("".join(l.itertext()).split())[:44],
                                 " ".join(second)[:44]])])
    rows.sort(key=lambda r: (str(r[0]), r[1] if isinstance(r[1], int) else 0))
    write_tsv(out, ["scene", "line", "page", "finding", "p4_part", "fold_from", "rows"], rows)
    return rows


def report_folger(out: Path, lines, toks, folger: Path) -> dict:
    """The shared-line structure against the Folger's @part and #short. A
    report only: the page decides (doc/forum.org #lineation/shared-lines-table),
    and these numbers are the reason -- the Folger marks a half of many of our
    shared lines as standing alone."""
    try:
        result = folger_check.compare(lines, toks, folger)
    except OSError:  # the Folger edition is not on this machine
        return {}
    write_tsv(out, ["scene", "line", "page", "finding", "folger", "folger_ids", "rows"],
              result["rows"])
    return result


def corpus_branch_refusal(corpus: Path, flags) -> str | None:
    """Why the build must not run against canonical-engLit's checkout, or None.

    The P4 and the shell are read from its working tree, so they change with
    whatever is checked out; every out/lr/ build before 2026-09-28 was made
    from alignment-oracles by accident (doc/agenda.org #build/old-vs-new-from-p4)."""
    if "--any-corpus-branch" in flags:
        return None
    branch = subprocess.run(["git", "-C", str(corpus), "branch", "--show-current"],
                            capture_output=True, text=True).stdout.strip()
    if branch == CORPUS_BRANCH:
        return None
    return (f"refusing to build: {corpus} has {branch or 'a detached HEAD'!s} checked out, "
            f"not {CORPUS_BRANCH}; the P4 and the shell are read from its working tree. "
            f"Check out {CORPUS_BRANCH}, or pass --any-corpus-branch for a development run")


def main(play: str = "lr", *flags) -> int:
    allow_pending = "--allow-pending" in flags
    scratch = next((f.split("=", 1)[1] for f in flags if f.startswith("--scratch=")), None)
    refusal = corpus_branch_refusal(CORPUS, flags)
    if refusal:
        print(refusal, file=sys.stderr)
        return 1
    # before anything is written: the reports are tracked, so writing them
    # first would make a tree dirty that was clean when the run began
    commit = emit_tei.workshop_commit(REPO)
    if scratch is None and commit.endswith("-DIRTY"):
        print("refusing to write out/ or reports/ from a dirty tree (CLAUDE.md: no -DIRTY "
              "stamp); use --scratch=DIR for a development run", file=sys.stderr)
        return 1
    table = shared_lines.read_table()
    text, toks, pages, lines, results = build(play, table)
    reports_dir = Path(scratch) / "reports" if scratch else REPO / "reports" / "globe"
    ovn, reviews, folger = write_reports(play, reports_dir, pages, lines, results, toks,
                                         text.body, table)
    failing = [iv for r in results for iv in r.failing]
    print(f"{play}: {len(lines)} Globe lines; {sum(1 for r in results if not r.failing)}/{len(results)} "
          f"pages pass; {len(failing)} failing intervals; P4 anchors: {ovn['mapped']}/{ovn['anchors']} "
          f"mapped, {ovn['agree']} agreeing ({ovn['agree_clean']}/{ovn['clean']} in scenes that pass), "
          f"{ovn['unmapped']} unmapped", file=sys.stderr)
    if folger:
        c = folger["counts"]
        print(f"folger: of {sum(c.values())} shared lines it marks {c['part']} as part=I/F, "
              f"{c['short']} with a half standing alone, {c['silent']} not at all; of its "
              f"{folger['pairs']} I/F pairs {folger['together']} fall in one Globe line, "
              f"{folger['split']} across two ({folger['aligned']:.0%} of its words aligned)",
              file=sys.stderr)
    for iv in failing:
        print(f"  p.{iv['page']} {iv['witness']} {iv['div']} {iv['frm']} -> {iv['to']}: "
              f"counted {iv['counted_gap']}, printed {iv['printed_gap']} ({iv['error']:+d})", file=sys.stderr)
    if failing:
        print("gate failed: the play is not written", file=sys.stderr)
        return 1

    out_dir = Path(scratch) / play if scratch else REPO / "out" / "globe" / play
    written = emit_builds(play, lines, results, toks, reviews, out_dir, allow_pending, table, commit)
    for kind, path in written.items():
        print(f"{kind}: {path.relative_to(REPO) if REPO in path.parents else path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
