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

        subgraphs: tp.List[SubGraph] = [graph]
        if self._include_history:
            subgraphs = graph.get_subgraphs()

        subsolutions: tp.List[SubGraph] = []
        for subgraph in subgraphs:
            print(f"gui/OptimisationHandler: Optimising '{subgraph.to_unique()}'...")
            subsolution: SubGraph = self._optimiser.instance_optimise(subgraph, compute_marginals=False)
            if subsolutions:
                subsolution.set_previous(subsolutions[-1])
            subsolutions.append(subsolution)
        solution: SubGraph = Graph.from_subgraphs(subsolutions)

        trajectory_node: TrajectoryTreeNode = self._graph_node.get_parent()
        trajectory_node.add_graph(solution)
