import typing as tp
from abc import abstractmethod

from PyQt5 import QtCore
from src.framework.graph.FactorGraph import SubElement
from src.framework.graph.Graph import SubGraph
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


class GraphicsToggle(Toggle):
    """
    A toggleable object that stores a graphics-item.
    """

    def __init__(self, graphic: SubGraphicsItem):
        super().__init__()
        self._graphic = graphic

    def get_graphic(self) -> SubGraphicsItem:
        return self._graphic


class Container(object):
    """
    An abstract class for a tree-element that (at least) stores toggles for graphics-item-types.
    """

    _toggles: tp.Dict[Type, SubToggle]
    _children: tp.Dict[str, SubContainer]

    def __init__(self):
        super().__init__()
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

    def get_toggle(self, type_: Type):
        """ Returns the toggle corresponding to a given graphics-item-type. """
        return self._toggles[type_]

    def get_toggles(self) -> tp.List[SubToggle]:
        """ Returns the list of all available toggles. """
        return list(self._toggles.values())

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
            types: tp.List[Type],
            elements: tp.List[SubElement]
    ):
        super().__init__()
        self._elements = elements
        self._element_type: tp.Type[SubElement] = type(elements[0])

        # for all of the given graphics-item-types
        type_: tp.Type[SubGraphicsItem]
        for type_ in types:

            # if a graphics-item-type is defined for the element-type
            if type_.check(self._element_type):

                # create the graphics-item
                graphic: SubGraphicsItem = type_.from_elements(elements)

                self._toggles[type_] = GraphicsToggle(graphic)

    def get_name(self) -> str:
        return str(self.get_element_type().__name__)

    def get_elements(self) -> tp.List[SubElement]:
        return self._elements

    def get_element_type(self) -> tp.Type[SubElement]:
        """ Returns the graph-element-type that this tree-element represents. """
        return self._element_type

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self._toggles[type_].is_checked():
            graphics.append(self._toggles[type_].get_graphic())
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
            types: tp.List[Type],
            graph: SubGraph
    ):
        super().__init__()
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
                    self._children[str(element_type.__name__)] = ElementContainer(types, elements)

                    # if a toggle is not yet defined
                    if type_ not in self._toggles:
                        self._toggles[type_] = Toggle()

    def get_name(self) -> str:
        return self.get_graph().to_name()

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

    def has_child(self, type_: tp.Type[SubElement]):
        """ Returns whether this tree-element is comprised of the given graph-element-type. """
        return str(type_.__name__) in self._children

    def get_child(self, type_: tp.Type[SubElement]):
        """ Returns the child tree-element that represents the given graph-element-type. """
        assert self.has_child(type_)
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
            types: tp.List[Type],
            id_: int,
    ):
        super().__init__()
        self._id: int = id_
        for type_ in types:
            self._toggles[type_] = Toggle()
        self._id_counter: int = 0
        self._true: tp.Optional[SubGraph] = None

    def get_name(self) -> str:
        return str(self.get_id())

    def get_id(self) -> int:
        return self._id

    # graph-management
    def count_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def add_graph(self, graph: SubGraph) -> None:
        id_: int = self.count_id(increment=True)
        graph.set_id(id_)
        self._children[str(id_)] = GraphContainer(self.get_types(), graph)
        self.signal_update.emit(id_)

    def get_graphs(self) -> tp.List[SubGraph]:
        return [child.get_graph() for child in self.get_children()]

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubGraph:
        assert self.has_true()
        return self._true

    def set_as_true(self, graph: SubGraph):
        assert not self.has_true()
        self._true = graph
        for child in self.get_nontrue_children():
            child.get_graph().assign_true(graph)

    def get_nontrue_children(self) -> tp.List[GraphContainer]:
        if self.has_true():
            id_: int = self.get_true().get_id()
            return [child for child in self.get_children() if child.get_graph().get_id() != id_]
        return self.get_children()

    def add_true_graph(self, graph: SubGraph):
        assert not graph.is_perturbed()
        self.add_graph(graph)
        self.set_as_true(graph)

    def remove_graph(self, graph: SubGraph):
        assert graph is not self._true
        id_: int = graph.get_id()
        assert str(id_) in self._children
        del self._children[str(id_)]
        self.signal_update.emit(id_)

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.contains_graphic(type_) and self._toggles[type_].is_checked():
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
            self._toggles[item.value] = Toggle()

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
        trajectory = TrajectoryContainer(self.get_types(), id_)
        self._children[str(id_)] = trajectory

        if true is not None:
            trajectory.add_true_graph(true)
        for graph in graphs:
            trajectory.add_graph(graph)

        self.signal_update.emit(id_)
        return trajectory

    def remove_trajectory(self, id_: int) -> None:
        assert id_ in self._children
        del self._children[str(id_)]
        self.signal_update.emit(id_)

    def clear(self) -> None:
        for id_ in self._children.keys():
            del self._children[id_]
        self.signal_update.emit(0)

    def get_graphs(self) -> tp.List[SubGraph]:
        graphs: tp.List[SubGraph] = []
        child: TrajectoryContainer
        for child in self.get_children():
            graphs += child.get_graphs()
        return graphs

    def is_empty(self) -> bool:
        return len(self.get_graphs()) == 0

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
