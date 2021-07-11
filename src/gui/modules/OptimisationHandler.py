import typing as tp

from PyQt5 import QtCore

from src.framework.graph.Graph import Graph, SubGraph
from src.framework.optimiser.Optimiser import Optimiser, Library, Solver
from src.gui.modules.Container import TopContainer, GraphContainer, TrajectoryContainer


class OptimisationHandler(QtCore.QObject):

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimiser = Optimiser()
        self._graph_container: tp.Optional[GraphContainer] = None

    def set_graph(
            self,
            graph_container: tp.Optional[GraphContainer]
    ):
        if graph_container is not None:
            self._graph_container = graph_container
            print(
                "gui/OptimisationHandler: Graph '{}/{}' set.".format(
                    graph_container.get_parent().get_name(),
                    graph_container.get_name()
                )
            )
            self.signal_update.emit(0)
        else:
            self.signal_update.emit(-1)

    def get_optimiser(self) -> Optimiser:
        return self._optimiser

    def optimise(self):
        assert self._graph_container is not None
        graph: SubGraph = self._graph_container.get_graph()
        print(f"gui/OptimisationHandler: Optimising '{graph.to_unique()}'...")
        graph: Graph = self._optimiser.optimise(graph)
        trajectory_container: TrajectoryContainer = self._graph_container.get_parent()
        trajectory_container.add_graphs(None, graph)
