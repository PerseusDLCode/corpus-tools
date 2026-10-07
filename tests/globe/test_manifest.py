"""doc/globe-lineation.org: the witness manifest pins what the build reads,
and globe-verify compares a build with the published file stamp aside.

Added with the move into corpus-tools; not among the workshop's tests.
"""

import subprocess
from pathlib import Path

import pytest

from commands.globe_lineation import without_stamp
from globe import manifest, witnesses
from globe.manifest import ManifestError

REGISTRY_TOML = """
[toy]
catalog = { ia = "toy_item" }
scans = { dir = "Toy/scans", pattern = "s_{leaf}.jpg" }
leaves = "data/leaves-toy.tsv"

[toy.ocr.kraken]
format = "kraken-alto"
dir = "Toy/kraken"
pattern = "{leaf}.xml"
"""
ORDER = [("toy", "kraken")]


def setup(tmp_path: Path):
    """Witness files under root, the leaf table and registry under repo."""
    root, repo = tmp_path / "witnesses", tmp_path / "repo"
    (root / "Toy/scans").mkdir(parents=True)
    (root / "Toy/kraken").mkdir(parents=True)
    (repo / "data").mkdir(parents=True)
    rows = ""
    for leaf, printed in [("001", 10), ("002", 11), ("003", 12)]:
        (root / f"Toy/scans/s_{leaf}.jpg").write_bytes(b"x")
        (root / f"Toy/kraken/{leaf}.xml").write_text(f"<alto n='{leaf}'/>")
        rows += f"{leaf}\ts_{leaf}.jpg\t{printed}\taudit\t\n"
    (repo / "data/leaves-toy.tsv").write_text("leaf\tfile\tprinted\tbasis\tnote\n" + rows)
    (repo / "witnesses.toml").write_text(REGISTRY_TOML)
    reg = witnesses.load(registry=repo / "witnesses.toml", repo=repo, root=root)
    return reg, root, repo, repo / "manifest.tsv"


def test_the_manifest_lists_the_leaf_table_and_one_alto_per_page(tmp_path):
    reg, root, repo, m = setup(tmp_path)
    assert manifest.write("toy", reg, ORDER, 10, 11, m, root, repo) == 3
    got = [(r["base"], r["path"], r["catalog"]) for r in manifest.read(m)]
    assert got == [("repo", "data/leaves-toy.tsv", "ia=toy_item"),
                   ("GLOBE_WITNESSES", "Toy/kraken/001.xml", "ia=toy_item"),
                   ("GLOBE_WITNESSES", "Toy/kraken/002.xml", "ia=toy_item")]
    manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo)


def test_a_changed_leaf_is_refused_and_named(tmp_path):
    reg, root, repo, m = setup(tmp_path)
    manifest.write("toy", reg, ORDER, 10, 11, m, root, repo)
    (root / "Toy/kraken/002.xml").write_text("<alto n='edited'/>")
    with pytest.raises(ManifestError, match=r"sha256 differs.*Toy/kraken/002\.xml"):
        manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo)


def test_a_page_the_manifest_does_not_pin_is_refused(tmp_path):
    reg, root, repo, m = setup(tmp_path)
    manifest.write("toy", reg, ORDER, 10, 11, m, root, repo)
    with pytest.raises(ManifestError, match=r"not in the manifest.*Toy/kraken/003\.xml"):
        manifest.verify("toy", reg, ORDER, 10, 12, m, root, repo)


def test_rewriting_one_play_keeps_the_others_rows(tmp_path):
    reg, root, repo, m = setup(tmp_path)
    manifest.write("toy", reg, ORDER, 10, 11, m, root, repo)
    manifest.write("other", reg, ORDER, 12, 12, m, root, repo)
    manifest.write("toy", reg, ORDER, 10, 10, m, root, repo)
    assert [r["play"] for r in manifest.read(m)] == ["other", "other", "toy", "toy"]


def dracor_clone(tmp_path: Path) -> tuple[Path, str]:
    """A git clone with one committed play file; returns it and its commit."""
    clone = tmp_path / "shakedracor"
    (clone / "tei").mkdir(parents=True)
    (clone / "tei/toy.xml").write_text('<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="shake000099"/>')

    def git(*args):
        return subprocess.run(["git", "-C", str(clone), "-c", "user.name=t", "-c", "user.email=t@example.org",
                               *args], check=True, capture_output=True, text=True).stdout.strip()
    git("init", "-q")
    git("add", "tei/toy.xml")
    git("commit", "-q", "-m", "toy")
    return clone, git("rev-parse", "--short=7", "HEAD")


