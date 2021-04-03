import typing as tp

from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.Database import Database
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import CalibratingEdge
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.utils.TwoWayDict import TwoWayDict

Node = tp.TypeVar('Node', bound=CalibratingNode)
Edge = tp.TypeVar('Edge', bound=CalibratingEdge)
Element = tp.Union[Node, Edge]

class SuffixDatabase(Database):

    def __init__(self):
        self._element_types = TwoWayDict()
        self._datatypes = TwoWayDict()
        self._paramtypes = TwoWayDict()
        self._infotypes = TwoWayDict()

    # register
    def register_type(
            self,
            tag: str,
            type_: tp.Type[Element]
    ) -> None:
        self._element_types[tag] = type_

    def register_data_suffix(
            self,
            suffix: str,
            type_: tp.Type[Supported]
    ) -> None:
        self._datatypes[suffix] = type_

    def register_parameter_suffix(
            self,
            suffix: str,
            type_: tp.Type[Supported]
    ) -> None:
        self._paramtypes[suffix] = type_

    def register_information_suffix(
            self,
            suffix: str,
            type_: tp.Type[Supported]
    ) -> None:
        self._infotypes[suffix] = type_

    # tag to element
    def from_tag(self, tag: str) -> Element:
        key: str
        type_: tp.Optional[tp.Type[Element]] = None
        for key in self._element_types.keys():
            if tag.find(key) >= 0:
                type_ = self._element_types[key]
                tag = tag.replace(f'{key}_', '')
                break
        assert type_ is not None, f"'{tag}' has not been found in {self._element_types.keys()}."

        element: Element = type_()
        suffixes: tp.List[str] = tag.split('_')

        # if element is a node
        if isinstance(element, CalibratingNode):
            pass

        # if element is an edge
        elif isinstance(element, CalibratingEdge):
            suffix: str = suffixes[0]
            if not element.has_default_datatype():
                element.set_datatype(self._datatypes[suffix])
                suffixes = suffixes[1:]
            suffix = suffixes[0]
            if not element.has_default_paramtype():
                element.set_paramtype(self._paramtypes[suffix])
                suffixes = suffixes[1:]
            if not element.has_default_infotype():
                element.set_paramtype(self._infotypes[suffix])
                suffixes = suffixes[1:]

        # return instantiated element
        assert not suffixes, f"Unprocessed suffixes '{suffixes}' are not defined for elements of type {type_}."
        return element

    def contains_tag(self, tag: str) -> bool:
        return tag in self._element_types

    def from_element(self, element: Element) -> str:
        tag: str = self._element_types[type(element)]

        # if element is a node
        if isinstance(element, CalibratingNode):
            pass

        # if element is an edge
        elif isinstance(element, CalibratingEdge):
            suffixes: tp.List[str] = []
            if not element.has_default_datatype():
                suffixes.append(self._paramtypes[element.get_datatype()])
            if not element.has_default_paramtype():
                suffixes.append(self._paramtypes[element.get_paramtype()])
            if not element.has_default_infotype():
                suffixes.append(self._infotypes[element.get_infotype()])
            return f"{tag}_{'_'.join(suffixes)}"

    def contains_element(self, type_: tp.Type[Element]) -> bool:
        return type_ in self._element_types

