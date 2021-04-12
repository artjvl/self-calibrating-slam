import typing as tp
from abc import abstractmethod

from src.framework.graph.FactorGraph import SubElement


class Database(tp.Protocol):

    # read
    @abstractmethod
    def from_tag(self, tag: str) -> SubElement:
        pass

    @abstractmethod
    def contains_tag(self, tag: str) -> bool:
        pass

    # write
    @abstractmethod
    def from_element(self, element: SubElement) -> str:
        pass

    @abstractmethod
    def contains_element(self, element: tp.Type[SubElement]) -> bool:
        pass
