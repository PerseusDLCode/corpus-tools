from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Generic, TypeVar

from lxml import etree

from tei import TEIDocument, NS, XML_BASE, XML_ID


_T = TypeVar("_T")


# ---------------------------------------------------------------------------
# Shared dataclasses
# ---------------------------------------------------------------------------

@dataclass
class CitationLevel:
    element: str
    subtype: str
    depth: int
    count: int
    with_n: int
    with_base: int
    with_id: int
    base_correct: int
    base_wrong_examples: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class MilestoneInfo:
    unit: str
    count: int


@dataclass
class RefsDecl:
    xml_id: str
    n: str
    default: bool
    has_cite_structure: bool
    cite_units: list[str]
    cref_pattern_names: list[str]



# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class Auditor(ABC, Generic[_T]):
    def __init__(self, doc: TEIDocument) -> None:
        self._doc = doc

    @abstractmethod
    def audit(self) -> _T:
        ...

