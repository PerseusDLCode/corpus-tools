"""doc/agenda.org #phase0/witness-registry: the loader refuses to run on a mismatch.

The refusal tests build a tiny synthetic registry in a temp directory and
break it one way at a time, so each failure names exactly the problem.
The last tests read the real registry and leaf tables.
"""

from pathlib import Path

import pytest

from globe import witnesses
from globe.witnesses import RegistryError


REGISTRY_TOML = """
[toy]
scans = { dir = "scans", pattern = "s_{leaf}.jpg" }
leaves = "leaves.tsv"

[toy.ocr.kraken]
format = "kraken-alto"
dir = "kraken"
pattern = "{leaf}.xml"

[toy.ocr.djvu]
format = "djvu"
path = "text.xml"
key = "toy_{leaf}.djvu"
"""

LEAVES = [("001", 1, "offset"), ("002", 2, "audit"), ("003", 3, "reviewed")]


def build(tmp_path: Path) -> Path:
    """A consistent three-leaf witness; returns the registry path."""
    (tmp_path / "scans").mkdir()
    (tmp_path / "kraken").mkdir()
    for leaf, _, _ in LEAVES:
        (tmp_path / "scans" / f"s_{leaf}.jpg").write_bytes(b"x")
        (tmp_path / "kraken" / f"{leaf}.xml").write_text("<alto/>")
    rows = "".join(f"{leaf}\ts_{leaf}.jpg\t{printed}\t{basis}\t\n" for leaf, printed, basis in LEAVES)
    (tmp_path / "leaves.tsv").write_text("leaf\tfile\tprinted\tbasis\tnote\n" + rows)
    objects = "".join(f'<OBJECT usemap="toy_{leaf}.djvu" width="9" height="9"></OBJECT>' for leaf, _, _ in LEAVES)
    (tmp_path / "text.xml").write_text(f"<DjVuXML>{objects}<OBJECT usemap=\"toy_000.djvu\"/></DjVuXML>")
    reg = tmp_path / "witnesses.toml"
    reg.write_text(REGISTRY_TOML)
    return reg


def load(tmp_path: Path, reg: Path):
    return witnesses.load(registry=reg, repo=tmp_path, root=tmp_path)


def test_consistent_registry_loads(tmp_path):
    w = load(tmp_path, build(tmp_path)).witness("toy")
    assert len(w.leaves) == 3
    assert w.leaves.leaf_for_printed(2) == "002"
    assert w.scan_path("002").name == "s_002.jpg"
    assert w.layer("kraken").file_for("002").name == "002.xml"


def test_missing_alto_file_is_refused_and_named(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "kraken/002.xml").unlink()
    with pytest.raises(RegistryError) as e:
        load(tmp_path, reg)
    msg = str(e.value)
    assert "toy/kraken ALTO: 1 missing: 002.xml" in msg
    assert "kraken ALTO 2" in msg and "leaf table 3" in msg  # the counts are in the message


def test_count_mismatch_from_an_extra_file_is_refused(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "kraken/004.xml").write_text("<alto/>")
    with pytest.raises(RegistryError, match=r"toy/kraken ALTO: 1 not in the leaf table: 004\.xml"):
        load(tmp_path, reg)


def test_leaf_table_row_with_no_scan_is_refused(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "scans/s_003.jpg").unlink()
    with pytest.raises(RegistryError, match=r"scans: 1 missing: s_003\.jpg"):
        load(tmp_path, reg)


def test_leaf_with_no_djvu_text_is_refused(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "text.xml").write_text('<DjVuXML><OBJECT usemap="toy_001.djvu"/></DjVuXML>')
    with pytest.raises(RegistryError, match=r"toy/djvu: 2 leaves have no text in text\.xml: toy_002\.djvu, toy_003\.djvu"):
        load(tmp_path, reg)


def test_missing_directory_and_file_are_named(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "text.xml").unlink()
    for f in (tmp_path / "kraken").iterdir():
        f.unlink()
    (tmp_path / "kraken").rmdir()
    with pytest.raises(RegistryError) as e:
        load(tmp_path, reg)
    assert "toy/kraken: directory missing" in str(e.value)
    assert "toy/djvu: file missing" in str(e.value)


