import typing as tp

from src.framework.graph.Graph import SubNodeEdge, Node, Edge, SubParameterNode
from src.utils.TwoWayDict import TwoWayDict


class Database(object):

    def __init__(self):
        self._elements = TwoWayDict()
        self._parameters = TwoWayDict()

    # register
    def register_type(
            self,
            tag: str,
            type_: tp.Type[SubNodeEdge]
    ) -> None:
        self._elements[type_] = tag

    def register_parameter_suffix(
            self,
            suffix: str,
            type_: tp.Type[SubParameterNode]
    ) -> None:
        self._parameters[suffix] = type_

    # tag to element
    def from_tag(self, tag: str) -> tp.Tuple[tp.Type[SubNodeEdge], int]:
        element_type: tp.Optional[tp.Type[SubNodeEdge]] = None
        suffixes: tp.Optional[tp.List[str]] = None

        words: tp.List[str] = tag.split('_')
        for i in range(len(words)):
            subtag: str = '_'.join(words[: i + 1])
            if subtag in self._elements:
                element_type = self._elements[subtag]
                suffixes = words[i + 1:]
                break
        assert element_type is not None, f"Tag '{tag}' not found in database."
        count: int = 0

        # if element is a node
        if issubclass(element_type, Node):
            assert not suffixes, f"'{suffixes}' are unprocessed."

        # if element is an edge
        elif issubclass(element_type, Edge):
            count = element_type.cardinality()
            for suffix in suffixes:
                assert suffix in self._parameters, f"'{suffix}' is not found."
                count += 1
        return element_type, count

    def contains_tag(self, tag: str) -> bool:
        return tag in self._elements

    def contains_element(self, type_: tp.Type[SubNodeEdge]) -> bool:
        return type_ in self._elements


    def from_element(self, element: SubNodeEdge) -> str:
        element_type: tp.Type[SubNodeEdge] = type(element)
        assert element_type in self._elements
        tag: str = self._elements[element_type]

        # if element is a node
        if isinstance(element, Node):
            return tag

        # if element is an edge
        if isinstance(element, Edge):
            suffixes: tp.List[str] = []
            parameter: SubParameterNode
            for parameter in element.get_parameter_nodes():
                type_: tp.Type[SubParameterNode] = type(parameter)
                assert type_ in self._parameters
                suffixes.append(self._parameters[type_])
            return '_'.join([tag] + suffixes)