def pinned(tmp_path):
    """The toy play's manifest, with its ShakeDraCor file pinned."""
    reg, root, repo, m = setup(tmp_path)
    clone, commit = dracor_clone(tmp_path)
    n = manifest.write("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml", clone=clone)
    return reg, root, repo, m, clone, commit, n


def test_the_dracor_file_is_pinned_with_its_commit_and_play_id(tmp_path):
    """canonical-engLit doc/agenda.org #globe/pin-dracor."""
    reg, root, repo, m, clone, commit, n = pinned(tmp_path)
    assert n == 4
    row = manifest.read(m)[-1]
    assert (row["witness"], row["file"], row["base"], row["path"]) == (
        "dracor", "folger", "SHAKEDRACOR", "tei/toy.xml")
    assert row["catalog"] == f"github=dracor-org/shakedracor commit={commit} play=shake000099"
    assert row["sha256"] == manifest.sha256(clone / "tei/toy.xml")
    pin = manifest.dracor_pin("toy", m)
    assert (pin["commit"], pin["play"], pin["path"]) == (commit, "shake000099", "tei/toy.xml")
    manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml", clone=clone)


def test_a_changed_dracor_file_is_refused_and_named(tmp_path):
    """The build read whatever the clone had checked out; now it must be the
    pinned bytes."""
    reg, root, repo, m, clone, _, _ = pinned(tmp_path)
    (clone / "tei/toy.xml").write_text("<TEI xml:id='edited'/>")
    with pytest.raises(ManifestError, match=r"sha256 differs.*SHAKEDRACOR/tei/toy\.xml"):
        manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml", clone=clone)


def test_an_absent_clone_is_not_refused_but_an_unpinned_dracor_file_is(tmp_path):
    """Without the clone the Folger report is skipped, as before; the pin
    itself is required, since the header is written from it."""
    reg, root, repo, m, clone, _, _ = pinned(tmp_path)
    manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml",
                    clone=tmp_path / "nowhere")
    manifest.write("toy", reg, ORDER, 10, 11, m, root, repo)  # rewritten without the pin
    with pytest.raises(ManifestError, match=r"not in the manifest: SHAKEDRACOR/tei/toy\.xml"):
        manifest.verify("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml", clone=clone)
    with pytest.raises(ManifestError, match="0 ShakeDraCor rows for toy"):
        manifest.dracor_pin("toy", m)


def test_a_dracor_file_is_pinned_only_as_it_is_committed(tmp_path):
    """The commit recorded must be true of the bytes pinned beside it."""
    reg, root, repo, m = setup(tmp_path)
    clone, commit = dracor_clone(tmp_path)
    (clone / "tei/toy.xml").write_text("<TEI xml:id='edited'/>")
    with pytest.raises(ManifestError, match=rf"differs from the clone's commit {commit}"):
        manifest.write("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml", clone=clone)
    with pytest.raises(ManifestError, match="is not on this machine"):
        manifest.write("toy", reg, ORDER, 10, 11, m, root, repo, dracor="tei/toy.xml",
                       clone=tmp_path / "nowhere")
    assert not m.exists()  # a refused pin writes nothing


def test_lear_is_pinned_at_the_commit_its_published_header_names():
    pin = manifest.dracor_pin("lr")
    assert (pin["commit"], pin["play"], pin["path"]) == ("c34c2d4", "shake000033", "tei/king-lear.xml")


STAMPED = (b'<revisionDesc><change when="{when}"><ab>Globe lineation regenerated from the witness '
           b'pages by regenerate.py 0.1.0 at {commit}; sources: x. Generated file: DO NOT EDIT.</ab>'
           b'</change><change><ab>converted to TEI P5</ab></change></revisionDesc><body>{body}</body>')


def stamped(when=b"2026-09-29", commit=b"commit b413a28", body=b"text") -> bytes:
    return STAMPED.replace(b"{when}", when).replace(b"{commit}", commit).replace(b"{body}", body)


def test_verify_ignores_the_stamp_and_nothing_else():
    a = stamped()
    assert without_stamp(a) == without_stamp(stamped(b"2026-10-07", b"corpus-tools commit 1234567"))
    assert without_stamp(a) != without_stamp(stamped(body=b"texts"))
    assert b"converted to TEI P5" in without_stamp(a)


def test_verify_refuses_a_file_without_exactly_one_stamp():
    with pytest.raises(ValueError, match="found 0"):
        without_stamp(b"<revisionDesc/>")
    with pytest.raises(ValueError, match="found 2"):
        without_stamp(stamped() + stamped())
