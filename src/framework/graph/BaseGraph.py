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

        # default the element name to the class name
        if name is None:
            name = self.__class__.__name__
        self._name = name

    # name
    def get_name(self) -> str:
        """ Returns the element name. """
        return self._name

    def set_name(self, name: str):
        """ Sets the element name. """
        self._name = name

    # equivalence
    @abstractmethod
    def is_equivalent(self, element: SubBaseElement) -> bool:
        """ Returns whether the other element is equivalent. """
        pass

    # copy
    def copy_attributes_to(self, element: SubBaseElement) -> SubBaseElement:
        """ Copies relevant attributes to the other element. """
        assert self.is_equivalent(element)
        element._name = self._name
        return element


class NodeContainer(object):
    _nodes: tp.Dict[int, SubBaseNode]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nodes = {}

    # nodes
    def add_node(self, node: SubBaseNode) -> None:
        id_: int = node.get_id()
        assert not self.contains_node_id(id_)
        self._nodes[id_] = node

    def get_nodes(self) -> tp.List[SubBaseNode]:
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

    # active nodes (i.e., nodes that are not fixed)
    def get_active_nodes(self) -> tp.List[SubBaseNode]:
        return list(filter(lambda node: not node.is_fixed(), self.get_nodes()))

    def get_active_node_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_active_nodes()]

    def get_active_node_index(self, id_: int) -> int:
        assert self.contains_node_id(id_)
        return self.get_active_node_ids().index(id_)

    # endpoints (i.e., pose-nodes)
    def get_endpoints(self) -> tp.List[SubBaseNode]:
        """ Returns only nodes of interest. """
        return self.get_nodes()

    def get_endpoint_ids(self) -> tp.List[int]:
        return [node.get_id() for node in self.get_endpoints()]


