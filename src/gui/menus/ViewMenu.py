import functools

from PyQt5.QtWidgets import QMenu, QAction

from src.gui.menus.Menu import Menu
from src.gui.modules.Container import ViewerContainer, Type, GraphContainer, ElementContainer, SubToggle
from src.gui.viewer.Viewer import Viewer


class ViewMenu(Menu):

    # constructor
    def __init__(self, container: ViewerContainer, viewer: Viewer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&View')
        self._container: ViewerContainer = container
        self._viewer = viewer

        self._construct_menu()
        self._container.signal_update.connect(self._handle_signal)
        self._show_all: bool = True

    # helper-methods
    def _construct_menu(self):
        self.clear()
        self._construct_view_section()
        self.addSeparator()
        self.add_action(
            menu=self,
            name='Grid',
            handler=self._viewer.toggle_grid,
            checked=True
        )
        self._construct_container_section()
        self.addSeparator()
        self.add_action(
            menu=self,
            name='Show &All',
            handler=self._handle_show_all,
            checked=True
        )

    def _construct_container_section(self):
        container: ViewerContainer = self._container

        # top-menu
        type_: Type
        for type_ in container.get_types():
            toggle: SubToggle = container.get_toggle(type_)
            action = self.add_action(
                menu=self,
                name=type_.__name__,
                handler=functools.partial(container.toggle, toggle),
                checked=toggle.is_checked()
            )
            action.obj = toggle

        self.addSeparator()

        graph_container: GraphContainer
        for graph_container in container.get_children():

            # graph sub-menu
            graph_menu: QMenu = self.add_menu(
                menu=self,
                name=graph_container.get_graph().to_name()
            )
            for type_ in graph_container.get_types():
                toggle: SubToggle = graph_container.get_toggle(type_)
                action = self.add_action(
                    menu=graph_menu,
                    name=type_.__name__,
                    handler=functools.partial(container.toggle, toggle),
                    checked=toggle.is_checked()
                )
                action.obj = toggle

            graph_menu.addSeparator()

            element_container: ElementContainer
            for element_container in graph_container.get_children():

                # element sub-menu
                element_menu: QMenu = self.add_menu(
                    menu=graph_menu,
                    name=element_container.get_element_type().__name__
                )

                element_menu.addSeparator()

                for type_ in element_container.get_types():
                    toggle: SubToggle = element_container.get_toggle(type_)
                    action = self.add_action(
                        menu=element_menu,
                        name=type_.__name__,
                        handler=functools.partial(container.toggle, toggle),
                        checked=toggle.is_checked()
                    )
                    action.obj = toggle

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

    @classmethod
    def _update_menu(cls, menu: QMenu):
        action: QAction
        for action in menu.actions():
            if action.menu():
                cls._update_menu(action.menu())
            elif not action.isSeparator():
                if hasattr(action, 'obj'):
                    toggle: SubToggle = action.obj
                    action.setChecked(toggle.is_checked())

    # handlers
    def _handle_signal(self, signal: int):
        if signal >= 0:
            self._construct_menu()
        else:
            self._update_menu(self)

    def _handle_show_all(self):
        self._show_all = not self._show_all
        self._container.show_all(self._show_all)
