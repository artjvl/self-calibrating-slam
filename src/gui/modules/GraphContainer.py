from __future__ import annotations

import pathlib
from typing import *

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog

from src.framework.graph.Graph import Graph
from src.gui.viewer.items import GraphicsItem, Items
from src.utils.DictTree import DictTree


class GraphDictTreeData(object):
    """
    Data structure that contains Viewer-items, corresponding actions/menus for toggling the visibility of said items
    and a boolean indicating the toggled state.
    """

    # constructor
    def __init__(
            self,
            checked: Optional[bool],
            obj: Optional[Any],
            graphics: Optional[GraphicsItem]
    ):
        self._checked: Optional[bool] = checked
        self._object: Optional[Any] = obj
        self._graphics: Optional[GraphicsItem] = graphics

    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, checked: bool):
        self._checked = checked

    def toggle(self):
        self._checked = not self._checked

    def get_object(self) -> Any:
        return self._object

    def get_graphics(self) -> GraphicsItem:
        return self._graphics

    def __str__(self):
        return '{{checked: {}, object: {}, graphics: {}}}'.format(self._checked, self._object, self._graphics)


GraphDictTree = DictTree[str, GraphDictTreeData]


class GraphContainer(QObject):
    """
    Data structure that manages the loaded graphs and corresponding Viewer-items.
    """

    # tree forks
    GRAPHICS = 'graphics'
    GRAPHS = 'graphs'
    ELEMENTS = 'elements'

    # PyQt signals
    signal_update = pyqtSignal(int)

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id_counter: int = 0

        """ Container -> (Type[Graphics]) / (Graph -> (Type[Element]) / (Type[GraphicsItem] -> Type[Element])) """
        self._tree: GraphDictTree = DictTree()
        # fork: GRAPHICS / GRAPHS
        self._tree.add_child(self.GRAPHICS, self._construct_graphics_tree())
        self._tree.add_child(self.GRAPHS, DictTree())

    # graph management
    def add_graph(self, graph: Graph):
        assert graph is not None
        graph_id = self._id_counter
        self._id_counter += 1
        graph.set_id(graph_id)
        self._get_graph_tree().add_child(str(graph_id), self._construct_graph_tree(graph))
        self.signal_update.emit(graph_id)

    def remove_graph(
            self,
            graph: Graph
    ):
        graph_id = graph.get_id()
        self._get_graph_tree().remove_child(str(graph_id))
        self.signal_update.emit(graph_id)

    # graph management handlers
    def load_graph(self):
        graph: Graph = self.load_from_file()
        if graph is not None:
            self.add_graph(graph)

    def replace_graph(
            self,
            old: Graph
    ):
        new: Graph = self.load_from_file()
        if new is not None:
            graph_id = old.get_id()
            new.set_id(graph_id)
            self._get_graph_tree().set_child(str(graph_id), self._construct_graph_tree(new))
            self.signal_update.emit(graph_id)

    @staticmethod
    def load_from_file():
        print("Loading file...")
        filename = QFileDialog.getOpenFileName(caption='Select file', directory='', filter='g2o (*.g2o)')
        if filename[0]:
            graph = Graph()
            graph.load(pathlib.Path(filename[0]), save_file=True)
            return graph
        return None

    # getter: graphics
    def get_graphics(self) -> List[GraphicsItem]:
        items: List[GraphicsItem] = []

        # get: Container -> GRAPHICS
        super_graphics_tree = self._get_graphics_tree()

        # iterate over: Container -> GRAPH -> Graph
        graph_tree: GraphDictTree
        for graph_tree in self._get_graph_tree().get_children():
            graph_value = graph_tree.get_value()
            if graph_value.is_checked():
                graph = graph_value.get_object()

                # get: Container -> GRAPH -> Graph -> ELEMENTS
                super_element_tree = self._get_element_tree(graph.get_id())

                # iterate over: Container -> GRAPH -> Graph -> GRAPHICS -> Type[GraphicsItem]
                for graphics_tree in self._get_graphics_tree(graph.get_id()).get_children():
                    graphics_value = graphics_tree.get_value()
                    graphics_type = graphics_value.get_object()
                    super_graphics_value = super_graphics_tree[repr(graphics_type)].get_value()
                    if super_graphics_value.is_checked() and graphics_value.is_checked():

                        # iterate over: Container -> GRAPH -> Graph -> GRAPHICS -> Type[GraphicsItem] -> Type[Element]
                        for element_tree in self._get_element_tree(graph.get_id(), graphics_type).get_children():
                            element_value = element_tree.get_value()
                            element_type = element_value.get_object()
                            super_element_value = super_element_tree[repr(element_type)].get_value()
                            if super_element_value.is_checked() and element_value.is_checked():
                                items.append(element_value.get_graphics())
        return items

    def get_graphs(self) -> List[Graph]:
        return [graph_value.get_object() for graph_value in self.get_graphs_values()]

    def get_graph(self, graph_id: int) -> Graph:
        return self.get_graph_value(graph_id).get_object()

    # getters: values
    def get_graphs_values(self) -> List[GraphDictTreeData]:
        return [graph_tree.get_value() for graph_tree in self._get_graph_tree().get_children()]

    def get_element_values(
            self,
            graph_id: int,
            graphics_type: Optional[Type[GraphicsItem]] = None
    ) -> List[GraphDictTreeData]:
        tree = self._get_element_tree(graph_id, graphics_type)
        return tree.values()

    def get_graphics_values(
            self,
            graph_id: Optional[int] = None
    ) -> List[GraphDictTreeData]:
        tree = self._get_graphics_tree(graph_id)
        return tree.values()

    # getters: value
    def get_graph_value(
            self,
            graph_id: int
    ) -> GraphDictTreeData:
        graph_tree = self._get_graph_tree()
        assert str(graph_id) in graph_tree
        return graph_tree[str(graph_id)].get_value()

    def get_element_value(
            self,
            element_type: Type[Any],
            graph_id: int,
            graphics_type: Optional[Type[GraphicsItem]] = None
    ) -> GraphDictTreeData:
        element_tree = self._get_element_tree(graph_id, graphics_type)
        return element_tree[repr(element_type)].get_value()

    def get_graphics_value(
            self,
            graphics_type: Type[GraphicsItem],
            graph_id: Optional[int] = None
    ) -> GraphDictTreeData:
        graphics_tree = self._get_graphics_tree(graph_id)
        return graphics_tree[repr(graphics_type)].get_value()

    # handler: toggle
    def toggle(self, value: GraphDictTreeData):
        value.toggle()
        self.signal_update.emit(-1)

    def show_all(self, visible: bool = True):
        # iterate over: Container -> GRAPHICS = graphics
        for graphics_value in self._get_graphics_tree().values():
            graphics_value.set_checked(visible)
        # iterate over: Container -> GRAPHS = graphs
        for graph_value in self._get_graph_tree().values():
            graph_value.set_checked(visible)
            graph = graph_value.get_object()
            # iterate over: Container -> GRAPHS -> ELEMENTS = elements
            for element_value in self._get_element_tree(graph.get_id()).values():
                element_value.set_checked(visible)
            # iterate over: Container -> GRAPHS -> GRAPHICS = graphics
            for graphics_value in self._get_graphics_tree(graph.get_id()).values():
                graphics_value.set_checked(visible)
                graphics_type = graphics_value.get_object()
                # iterate over: Container -> GRAPHS -> GRAPHICS -> Type[Graphics] = elements
                for element_value in self._get_element_tree(graph.get_id(), graphics_type).values():
                    element_value.set_checked(visible)
        self.signal_update.emit(-1)

    # getter helper-methods: tree
    def _get_graph_tree(self) -> GraphDictTree:
        return self._tree[self.GRAPHS]

    def _get_graphics_tree(
            self,
            graph_id: Optional[int] = None
    ) -> GraphDictTree:
        tree = self._tree
        if graph_id is not None:
            return tree[self.GRAPHS][str(graph_id)][self.GRAPHICS]
        else:
            return tree[self.GRAPHICS]

    def _get_element_tree(
            self,
            graph_id: int,
            graphics_type: Optional[Type[GraphicsItem]] = None
    ) -> GraphDictTree:
        tree = self._tree[self.GRAPHS][str(graph_id)]
        if graphics_type is not None:
            return tree[self.GRAPHICS][repr(graphics_type)]
        else:
            return tree[self.ELEMENTS]

    def is_empty(self) -> bool:
        return len(self.get_graphs()) == 0

    # sub-tree helper-methods
    def _construct_graphics_tree(self) -> GraphDictTree:
        """ DictTree: Container -> Type[GraphicsItem] """

        graphics_tree: GraphDictTree = DictTree()

        # iterate over graphics-item types
        item_type: Type[GraphicsItem]
        for item_type in [item.value for item in Items]:
            data = GraphDictTreeData(
                checked=True,
                obj=item_type,
                graphics=None
            )
            graphics_tree.add_value(repr(item_type), data)
        return graphics_tree

    def _construct_graph_tree(self, graph: Graph) -> GraphDictTree:
        """ Container -> Graph -> (Type[Element]) / (Type[GraphicsItem] -> Type[Element]) """

        # graph-tree root
        graph_tree: GraphDictTree = DictTree()
        graph_value = GraphDictTreeData(
            checked=True,
            obj=graph,
            graphics=None
        )
        graph_tree.set_value(graph_value)

        # fork: ELEMENTS / GRAPHICS
        graph_tree.add_child(self.ELEMENTS, self._construct_graph_element_tree(graph))
        graph_tree.add_child(self.GRAPHICS, self._construct_graph_graphics_element_tree(graph))

        return graph_tree

    def _construct_graph_element_tree(self, graph: Graph) -> GraphDictTree:
        """ DictTree: Container -> Graph -> Type[Element] """

        # depth 0: tree
        tree: GraphDictTree = DictTree()

        # iterate over graph-element types
        element_type: Type[Any]
        for element_type in graph.get_element_types():
            element_value = GraphDictTreeData(
                checked=True,
                obj=element_type,
                graphics=None
            )
            # depth 1: element_tree
            tree.add_value(repr(element_type), element_value)
        return tree

    def _construct_graph_graphics_element_tree(self, graph: Graph) -> GraphDictTree:
        """ DictTree: Container -> Graph -> Type[GraphicsItem] -> Type[Element] """

        # depth 0: tree
        tree: GraphDictTree = DictTree()

        # iterate over graphics-item types
        graphics_type: Type[GraphicsItem]
        for graphics_type in [data.get_object() for data in self._tree[self.GRAPHICS].values()]:

            # depth 1: graphics_tree
            graphics_tree: GraphDictTree = DictTree()
            graphics_value = GraphDictTreeData(
                checked=True,
                obj=graphics_type,
                graphics=None
            )
            graphics_tree.set_value(graphics_value)

            # iterate over graph-element types
            for element_type in graph.get_element_types():
                if graphics_type.check(element_type):
                    elements = graph.get_elements_of_type(element_type)
                    graphics: GraphicsItem = graphics_type.from_elements(elements)
                    element_value = GraphDictTreeData(
                        checked=True,
                        obj=element_type,
                        graphics=graphics
                    )
                    # depth 2: element_tree
                    graphics_tree.add_value(repr(element_type), element_value)

            # check if graphics-item type is available for graph-element type
            if graphics_tree.get_children():
                tree.add_child(repr(graphics_type), graphics_tree)
        return tree
