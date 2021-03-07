from typing import *

from PyQt5 import QtCore

from src.framework.graph.Graph import Graph
from src.framework.optimiser.Optimiser import Optimiser, Library, Solver
from src.gui.modules.GraphContainer import GraphContainer


class OptimisationHandler(QtCore.QObject):

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimiser = Optimiser()
        self._container = container

    def set_graph(self, graph: Optional[Graph]):
        self._optimiser.set_graph(graph)
        print("Graph '{}' selected".format(graph))

    def get_graph(self) -> Optional[Graph]:
        return self._optimiser.get_graph()

    def optimise(self):
        print('Optimising {}...'.format(self._optimiser.get_graph()))
        self._optimiser.optimise('solved.g2o')

    def set_library(self, library: Library):
        self._optimiser.set_library(library)
        print("Library '{}' set".format(library.value))
        self.signal_update.emit(1)

    def get_solver(self) -> Solver:
        return self._optimiser.get_solver()

    def set_solver(self, solver: Solver):
        self._optimiser.set_solver(solver)
        print("Solver '{}' set".format(solver.value))

    def get_libraries(self) -> List[Library]:
        return self._optimiser.get_libraries()

    def get_solvers(self) -> List[Solver]:
        return self._optimiser.get_solvers()
