import typing as tp

from PyQt5 import QtCore
from src.framework.graph.Graph import SubGraph, Graph
from src.framework.optimiser.Optimiser import Optimiser
from src.gui.modules.TreeNode import GraphTreeNode, TrajectoryTreeNode


class OptimisationHandler(QtCore.QObject):

    _optimiser: Optimiser
    _graph_node: tp.Optional[GraphTreeNode]
    _include_history: bool

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimiser = Optimiser()
        self._graph_node = None
        self._include_history = False

    def set_graph(
            self,
            graph_node: tp.Optional[GraphTreeNode]
    ) -> None:
        if graph_node is not None:
            self._graph_node = graph_node
            print(
                "gui/OptimisationHandler: Graph '{}/{}' set.".format(
                    graph_node.get_parent().get_gui_name(),
                    graph_node.get_gui_name()
                )
            )
            self.signal_update.emit(0)
        else:
            self.signal_update.emit(-1)

    def get_optimiser(self) -> Optimiser:
        return self._optimiser

    def set_include_history(self, include_history: bool = True) -> None:
        self._include_history = include_history

    def get_include_history(self) -> bool:
        return self._include_history

    def optimise(self) -> None:
        assert self._graph_node is not None
        graph: SubGraph = self._graph_node.get_graph()

        graphs: tp.List[SubGraph] = [graph]
        if self._include_history:
            graphs = graph.get_subgraphs()

        solutions: tp.List[SubGraph] = []
        for graph_ in graphs:
            print(f"gui/OptimisationHandler: Optimising '{graph_.to_unique()}'...")
            solution_: SubGraph = self._optimiser.instance_optimise(graph_, compute_marginals=False)
            solutions.append(solution_)
        solution: SubGraph = Graph.from_subgraphs(solutions)

        trajectory_node: TrajectoryTreeNode = self._graph_node.get_parent()
        trajectory_node.add_graph(solution)
