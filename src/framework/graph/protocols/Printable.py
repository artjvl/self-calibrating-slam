from abc import abstractmethod, ABC


class Printable(ABC):
    """ An object that can be printed in various manners. """

    @abstractmethod
    def to_id(self) -> str:
        """ Returns the object's user-interpretable identifier (id). """
        pass

    def to_name(self) -> str:
        """ Returns the object's name (class name and id). """
        return f'{self.__class__.__name__}({self.to_id()})'

    def to_unique(self) -> str:
        """ Returns the object's *unique* name (name and memory address). """
        return f'{self.to_name()} <at {hex(id(self))}>'
