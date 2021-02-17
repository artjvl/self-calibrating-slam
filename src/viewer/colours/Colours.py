from enum import Enum

from src.viewer.colours.Colour import Colour


class Colours(Enum):
    RED: Colour = Colour(1, 0, 0, 1)
    GREEN: Colour = Colour(0, 1, 0, 1)
    BLUE: Colour = Colour(0, 0, 1, 0)
    YELLOW: Colour = Colour(1, 1, 0, 1)
    FUCHSIA: Colour = Colour(1, 0, 1, 1)
    CYAN: Colour = Colour(0, 1, 1, 1)
    WHITE: Colour = Colour(1, 1, 1, 1)
    BLACK: Colour = Colour(0, 0, 0, 1)
