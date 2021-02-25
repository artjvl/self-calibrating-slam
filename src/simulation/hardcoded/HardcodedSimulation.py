from typing import *

import numpy as np

from src.framework.graph.Graph import Graph
from src.framework.groups import SE2
from src.framework.simulation.Simulation2D import Simulation2D
from src.framework.structures import Vector


class HardcodedSimulation(Simulation2D):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def simulate(self) -> Tuple[Graph, Graph]:
        variance = Vector([0.1, 0.2, np.deg2rad(3)])
        self.add_odometry(SE2.from_elements(1., 0.2, 0.4), variance)
        self.add_odometry(SE2.from_elements(0.2, 1., 0.8), variance)
        self.add_proximity(2, variance=variance)
        self.save('test')
        return self.get_graphs()
