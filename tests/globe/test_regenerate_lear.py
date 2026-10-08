"""doc/agenda.org #build/regenerate-lear: the build against real inputs.

- the vendored P4 conversion equals corpus-tools' own at the pinned commit;
- the three spike pages (847, 856, 860) reproduce the spike's line starts and
  numbers (tests/globe/fixtures/spike-lr-*.tsv);
- the gate's outcome on Lear, as recorded in the agenda status.

Skipped when the sibling repos or the witness OCR are not on disk.
"""

import csv
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

from globe import p4_convert

REPO = Path(__file__).resolve().parent.parent.parent

TEI_NS = "http://www.tei-c.org/ns/1.0"

CORPUS_TOOLS = REPO
P4 = REPO.parent / "canonical-engLit/Renaissance/Shakespeare/opensource/lr.xml"
VENDORED_FROM = "10a6f74"
FIXTURES = REPO / "tests/globe/fixtures"

needs_p4 = pytest.mark.skipif(not P4.is_file(), reason="canonical-engLit P4 source not on disk")


def _witnesses_present() -> bool:
    try:
        from globe import witnesses
        witnesses.load(["miun", "trent"])
        return P4.is_file()
    except Exception:
        return False


needs_witnesses = pytest.mark.skipif(not _witnesses_present(), reason="witness OCR not on disk")


@needs_p4
@pytest.mark.skipif(not (CORPUS_TOOLS / ".git").exists(), reason="corpus-tools not on disk")
def test_vendored_conversion_equals_corpus_tools_at_the_pinned_commit(tmp_path):
    for name in ("globe_lineation.py", "tei.py"):
        src = subprocess.run(["git", "-C", str(CORPUS_TOOLS), "show", f"{VENDORED_FROM}:src/{name}"],
                             check=True, capture_output=True, text=True).stdout
        (tmp_path / name).write_text(src)
    sys.path.insert(0, str(tmp_path))
    try:
        spec = importlib.util.spec_from_file_location("upstream_globe_lineation", tmp_path / "globe_lineation.py")
        upstream = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = upstream  # its dataclasses look their module up
        spec.loader.exec_module(upstream)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("upstream_globe_lineation", None)
        sys.modules.pop("tei", None)
    ours = p4_convert.convert_body(p4_convert.parse_p4(P4), p4_convert.ConversionStats())
    theirs = upstream.convert_body(upstream.parse_p4(P4), upstream.ConversionStats())
    assert etree.tostring(ours) == etree.tostring(theirs)


@pytest.fixture(scope="module")
def lear():
    from globe import regenerate
    from globe import shared_lines
    return regenerate.build("lr", shared_lines.read_table())


@pytest.fixture(scope="module")
def lear_untabled():
    from globe import regenerate
    return regenerate.build("lr", table=[])


def _fixture(page):
    with (FIXTURES / f"spike-lr-{page}.tsv").open() as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"))


@needs_witnesses
@pytest.mark.parametrize("page", [847, 856, 860])
def test_spike_pages_reproduce(lear, page):
    """Every line the spike numbered starts at the same word, with the same
    number. Speaker names are skipped when comparing: they are tokens here
    (alignment anchors) and were not in the spike."""
    _, toks, _, lines, _ = lear
    by = {(ln.div, ln.n): ln for ln in lines}
    for r in _fixture(page):
        ln = by.get((r["div"], int(r["n"])))
        assert ln is not None, r
        words = [t.t for t in toks[ln.start:ln.start + 12] if t.kind != "speaker"][:5]
        assert " ".join(words) == r["start_words"], (r, words)


@needs_witnesses
def test_the_gate_passes_with_the_reviewed_table(lear):
    """With data/shared-lines.tsv applied, every page passes: each of its 273
    intervals between printed marginal numbers closes exactly."""
    *_, results = lear
    assert [iv for r in results for iv in r.failing] == []
    assert len(results) == 32
    intervals = [iv for r in results for iv in r.intervals]
    assert len(intervals) == 273


