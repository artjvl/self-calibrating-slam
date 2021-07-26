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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nodes = {}

    def add_node(self, node: SubBaseNode) -> None:
        id_: int = node.get_id()
        assert not self.contains_node_id(id_)
        self._nodes[id_] = node

    def has_nodes(self) -> bool:
        return bool(self._nodes)

    def contains_node(self, node: SubBaseNode) -> bool:
        return node in self.get_nodes()

    def contains_node_id(self, id_: int) -> bool:
        return id_ in self._nodes

    def get_node(self, id_: int) -> SubBaseNode:
        assert self.contains_node_id(id_)
        return self._nodes[id_]

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return list(self._nodes.values())

    def get_node_index(self, id_: int) -> int:
        assert self.contains_node_id(id_)
        return self.get_node_ids().index(id_)

    def get_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_nodes()]

    def get_active_nodes(self) -> tp.List[SubBaseNode]:
        return list(filter(lambda node: not node.is_fixed(), self.get_nodes()))

    def get_active_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_active_nodes()]

    def get_active_node_index(self, id_: int) -> int:
        assert self.contains_node_id(id_)
        return self.get_active_node_ids().index(id_)

    # copy
    def __copy__(self):
        new = type(self)()
        new._nodes = copy.copy(self._nodes)
        return new


class BaseGraph(NodeContainer, Printable):

    _edges: tp.List[SubBaseEdge]
    _sorted: TypeDict[SubBaseElement]

    def __init__(self):
        super().__init__()
        self._edges = []
        self._sorted = TypeDict[SubBaseElement]()

    # NodeContainer
    def add_node(self, node: SubBaseNode) -> None:
        super().add_node(node)
        self._sorted.add(node)

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    # edges
    def add_edge(
            self,
            edge: SubBaseEdge
    ) -> None:
        assert edge not in self.get_edges()
        for node in edge.get_nodes():
            assert self.contains_node(node)
        self._edges.append(edge)
        self._sorted.add(edge)

    def get_edges(self) -> tp.List[SubBaseEdge]:
        return self._edges

    def get_edge(self, i: int) -> SubBaseEdge:
        return self._edges[i]

    def get_connected_edges(self, id_: int):
        edges: tp.List[SubBaseEdge] = []
        for edge in self.get_edges():
            if edge.contains_node_id(id_):
                edges.append(edge)
        return edges

    # types
    def get_types(self) -> tp.List[tp.Type[SubBaseElement]]:
        return self._sorted.get_types()

    def get_of_type(self, type_: tp.Type[SubBaseElement]) -> tp.List[SubBaseElement]:
        return self._sorted[type_]

    # Printable
    def to_id(self) -> str:
        return f'{len(self._nodes)};{len(self._edges)}'

    # subgraphs
    def get_subgraphs(self) -> tp.List[SubBaseGraph]:
        graph: SubBaseGraph = type(self)()
        graphs: tp.List[SubBaseGraph] = []

        edge: SubBaseEdge
        for edge in self._edges:
            node: SubBaseNode
            for node in edge.get_nodes():
                if not graph.contains_node_id(node.get_id()):
                    graph.add_node(node)
            graph.add_edge(edge)
            graphs.append(copy.copy(graph))
        return graphs

    # copy
    def __copy__(self):
        new = super().__copy__()
        new._edges = copy.copy(self._edges)
        new._sorted = copy.copy(self._sorted)
        return new


class BaseNode(Printable):

    _id: tp.Optional[int]

    def __init__(
            self,
            id_: tp.Optional[int] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._id = id_

    # id
    def has_id(self) -> bool:
        return self._id is not None

    def set_id(self, id_: int) -> None:
        assert not self.has_id()
        self._id = id_

    def get_id(self) -> int:
        assert self.has_id()
        return self._id

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}'


class BaseEdge(NodeContainer, Printable):

    def __init__(
            self,
            *nodes: SubBaseNode,
            **kwargs
    ):
        super().__init__(**kwargs)
        for node in nodes:
            self.add_node(node)

    # Printable
    def to_id(self) -> str:
        return '-'.join([f'{id_}' for id_ in self.get_node_ids()])
