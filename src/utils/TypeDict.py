import typing as tp

T = tp.TypeVar('T')


class TypeDict(tp.Generic[T]):
    def __init__(self):
        self._dict: tp.Dict[tp.Type[T], tp.List[T]] = {}

    def add(self, element: T):
        type_ = type(element)
        if type_ not in self._dict:
            self._dict[type_] = []
        self._dict[type_].append(element)

    def get_types(self) -> tp.List[tp.Type[T]]:
        return list(self._dict.keys())

    def __contains__(self, type_: tp.Type[T]) -> bool:
        return type_ in self._dict

    def __getitem__(self, type_: tp.Type[T]) -> tp.List[T]:
        assert type_ in self
        return self._dict[type_]
