import pathlib
import typing as tp
from abc import abstractmethod

from PyQt5 import QtCore, QtWidgets

from src.framework.graph.FactorGraph import SubElement
from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphParser import GraphParser
from src.gui.viewer.items import Items
from src.gui.viewer.items.GraphicsItem import SubGraphicsItem

Type = tp.Type[SubGraphicsItem]
SubToggle = tp.TypeVar('SubToggle', bound='Toggle')
SubContainer = tp.TypeVar('SubContainer', bound='Container')


class Toggle(object):
    def __init__(self):
        self._checked: bool = True

    def toggle(self) -> None:
        self._checked = not self._checked

    def set_checked(self, checked: bool = True) -> None:
        self._checked = checked

    def is_checked(self) -> bool:
        return self._checked


class GraphicsToggle(Toggle):
    def __init__(self, graphic: SubGraphicsItem):
        super().__init__()
        self._graphic = graphic

    def get_graphic(self) -> SubGraphicsItem:
        return self._graphic


class Container(object):
    _toggles: tp.Dict[Type, SubToggle]
    _children: tp.Dict[str, SubContainer]

    def __init__(self):
        super().__init__()
        self._toggles = {}
        self._children = {}

    def contains_graphic(self, type_: Type):
        return type_ in self._toggles

    @abstractmethod
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        pass

    def get_types(self) -> tp.List[Type]:
        return list(self._toggles.keys())

    def get_toggle(self, type_: Type):
        return self._toggles[type_]

    def get_toggles(self) -> tp.List[SubToggle]:
        return list(self._toggles.values())

    def get_children(self) -> tp.List[SubContainer]:
        return list(self._children.values())

    def show_all(self, checked: bool = True) -> None:
        toggle: SubToggle
        for toggle in self.get_toggles():
            toggle.set_checked(checked)
        for child in self.get_children():
            child.show_all(checked)


class ElementContainer(Container, Toggle):
    def __init__(
            self,
            types: tp.List[Type],
            elements: tp.List[SubElement]
    ):
        super().__init__()
        self._element_type: tp.Type[SubElement] = type(elements[0])

        type_: tp.Type[SubGraphicsItem]
        for type_ in types:
            if type_.check(self._element_type):
                graphic: SubGraphicsItem = type_.from_elements(elements)
                self._toggles[type_] = GraphicsToggle(graphic)

    def get_element_type(self) -> tp.Type[SubElement]:
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
    def __init__(
            self,
            types: tp.List[Type],
            graph: SubGraph
    ):
        super().__init__()
        self._graph = graph

        type_: tp.Type[SubGraphicsItem]
        for type_ in types:
            element_type: tp.Type[SubElement]
            for element_type in graph.get_types():
                if type_.check(element_type):
                    elements: tp.List[SubElement] = graph.get_of_type(element_type)
                    self._children[str(element_type.__name__)] = ElementContainer(types, elements)
                    if type_ not in self._toggles:
                        self._toggles[type_] = Toggle()

    def get_graph(self) -> SubGraph:
        return self._graph

    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.is_checked() and self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: ElementContainer
            for child in self.get_children():
                graphics += child.get_graphic(type_)
        return graphics

    def has_child(self, type_: tp.Type[SubElement]):
        return str(type_.__name__) in self._children

    def get_child(self, type_: tp.Type[SubElement]):
        assert self.has_child(type_)
        return self._children[str(type_.__name__)]

    def show_all(self, checked: bool = True) -> None:
        self.set_checked(checked)
        super().show_all(checked)


class ViewerContainer(Container, QtCore.QObject):
    signal_update = QtCore.pyqtSignal(int)

    def __init__(self, parser: GraphParser):
        super().__init__()
        self._parser = parser
        self._id_counter: int = 0

        for item in Items:
            self._toggles[item.value] = Toggle()

    # graph-management
    def get_id(self, increment: bool = False) -> int:
        id_: int = self._id_counter
        if increment:
            self._id_counter += 1
        return id_

    def add_graph(self, graph: SubGraph) -> None:
        id_: int = self.get_id()
        graph.set_id(id_)
        self._children[str(id_)] = GraphContainer(self.get_types(), graph)
        self.signal_update.emit(self.get_id(increment=True))

    def remove_graph(
            self,
            graph: SubGraph
    ) -> None:
        id_: int = graph.get_id()
        del self._children[str(id_)]
        self.signal_update.emit(id_)

    def load_graph(self) -> None:
        graph: SubGraph = self.load_from_file()
        if graph is not None:
            self.add_graph(graph)

    def replace_graph(
            self,
            old: SubGraph
    ) -> None:
        new: tp.Optional[SubGraph] = self.load_from_file()
        if new is not None:
            id_ = old.get_id()
            new.set_id(id_)
            self._children[str(id_)] = GraphContainer(self.get_types(), new)
            self.signal_update.emit(id_)

    def load_from_file(self) -> tp.Optional[SubGraph]:
        print("Loading file...")
        filename: tp.Optional[tp.Tuple[str, str]] = QtWidgets.QFileDialog.getOpenFileName(
            caption='Select file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename[0]:
            path = pathlib.Path(filename[0])
            graph: SubGraph = self._parser.load(path)
            return graph
        return None

    def get_graphs(self) -> tp.List[SubGraph]:
        return [child.get_graph() for child in self.get_children()]

    def is_empty(self) -> bool:
        return len(self.get_graphs()) == 0

    # graphics
    def get_graphic(self, type_: Type) -> tp.List[SubGraphicsItem]:
        graphics: tp.List[SubGraphicsItem] = []
        if self.contains_graphic(type_) and self._toggles[type_].is_checked():
            child: GraphContainer
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