def test_every_problem_is_reported_not_just_the_first(tmp_path):
    reg = build(tmp_path)
    (tmp_path / "kraken/001.xml").unlink()
    (tmp_path / "scans/s_002.jpg").unlink()
    with pytest.raises(RegistryError) as e:
        load(tmp_path, reg)
    assert "toy/kraken ALTO: 1 missing" in str(e.value) and "scans: 1 missing" in str(e.value)


def test_leaf_table_that_disagrees_with_the_scan_pattern_is_refused(tmp_path):
    reg = build(tmp_path)
    t = tmp_path / "leaves.tsv"
    t.write_text(t.read_text().replace("s_002.jpg", "wrong.jpg"))
    with pytest.raises(RegistryError, match="not the registry's scan pattern"):
        load(tmp_path, reg)


def test_duplicate_printed_page_and_bad_basis_are_refused(tmp_path):
    reg = build(tmp_path)
    t = tmp_path / "leaves.tsv"
    t.write_text(t.read_text().replace("003\ts_003.jpg\t3\treviewed", "003\ts_003.jpg\t2\tguess"))
    with pytest.raises(RegistryError) as e:
        load(tmp_path, reg)
    assert "printed page on more than one leaf: 2" in str(e.value)
    assert "basis must be one of" in str(e.value)


def test_printed_page_lookup_must_match_exactly_one_leaf(tmp_path):
    w = load(tmp_path, build(tmp_path)).witness("toy")
    with pytest.raises(RegistryError, match="printed page 99 matches 0 leaves"):
        w.leaves.leaf_for_printed(99)


def test_unknown_witness_and_layer_are_named(tmp_path):
    reg = load(tmp_path, build(tmp_path))
    with pytest.raises(RegistryError, match="no witness 'mdp'"):
        reg.witness("mdp")
    with pytest.raises(RegistryError, match="no OCR layer 'tesseract'"):
        reg.witness("toy").layer("tesseract")


def test_missing_registry_or_leaf_table_is_refused(tmp_path):
    with pytest.raises(RegistryError, match="registry missing"):
        witnesses.load(registry=tmp_path / "nope.toml", repo=tmp_path, root=tmp_path)
    reg = build(tmp_path)
    (tmp_path / "leaves.tsv").unlink()
    with pytest.raises(RegistryError, match="leaf table missing"):
        load(tmp_path, reg)


# ------------------------------------------------- the real registry


@pytest.fixture(scope="module")
def real():
    return witnesses.load()


def test_real_registry_pairs(real):
    assert real.pairs() == [("trent", "djvu"), ("trent", "kraken"), ("miun", "kraken")]


@pytest.mark.parametrize("wid", ["trent", "miun"])
def test_real_leaf_tables_have_1054_rows_printed_1_to_1054(real, wid):
    rows = real.witness(wid).leaves.rows
    assert len(rows) == 1054
    assert sorted(r.printed for r in rows) == list(range(1, 1055))


def test_real_p860_leaves(real):
    assert real.witness("trent").leaves.leaf_for_printed(860) == "0876"
    assert real.witness("miun").leaves.leaf_for_printed(860) == "00000874"


def test_miun_transposition_is_recorded_explicitly(real):
    t = real.witness("miun").leaves
    assert t.row("00000267").printed == 254 and t.row("00000268").printed == 253
    assert t.row("00000267").basis == t.row("00000268").basis == "reviewed"
    # everywhere else it is the constant +14 offset
    others = [r for r in t.rows if r.leaf not in ("00000267", "00000268")]
    assert all(r.printed == int(r.leaf) - 14 for r in others)


def test_trent_table_is_a_constant_offset_with_one_reviewed_row(real):
    t = real.witness("trent").leaves
    assert all(r.printed == int(r.leaf) - 16 for r in t.rows)
    assert [r.leaf for r in t.rows if r.basis == "reviewed"] == ["0876"]
    assert {r.basis for r in t.rows if r.leaf != "0876"} == {"offset"}


def test_missing_registered_metadata_file_is_refused(tmp_path):
    reg = build(tmp_path)
    reg.write_text(reg.read_text() + '\n[toy.metadata]\npage_numbers = "meta.json"\n')
    with pytest.raises(RegistryError, match=r"toy metadata 'page_numbers': file missing"):
        load(tmp_path, reg)
    (tmp_path / "meta.json").write_text("{}")
    assert load(tmp_path, reg).witness("toy").metadata["page_numbers"].name == "meta.json"