@needs_witnesses
def test_without_the_table_the_gate_fails_where_it_did(lear_untabled):
    """The failures the table answers, as recorded in the agenda status: two
    from p.852's numeral, and one +1 for each undisplaceable shared line."""
    *_, results = lear_untabled
    failing = [(iv["page"], iv["div"], iv["to"], iv["error"]) for r in results for iv in r.failing]
    assert failing == [
        (852, "1.4", 30, 9), (852, "1.4", 60, -9),
        (866, "3.7", 50, 1), (868, "4.2", 20, 1), (871, "4.6", 40, 1), (872, "4.6", 230, 1),
        (875, "5.3", 30, 1), (877, "5.3", 151, 1), (878, "5.3", 259, 1), (878, "5.3", 271, 1),
    ]


@needs_witnesses
def test_the_output_is_the_p4_text_with_a_milestone_on_every_line(lear, tmp_path):
    """The build's own checks, end to end: the word stream is the P4's, every
    Globe line has one numbered milestone, no F1 milestone survives, and the
    review build reduces to the canonical one."""
    from globe import plays
    from globe import regenerate
    from globe import shared_lines
    from globe import tokens as tk
    from lxml import etree

    _, toks, pages, lines, results = lear
    _, reviews, _ = regenerate.write_reports("lr", tmp_path / "reports", pages, lines, results, toks)
    written = regenerate.emit_builds("lr", lines, results, None, reviews, tmp_path,
                                     allow_pending=True, table=shared_lines.read_table())
    assert set(written) == {"review", "canonical"}
    root = etree.parse(str(written["canonical"])).getroot()
    body = root.find(f"{{{TEI_NS}}}text/{{{TEI_NS}}}body")
    ms = [m for m in body.iter(f"{{{TEI_NS}}}milestone")]
    assert len(ms) == len(lines)
    assert all(m.get("ed") == "Globe" and m.get("n") for m in ms)
    assert all(m.get("source") is None and m.get("type") is None for m in ms)
    by_scene = {}
    for ln in lines:
        by_scene.setdefault(ln.div, []).append(ln.n)
    assert all(ns == list(range(1, len(ns) + 1)) for ns in by_scene.values())
    from globe import emit_tei
    assert emit_tei.strip_reviews(written["review"].read_bytes()) == written["canonical"].read_bytes()

    header = root.find(f"{{{TEI_NS}}}teiHeader")
    source_desc = etree.tostring(header.find(f".//{{{TEI_NS}}}sourceDesc"), encoding="unicode")
    assert 'xml:id="witness-miun"' in source_desc and 'xml:id="witness-trent"' in source_desc
    assert 'xml:id="globe-edition"' not in source_desc  # retired with @source
    assert "1893" not in source_desc and "1853" not in source_desc  # #build/header-fixes
    editorial_decl = etree.tostring(header.find(f".//{{{TEI_NS}}}editorialDecl"), encoding="unicode")
    assert "not carried by this edition" in editorial_decl  # F1
    assert "mapping" not in editorial_decl  # no Globe-TLN map is planned (#build/retire-rederive)
    import re

    from globe import tei_header
    count = tei_header.count_junctions(shared_lines.read_table())
    assert f"{tei_header._spell(count).capitalize()} junctions" in editorial_decl
    assert f"{count} junctions" not in editorial_decl  # spelled, not a digit

    pub_stmt = etree.tostring(header.find(f".//{{{TEI_NS}}}publicationStmt"), encoding="unicode")
    assert f'idno type="filename">{written["canonical"].name}<' in pub_stmt
    body_xml_base = body.get("{http://www.w3.org/XML/1998/namespace}base")
    assert f'idno type="CTS">{body_xml_base}<' in pub_stmt
    assert "<date" not in pub_stmt

    change = header.find(f".//{{{TEI_NS}}}revisionDesc/{{{TEI_NS}}}change")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", change.get("when"))
    # the shell is pinned beside the other sources (#build/old-vs-new-from-p4)
    shell_rel = plays.get("lr").shell
    stamp = "".join(change.itertext())
    assert f"shell {shell_rel} sha256 {emit_tei.sha256(regenerate.CORPUS / shell_rel)[:16]}" in stamp
    refs_decl = header.find(f".//{{{TEI_NS}}}refsDecl")
    assert refs_decl.find(f"{{{TEI_NS}}}citeStructure").get("match") == "/TEI/text/body"
    # every Globe line is citable through it, and the cast list is not an act
    tei_header.check_every_line_citable(body)
    assert "@n != 'cast'" in etree.tostring(refs_decl, encoding="unicode")


