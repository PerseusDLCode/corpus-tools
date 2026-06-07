from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from tei import TEIDocument


_T = TypeVar("_T")


class Auditor(ABC, Generic[_T]):
    def __init__(self, doc: TEIDocument) -> None:
        self._doc = doc

    @abstractmethod
    def audit(self) -> _T:
        ...
