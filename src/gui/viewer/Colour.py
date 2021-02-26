from typing import *

import numpy as np


class Colour(object):

    WHITE = (1, 1, 1)
    RED = (1, 0, 0)
    ORANGE = (1, 0.5, 0)
    YELLOW = (1, 1, 0)
    GREEN = (0, 1, 0)
    CYAN = (0, 1, 1)
    BLUE = (0, 0, 1)
    FUCHSIA = (1, 0, 1)

    @classmethod
    def random(
            cls,
            pastel: Optional[float] = 0.5
    ) -> Tuple[float, ...]:
        return cls.pastelify(tuple(np.random.uniform(0., 1., 3)), pastel)

    @classmethod
    def similar(
            cls,
            reference: Tuple[float, ...],
            similarity: Optional[float] = 0.6,
            pastel: Optional[float] = 0.
    ) -> Tuple[float, ...]:
        assert 0 <= similarity <= 1
        random_array = np.random.uniform(0., 1., 3)
        similar = tuple(similarity * np.array(reference) + (1 - similarity) * random_array)
        return cls.pastelify(similar, pastel)

    @classmethod
    def normal(
            cls,
            reference: Tuple[float, ...],
            std: Optional[float] = 0.2,
            pastel: Optional[float] = 0.
    ) -> Tuple[float, ...]:
        random_array = np.array(reference) + np.random.normal(0., std, 3)
        similar = tuple([min(max(c, 0.), 1.) for c in random_array])
        return cls.pastelify(similar, pastel)

    @staticmethod
    def pastelify(
            reference: Tuple[float, ...],
            pastel: Optional[float] = 0.5
    ) -> Tuple[float, ...]:
        assert 0 <= pastel <= 1
        return tuple([c + (1 - c) * pastel for c in reference])
        # return tuple((reference + pastel)/(1 + pastel))
