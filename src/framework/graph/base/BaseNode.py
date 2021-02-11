class BaseNode(object):

    # constructor
    def __init__(self, id: int, **kwargs):
        super().__init__(**kwargs)
        self._id = id

    # public methods
    def id(self) -> int:
        return self._id

    def set_id(self, id: int):
        self._id = id

    # object methods
    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.id())

    def __repr__(self) -> str:
        return '{} <at {}>'.format(str(self), hex(id(self)))
