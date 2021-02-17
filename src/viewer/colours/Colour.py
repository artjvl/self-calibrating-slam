from typing import *


class Colour(object):

    # constructor
    def __init__(self, r: float, g: float, b: float, alpha: float):
        assert all(0. <= value <= 1. for value in (r, g, b, alpha))
        self._tuple: Tuple[float, float, float, float] = (r, g, b, alpha)

    def tuple(self) -> Tuple[float, float, float, float]:
        return self._tuple