class EdgeContainer(object):
    _edges: tp.List[SubBaseEdge]

    def __init__(
            self,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._edges = []

    def add_edge(self, edge: SubBaseEdge):
        self._edges.append(edge)

    def get_edges(self) -> tp.List[SubBaseEdge]:
        return self._edges

    def get_edge_from_ids(self, node_ids: tp.Tuple[int, ...]) -> SubBaseEdge:
        by_node_ids: tp.Dict[tp.Tuple[int, ...], SubBaseEdge] = {tuple(edge.get_node_ids()): edge for edge in self._edges}
        assert node_ids in by_node_ids
        return by_node_ids[node_ids]

    def get_edge_from_index(self, index: int) -> SubBaseEdge:
        return self._edges[index]


class BaseGraph(BaseElement, NodeContainer, EdgeContainer, Printable):
    # sorting
    _by_type: tp.Dict[tp.Type[SubBaseElement], tp.List[SubBaseElement]]  # elements grouped by type
    _by_name: tp.Dict[str, tp.List[SubBaseNode]]  # elements grouped by name

    # previous
    _previous: tp.Optional[SubBaseGraph]  # reference to a previous graph state

    def __init__(
            self,
            name: tp.Optional[str] = None,
            **kwargs
    ):
        super().__init__(name=name, **kwargs)

        # sorting
        self._by_type = {}
        self._by_name = {}

        # references
        self._previous = None

    # NodeContainer
    def add_node(self, node: SubBaseNode) -> None:
        self.register_element(node)
        super().add_node(node)

    def get_nodes(self) -> tp.List[SubBaseNode]:
        """ Returns nodes sorted by node id. """
        return [self._nodes[key] for key in sorted(self._nodes)]

    def clear(self) -> None:
        self._nodes = {}
        self._edges = []
        self._by_type = {}
        self._by_name = {}

    # edges
    def add_edge(self, edge: SubBaseEdge) -> None:
        for node in edge.get_nodes():
            assert self.contains_node(node)
        self.register_element(edge)
        super().add_edge(edge)

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

    def has_name(self, name: str) -> bool:
        return name in self._by_name

    def get_names(self) -> tp.List[str]:
        return sorted(self._by_name.keys())

    def get_node_names(self) -> tp.List[str]:
        return [name for name in self.get_names() if issubclass(self.get_type_of_name(name), BaseNode)]

    def get_edge_names(self) -> tp.List[str]:
        return [name for name in self.get_names() if issubclass(self.get_type_of_name(name), BaseEdge)]

    def get_of_name(self, name: str) -> tp.List[SubBaseElement]:
        assert self.has_name(name)
        return self._by_name[name]

    def get_type_of_name(self, name: str) -> tp.Type[SubBaseElement]:
        assert self.has_name(name)
        return type(self._by_name[name][0])

    def has_type(self, type_: tp.Type[SubBaseElement]) -> bool:
        return type_ in self._by_type

    def get_types(self) -> tp.List[tp.Type[SubBaseElement]]:
        return list(self._by_type.keys())

    def get_node_types(self) -> tp.List[tp.Type[SubBaseNode]]:
        return [type_ for type_ in self.get_types() if issubclass(type_, BaseNode)]

    def get_edge_types(self) -> tp.List[tp.Type[SubBaseEdge]]:
        return [type_ for type_ in self.get_types() if issubclass(type_, BaseEdge)]

    def get_of_type(self, type_: tp.Type[SubBaseElement]) -> tp.List[SubBaseElement]:
        assert self.has_type(type_)
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
    def previous_depth(self) -> int:
        graph: SubBaseGraph = self
        depth: int = 1
        while graph.has_previous():
            graph = graph.get_previous()
            depth += 1
        return depth

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

    def subgraphs(self) -> tp.List[SubBaseGraph]:
        graph: SubBaseGraph = self
        graphs: tp.List[SubBaseGraph] = [graph]
        while graph.has_previous():
            graph = graph.get_previous()
            graphs.append(graph)
        return graphs[::-1]

    @staticmethod
    def from_subgraphs(subgraphs: tp.List[SubBaseGraph]) -> SubBaseGraph:
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
        has_similar_edges: bool = graph_edges_ids == self_edges_ids
        has_equivalent_endpoints: bool = graph.get_endpoint_ids() == self.get_endpoint_ids()
        return has_similar_edges and has_equivalent_endpoints

    def is_equivalent(self, graph: SubBaseGraph) -> bool:
        """
        Equivalence: the graph contains identical connectivity.
        Returns whether this graph is equivalent to <graph> by comparing the set of connected nodes for all edges.
        """
        graph_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_node_ids()) for edge in graph.get_edges()]
        self_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(edge.get_node_ids()) for edge in self.get_edges()]
        has_equivalent_edges: bool = graph_edges_ids == self_edges_ids
        has_equivalent_nodes: bool = graph.get_node_ids() == self.get_node_ids()
        return has_equivalent_edges and has_equivalent_nodes

    def is_equal(self, graph: SubBaseGraph) -> bool:
        """
        Equality: the graph contains identical (i.e., same memory instances) set of nodes and edges.
        Returns whether this graph is equal to <graph> (i.e., the same as a copy) by comparing all element instances.
        """
        return graph.get_elements() == self.get_elements()

    # def copy(self, is_shallow: bool = False) -> SubBaseGraph:
    #     copy_: SubBaseGraph = copy.copy(self) if is_shallow else copy.deepcopy(self)
    #     self.copy_attributes_to(copy_)
    #     return copy_
    #
    # def __copy__(self):
    #     new = self.__class__()
    #     new._nodes = copy.copy(self._nodes)
    #     new._edges = copy.copy(self._edges)
    #     new._by_type = {type_: copy.copy(elements) for (type_, elements) in self._by_type.items()}
    #     new._by_name = {name: copy.copy(elements) for (name, elements) in self._by_name.items()}
    #     return new
    #
    # def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
    #     if memo is None:
    #         memo = {}
    #     new = self.__class__()
    #     memo[id(self)] = new
    #     new._nodes = copy.deepcopy(self._nodes, memo)
    #     new._edges = copy.deepcopy(self._edges, memo)
    #     new._by_type = {type_: copy.deepcopy(elements, memo) for (type_, elements) in self._by_type.items()}
    #     new._by_name = {name: copy.deepcopy(elements, memo) for (name, elements) in self._by_name.items()}
    #     return new


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

    # equivalence
    def is_equivalent(self, node: SubBaseNode) -> bool:
        return node._id == self._id

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}'

    # def copy(self, is_shallow: bool = False) -> SubBaseNode:
    #     copy_: SubBaseNode = copy.copy(self) if is_shallow else copy.deepcopy(self)
    #     self.copy_attributes_to(copy_)
    #     return copy_
    #
    # def __copy__(self):
    #     new = self.__class__()
    #     new._id = self._id
    #     return new
    #
    # def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
    #     if memo is None:
    #         memo = {}
    #     new = self.__copy__()
    #     memo[id(self)] = new
    #     new._id = self._id
    #     return new


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

    # equivalence
    def is_equivalent(self, edge: SubBaseEdge) -> bool:
        return edge.get_node_ids() == self.get_node_ids()

    # Printable
    def to_id(self) -> str:
        return '-'.join([f'{id_}' for id_ in self.get_node_ids()])

    # def copy(self, is_shallow: bool = False) -> SubBaseEdge:
    #     copy_: SubBaseEdge = copy.copy(self) if is_shallow else copy.deepcopy(self)
    #     self.copy_attributes_to(copy_)
    #     return copy_
    #
    # def __copy__(self):
    #     new = self.__class__()
    #     new._nodes = copy.copy(self._nodes)
    #     return new
    #
    # def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
    #     if memo is None:
    #         memo = {}
    #     new = self.__class__()
    #     memo[id(self)] = new
    #     new._nodes = copy.deepcopy(self._nodes, memo)
    #     return new