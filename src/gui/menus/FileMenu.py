import pathlib
import typing as tp

from PyQt5 import QtWidgets
from src.framework.graph.Graph import SubGraph
from src.gui.menus.Menu import Menu
from src.gui.modules.TreeNode import TopTreeNode
from src.gui.utils.PopUp import PopUp


class FileMenu(Menu):
    _tree: TopTreeNode

    # constructor
    def __init__(self, tree: TopTreeNode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&File')
        self._tree = tree
        self._construct_menu()
        self._tree.signal_update.connect(self._handle_signal)

    # helper-methods
    def _construct_menu(self):
        self.clear()
        self.add_action(
            menu=self,
            name='&Load',
            handler=self._handle_load
        )
        self.addSeparator()
        self.add_action(
            menu=self,
            name='&Quit',
            handler=self._handle_quit
        )

    # handler
    def _handle_load(self):
        load: tp.Optional[tp.Tuple[SubGraph, pathlib.Path]] = PopUp.load_from_file()
        if load is not None:
            graph: SubGraph
            path: pathlib.Path
            graph, path = load
            self._tree.add_graph(graph, origin=path.name)

    def _handle_signal(self, signal):
        if signal >= 0:
            self._construct_menu()

    @staticmethod
    def _handle_quit():
        QtWidgets.qApp.quit()
