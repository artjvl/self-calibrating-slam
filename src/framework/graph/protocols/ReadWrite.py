import typing as tp
from abc import abstractmethod, ABC


class ReadWrite(ABC):
    """ An object that can be read (parsed) and written (serialised). """

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
    @abstractmethod
    def get_length(cls) -> int:
        """ Returns the length of the list of words necessary to instantiate the class instance. """
        pass
