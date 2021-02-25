from typing import *

from src.framework.graph.Graph import Graph
from src.framework.simulation.Simulation2D import Simulation2D
from src.gui.modules.GraphContainer import GraphContainer


class SimulationHandler(object):

    # constructor
    def __init__(
            self,
            container: GraphContainer
    ):
        self._container = container
        self._simulation: Optional[Simulation2D] = None

    def set_simulation(self, simulation: Simulation2D):
        self._simulation = simulation
        print('Selected: {}'.format(simulation))

    def simulate(self):
        graph_true, graph_perturbed = self._simulation.simulate()
        self._container.add_graph(graph_true)
        self._container.add_graph(graph_perturbed)
