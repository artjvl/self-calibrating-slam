import typing as tp

import numpy as np

Key = tp.Union[int, str]
SubData = tp.TypeVar('SubData', bound='Data')
SubTimeData = tp.TypeVar('SubTimeData', bound='TimeData')


class Data(object):
    _len: tp.Optional[int]
    _data: tp.Dict[Key, np.ndarray]

    def __init__(self):
        self._len = None
        self._data = {}

    def has_first(self) -> bool:
        return self._len is not None

    def dim(self) -> int:
        assert self.has_first()
        return len(self._data.keys())

    def length(self) -> int:
        return self._len

    def has_key(self, key: Key) -> bool:
        return key in self._data

    def keys(self) -> tp.List[Key]:
        return list(self._data.keys())

    def add(
            self,
            key: Key,
            value: tp.List[float]
    ) -> None:
        if not self.has_first():
            self._len = len(value)

        if key not in self._data:
            self._data[key] = np.array([value])
        else:
            self._data[key] = np.vstack((self._data[key], [value]))

    def data(self, key: Key) -> np.ndarray:
        assert self.has_first()
        assert self.has_key(key)
        return self._data[key]

    def num_rows(self, key: Key) -> int:
        data: np.ndarray = self.data(key)
        return data.shape[0]

    def row(self, key: Key, row: int) -> np.ndarray:
        data: np.ndarray = self.data(key)
        return data[row, :]

    def mean(self, key: Key) -> np.ndarray:
        return np.mean(self.data(key), axis=0)

    def std(self, key: Key) -> np.ndarray:
        return np.std(self.data(key), axis=0)


class TimeData(Data):
    _time: tp.List[float]

    def __init__(self, time: tp.List[float]):
        super().__init__()
        self._time = time
        self._len = len(time)

    def time(self) -> tp.List[float]:
        return self._time
