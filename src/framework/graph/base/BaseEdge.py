from typing import *

from src.framework.graph.base.BaseNode import BaseNode


class BaseEdge(object):

    # constructor
    def __init__(self, nodes: List[BaseNode], **kwargs):
        super().__init__(**kwargs)
        self._nodes = nodes

    # public methods
    def get_nodes(self) -> List[BaseNode]:
        return self._nodes

    def get_node(self, index: int) -> BaseNode:
        if index < len(self._nodes):
            return self._nodes[index]
        raise Exception('No node found at index {}'.format(index))
        # return None

    # object methods
    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, ', '.join([str(node.id()) for node in self.get_nodes()]))

    def __repr__(self) -> str:
        return '{} <at {}>'.format(str(self), hex(id(self)))
