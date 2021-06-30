from __future__ import annotations

import typing as tp
from abc import abstractmethod

from PyQt5 import QtCore
from src.framework.graph.Graph import SubGraph, SubElement
from src.gui.viewer.items import Items
from src.gui.viewer.items.GraphicsItem import SubGraphicsItem

Type = tp.Type[SubGraphicsItem]
SubToggle = tp.TypeVar('SubToggle', bound='Toggle')
SubContainer = tp.TypeVar('SubContainer', bound='Container')


class Toggle(object):
    """
    Parent-class for a toggleable object.
    """

    def __init__(self):
        super().__init__()
        self._checked: bool = True

    def toggle(self) -> None:
        self._checked = not self._checked

    def set_checked(self, checked: bool = True) -> None:
        self._checked = checked

    def is_checked(self) -> bool:
        return self._checked


class Container(object):
    """
    An abstract class for a tree-element that (at least) stores toggles for graphics-item-types.
    """

    _toggles: tp.Dict[Type, SubToggle]
    _children: tp.Dict[str, SubContainer]

    def __init__(
            self,
            parent: tp.Optional[SubContainer] = None
    ):
        super().__init__()
        self._parent: tp.Optional[SubContainer] = parent
        self._toggles = {}
        self._children = {}

    def get_name(self) -> str:
        """ Returns the name of this tree-element for use in the GUI. """
        return ''

    def contains_graphic(self, type_: Type):
        """ Returns whether this tree-element is comprised of this graphic-item-type. """
        return type_ in self._toggles

    @abstractmethod
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        """ Returns the list of all graphics-items that comprise this tree-element of a given graphics-item-type. """
        pass

    def get_types(self) -> tp.List[Type]:
        """ Returns the list of all graphic-item-types that comrpise this tree-element. """
        return list(self._toggles.keys())

    def add_toggle(self, type_: Type):
        """ Creates a new toggle for the given graphics-item type. """
        self._toggles[type_] = Toggle()

    def get_toggle(self, type_: Type):
        """ Returns the toggle corresponding to a given graphics-item-type. """
        return self._toggles[type_]

    def get_toggles(self) -> tp.List[SubToggle]:
        """ Returns the list of all available toggles. """
        return list(self._toggles.values())

    def has_parent(self) -> bool:
        return self._parent is not None

    def get_parent(self) -> SubContainer:
        assert self.has_parent()
        return self._parent

    def has_child(self, key: str) -> bool:
        return key in self._children

    def get_child(self, key: str) -> SubContainer:
        assert self.has_child(key)
        return self._children[key]

    def get_children(self) -> tp.List[SubContainer]:
        """ Returns the list of all child tree-elements. """
        return list(self._children.values())

    def show_all(self, checked: bool = True) -> None:
        """ Recursively sets the toggle of all child tree-elements. """
        toggle: SubToggle
        for toggle in self.get_toggles():
            toggle.set_checked(checked)
        for child in self.get_children():
            child.show_all(checked)


class ElementContainer(Container, Toggle):
    """
    A tree-element that represents a graph-element-type that comprises graphics-items of the given types.
    """

    def __init__(
            self,
            parent: GraphContainer,
            types: tp.List[Type],
            elements: tp.List[SubElement]
    ):
        super().__init__(parent)
        self._elements = elements
        self._element_type: tp.Type[SubElement] = type(elements[0])
        self._graphics: tp.Dict[Type, SubGraphicsItem] = {}

        # for all of the given graphics-item-types
        type_: tp.Type[SubGraphicsItem]
        for type_ in types:

            # if a graphics-item-type is defined for the element-type
            if type_.check(self._element_type):

                # create the graphics-item
                graphic: SubGraphicsItem = type_.from_elements(elements)

                self.add_toggle(type_)
                self._graphics[type_] = graphic

    def get_name(self) -> str:
        return str(self.get_element_type().__name__)

    def get_elements(self) -> tp.List[SubElement]:
        return self._elements

    def get_element_type(self) -> tp.Type[SubElement]:
        """ Returns the graph-element-type that this tree-element represents. """
        return self._element_type

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self.get_toggle(type_).is_checked():
            graphics.append(self._graphics[type_])
        return graphics

    def show_all(self, checked: bool = True) -> None:
        self.set_checked(checked)
        super().show_all(checked)


