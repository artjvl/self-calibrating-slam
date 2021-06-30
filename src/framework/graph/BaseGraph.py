import copy
import typing as tp

from src.framework.graph.protocols.Printable import Printable
from src.utils.TypeDict import TypeDict

SubBaseGraph = tp.TypeVar('SubBaseGraph', bound='BaseGraph', covariant=True)
SubBaseNode = tp.TypeVar('SubBaseNode', bound='BaseNode', covariant=True)
SubBaseEdge = tp.TypeVar('SubBaseEdge', bound='BaseEdge', covariant=True)
SubBaseElement = tp.Union[SubBaseNode, SubBaseEdge]


class NodeContainer(object):
    _nodes: tp.Dict[int, SubBaseNode]

    def __init__(self):
        super().__init__()
        self._nodes = {}

    def add_node(self, node: SubBaseNode) -> None:
        id_: int = node.get_id()
        assert id_ not in self._nodes
        self._nodes[id_] = node

    def has_nodes(self) -> bool:
        return bool(self._nodes)

    def contains_node(self, node: tp.Union[SubBaseNode, int]) -> bool:
        if isinstance(node, BaseNode):
            node = node.get_id()
        assert isinstance(node, int)
        return self.contains_node_id(node)

    def contains_node_id(self, id_: int) -> bool:
        if id_ in self._nodes:
            assert self._nodes[id_].get_id() == id_
            return True
        return False

    def get_node(self, id_: int) -> SubBaseNode:
        assert self.contains_node_id(id_)
        return self._nodes[id_]

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return list(self._nodes.values())

    def get_node_index(self, node: tp.Union[SubBaseNode, int]) -> int:
        if isinstance(node, BaseNode):
            node = node.get_id()
        assert isinstance(node, int)
        assert self.contains_node_id(node)
        return list(self._nodes.keys()).index(node)

    def get_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_nodes()]


class BaseGraph(NodeContainer, Printable):

    _edges: tp.List[SubBaseEdge]
    _sorted: TypeDict[SubBaseElement]

    def __init__(self):
        super().__init__()
        self._edges = []
        self._sorted = TypeDict[SubBaseElement]()

    # nodes
    def add_node(self, node: SubBaseNode) -> None:
        assert not self.contains_node(node), f'Node {node.to_unique()} already present in {self.to_unique()}.'
        self._nodes[node.get_id()] = node
        self._sorted.add(node)

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    # edges
    def add_edge(
            self,
            edge: SubBaseEdge,
            add_nodes: bool = False
    ) -> None:
        assert edge not in self.get_edges(), f'{edge.to_unique()} already present in {self.to_unique()}.'
        for node in edge.get_nodes():
            if add_nodes and not self.contains_node(node):
                self.add_node(node)
            assert self.contains_node(node), f'{node.to_unique()} is not present in {self.to_unique()}.'
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
                if not graph.contains_node_id(node.get_id()):
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


class BaseEdge(NodeContainer, Printable):

    def __init__(
            self,
            *nodes: SubBaseNode
    ):
        super().__init__()
        for node in nodes:
            self.add_node(node)

    # Printable
    def to_id(self) -> str:
        return '-'.join([f'{id_}' for id_ in self.get_node_ids()])
