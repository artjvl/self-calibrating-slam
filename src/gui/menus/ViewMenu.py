import functools

from PyQt5.QtWidgets import QMenu, QAction
from src.gui.menus.Menu import Menu
from src.gui.modules.Container import TopContainer, Type, SubToggle, SubContainer
from src.gui.viewer.Viewer import Viewer


class ViewMenu(Menu):

    # constructor
    def __init__(self, container: TopContainer, viewer: Viewer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&View')
        self._container: TopContainer = container
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

    def _construct_recursive_container(
            self,
            menu: QMenu,
            container: SubContainer
    ):
        # type-toggles
        type_: Type
        for type_ in container.get_types():
            toggle: SubToggle = container.get_toggle(type_)
            action = self.add_action(
                menu=menu,
                name=type_.__name__,
                handler=functools.partial(self._container.toggle, toggle),
                checked=toggle.is_checked()
            )
            action.obj = toggle

        # separator
        menu.addSeparator()

        # sub-menus
        sub_container: SubContainer
        for sub_container in container.get_children():
            sub_menu: QMenu = self.add_menu(
                menu=menu,
                name=sub_container.get_name()
            )
            self._construct_recursive_container(sub_menu, sub_container)

    def _construct_container_section(self):
        self._construct_recursive_container(self, self._container)

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