class GraphContainer(Container, Toggle):
    """
    A tree-element that represents a graph that comprises graphics-items of the given types.
    """

    def __init__(
            self,
            parent: TrajectoryContainer,
            types: tp.List[Type],
            id_: int,
            graph: SubGraph
    ):
        super().__init__(parent)
        self._id: int = id_
        self._graph = graph

        # for all of the given graphics-item-types
        type_: Type
        for type_ in types:

            # for all of the element-types in the graph
            element_type: tp.Type[SubElement]
            for element_type in graph.get_types():

                # if a graphics-item-type is defined for the element-type
                if type_.check(element_type):

                    # create a subtree-element for each graph-element
                    elements: tp.List[SubElement] = graph.get_of_type(element_type)
                    self._children[str(element_type.__name__)] = ElementContainer(self, types, elements)

                    # if a toggle is not yet defined
                    if type_ not in self._toggles:
                        self.add_toggle(type_)

    def get_id(self) -> int:
        return self._id

    def get_name(self) -> str:
        return f'{type(self.get_graph()).__name__}({self.get_id()})'

    def get_graph(self) -> SubGraph:
        """ Returns the graph that this tree-element represents. """
        return self._graph

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: ElementContainer
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics

    def has_child_type(self, type_: tp.Type[SubElement]):
        """ Returns whether this tree-element is comprised of the given graph-element-type. """
        return str(type_.__name__) in self._children

    def get_child_type(self, type_: tp.Type[SubElement]):
        """ Returns the child tree-element that represents the given graph-element-type. """
        assert self.has_child_type(type_)
        return self._children[str(type_.__name__)]

    def show_all(self, checked: bool = True) -> None:
        self.set_checked(checked)
        super().show_all(checked)


class TrajectoryContainer(Container, Toggle, QtCore.QObject):
    """
    A tree-element that represents a trajectory (or path) that comprises graphics-items of the given types.
    """

    """
    Signal that updates GUI:
    - signal >= 0: update menus (signal = graph_id)
    - signal < 0: update Viewer only
    """
    signal_update = QtCore.pyqtSignal(int)

    def __init__(
            self,
            parent: TopContainer,
            types: tp.List[Type],
            id_: int
    ):
        super().__init__(parent)
        self._id: int = id_

        for type_ in types:
            self.add_toggle(type_)
        self._id_counter: int = 0
        self._true: tp.Optional[SubGraph] = None

    def remove(self) -> None:
        parent: TopContainer = self.get_parent()
        parent.remove_id(self.get_id())

    def get_name(self) -> str:
        name: str = f'Trajectory({self.get_id()})'
        children: tp.List[GraphContainer] = self.get_children()
        if children:
            name = f'{name}: {children[0].get_graph().to_name()}'
        return name

    def get_id(self) -> int:
        return self._id

    # graph-management
    def count_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def add_graph(
            self,
            graph: SubGraph,
            suppress: bool = False
    ) -> GraphContainer:
        if not self.is_empty():
            first: SubGraph = self.get_children()[0].get_graph()
            assert len(graph.get_types()) == len(first.get_types())
            assert len(graph.get_nodes()) == len(first.get_nodes())
            assert len(graph.get_edges()) == len(first.get_edges())
        if self.has_true():
            graph.assign_true(self.get_true())
        id_: int = self.count_id(increment=True)
        graph_container = GraphContainer(self, self.get_types(), id_, graph)
        self._children[str(id_)] = graph_container
        if not suppress:
            self.signal_update.emit(self.get_id())
        return graph_container

    def add_graphs(
            self,
            true: tp.Optional[SubGraph],
            *graphs: SubGraph,
            **kwargs: bool
    ) -> None:
        suppress: bool = False
        if kwargs:
            suppress = kwargs['suppress']

        graph_containers: tp.List[GraphContainer] = []
        if true is not None:
            graph_containers.append(self.add_true_graph(true, suppress=True))
        for graph in graphs:
            if true is not None:
                graph.assign_true(true)
            graph_containers.append(self.add_graph(graph, suppress=True))

        print(
            "gui/TrajectoryContainer: Graphs added to '{}':\n{}".format(
                f'{self.get_name()}',
                '\n'.join([f'    {child.get_name()} = {child.get_graph().to_unique()}' for child in graph_containers])
            )
        )
        if not suppress:
            self.signal_update.emit(self.get_id())

    def get_graphs(self) -> tp.List[SubGraph]:
        return [child.get_graph() for child in self.get_children()]

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubGraph:
        assert self.has_true()
        return self._true

    def set_as_true(
            self,
            graph: SubGraph,
            suppress: bool = False
    ):
        assert not self.has_true()
        self._true = graph
        for child in self.get_nontrue_children():
            child.get_graph().assign_true(graph)
        if not suppress:
            self.signal_update.emit(self.get_id())

    def get_nontrue_children(self) -> tp.List[GraphContainer]:
        if self.has_true():
            true: SubGraph = self.get_true()
            return [child for child in self.get_children() if child.get_graph() != true]
        return self.get_children()

    def add_true_graph(
            self,
            graph: SubGraph,
            suppress: bool = False
    ):
        assert not graph.is_perturbed()
        graph_container: GraphContainer = self.add_graph(graph, suppress=True)
        self.set_as_true(graph, suppress=True)
        if not suppress:
            self.signal_update.emit(self.get_id())
        return graph_container

    def remove_graph(self, graph_container: GraphContainer):
        id_: int = graph_container.get_id()
        self.remove_id(id_)

    def is_empty(self) -> bool:
        return len(self.get_children()) == 0

    def remove_id(self, id_: int):
        assert str(id_) in self._children
        graph_container: GraphContainer = self._children[str(id_)]
        print(
            "gui/TrajectoryContainer: '{}' removed from '{}'.".format(
                graph_container.get_name(),
                self.get_name()
            )
        )
        del self._children[str(id_)]
        self.signal_update.emit(self.get_id())
        if self.is_empty():
            self.get_parent().remove_id(self.get_id())

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: GraphContainer
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics


