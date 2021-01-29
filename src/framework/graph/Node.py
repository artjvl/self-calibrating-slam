from src.framework.graph.Edge import Edge


class Node(object):

    # constructor
    def __init__(self, id):
        self._id = id

    def get_id(self):
        return self._id
