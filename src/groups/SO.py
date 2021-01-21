from abc import ABC, abstractmethod
from src.structures import *
from src.groups.Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, vector):
        assert isinstance(vector, Vector)
        super().__init__(vector)

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        pass
