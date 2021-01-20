from abc import ABC, abstractmethod
from .Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, vector):
        super().__init__(vector)

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        pass
