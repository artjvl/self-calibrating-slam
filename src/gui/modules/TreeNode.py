from __future__ import annotations

import typing as tp
from abc import abstractmethod

from PyQt5 import QtCore
from src.framework.graph.Graph import SubGraph, SubElement
from src.framework.graph.GraphAnalyser import GraphAnalyser
from src.framework.graph.GraphContainer import SubGraphContainer, GraphContainer
from src.gui.viewer.items import Items
from src.gui.viewer.items.GraphicsItem import SubGraphicsItem

Type = tp.Type[SubGraphicsItem]
SubToggle = tp.TypeVar('SubToggle', bound='Toggle')
SubTreeNode = tp.TypeVar('SubTreeNode', bound='TreeNode')
SubGraphicsTreeNode = tp.TypeVar('SubGraphicsTreeNode', bound='GraphicsTreeNode')


class Toggle(object):
    """
    Parent-class for a toggleable object.
    """

    _relay: tp.Optional[SubToggle]
    _checked: bool

    _signal_checked: int = -1

    def __init__(
            self,
            relay: tp.Optional[SubToggle] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._relay = relay
        self._checked = True

    def toggle(
            self,
            should_broadcast: bool = True
    ) -> None:
        self.set_checked(not self._checked, should_broadcast=should_broadcast)

    def set_checked(
            self,
            checked: bool = True,
            should_broadcast: bool = True
    ) -> None:
        self._checked = checked
        if should_broadcast:
            self.broadcast(self._signal_checked)

    def is_checked(self) -> bool:
        return self._checked

    def has_relay(self) -> bool:
        return self._relay is not None

    def broadcast(self, signal: int) -> None:
        assert self.has_relay()
        self._relay.broadcast(signal)


class TreeNode(object):
    """
    An abstract class for a tree-element that (at least) stores toggles for graphics-item-types.
    """
    _children: tp.Dict[str, SubTreeNode]  # children nodes
    _parent: SubTreeNode  # parent node

    def __init__(
            self,
            parent: tp.Optional[SubTreeNode] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._children = {}
        self._parent = parent

    # parent
    def has_parent(self) -> bool:
        return self._parent is not None

    def get_parent(self) -> SubTreeNode:
        assert self.has_parent()
        return self._parent

    # current
    @abstractmethod
    def get_key(self) -> str:
        pass

    def get_gui_name(self) -> str:
        return f'{self.__class__.__name__}({self.get_key()})'

    def remove(self) -> None:
        assert self.has_parent()
        self._parent.remove_key(self.get_key())

    # child
    def add_child(
            self,
            node: SubTreeNode
    ) -> None:
        self._children[node.get_key()] = node

    def has_key(self, key: str) -> bool:
        return key in self._children

    def has_children(self) -> bool:
        return bool(self._children)

    def get_child(self, key: str) -> SubTreeNode:
        assert self.has_key(key)
        return self._children[key]

    def get_children(self) -> tp.List[SubTreeNode]:
        """ Returns the list of all child tree-elements. """
        return list(self._children.values())

    def remove_key(
            self,
            key: str
    ) -> None:
        assert self.has_key(key)
        del self._children[key]


class GraphicsTreeNode(TreeNode, Toggle):

    _toggles: tp.Dict[Type, SubToggle]  # current-level graphics-type toggles

    _signal_remove: int = 0
    _signal_change: int = 1

    def __init__(
            self,
            parent: tp.Optional[SubTreeNode] = None
    ):
        super().__init__(parent=parent, relay=parent)
        self._toggles = {}

    # graphics
    def get_types(self) -> tp.List[Type]:
        """ Returns the list of all graphic-item-types that comprise this tree-element. """
        return list(self._toggles.keys())

    def contains_graphic(self, type_: Type):
        """ Returns whether this tree-element is comprised of this graphic-item-type. """
        return type_ in self._toggles

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        """ Returns the list of all graphics-items that comprise this tree-element of a given graphics-item-type. """

        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: SubGraphicsTreeNode
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics

    def show_all(
            self,
            checked: bool = True
    ) -> None:
        """ Recursively sets the toggle of all child tree-elements. """

        self.set_checked(checked, should_broadcast=False)
        for toggle in self.get_toggles():
            toggle.set_checked(checked, should_broadcast=False)
        for child in self.get_children():
            child.show_all(checked)

    # toggles
    def add_toggle(self, type_: Type):
        """ Creates a new toggle for the given graphics-item type. """
        self._toggles[type_] = Toggle(self)

    def get_toggle(self, type_: Type):
        """ Returns the toggle corresponding to a given graphics-item-type. """
        return self._toggles[type_]

    def get_toggles(self) -> tp.List[SubToggle]:
        """ Returns the list of all available toggles. """
        return list(self._toggles.values())

    # signals
    @classmethod
    def get_signal_checked(cls) -> int:
        return cls._signal_checked

    @classmethod
    def get_signal_remove(cls) -> int:
        return cls._signal_remove

    @classmethod
    def get_signal_change(cls) -> int:
        return cls._signal_change

    # TreeItem
    def remove(
            self,
            should_broadcast: bool = True
    ) -> None:
        super().remove()
        if should_broadcast:
            self.broadcast(self._signal_remove)

    def get_key(self) -> str:
        return ''


class ElementTreeNode(GraphicsTreeNode):
    """
    A tree-element that represents a graph-element-type that comprises graphics-items of the given types.
    """

    _elements: tp.List[SubElement]  # list of graph-elements stored in this node
    _graphics: tp.Dict[Type, SubGraphicsItem]  # graphics-item for each supported graphics-type

    def __init__(
            self,
            parent: GraphTreeNode,  # parent-node
            types: tp.List[Type],  # supported graphics-types
            elements: tp.List[SubElement]  # graph-elements
    ):
        super().__init__(parent)
        self._elements = elements
        self._graphics = {}

        # for all of the given graphics-item-types
        element_type = self.get_element_type()
        type_: tp.Type[SubGraphicsItem]
        for type_ in types:

            # if a graphics-item-type is defined for the element-type
            if type_.check(element_type):
                # create the graphics-item
                graphic: SubGraphicsItem = type_.from_elements(elements)

                self.add_toggle(type_)
                self._graphics[type_] = graphic

    def get_element_type(self) -> tp.Type[SubElement]:
        """ Returns graph-element-type of stored elements. """
        return type(self._elements[0])

    def get_elements(self) -> tp.List[SubElement]:
        """ Returns list of stored graph-elements. """
        return self._elements

    # TreeNode
    def get_key(self) -> str:
        return self._elements[0].get_name()

    def get_gui_name(self) -> str:
        return str(self.get_element_type().__name__)

    # GraphicsTreeNode
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self.get_toggle(type_).is_checked():
            graphics.append(self._graphics[type_])
        return graphics


class GraphTreeNode(GraphicsTreeNode):
    """
    A tree-element that represents a graph that comprises graphics-items of the given types.
    """

    _id: int  # node id
    _types: tp.List[Type]  # supported
    _graph_container: SubGraphContainer  # graph-container
    _timestamp: tp.Optional[float]  # current time-stamp

    def __init__(
            self,
            parent: TrajectoryTreeNode,  # parent-node
            types: tp.List[Type],  # supported types
            id_: int,  # node id
            graph_container: SubGraphContainer  # graph-container
    ):
        super().__init__(parent)
        self._id = id_
        self._types = types
        self._graph_container = graph_container
        self._timestamp = None
        if not graph_container.is_singular():
            self._timestamp = graph_container.get_timestamps()[-1]
        self.init_graph(self._graph_container.get_graph())

    def init_graph(self, graph: SubGraph):
        # for all of the given graphics-item-types
        type_: Type
        for type_ in self._types:

            # for all of the element-types in the graph
            name: str
            for name in graph.get_names():

                # if a graphics-item-type is defined for the element-type
                if type_.check(graph.get_type_of_name(name)):

                    # create a subtree-element for each graph-element
                    elements: tp.List[SubElement] = graph.get_of_name(name)
                    node: ElementTreeNode = ElementTreeNode(self, self._types, elements)
                    self.add_child(node)

                    # if a toggle is not yet defined
                    if type_ not in self._toggles:
                        self.add_toggle(type_)

    def get_id(self) -> int:
        return self._id

    # timestamp
    def set_timestamp(self, timestamp: float):
        assert self._graph_container.has_timestamp(timestamp)
        self._timestamp = timestamp
        self.init_graph(self.get_graph())
        self.broadcast(self.get_id())

    def get_timestamp(self) -> float:
        return self._timestamp

    # graphs
    def get_graph(self, is_final: bool = False) -> SubGraph:
        """ Returns the graph that this tree-element represents. """
        timestamp: tp.Optional[float] = None
        if not is_final:
            timestamp = self._timestamp
        return self._graph_container.get_graph(timestamp)

    def get_graph_container(self) -> SubGraphContainer:
        return self._graph_container

    # truth
    def set_truth(self, graph_container: SubGraphContainer):
        timestamp: float = self._graph_container.get_timestamps()[-1]
        self._graph_container.get_graph(timestamp).assign_truth(graph_container.get_graph(timestamp))

    def set_as_truth(self) -> None:
        assert self.is_eligible_for_truth()
        self.get_parent().set_as_truth(self._graph_container)

    def is_eligible_for_truth(self) -> bool:
        return self.get_parent().is_eligible_for_truth(self._graph_container)

    # GraphContainer interface
    def get_timestamps(self) -> tp.List[float]:
        return self._graph_container.get_timestamps()

    def is_singular(self) -> bool:
        return self._graph_container.is_singular()

    def find_subgraphs(self) -> None:
        assert self.is_singular()
        self._graph_container.find_subgraphs()
        self.set_timestamp(self.get_timestamps()[-1])

    # TreeNode
    def get_key(self) -> str:
        return str(self.get_id())

    def get_gui_name(self) -> str:
        graph: SubGraph = self.get_graph()
        return f'Graph({self.get_id()})[{graph.to_id()}]'

    def remove(
            self,
            should_broadcast: bool = True
    ) -> None:
        print(f"gui/GraphContainer: '{self.get_gui_name()}' removed from '{self.get_parent().get_gui_name()}'.")
        super().remove(should_broadcast)


class TrajectoryTreeNode(GraphicsTreeNode, QtCore.QObject):
    """
    A tree-element that represents a trajectory (or path) that comprises graphics-items of the given types.
    """

    _id: int  # node id
    _origin: tp.Optional[str]  # description of trajectory origin (e.g. file or simulation)
    _truth: tp.Optional[SubGraphContainer]  # 'true' (ground-truth) graph-container

    def __init__(
            self,
            parent: TopTreeNode,  # parent node
            types: tp.List[Type],  # supported types
            id_: int,  # node id
            origin: tp.Optional[str] = None  # description of trajectory origin (e.g. file or simulation)
    ):
        super().__init__(parent)
        self._id = id_
        self._origin = origin

        for type_ in types:
            self.add_toggle(type_)
        self._id_counter: int = 1
        self._truth = None

    def get_id(self) -> int:
        return self._id

    # graph-management
    def count_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def _add_graph(
            self,
            graph_container: SubGraphContainer
    ) -> GraphTreeNode:
        node = GraphTreeNode(self, self.get_types(), self.count_id(increment=True), graph_container)
        self.add_child(node)
        print(
            f"gui/TrajectoryContainer: Graph '{graph_container.get_graph().to_unique()}' added to {self.get_gui_name()}"
        )
        return node

    def add_graph(
            self,
            graph: SubGraph,
            should_broadcast: bool = True
    ) -> None:
        graph_container: SubGraphContainer = GraphContainer(graph)
        if self.has_children():
            first_child: GraphTreeNode = self.get_children()[0]
            assert first_child.get_graph_container().is_superset_similar(graph_container)

        if graph.has_truth():
            truth_container: SubGraphContainer = GraphContainer(graph.get_truth())
            if self.has_truth():
                assert self._truth.is_superset_equal(truth_container)
            else:
                assert self.is_eligible_for_truth(truth_container)
                self._add_graph(truth_container)
                self.set_as_truth(truth_container, should_broadcast=False)

        node: GraphTreeNode = self._add_graph(graph_container)
        if self.has_truth() and not graph.has_truth():
            node.set_truth(self._truth)

        if should_broadcast:
            self.broadcast(self.get_signal_change())

    def set_as_truth(
            self,
            graph_container: SubGraphContainer,
            should_broadcast: bool = True
    ) -> None:
        assert self.is_eligible_for_truth(graph_container)
        self._truth = graph_container
        for child in self.get_children():
            if child.get_graph_container() != graph_container:
                child.set_truth(graph_container)
        if should_broadcast:
            self.broadcast(self.get_signal_change())

    def is_eligible_for_truth(self, graph_container: SubGraphContainer) -> bool:
        if self.has_truth():
            return False
        if graph_container.get_graph().is_perturbed():
            return False
        for child in self.get_children():
            if not graph_container.is_superset_similar(child.get_graph_container()):
                return False
        return True

    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubGraphContainer:
        assert self.has_truth()
        return self._truth

    def get_graphs(self) -> tp.List[SubGraph]:
        return [child.get_graph() for child in self.get_children()]

    # TreeNode
    def get_key(self) -> str:
        return str(self.get_id())

    def get_gui_name(self) -> str:
        name: str = f'Trajectory({self.get_id()})'
        if self._origin is not None:
            name = f'{name} - {self._origin}'
        return name

    def remove_key(self, key: str) -> None:
        super().remove_key(key)
        if not self.has_children():
            self.remove(should_broadcast=True)
        else:
            self.broadcast(self.get_signal_remove())

    def remove(
            self,
            should_broadcast: bool = True
    ) -> None:
        print(f"gui/TrajectoryContainer: '{self.get_gui_name()}' removed.")
        super().remove(should_broadcast)


class TopTreeNode(GraphicsTreeNode, QtCore.QObject):
    """
    A root tree-element that stores trajectory-elements that comprises graphics-items.
    """

    """
    Signal that updates GUI:
    - signal > 0: update menus (signal = graph_id)
    - signal = 1: clear menus
    - signal < 0: update Viewer only
    """

    _id_counter: int
    _analyser: GraphAnalyser

    signal_update = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._id_counter = 1
        self._analyser = GraphAnalyser()

        for item in Items:
            self.add_toggle(item.value)

    def get_key(self) -> str:
        return ''

    # graph-management
    def count_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def _add_trajectory(
            self,
            origin: tp.Optional[str] = None
    ) -> TrajectoryTreeNode:
        node = TrajectoryTreeNode(self, self.get_types(), self.count_id(increment=True), origin=origin)
        self.add_child(node)
        return node

    def add_graph(
            self,
            graph: SubGraph,
            origin: tp.Optional[str] = None
    ) -> None:
        trajectory: TrajectoryTreeNode = self._add_trajectory(origin=origin)
        trajectory.add_graph(graph)

    def clear(self) -> None:
        child: SubGraphicsTreeNode
        for child in self.get_children():
            child.remove(should_broadcast=False)
        self.signal_update.emit(self.get_signal_remove())

    def get_analyser(self) -> GraphAnalyser:
        return self._analyser

    def get_graphs(self) -> tp.List[SubGraph]:
        graphs: tp.List[SubGraph] = []
        child: TrajectoryTreeNode
        for child in self.get_children():
            graphs += child.get_graphs()
        return graphs

    def is_empty(self) -> bool:
        return len(self.get_children()) == 0

    # graphics
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: TrajectoryTreeNode
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics

    def get_graphics(self) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        for type_ in self.get_types():
            graphics += self.get_graphic(type_)
        return graphics

    # toggle
    def broadcast(self, signal: int) -> None:
        self.signal_update.emit(signal)

    def show_all(self, checked: bool = True) -> None:
        super().show_all(checked)
        self.broadcast(self.get_signal_checked())
