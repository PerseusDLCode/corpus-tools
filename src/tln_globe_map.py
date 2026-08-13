from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from tei import TEIDocument, XML_ID, NS


@dataclass
class LineRecord:
    tln: int
    globe: str
    part: str | None
    element: str


class DuplicateKeyError(ValueError):
    pass


class PlayMapper:
    def __init__(self, file_path: Path | str) -> None:
        self.doc = TEIDocument(file_path)
        self._records: list[LineRecord] | None = None
        self._globe_map: dict[str, int] | None = None
        self._tln_map: dict[int, str] | None = None

    @property
    def records(self) -> list[LineRecord]:
        if self._records is None:
            records = []
            for line in self._lines_with_ftln():
                ftln = line.get(XML_ID)
                _, _, tln_str = ftln.partition('-')
                records.append(LineRecord(
                    tln=int(tln_str),
                    globe=line.get('n'),
                    part=line.get('part'),
                    element=etree_localname(line),
                ))
            self._records = records
        return self._records

    @property
    def globe_map(self) -> dict[str, int]:
        if self._globe_map is None:
            number_map: dict[str, int] = {}
            for record in self.records:
                if record.globe in number_map:
                    raise DuplicateKeyError(
                        f"{self.doc.path}: duplicate Globe reference {record.globe!r} "
                        f"(TLNs {number_map[record.globe]} and {record.tln})"
                    )
                number_map[record.globe] = record.tln
            self._globe_map = number_map
        return self._globe_map

    @property
    def tln_map(self) -> dict[int, str]:
        if self._tln_map is None:
            number_map: dict[int, str] = {}
            for record in self.records:
                if record.tln in number_map:
                    raise DuplicateKeyError(
                        f"{self.doc.path}: duplicate TLN {record.tln} "
                        f"(Globe refs {number_map[record.tln]!r} and {record.globe!r})"
                    )
                number_map[record.tln] = record.globe
            self._tln_map = number_map
        return self._tln_map

    def _lines_with_ftln(self):
        return self.doc.root.xpath("//*[starts-with(@xml:id, 'ftln') and @n]", namespaces=NS)

    @property
    def title(self) -> str | None:
        titles = self.doc.root.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[1]/text()",
            namespaces=NS,
        )
        return titles[0] if titles else None

    @property
    def dracor_id(self) -> str | None:
        return self.doc.root.get(XML_ID)

    @property
    def folger_idno(self) -> str | None:
        idnos = self.doc.root.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno[not(@type)][1]/text()",
            namespaces=NS,
        )
        return idnos[0] if idnos else None

    @property
    def playid(self) -> str | None:
        idno = self.folger_idno
        return idno.lower() if idno else None

    def tln(self, globe_ref: str) -> int | None:
        return self.globe_map.get(globe_ref)


def etree_localname(element) -> str:
    tag = element.tag
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


def build_corpus_map(tei_dir: Path | str, *, on_error=None) -> dict:
    """Build the combined play map for every *.xml file in tei_dir.

    By default, any per-file error (bad XML, missing idno, duplicate
    globe/TLN keys within a file, or a playid collision across files)
    aborts the whole build. Pass on_error=callback(source, exc) to instead
    skip the offending file and continue with the rest.
    """
    tei_dir = Path(tei_dir)
    plays: dict[str, dict] = {}
    for source in sorted(tei_dir.glob("*.xml")):
        try:
            mapper = PlayMapper(source)
            playid = mapper.playid
            if playid is None:
                raise ValueError(f"{source}: no Folger idno found; cannot derive playid")
            if playid in plays:
                raise DuplicateKeyError(
                    f"{source}: playid {playid!r} already used by "
                    f"{plays[playid]['source_file']!r}"
                )
            plays[playid] = {
                "title": mapper.title,
                "dracor_id": mapper.dracor_id,
                "folger_idno": mapper.folger_idno,
                "source_file": source.name,
                "lines": [asdict(r) for r in mapper.records],
            }
        except Exception as exc:
            if on_error is None:
                raise
            on_error(source, exc)
    return {"plays": plays}


def serialize(data: dict, path: Path | str) -> None:
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


class CorpusMap:
    def __init__(self, data: dict) -> None:
        self._data = data
        self._globe_index: dict[str, dict[str, dict]] = {}
        self._tln_index: dict[str, dict[int, dict]] = {}
        for playid, play in data.get("plays", {}).items():
            globe_index: dict[str, dict] = {}
            tln_index: dict[int, dict] = {}
            for line in play["lines"]:
                globe_index[line["globe"]] = line
                tln_index[line["tln"]] = line
            self._globe_index[playid] = globe_index
            self._tln_index[playid] = tln_index

    @classmethod
    def load(cls, path: Path | str) -> "CorpusMap":
        with open(path) as f:
            return cls(json.load(f))

    def line_number_map(
        self, playid: str, *, globe: str | None = None, tln: int | None = None
    ) -> dict | None:
        if (globe is None) == (tln is None):
            raise ValueError("line_number_map: pass exactly one of globe= or tln=")
        if globe is not None:
            return self._globe_index.get(playid, {}).get(globe)
        return self._tln_index.get(playid, {}).get(int(tln))
