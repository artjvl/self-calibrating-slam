from functools import partial

from PyQt5.QtWidgets import qApp

from src.gui.menus.Menu import Menu
from src.gui.modules.Container import ViewerContainer


class FileMenu(Menu):

    # constructor
    def __init__(self, container: ViewerContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&File')
        self._container = container
        self._construct_menu()
        self._container.signal_update.connect(self._handle_signal)

    # helper-methods
    def _construct_menu(self):
        self.clear()
        self.add_action(
            menu=self,
            name='&Load',
            handler=self._container.load_graph
        )
        menu_replace = self.add_menu(
            menu=self,
            name='&Replace'
        )
        menu_remove = self.add_menu(
            menu=self,
            name='Remove'
        )
        if self._container.is_empty():
            menu_replace.setEnabled(False)
            menu_remove.setEnabled(False)
        else:
            for graph in self._container.get_graphs():
                self.add_action(
                    menu=menu_replace,
                    name=graph.to_name(),
                    handler=partial(
                        self._container.replace_graph,
                        graph
                    )
                )
                self.add_action(
                    menu=menu_remove,
                    name=graph.to_name(),
                    handler=partial(
                        self._container.remove_graph,
                        graph
                    )
                )
        self.addSeparator()
        self.add_action(
            menu=self,
            name='&Quit',
            handler=self._handle_quit
        )

    # handler
    def _handle_signal(self, signal):
        if signal >= 0:
            self._construct_menu()

    @staticmethod
    def _handle_quit():
        qApp.quit()
