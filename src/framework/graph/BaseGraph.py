import copy
import typing as tp
from abc import abstractmethod

from src.framework.graph.protocols.Printable import Printable

SubBaseGraph = tp.TypeVar('SubBaseGraph', bound='BaseGraph', covariant=True)
SubBaseNode = tp.TypeVar('SubBaseNode', bound='BaseNode', covariant=True)
SubBaseEdge = tp.TypeVar('SubBaseEdge', bound='BaseEdge', covariant=True)
SubBaseElement = tp.TypeVar('SubBaseElement', bound='BaseElement', covariant=True)


class BaseElement(object):
    _name: str

    def __init__(
            self,
            name: tp.Optional[str] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        if name is None:
            name = self.__class__.__name__
        self._name = name

    # name
    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    # copy
    @abstractmethod
    def is_equivalent(self, element: SubBaseElement) -> bool:
        pass

    def copy_to(self, element: SubBaseElement) -> SubBaseElement:
        assert self.is_equivalent(element)
        element._name = self._name
        return element


class NodeContainer(object):
    _nodes: tp.Dict[int, SubBaseNode]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nodes = {}

    def add_node(self, node: SubBaseNode) -> None:
        id_: int = node.get_id()
        assert not self.contains_node_id(id_)
        self._nodes[id_] = node

    def clear(self) -> None:
        self._nodes = {}

    # nodes
    def get_nodes(self) -> tp.List[SubBaseNode]:
        """ Returns all nodes. """
        return list(self._nodes.values())

    def has_nodes(self) -> bool:
        return bool(self._nodes)

    def contains_node(self, node: SubBaseNode) -> bool:
        return node in self.get_nodes()

    def contains_node_id(self, id_: int) -> bool:
        return id_ in self._nodes

    def get_node(self, id_: int) -> SubBaseNode:
        assert self.contains_node_id(id_)
        return self._nodes[id_]

    def get_node_index(self, id_: int) -> int:
        assert self.contains_node_id(id_)
        return self.get_node_ids().index(id_)

    def get_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_nodes()]

    def remove_node(self, node: SubBaseNode) -> None:
        self.remove_node_id(node.get_id())

    def remove_node_id(self, id_: int) -> None:
        assert self.contains_node_id(id_)
        del self._nodes[id_]

    # active nodes
    def get_active_nodes(self) -> tp.List[SubBaseNode]:
        """ Returns only active nodes (i.e., nodes that are not fixed). """
        return list(filter(lambda node: not node.is_fixed(), self.get_nodes()))

    def get_active_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_active_nodes()]

    def get_active_node_index(self, id_: int) -> int:
        assert self.contains_node_id(id_)
        return self.get_active_node_ids().index(id_)

    # endpoints
    def get_endpoints(self) -> tp.List[SubBaseNode]:
        """ Returns only nodes of interest. """
        return self.get_nodes()

    def get_endpoint_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_endpoints()]


