import typing as tp
from abc import ABC

from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.simulation.BiSimulation2D import BiSimulation2D

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph
    from src.framework.math.lie.transformation import SE2


class InputSimulation2D(BiSimulation2D, ABC):
    _poses: tp.Optional[tp.List['SE2']]
    _iter: tp.Optional[iter]
    _next: tp.Optional['SE2']

    _counter: int

    def __init__(self):
        self._poses = None
        self._counter = 1
        super().__init__()

    def reset(self) -> None:
        super().reset()
        self._counter = 1

    def has_next(self) -> bool:
        return self._poses is not None and \
               self._counter < len(self._poses)

    def auto_odometry(
            self,
            sensor_name: str
    ) -> None:
        assert self.has_next()
        self.add_odometry_to(sensor_name, self._poses[self._counter])
        self._counter += 1

    def set_input_poses(
            self,
            poses: tp.List['SE2']
    ) -> None:
        self._poses = poses
        self.reset()

    def set_input_graph(
            self,
            graph: 'SubGraph'
    ) -> None:
        self._poses = [node.get_value() for node in graph.get_of_type(NodeSE2)]
        self.reset()
