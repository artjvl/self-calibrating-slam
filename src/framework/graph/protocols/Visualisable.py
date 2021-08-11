import typing as tp
from abc import abstractmethod

from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb

SubVisualisable = tp.TypeVar('SubVisualisable', bound='Visualisable')


class Visualisable(object):

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.WHITE


class DrawEdge(Visualisable):

    @abstractmethod
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        pass


class DrawPoint(Visualisable):

    @abstractmethod
    def draw_point(self) -> Vector3:
        pass


class DrawAxis(DrawPoint):

    @abstractmethod
    def draw_pose(self) -> SE3:
        pass

    def draw_point(self) -> Vector3:
        pose = self.draw_pose()
        return pose.translation()
