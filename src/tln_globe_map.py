from __future__ import annotations
from pathlib import Path
import json

from lxml import etree

from tei import XML_ID


class Mapper:
    def __init__(self, file_path: Path | str) -> None:
        self.tree = etree.parse(file_path)
        self._globe_map: dict[str,str] | None = None
        self._tln_map: dict[str,str] | None = None


    @property
    def globe_map(self) -> dict:
        if self._globe_map is None:
            number_map: dict[str,str] = dict()
            marked = self.lines_with_ftln()
            for line in marked:
                ftln = line.get(XML_ID)
                n = line.get('n')
                _,_,tln = ftln.partition('-')
                number_map[n] = tln

            self._globe_map = number_map
        return self._globe_map
        

    @property
    def tln_map(self) -> dict:
        if self._tln_map is None:
            number_map: dict[str,str] = dict()
            marked = self.lines_with_ftln()
            for line in marked:
                ftln = line.get(XML_ID)
                n = line.get('n')
                _,_,tln = ftln.partition('-')
                number_map[tln] = n

            self._tln_map = number_map
        return self._tln_map
        

    def lines_with_ftln(self):
        return self.tree.xpath("//*[starts-with(@xml:id, 'ftln') and @n]")

    def tln(self, globe_number) -> str:
       tln = self.globe_map.get(globe_number)
       return tln

    def serialize_globe_map(self, p):
       with open(p, 'w') as f:
           json.dump(self.globe_map, f, indent=4)
 
    def serialize_tln_map(self, p):
       with open(p, 'w') as f:
           json.dump(self.tln_map, f, indent=4)
