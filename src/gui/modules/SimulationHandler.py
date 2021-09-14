import typing as tp

from PyQt5.QtCore import QObject, pyqtSignal
from src.framework.simulation.Model2D import Model2D
from src.gui.action_pane.ConfigurationTree import ConfigurationTree
from src.gui.modules.TreeNode import TopTreeNode
from framework.simulation.Simulation import SubSimulationManager


class SimulationHandler(QObject):
    _tree: TopTreeNode
    _config: ConfigurationTree
    _simulation: tp.Optional['SubSimulationManager']

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            config: ConfigurationTree,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._tree = tree
        self._config = config
        self._simulation = None

    def set_simulation(self, simulation: 'SubSimulationManager'):
        simulation.set_optimiser(self._tree.get_optimiser())
        self._simulation = simulation

        # if self._simulation.has_config():
        #     self._config.construct_tree(self._simulation.get_config())
        # else:
        self._config.clear()

        print(f"gui/SimulationHandler: Simulation '{simulation.name()}' selected")
        self.signal_update.emit(1)

    def get_simulation(self) -> Model2D:
        return self._simulation

    def simulate(self):
        print(f'gui/SimulationHandler: Simulating trajectory with {self._simulation.name()}...')
        graph_truth, graph_estimate = self._simulation.run()
        self._tree.add_graph(
            graph_estimate,
            origin=self._simulation.name()
        )
