from abc import abstractmethod, ABC


class Printable(ABC):

    @abstractmethod
    def to_id(self) -> str:
        pass

    def to_name(self) -> str:
        return f'{self.__class__.__name__}({self.to_id()})'

    def to_unique(self) -> str:
        return f'{self.to_name()} <at {hex(id(self))}>'
