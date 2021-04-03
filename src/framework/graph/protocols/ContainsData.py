import typing as tp

from src.framework.graph.attributes.Data import SubData
from src.framework.graph.attributes.DataFactory import DataFactory, Supported


class ContainsData(object):

    default_datatype: tp.Optional[tp.Type[Supported]] = None

    def __init__(self):
        super().__init__()
        self._datatype: tp.Optional[tp.Type[Supported]] = self.default_datatype
        self._data: tp.Optional[SubData] = None
        if self.default_datatype is not None:
            self._data = DataFactory.from_type(self.default_datatype)()

    def has_default_datatype(self) -> bool:
        return self.default_datatype is not None

    def set_datatype(self, type_: tp.Type[Supported]) -> None:
        assert not self.has_default_datatype(), f"Default data-type '{self.default_datatype}' cannot be overwritten."
        self._data = DataFactory.from_type(type_)

    def get_datatype(self) -> tp.Type[Supported]:
        assert self._datatype is not None
        return self._datatype

    def set_data(self, value: Supported) -> None:
        if self.has_default_datatype():
            assert isinstance(value, self.default_datatype), f"{value} should be of type '{self.default_datatype}'."
        self._data = DataFactory.from_value(value)

    def get_data(self) -> Supported:
        assert self._data is not None
        return self._data.get_value()
