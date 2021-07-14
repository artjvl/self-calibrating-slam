import typing as tp
import numpy as np

RgbTuple = tp.Tuple[float, float, float]


class Rgb(object):
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
            pastel: tp.Optional[float] = 0.5
    ) -> RgbTuple:
        return cls.pastelify(tuple(np.random.uniform(0., 1., 3)), pastel)

    @classmethod
    def similar(
            cls,
            reference: RgbTuple,
            similarity: tp.Optional[float] = 0.6,
            pastel: tp.Optional[float] = 0.
    ) -> RgbTuple:
        assert 0 <= similarity <= 1
        random_array = np.random.uniform(0., 1., 3)
        similar: RgbTuple = tuple(similarity * np.array(reference) + (1 - similarity) * random_array)
        return cls.pastelify(similar, pastel)

    @classmethod
    def normal(
            cls,
            reference: RgbTuple,
            std: tp.Optional[float] = 0.2,
            pastel: tp.Optional[float] = 0.
    ) -> RgbTuple:
        random_array = np.array(reference) + np.random.normal(0., std, 3)
        similar: RgbTuple = tuple(min(max(c, 0.), 1.) for c in random_array)
        return cls.pastelify(similar, pastel)

    @staticmethod
    def pastelify(
            reference: RgbTuple,
            pastel: tp.Optional[float] = 0.5
    ) -> RgbTuple:
        assert 0 <= pastel <= 1
        return tuple(c + (1 - c) * pastel for c in reference)
        # return tuple((reference + pastel)/(1 + pastel))

    @staticmethod
    def to_hex(rgb: RgbTuple):
        return '#{0:02x}{1:02x}{2:02x}'.format(*[255*c for c in rgb])

    @staticmethod
    def invert(rgb: RgbTuple):
        return 1 - rgb[0], 1 - rgb[1], 1 - rgb[2]
