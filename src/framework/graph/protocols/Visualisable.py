import typing as tp

from src.gui.viewer.Rgb import RgbTuple, Rgb

SubVisualisable = tp.TypeVar('SubVisualisable', bound='Visualisable')


class Visualisable(object):

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.WHITE
