from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.matrix.vector import Vector1
from src.simulation.manhattan.ManhattanSim import ManhattanSim


class ManhattanSimWith(ManhattanSim):

    def init(self) -> None:
        super().init()
        self.set_path_rng(4)
        self.set_sensor_seed(1)

        self.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=1)
        # self.add_sliding_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, 40, index=1)