class BaseGraph(BaseElement, NodeContainer, Printable):
    # sorting
    _edges: tp.List[SubBaseEdge]  # list of edges
    _by_type: tp.Dict[tp.Type[SubBaseElement], tp.List[SubBaseElement]]  # elements grouped by type
    _by_name: tp.Dict[str, tp.List[SubBaseNode]]  # elements grouped by name

    # references
    _previous: tp.Optional[SubBaseGraph]  # reference to a previous graph state

    def __init__(
            self,
            name: tp.Optional[str] = None,
            **kwargs
    ):
        super().__init__(name=name, **kwargs)

        # sorting
        self._edges = []
        self._by_type = {}
        self._by_name = {}

        # references
        self._previous = None

    # NodeContainer
    def add_node(self, node: SubBaseNode) -> None:
        self.register_element(node)
        super().add_node(node)

    def get_nodes(self) -> tp.List[SubBaseNode]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    def clear(self) -> None:
        super().clear()
        self._edges = []
        self._by_type = {}
        self._by_name = {}

    # edges
    def add_edge(self, edge: SubBaseEdge) -> None:
        assert edge not in self.get_edges()
        for node in edge.get_nodes():
            assert self.contains_node(node)
        self.register_element(edge)
        self._edges.append(edge)

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

    # sorting
    def register_element(self, element: SubBaseElement) -> None:
        # by type
        element_type: tp.Type[SubBaseElement] = type(element)
        if element_type not in self._by_type:
            self._by_type[element_type] = []
        self._by_type[element_type].append(element)

        # by name
        element_name: str = element.get_name()
        if element_name not in self._by_name:
            self._by_name[element_name] = []
        else:
            # ensure all elements of a certain name are of the same type
            assert type(element) == self.get_type_of_name(element_name)
        self._by_name[element_name].append(element)

    def get_names(self) -> tp.List[str]:
        return sorted(self._by_name.keys())

    def get_of_name(self, name: str) -> tp.List[SubBaseElement]:
        assert name in self._by_name
        return self._by_name[name]

    def get_type_of_name(self, name: str) -> tp.Type[SubBaseElement]:
        assert name in self._by_name
        return type(self._by_name[name][0])

    def get_types(self) -> tp.List[tp.Type[SubBaseElement]]:
        return list(self._by_type.keys())

    def get_of_type(self, type_: tp.Type[SubBaseElement]) -> tp.List[SubBaseElement]:
        assert type_ in self._by_type
        return self._by_type[type_]

    # elements
    def get_elements(self) -> tp.List[SubBaseElement]:
        return self.get_nodes() + self.get_edges()

    # alternative constructor
    def from_nodes_edges(
            self,
            nodes: tp.List[SubBaseNode],
            edges: tp.List[SubBaseEdge]
    ) -> SubBaseGraph:
        graph = self.__class__()
        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)
        return graph

    # Printable
    def to_id(self) -> str:
        return f'{len(self._nodes)};{len(self._edges)}'

    # subgraphs
    def length(self) -> int:
        graph: SubBaseGraph = self
        length_: int = 1
        while graph.has_previous():
            graph = graph.get_previous()
            length_ += 1
        return length_

    def set_previous(self, previous: SubBaseGraph) -> None:
        # assert not self.has_previous()
        self._previous = previous

    def has_previous(self) -> bool:
        return self._previous is not None

    def get_previous(self) -> SubBaseGraph:
        assert self.has_previous()
        return self._previous

    def find_subgraphs(self) -> None:
        """
        Returns the evolution of the graph as a set of subgraphs.
        Assumption: a graph evolves when a new 'endpoint' node is added.
        """
        assert not self.has_previous()

        graph: SubBaseGraph = self.__class__()
        graphs: tp.List[SubBaseGraph] = []

        # initialise an empty node-set and edge-iterator
        node_set: tp.Set[SubBaseNode] = set()
        edge_iter: iter = iter(self.get_edges())
        edge: tp.Optional[SubBaseEdge] = next(edge_iter)

        is_completed: bool = False
        while not is_completed:
            # add nodes connected to current edge to node-set
            edges_to_add: tp.List[SubBaseEdge] = []
            node_set_next: tp.Set[SubBaseNode] = node_set.copy()
            node_set_next.update(edge.get_endpoints())

            # find all edges contained in the current node-set
            is_contained = True
            while is_contained:
                edges_to_add.append(edge)
                edge = next(edge_iter, None)
                if edge is None:
                    is_completed = True
                    is_contained = False
                else:
                    is_contained = (set(edge.get_endpoints()) <= node_set_next)

            # extend node-set
            node_set = node_set_next

            # copy graph
            if is_completed:
                graphs.append(self)
            else:
                for edge_to_add in edges_to_add:
                    for node in edge_to_add.get_nodes():
                        if not graph.contains_node_id(node.get_id()):
                            graph.add_node(node)
                    graph.add_edge(edge_to_add)
                graphs.append(copy.copy(graph))

        # store subgraphs
        for i in range(1, len(graphs)):
            graphs[i]._previous = graphs[i - 1]

    def get_subgraphs(self) -> tp.List[SubBaseGraph]:
        graph: SubBaseGraph = self
        graphs: tp.List[SubBaseGraph] = [graph]
        while graph.has_previous():
            graph = graph.get_previous()
            graphs.append(graph)
        return graphs[::-1]

    @staticmethod
    def from_subgraphs(subgraphs: tp.List[SubBaseGraph]) -> SubBaseGraph:
        # graph_iter: iter = iter(subgraphs)
        # graph: SubBaseGraph = next(graph_iter)
        #
        # next_graph: tp.Optional[SubBaseGraph]
        # is_finished: bool = False
        # while not is_finished:
        #     next_graph = next(graph_iter, None)
        #     if next_graph is not None:
        #         next_graph._previous = graph
        #         graph = next_graph
        #     else:
        #         is_finished = True
        # return graph

        for i in range(1, len(subgraphs)):
            subgraphs[i]._previous = subgraphs[i - 1]
        return subgraphs[-1]

    # compare
    def is_similar(self, graph: SubBaseGraph) -> bool:
        """
        Similarity: the graph contains identical connectivity between endpoints.
        Returns whether this graph is similar to <graph> by comparing the set of connected endpoints for all edges that
        are connected to endpoints.
        """
        graph_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_endpoint_ids()) for edge in graph.get_edges() if edge.get_endpoint_ids()]
        self_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_endpoint_ids()) for edge in self.get_edges() if edge.get_endpoint_ids()]
        return graph.get_endpoint_ids() == self.get_endpoint_ids() and graph_edges_ids == self_edges_ids

    def is_equivalent(self, graph: SubBaseGraph) -> bool:
        """
        Equivalence: the graph contains identical connectivity.
        Returns whether this graph is equivalent to <graph> by comparing the set of connected nodes for all edges.
        """
        graph_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_node_ids()) for edge in graph.get_edges()]
        self_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_node_ids()) for edge in self.get_edges()]
        return graph.get_node_ids() == self.get_node_ids() and graph_edges_ids == self_edges_ids

    def is_equal(self, graph: SubBaseGraph) -> bool:
        """
        Equality: the graph contains identical (i.e., same memory instances) set of nodes and edges.
        Returns whether this graph is equal to <graph> (i.e., the same as a copy) by comparing all element instances.
        """
        return graph.get_elements() == self.get_elements()

    # copy
    def copy_to(self, graph: SubBaseGraph) -> SubBaseGraph:
        graph = super().copy_to(graph)
        nodes: tp.List[SubBaseNode] = graph.get_nodes()
        edges: tp.List[SubBaseEdge] = graph.get_edges()
        graph.clear()

        for node in nodes:
            self.get_node(node.get_id()).copy_to(node)
            graph.add_node(node)
        for i, edge in enumerate(edges):
            self.get_edge(i).copy_to(edge)
            graph.add_edge(edge)

        graph._name = self._name
        graph._previous = self._previous
        return graph

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new._name = self._name
        new._nodes = copy.copy(self._nodes)
        new._edges = copy.copy(self._edges)
        new._by_type = {type_: copy.copy(elements) for (type_, elements) in self._by_type.items()}
        new._by_name = {name: copy.copy(elements) for (name, elements) in self._by_name.items()}
        new._previous = self._previous
        return new


class BaseNode(BaseElement, Printable):
    _id: tp.Optional[int]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            **kwargs
    ):
        super().__init__(name=name, **kwargs)
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

    # copy
    def is_equivalent(self, node: SubBaseNode) -> bool:
        return node._id == self._id

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}'


class BaseEdge(BaseElement, NodeContainer, Printable):

    def __init__(
            self,
            name: tp.Optional[str] = None,
            nodes: tp.Optional[tp.List[SubBaseNode]] = None,
            **kwargs
    ):
        super().__init__(name=name, **kwargs)
        if nodes is not None:
            for node in nodes:
                self.add_node(node)

    # copy
    def is_equivalent(self, edge: SubBaseEdge) -> bool:
        return edge.get_node_ids() == self.get_node_ids()

    # Printable
    def to_id(self) -> str:
        return '-'.join([f'{id_}' for id_ in self.get_node_ids()])
