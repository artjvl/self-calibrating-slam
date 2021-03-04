from pathlib import Path
from typing import *

import numpy as np

from src.framework.graph.Graph import Graph
from src.framework.groups import SE2
from src.framework.simulation.Simulation2D import Simulation2D
from src.framework.structures import Vector


class TutorialSimulation(Simulation2D):

    # constructor
    def __init__(self):
        super().__init__()
        self.read_parameters(Path(__file__).parent)

    # public methods
    def _simulate(self) -> Tuple[Graph, Graph]:
        parameters = self.get_parameters()
        assert parameters is not None
        num_nodes = parameters['num_nodes']
        step_length = parameters['step_length']
        translation_noise_x = parameters['translation_noise_x']
        translation_noise_y = parameters['translation_noise_y']
        rotation_noise_deg = parameters['rotation_noise_deg']
        proximity_probability = parameters['proximity_probability']
        proximity_separation = parameters['proximity_separation']
        reach = parameters['reach']
        closure_probability = parameters['closure_probability']
        closure_separation = parameters['closure_separation']

        variance = Vector([
            translation_noise_x,
            translation_noise_y,
            np.deg2rad(rotation_noise_deg)
        ])

        angle: float = np.deg2rad(0)
        while self.get_node_count() < num_nodes:
            for _ in range(int(parameters['step_count'])):
                motion = SE2.from_elements(step_length, 0, angle)
                angle = np.deg2rad(0)
                self.add_odometry(motion, variance=variance)
                if self.get_probability() >= proximity_probability:
                    self.add_proximity(proximity_separation, variance)
                if self.get_probability() >= closure_probability:
                    self.add_loop_closure(closure_separation, reach, variance)
                if self.get_node_count() >= num_nodes:
                    break
            angle = np.deg2rad(np.random.choice([90, -90]))

        self.save('test')
        return self.get_graphs()
