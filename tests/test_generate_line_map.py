from __future__ import annotations

import json
import shutil
import sys

import pytest

from commands.generate_line_map import main


def _invoke(argv: list[str]) -> int:
    sys.argv = argv
    with pytest.raises(SystemExit) as exc:
        main()
    return exc.value.code


@pytest.fixture
def corpus_dir(tmp_path, shared_datadir):
    d = tmp_path / "corpus"
    d.mkdir()
    shutil.copy(shared_datadir / "hamlet-excerpt.xml", d / "hamlet.xml")
    shutil.copy(shared_datadir / "macbeth-excerpt.xml", d / "macbeth.xml")
    return d


def test_generate_line_map_writes_combined_json(corpus_dir, tmp_path):
    output = tmp_path / "line-map.json"
    exit_code = _invoke(["generate-line-map", str(corpus_dir), "-o", str(output)])

    assert exit_code == 0
    data = json.loads(output.read_text())
    assert set(data["plays"]) == {"ham", "mac"}
    assert data["plays"]["ham"]["source_file"] == "hamlet.xml"
    assert len(data["plays"]["ham"]["lines"]) == 5


def test_generate_line_map_skips_bad_file_and_reports_error(corpus_dir, tmp_path):
    (corpus_dir / "broken.xml").write_text("<TEI><unclosed>")
    output = tmp_path / "line-map.json"

    exit_code = _invoke(["generate-line-map", str(corpus_dir), "-o", str(output)])

    assert exit_code == 1
    data = json.loads(output.read_text())
    assert set(data["plays"]) == {"ham", "mac"}