class TopContainer(Container, QtCore.QObject):
    """
    A root tree-element that stores trajectory-elements that comprises graphics-items.
    """

    """
    Signal that updates GUI:
    - signal >= 0: update menus (signal = graph_id)
    - signal < 0: update Viewer only
    """
    signal_update = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._id_counter: int = 0

        for item in Items:
            self.add_toggle(item.value)

    # graph-management
    def count_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def add_graphs(
            self,
            true: tp.Optional[SubGraph],
            *graphs: SubGraph
    ) -> TrajectoryContainer:
        id_: int = self.count_id(increment=True)
        trajectory = TrajectoryContainer(self, self.get_types(), id_)
        trajectory.signal_update.connect(self.handle_signal)
        self._children[str(id_)] = trajectory

        trajectory.add_graphs(true, *graphs, suppress=True)
        self.signal_update.emit(id_)
        return trajectory

    def remove_id(self, id_: int) -> None:
        assert str(id_) in self._children
        trajectory_container: TrajectoryContainer = self._children[str(id_)]
        print(
            "gui/TopContainer: '{}' removed.".format(
                trajectory_container.get_name()
            )
        )
        del self._children[str(id_)]
        self.signal_update.emit(id_)

    def clear(self) -> None:
        keys: tp.List[str] = list(self._children.keys())
        for id_ in keys:
            del self._children[id_]
        self.signal_update.emit(0)

    def get_graphs(self) -> tp.List[SubGraph]:
        graphs: tp.List[SubGraph] = []
        child: TrajectoryContainer
        for child in self.get_children():
            graphs += child.get_graphs()
        return graphs

    def is_empty(self) -> bool:
        return len(self.get_children()) == 0

    # graphics
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: TrajectoryContainer
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics

    def get_graphics(self) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        for type_ in self.get_types():
            graphics += self.get_graphic(type_)
        return graphics

    # toggle
    def toggle(self, toggle: SubToggle) -> None:
        toggle.toggle()
        self.signal_update.emit(-1)

    def show_all(self, checked: bool = True) -> None:
        super().show_all(checked)
        self.signal_update.emit(-1)

    # signal
    def handle_signal(self, signal: int) -> None:
        self.signal_update.emit(signal)
