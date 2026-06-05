# tei.py
#
from __future__ import annotations

from pathlib import Path
from lxml import etree

# Constants
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

NS = {"tei": TEI_NS, "xml": XML_NS}

XML_BASE = f"{{{XML_NS}}}base"
XML_ID   = f"{{{XML_NS}}}id"
XML_LANG = f"{{{XML_NS}}}lang"

class TEIDocument:
    def __init__(self, doc_path: Path | str) -> None:
        self._path = Path(doc_path)

        # Use strict parsing; insist that Perseus TEI be good
        parser = etree.XMLParser(ns_clean=True, remove_comments=False)
        self._tree: etree._ElementTree = etree.parse(source=self._path, parser=parser)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def tree(self) -> etree._ElementTree:
        return self._tree

    @property
    def root(self) -> etree._Element:
        return self.tree.getroot()
        




test_doc = Path("/Users/wulfmanc/repos/gh/PerseusDLCode/canonicalLit/canonical-greekLit/data/tlg0031/tlg001/tlg0031.tlg001.perseus-grc2.xml")
    

    
