from copy import deepcopy
from typing import *

import numpy as np

from src.framework.graph.Graph import Graph
from src.framework.graph.types.scslam2d.nodes.information import InformationNodeFull3
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector6
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors.SensorSE2 import SensorSE2


class HardcodedSimulation(BiSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def _simulate(self) -> Tuple[Graph, Graph]:

        info = InformationNodeFull3()
        info.set_value(Vector6([800, 0, 0, 600, 0, 400]))
        par = ParameterNodeSE2()
        par.set_value(SE2.from_translation_angle_elements(0.2, 0.3, 0.02))
        par.set_as_bias()
        true = SensorSE2()
        true.add_parameter(par)
        true.set_information(Square3([[800, 0, 0], [0, 600, 0], [0, 0, 400]]))
        self.add_sensor('lidar', true, deepcopy(true))

        # self.add_odometry(SE2.from_elements(1., 0.2, 0.4), 'lidar')
        # self.add_odometry(SE2.from_elements(0.2, 1., 0.8), 'lidar')

        num: int = 5
        for _ in range(8):
            for __ in range(num):
                angle: float = np.deg2rad(np.random.choice([90, -90])) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry(motion, 'lidar')
                self.add_proximity(5, 'lidar', threshold=0.4)
                self.add_closure(3., 'lidar', threshold=0.4)

        return self.get_graphs()
