from functools import partial

from PyQt5.QtWidgets import QMenu, QAction

from src.gui.GraphContainer import GraphContainer
from src.gui.GraphContainer import GraphDictTreeData
from src.gui.menus.Menu import Menu
from src.gui.viewer.Viewer import Viewer


class ViewMenu(Menu):

    # constructor
    def __init__(self, container: GraphContainer, viewer: Viewer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&View')
        self._container = container
        self._viewer = viewer
        self._construct_menu()
        self._container.signal_update.connect(self._handle_signal)

    # helper-methods
    def _construct_menu(self):
        self.clear()
        self._construct_view_section()
        self.addSeparator()
        self._construct_item_section()
        self.addSeparator()
        for graph in self._container.get_graphs():
            self._construct_graph_menu(graph.get_id())

    def _construct_view_section(self):
        self.add_action(
            menu=self,
            name='&Top',
            handler=self._viewer.set_top_view
        )
        self.add_action(
            menu=self,
            name='&Isometric',
            handler=self._viewer.set_isometric_view
        )
        self.add_action(
            menu=self,
            name='&Home',
            handler=self._viewer.set_home_view
        )

    def _construct_item_section(self):
        graphics_value: GraphDictTreeData
        self.add_action(
            menu=self,
            name='Grid',
            handler=self._viewer.toggle_grid,
            checked=True
        )
        for graphics_value in self._container.get_graphics_values():
            action = self.add_action(
                menu=self,
                name=graphics_value.get_object().name,
                handler=partial(self._container.toggle, graphics_value),
                checked=graphics_value.is_checked()
            )
            action.instance_item = graphics_value

    def _construct_graph_menu(self, id):
        graph_value = self._container.get_graph_value(id)
        graph_menu = self.add_menu(
            menu=self,
            name=graph_value.get_object().get_name(short=True)
        )
        for element_value in self._container.get_element_values(graph_id=id):
            action = self.add_action(
                menu=graph_menu,
                name=element_value.get_object().__name__,
                handler=partial(self._container.toggle, element_value),
                checked=element_value.is_checked()
            )
            action.instance_item = element_value
        graph_menu.addSeparator()
        for graphics_value in self._container.get_graphics_values(graph_id=id):
            graphics_type = graphics_value.get_object()
            graphics_menu = self.add_menu(
                menu=graph_menu,
                name=graphics_type.name
            )
            for element_value in self._container.get_element_values(
                    graph_id=id,
                    graphics_type=graphics_type
            ):
                element_type = element_value.get_object()
                action = self.add_action(
                    menu=graphics_menu,
                    name=element_type.__name__,
                    handler=partial(self._container.toggle, element_value),
                    checked=element_value.is_checked()
                )
                action.instance_item = element_value

    @classmethod
    def _update_menu(cls, menu: QMenu):
        action: QAction
        for action in menu.actions():
            if action.menu():
                cls._update_menu(action.menu())
            elif not action.isSeparator():
                if hasattr(action, 'instance_item'):
                    value: GraphDictTreeData = action.instance_item
                    action.setChecked(value.is_checked())

    # handlers
    def _handle_signal(self, signal: int):
        if signal >= 0:
            self._construct_menu()
        else:
            self._update_menu(self)