@needs_witnesses
def test_an_unchecked_table_row_refuses_the_canonical_build(lear, tmp_path):
    """The canonical build waits on a person having read the page: a row whose
    `checked` column is empty blocks it, and the review build is written
    anyway, so the question stays visible in the text."""
    import dataclasses

    from globe import regenerate
    from globe import shared_lines

    _, toks, pages, lines, results = lear
    pending = dataclasses.replace(shared_lines.read_table()[0], checked="")
    saved = [r.applied for r in results]  # the fixture is shared: put it back
    try:
        for r in results:
            r.applied = [(k, pending) for k, _ in r.applied]
        _, reviews, _ = regenerate.write_reports("lr", tmp_path / "reports", pages, lines,
                                                 results, toks)
        written = regenerate.emit_builds("lr", lines, results, None, reviews, tmp_path,
                                         allow_pending=False, table=shared_lines.read_table())
    finally:
        for r, applied in zip(results, saved):
            r.applied = applied
    assert set(written) == {"review"}
    assert "PENDING" in written["review"].read_text()


@needs_witnesses
def test_the_review_build_comments_every_page_and_every_kind(lear, tmp_path):
    """The review build is what Cliff reads, so each page says where it came
    from, and every kind the agenda lists appears where it applies."""
    import re

    from globe import regenerate
    from globe import shared_lines

    _, toks, pages, lines, results = lear
    _, reviews, _ = regenerate.write_reports("lr", tmp_path / "reports", pages, lines, results, toks)
    written = regenerate.emit_builds("lr", lines, results, None, reviews, tmp_path,
                                     allow_pending=True, table=shared_lines.read_table())
    text = written["review"].read_text()
    kinds = re.findall(r"<!-- REVIEW ([a-z-]+):", text)
    assert kinds.count("page") == 32
    assert set(kinds) >= {"page", "shared", "numeral", "witness", "turnover", "words",
                          "anchor", "verse-prose"}
    # six shared junctions and two unmarked turnovers, each recording its state
    assert kinds.count("shared") == 6
    assert "PENDING" not in text  # every table row has been checked on the image
    assert text.count("checked 2026-09-2") == 9
    assert "sets flush, not at the turnover indent" in text
    assert "REVIEW" not in written["canonical"].read_text()


@needs_witnesses
def test_misread_numerals_are_resolved_by_the_other_witness(lear):
    *_, results = lear
    readings = {(iv["page"], iv["to"]): iv["reading"] for r in results for iv in r.intervals if iv["reading"]}
    assert readings[(849, 260)] == "miun/kraken read 269; trent/kraken read 260"
    assert readings[(852, 71)] == "miun/kraken read 1; trent/kraken read 71"


@needs_p4
def test_p4_anchors_are_the_numbered_globe_markers_each_labelling_the_row_after_it():
    """#build/old-vs-new-from-p4: the old numbers come from the P4. Lear has
    274 numbered <lb ed="G"/>; its two stray <l n> are not markers and are not
    read. A marker ends a row and labels the next ("...acknowledge <lb n="11"/>him")."""
    from globe import source_text
    from globe import tokens as tk
    anchors = source_text.p4_anchors(P4)
    assert len(anchors) == 274
    toks = tk.tokenize(source_text.load_p4(P4).body)
    first = anchors[0]
    assert (first.div, first.n) == ("1.1", "11")
    assert [t.raw for t in toks[first.row_start:first.row_start + 3]] == ["him,", "that", "now"]
    assert all(a.row_start < a.row_end for a in anchors)


@needs_witnesses
def test_old_against_new_reads_the_p4_and_maps_only_rows_that_begin_a_line(lear, tmp_path):
    """The comparison as reported on 2026-09-28: of 274 anchors, 221 label a
    row that begins a Globe line and 219 of those carry its number; the 53
    whose row begins inside a line are unmapped, not scored. Its result must
    not depend on the shell: the P4 path is all it is given."""
    from globe import regenerate

    _, toks, pages, lines, results = lear
    out, summary = tmp_path / "ovn.tsv", tmp_path / "anchors.tsv"
    stats, reviews = regenerate.report_old_vs_new(out, summary, P4, toks, lines, set())
    assert (stats["anchors"], stats["mapped"], stats["agree"], stats["unmapped"]) == (274, 221, 219, 53)
    assert (stats["containing"], stats["next"], stats["neither"]) == (28, 24, 1)
    listed = [l.split("\t")[:3] for l in summary.read_text().splitlines()[6:]]
    assert listed == [["1.4", "340", "disagree"], ["4.7", "99", "disagree"],
                      ["5.3", "161", "unmapped (neither)"]]
    assert len(reviews) == 3
    for f in (out, summary):
        assert f.read_text().startswith("# baseline: the Globe numbers the P4 transcribed")


