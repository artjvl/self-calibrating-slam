import functools
import pathlib
import typing as tp
from PyQt5 import QtWidgets
from src.gui.menus.Menu import Menu
from src.framework.graph.GraphAnalyser import FigureParser
if tp.TYPE_CHECKING:
    from src.framework.graph.GraphAnalyser import GraphAnalyser

class AnalyserMenu(Menu):
    _analyser: 'GraphAnalyser'

    # constructor
    def __init__(
            self,
            analyser: 'GraphAnalyser',
            **kwargs
    ):
        super().__init__(**kwargs)
        self._analyser = analyser

        self.setTitle('Analyser')
        self.add_action(
            menu=self,
            name='Reset plots',
            tip='Resets the analyser plots',
            handler=self._analyser.clear
        )
        sub_save: QtWidgets.QMenu = self.add_menu(self, 'Save last figure')
        self.add_action(
            menu=sub_save,
            name='Save',
            tip='Saves last figure as a pickle automatically',
            handler=self._handle_save
        )
        self.add_action(
            menu=sub_save,
            name='Save as',
            tip='Saves last figure as a pickle with a given path',
            handler=self._handle_save_as
        )

    def _handle_save(self):
        self._analyser.save_last()

    def _handle_save_as(self):
        filename: tp.Optional[str]
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption='Save as pickle',
            directory=str(FigureParser.path()),
            filter='pickle (*.pickle)'
        )
        if filename:
            if not filename.endswith('.pickle'):
                filename += '.pickle'
            path: pathlib.Path = pathlib.Path(filename)
            self._analyser.save_last(path.name)
