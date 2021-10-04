import typing as tp

T = tp.TypeVar('T')

class Data(tp.Generic[T]):
    _type: tp.Type[T]
    _value: tp.Optional[T]

    def __init__(
            self,
            value: tp.Optional[T] = None
    ):
        self._value = None
        if value is not None:
            self.set_value(value)

    def set_value(self, value: T) -> None:
        assert isinstance(value, self._type)
        self._value = value

    def has_value(self) -> bool:
        return self._value is not None

    def get_value(self) -> T:
        assert self.has_value()
        return self._value

