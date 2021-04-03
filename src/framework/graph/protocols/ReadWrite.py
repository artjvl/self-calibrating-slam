import typing as tp
from abc import abstractmethod, ABC


class ReadWrite(ABC):

    def read_rest(self, words: tp.List[str]) -> tp.List[str]:
        count: int = self.get_word_count()
        assert len(words) >= count, f"Words <{words}> should have at least length {count}."
        self.read(words[: count])
        return words[count:]

    @abstractmethod
    def read(self, words: tp.List[str]) -> None:
        pass

    @abstractmethod
    def write(self) -> tp.List[str]:
        pass

    @abstractmethod
    def get_word_count(self) -> int:
        pass
