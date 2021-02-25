import configparser
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
        config = configparser.ConfigParser()
        base_path = Path(__file__).parent
        file_path = (base_path / "config.ini").resolve()
        config.read(file_path)
        self._parameters = config['PARAMETERS']

    # public methods
    def simulate(self) -> Tuple[Graph, Graph]:
        step_length = float(self._parameters['step_length'])
        translation_noise_x = float(self._parameters['translation_noise_x'])
        translation_noise_y = float(self._parameters['translation_noise_y'])
        rotation_noise_deg = float(self._parameters['rotation_noise_deg'])
        variance = Vector([
            translation_noise_x,
            translation_noise_y,
            np.deg2rad(rotation_noise_deg)
        ])
        motion = SE2.from_elements(step_length, 0, 0)
        self.add_odometry(motion, variance=variance)

        # num_nodes = 3
        # while self.get_node_count() < num_nodes:
        #     for _ in range(int(self._parameters['step_count'])):
        #
        #
        #         if self.get_node_count() >= num_nodes:
        #             break

        self.save('test')
        return self.get_graphs()