def _git_repo_on(path, branch):
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)
    return path


def test_the_build_refuses_unless_canonical_englit_is_on_mvp(tmp_path):
    from globe import regenerate
    assert regenerate.corpus_branch_refusal(_git_repo_on(tmp_path / "a", "mvp"), ()) is None
    other = _git_repo_on(tmp_path / "b", "alignment-oracles")
    refusal = regenerate.corpus_branch_refusal(other, ())
    assert "alignment-oracles" in refusal and "not mvp" in refusal
    assert regenerate.corpus_branch_refusal(other, ("--any-corpus-branch",)) is None


def test_main_stops_before_building_on_the_wrong_branch(tmp_path, monkeypatch, capsys):
    from globe import regenerate
    monkeypatch.setattr(regenerate, "CORPUS", _git_repo_on(tmp_path / "c", "main"))
    monkeypatch.setattr(regenerate, "build", lambda *a, **k: pytest.fail("built anyway"))
    assert regenerate.main("lr", f"--scratch={tmp_path / 'out'}") == 1
    assert "refusing to build" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_main_refuses_a_dirty_tree_before_writing_anything(tmp_path, monkeypatch, capsys):
    """Checked first: writing the tracked reports and then checking would
    refuse every run whose reports change."""
    from globe import emit_tei
    from globe import regenerate
    monkeypatch.setattr(regenerate, "CORPUS", _git_repo_on(tmp_path / "d", "mvp"))
    monkeypatch.setattr(emit_tei, "workshop_commit", lambda repo: "abc1234-DIRTY")
    monkeypatch.setattr(regenerate, "build", lambda *a, **k: pytest.fail("built anyway"))
    assert regenerate.main("lr") == 1
    assert "dirty tree" in capsys.readouterr().err


@needs_witnesses
def test_a_scratch_run_writes_nothing_in_the_repo(tmp_path):
    """--scratch=DIR puts the builds and every report under DIR."""
    from globe import regenerate

    def status():
        return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--ignored=no"],
                              check=True, capture_output=True, text=True).stdout
    before = status()
    mtimes = {p: p.stat().st_mtime_ns for p in (REPO / "reports" / "globe").glob("regenerate-lr-*")}
    assert regenerate.main("lr", f"--scratch={tmp_path}", "--any-corpus-branch") == 0
    assert status() == before
    assert {p: p.stat().st_mtime_ns for p in (REPO / "reports" / "globe").glob("regenerate-lr-*")} == mtimes
    anchors = (tmp_path / "reports" / "regenerate-lr-old-vs-new-anchors.tsv").read_text()
    assert "transcribed anchors: 274; mapped (the row begins a line): 221" in anchors
    assert (tmp_path / "lr" / "shakespeare.lr.globe.xml").is_file()


@needs_witnesses
def test_the_stamp_names_the_commit_as_it_was_before_the_reports_were_written(tmp_path, monkeypatch):
    """A real run rewrites the tracked reports, which dirties the tree; the
    stamp must not pick that up. Here the commit reads dirty once the
    reports are written."""
    from globe import emit_tei
    from globe import regenerate
    written = []
    real = regenerate.write_reports
    monkeypatch.setattr(regenerate, "write_reports", lambda *a, **k: written.append(1) or real(*a, **k))
    monkeypatch.setattr(emit_tei, "workshop_commit",
                        lambda repo: "abc1234-DIRTY" if written else "abc1234")
    assert regenerate.main("lr", f"--scratch={tmp_path}", "--any-corpus-branch") == 0
    assert "at corpus-tools commit abc1234;" in (tmp_path / "lr" / "shakespeare.lr.globe.xml").read_text()
