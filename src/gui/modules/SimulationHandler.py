import typing as tp

from PyQt5.QtCore import QObject, pyqtSignal
from src.gui.action_pane.ConfigurationTree import ConfigurationTree
from src.gui.modules.TreeNode import TopTreeNode

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph
    from src.framework.simulation.BiSimulation import SubSimulation


class SimulationHandler(QObject):
    _tree: TopTreeNode
    _config: ConfigurationTree
    _simulation: tp.Optional['SubSimulation']

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            config: ConfigurationTree,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._tree = tree
        self._config = config
        self._simulation = None

    def set_simulation(self, simulation: 'SubSimulation'):
        simulation.set_optimiser(self._tree.optimiser())
        self._simulation = simulation

        # if self._simulation.has_config():
        #     self._config.construct_tree(self._simulation.get_config())
        # else:
        self._config.clear()

        print(f"gui/SimulationHandler: Simulation '{simulation.get_name()}' selected")
        self.signal_update.emit(1)

    def get_simulation(self) -> 'SubSimulation':
        return self._simulation

    def simulate(self) -> None:
        print(f"gui/SimulationHandler: Simulating trajectory with '{self._simulation.get_name()}'...")
        graph_estimate: 'SubGraph' = self._simulation.run()
        self._tree.add_graph(
            graph_estimate,
            origin=self._simulation.get_name()
        )

    def monte_carlo(self, num) -> None:
        print(f"gui/SimulationHandler: Monte Carlo simulation with '{self._simulation.get_name()}' (with n = {num})...")
        graphs: tp.List['SubGraph'] = self._simulation.monte_carlo(num)
        self._tree.add_graphs(graphs, self._simulation.get_name())
