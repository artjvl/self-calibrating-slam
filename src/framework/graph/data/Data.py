import typing as tp
from abc import abstractmethod

from src.framework.math.matrix.vector import SubVector

T = tp.TypeVar('T')
SubData = tp.TypeVar('SubData', bound='Data')


class Data(tp.Generic[T]):
    """ A data-object that contains a value and value-type, which can be read and written. """

    _type: tp.Type[T]
    _value: tp.Optional[T]

    def __init__(
            self,
            value: tp.Optional[T] = None
    ):
        super().__init__()
        self._value = None
        if value is not None:
            self.set_value(value)

    @abstractmethod
    def to_vector(self) -> SubVector:
        pass

    @abstractmethod
    def from_vector(self, vector: SubVector) -> None:
        pass

    # value
    def set_value(
            self,
            value: T
    ) -> None:
        """ Sets the value. """
        assert isinstance(value, self._type), f'Value <{value}> should be of type {self._type}.'
        self._value = value

    def get_value(self) -> T:
        """ Returns the value. """
        assert self.has_value()
        return self._value

    def has_value(self) -> bool:
        """ Returns whether a value is defined for this data-object. """
        return self._value is not None

    # oplus
    @abstractmethod
    def oplus(self, delta: SubVector) -> T:
        """ Increments the value with a delta. """
        pass

    # type
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the value-type. """
        return cls._type

    @classmethod
    @abstractmethod
    def get_dim(cls) -> int:
        """ Returns the dimension (i.e., minimal number of variables to fully define the data structure). """
        pass

    # read/write
    def read_rest(self, words: tp.List[str]) -> tp.List[str]:
        """ Takes an over-sized list of words and reads only the required portion, while returning the rest. """
        count: int = self.get_length()
        assert len(words) >= count, f"Words <{words}> should have at least length {count}."
        self.read(words[: count])
        return words[count:]

    @abstractmethod
    def read(self, words: tp.List[str]) -> None:
        """ Reads (or parses) the list of words (strings) and sets the class attributes. """
        pass

    @abstractmethod
    def write(self) -> tp.List[str]:
        """ Writes (or serialises) the class attributes to a list of words (strings). """
        pass

    @classmethod
    def get_length(cls) -> int:
        """ Returns the length of the list of words necessary to instantiate the class instance. """
        return cls.get_dim()
