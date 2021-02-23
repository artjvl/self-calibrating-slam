from src.framework.graph.base.BaseElement import BaseElement


class BaseNode(BaseElement):

    def __init__(self, id: int, **kwargs):
        self._id: int = id

    def id_string(self) -> str:
        return str(self.id())

    # getters/setters
    def id(self) -> int:
        return self._id

    def set_id(self, id: int):
        self._id = id
