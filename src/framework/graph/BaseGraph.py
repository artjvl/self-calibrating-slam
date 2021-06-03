import copy
import typing as tp

from src.framework.graph.protocols.Printable import Printable
from src.utils.TypeDict import TypeDict

SubBaseGraph = tp.TypeVar('SubBaseGraph', bound='BaseGraph', covariant=True)
SubBaseNode = tp.TypeVar('SubBaseNode', bound='BaseNode', covariant=True)
SubBaseEdge = tp.TypeVar('SubBaseEdge', bound='BaseEdge', covariant=True)
SubBaseElement = tp.Union[SubBaseNode, SubBaseEdge]


class BaseGraph(Printable):

    def __init__(self):
        self._nodes: tp.Dict[int, SubBaseNode] = {}
        self._edges: tp.List[SubBaseEdge] = []
        self._sorted = TypeDict[SubBaseElement]()

    # nodes
    def add_node(self, node: SubBaseNode) -> None:
        assert not self.contains_id(node.get_id()), f'Node with {node.get_id()} already present in {self.to_unique()}.'
        self._nodes[node.get_id()] = node
        self._sorted.add(node)

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    def get_node(self, id_: int) -> SubBaseNode:
        assert self.contains_id(id_), f'{id_} not present in {self.to_unique()}.'
        return self._nodes[id_]

    def contains_id(self, id_: int) -> bool:
        return id_ in self._nodes

    # edges
    def add_edge(self, edge: SubBaseEdge) -> None:
        for node in edge.get_nodes():
            assert self.contains_id(node.get_id()), f'{node.to_name()} with id {node.get_id()} is not present in {self.to_unique()}.'
        assert edge not in self.get_edges(), f'{edge.to_unique()} already present in {self.to_unique()}.'
        self._edges.append(edge)
        self._sorted.add(edge)

    def get_edges(self) -> tp.List[SubBaseEdge]:
        return self._edges

    # types
    def get_types(self) -> tp.List[tp.Type[SubBaseElement]]:
        return self._sorted.get_types()

    def get_of_type(self, type_: tp.Type[SubBaseElement]) -> tp.List[SubBaseElement]:
        return self._sorted[type_]

    # Printable
    def to_id(self) -> str:
        return f'{len(self._nodes)};{len(self._edges)}'

    def get_subgraphs(self) -> tp.List[SubBaseGraph]:
        graph = type(self)()
        graphs: tp.List[SubBaseGraph] = []
        for edge in self._edges:
            for node in edge.get_nodes():
                if not graph.contains_id(node.get_id()):
                    graph.add_node(node)
            graph.add_edge(edge)
            graphs.append(copy.copy(graph))
        return graphs


class BaseNode(Printable):

    _id: int

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__()
        self._id = id_

    # id
    def set_id(self, id_: int) -> None:
        self._id = id_

    def get_id(self) -> int:
        return self._id

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}'


class BaseEdge(Printable):

    _nodes: tp.Dict[int, SubBaseNode]

    def __init__(
            self,
            *nodes: SubBaseNode
    ):
        super().__init__()
        self._nodes = {}
        for node in nodes:
            self.add_node(node)

    # nodes
    def add_node(self, node: SubBaseNode) -> None:
        id_: int = node.get_id()
        assert id_ not in self._nodes, f'{node.to_unique()} already present in {self.to_unique()}.'
        self._nodes[id_] = node

    # def set_node(self, index: int, node: Node):
    #     assert 0 <= index < len(self._nodes), f'Index {index} out of bounds.'
    #     assert node not in self._nodes[:index] + self._nodes[index + 1:], f'{node.to_unique()} doubly present.'
    #     self._nodes[index] = node

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    def get_node(self, id_: int) -> SubBaseNode:
        assert id_ in self._nodes
        return self._nodes[id_]

    def get_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_nodes()]

    # Printable
    def to_id(self) -> str:
        return '-'.join([f'{id_}' for id_ in self.get_node_ids()])
