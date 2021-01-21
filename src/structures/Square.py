import numpy as np


class Square(np.ndarray):

    # constructor
    def __new__(cls, elements):
        array = np.asarray(elements)
        assert len(array.shape) == 2
        assert array.shape[0] == array.shape[1]
        return array.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return
