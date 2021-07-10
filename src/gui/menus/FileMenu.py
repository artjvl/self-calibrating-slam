from PyQt5 import QtWidgets
from src.framework.graph.Graph import SubGraph
from src.gui.menus.Menu import Menu
from src.gui.modules.Container import TopContainer
from src.gui.modules.PopUp import PopUp


class FileMenu(Menu):

    # constructor
    def __init__(self, container: TopContainer, *args, **kwargs):
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
            handler=self._handle_load
        )
        # menu_remove = self.add_menu(
        #     menu=self,
        #     name='Remove'
        # )
        # if self._container.is_empty():
        #     menu_remove.setEnabled(False)
        # else:
        #     for graph in self._container.get_graphs():
        #         self.add_action(
        #             menu=menu_remove,
        #             name=graph.to_name(),
        #             handler=partial(
        #                 self._container.remove_graph,
        #                 graph
        #             )
        #         )
        self.addSeparator()
        self.add_action(
            menu=self,
            name='&Quit',
            handler=self._handle_quit
        )

    # handler
    def _handle_load(self):
        graph: SubGraph = PopUp.load_from_file()
        if graph is not None:
            self._container.add_graphs(None, graph)

    def _handle_signal(self, signal):
        if signal >= 0:
            self._construct_menu()

    @staticmethod
    def _handle_quit():
        QtWidgets.qApp.quit()
