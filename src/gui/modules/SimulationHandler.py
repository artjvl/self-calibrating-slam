import typing as tp

from PyQt5.QtCore import QObject, pyqtSignal

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.gui.action_pane.ConfigurationTree import ConfigurationTree
from src.gui.modules.TreeNode import TopTreeNode


class SimulationHandler(QObject):
    _tree: TopTreeNode
    _config: ConfigurationTree
    _simulation: tp.Optional[BiSimulation2D]

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            config: ConfigurationTree,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._tree: TopTreeNode = tree
        self._config: ConfigurationTree = config
        self._simulation = None

    def set_simulation(self, sim_type: tp.Type[BiSimulation2D]):
        self._simulation = sim_type()
        if self._simulation.has_config():
            self._config.construct_tree(self._simulation.get_config())
        else:
            self._config.clear()

        print(f"gui/SimulationHandler: Simulation '{sim_type.__name__}' selected")
        self.signal_update.emit(1)

    def get_simulation(self) -> BiSimulation2D:
        return self._simulation

    def simulate(self):
        print(f'gui/SimulationHandler: Simulating trajectory with {type(self._simulation).__name__}...')
        graph_truth, graph_perturbed = self._simulation.simulate()
        self._tree.add_graph(
            graph_perturbed,
            origin=self._simulation.__class__.__name__
        )
