from typing import *

from src.framework.graph.base.BaseElement import BaseElement
from src.framework.graph.base.BaseNode import BaseNode


class BaseEdge(BaseElement):

    def __init__(self, nodes: List[BaseNode], **kwargs):
        super().__init__(**kwargs)
        self._nodes: List[BaseNode] = nodes

    def id_string(self) -> str:
        return '-'.join([str(node.get_id()) for node in self.get_nodes()])

    # getters
    def get_nodes(self) -> List[BaseNode]:
        return self._nodes

    def get_node(self, index: int):
        assert 0 <= index < len(self._nodes)
        return self._nodes[index]
