import typing as tp

from src.framework.graph.Database import Database
from src.framework.graph.Graph import SubNode, Edge, Node
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import CalibratingEdge, SubCalibratingEdge
from src.framework.graph.types.scslam2d.nodes.InformationNode import SubInformationNode
from src.framework.graph.types.scslam2d.nodes.ParameterNode import SubParameterNode
from src.utils.TwoWayDict import TwoWayDict

Element = tp.Union[SubNode, SubCalibratingEdge]


class SuffixDatabase(Database):

    def __init__(self):
        self._elements = TwoWayDict()
        self._parameters = TwoWayDict()
        self._informations = TwoWayDict()

    # register
    def register_type(
            self,
            tag: str,
            type_: tp.Type[Element]
    ) -> None:
        self._elements[type_] = tag

    def register_parameter_suffix(
            self,
            suffix: str,
            type_: tp.Type[SubParameterNode]
    ) -> None:
        self._parameters[suffix] = type_

    def register_information_suffix(
            self,
            suffix: str,
            type_: tp.Type[SubInformationNode]
    ) -> None:
        self._informations[suffix] = type_

    # tag to element
    def from_tag(self, tag: str) -> Element:
        element: tp.Optional[Element] = None
        suffixes: tp.Optional[tp.List[str]] = None

        words: tp.List[str] = tag.split('_')
        for i in range(len(words)):
            subtag: str = '_'.join(words[: i + 1])
            if subtag in self._elements:
                element = self._elements[subtag]()
                suffixes = words[i + 1:]
                break
        assert element is not None, f"Tag '{tag}' not found in database."

        # if element is a node
        if isinstance(element, Node):
            assert not suffixes, f"'{suffixes}' are unprocessed."

        # if element is an edge
        elif isinstance(element, CalibratingEdge):
            count: int = 0
            for suffix in suffixes:
                assert suffix in self._parameters or suffix in self._informations, f"'{suffix}' is not found."
                count += 1
            element.set_num_additional(count)
        return element

    def contains_tag(self, tag: str) -> bool:
        return tag in self._elements

    def from_element(self, element: Element) -> str:
        assert type(element) in self._elements
        tag: str = self._elements[type(element)]

        # if element is a node
        if isinstance(element, Node):
            return tag

        # if element is an edge
        if isinstance(element, Edge):
            if isinstance(element, CalibratingEdge):
                suffixes: tp.List[str] = []
                parameter: SubParameterNode
                for parameter in element.get_parameters():
                    type_: tp.Type[SubParameterNode] = type(parameter)
                    assert type_ in self._parameters
                    suffixes.append(self._parameters[type_])
                if element.has_info_node():
                    information: SubInformationNode = element.get_info_node()
                    type_: tp.Type[SubInformationNode] = type(information)
                    assert type_ in self._informations
                    suffixes.append(self._informations[type_])
                return '_'.join([tag] + suffixes)
            return tag

    def contains_element(self, type_: tp.Type[Element]) -> bool:
        return type_ in self._elements
