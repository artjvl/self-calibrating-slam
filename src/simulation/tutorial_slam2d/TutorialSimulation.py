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
    def _simulate(self) -> Tuple[Graph, Graph]:
        step_length = float(self._parameters['step_length'])
        translation_noise_x = float(self._parameters['translation_noise_x'])
        translation_noise_y = float(self._parameters['translation_noise_y'])
        rotation_noise_deg = float(self._parameters['rotation_noise_deg'])
        proximity_probability = float(self._parameters['proximity_probability'])
        proximity_separation = int(self._parameters['proximity_separation'])
        reach = float(self._parameters['reach'])
        closure_probability = float(self._parameters['closure_probability'])
        closure_separation = int(self._parameters['closure_separation'])

        variance = Vector([
            translation_noise_x,
            translation_noise_y,
            np.deg2rad(rotation_noise_deg)
        ])

        num_nodes = 100

        angle: float = np.deg2rad(0)
        while self.get_node_count() < num_nodes:
            for _ in range(int(self._parameters['step_count'])):
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
