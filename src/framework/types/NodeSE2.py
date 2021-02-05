from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.BaseGraph import BaseGraph


class NodeSE2(BaseGraph.Node):

    tag = 'VERTEX_SE2'

    # constructor
    def __init__(self, id, pose=None):
        assert isinstance(id, int)
        super().__init__(id)
        if pose is None:
            pose = SE2.from_elements(0, 0, 0)
        assert isinstance(pose, SE2)
        self._pose = pose

    # public methods
    def get_pose(self):
        return self._pose

    def set_pose(self, pose):
        assert isinstance(pose, SE2)
        self._pose = pose

    # abstract implementations
    def to_string(self):
        pose_string = self._array_to_string(self._pose.vector())
        return ' '.join([self.tag, str(self.id()), pose_string])

    def read(self, words):
        assert isinstance(words, list)
        assert all(isinstance(word, str) for word in words)
        elements = [float(word) for word in words]
        self.set_pose(SE2.from_vector(Vector(elements)))
