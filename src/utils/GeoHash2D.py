import numpy as np
from typing import *

T = TypeVar('T')


class Element(Generic[T]):

    # constructor
    def __init__(
            self,
            x: float,
            y: float,
            value: T
    ):
        self.x: float = x
        self.y: float = y
        self.value: T = value


class GeoHash2D(Generic[T]):

    # constructor
    def __init__(self, size: Optional[float] = .5):
        self._size: float = size
        self._hash: Dict[int, Dict[int, List[Element[T]]]] = {}

    # public methods
    def reset(self) -> None:
        self._hash = {}

    def get(
            self,
            a: int,
            b: int
    ) -> List[Element[T]]:
        """ Returns the element in bucket (a, b). """

        if a in self._hash:
            if b in self._hash[a]:
                return self._hash[a][b]
        return []

    def set(
            self,
            a: int,
            b: int,
            element: Element[T]
    ) -> None:
        """ Adds element 'element' to bucket (a, b). """

        if a not in self._hash:
            self._hash[a] = {}
        if b not in self._hash[a]:
            self._hash[a][b] = []
        self._hash[a][b].append(element)

    def add(
            self,
            x: float,
            y: float,
            item: T
    ) -> None:
        """ Adds item 'item' with coordinates (x, y) to the table at (a, b). """

        element = Element[T](x, y, item)
        a, b = self._find_nearest_xy(x, y)
        self.set(a, b, element)

    def get_closest(
            self,
            x: float,
            y: float
    ) -> List[T]:
        """ Finds the bucket (a, b) closest to coordinates (x, y). """

        a, b = self._find_nearest_xy(x, y)
        return [element.value for element in self.get(a, b)]

    def find_within(
            self,
            x: float,
            y: float,
            distance: float
    ) -> List[T]:
        """ Finds all elements within range 'distance' from coordinates (x, y). """

        a, b = self._find_nearest_xy(x, y)
        multiple: int = int(np.ceil(distance/self._size))
        steps = np.arange(-multiple, multiple + 1)
        neighbours: List[Element[T]] = []
        for i in steps:
            for j in steps:
                neighbours.extend(self.get(a + i, b + j))
        items: List[T] = []
        for element in neighbours:
            if (element.x - x)**2 + (element.y - y)**2 <= distance**2:
                items.append(element.value)
        return items

    # helper-methods
    def _find_nearest_xy(
            self,
            x: float,
            y: float
    ) -> Tuple[int, int]:
        """ Finds the indices (a, b) of the bucket closest to coordinates (x, y). """

        return self._find_nearest(x), self._find_nearest(y)

    def _find_nearest(self, x: float) -> int:
        return round(x/self._size)

    # object methods
    def __str__(self) -> str:
        return str(self._hash)

    def __repr__(self) -> str:
        return repr(self._hash)
