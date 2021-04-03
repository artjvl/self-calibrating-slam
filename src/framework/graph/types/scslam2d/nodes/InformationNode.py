import typing as tp
from abc import abstractmethod

from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.structures import Square

SubInfoNode = tp.TypeVar('SubInfoNode', bound='InformationNode')


class InformationNode(CalibratingNode):

    @abstractmethod
    def get_matrix(self) -> Square:
        pass
