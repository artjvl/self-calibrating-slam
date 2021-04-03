import typing as tp


class TypeDict(object):
    def __init__(self):
        self._dict: tp.Dict[tp.Type[tp.Any], tp.List[tp.Any]] = {}

    def add(self, element: tp.Any):
        type_ = type(element)
        if type_ not in self._dict:
            self._dict[type_] = []
        self._dict[type_].append(element)

    def get_types(self) -> tp.List[tp.Type[tp.Any]]:
        return list(self._dict.keys())

    def __contains__(self, type_: tp.Type[tp.Any]) -> bool:
        return type_ in self._dict

    def __getitem__(self, type_: tp.Type[tp.Any]) -> tp.List[tp.Any]:
        assert type_ in self
        return self._dict[type_]
