import typing as tp

from src.framework.graph.Graph import Graph

SubCalibratingGraph = tp.TypeVar('SubCalibratingGraph', bound='CalibratingGraph')


class CalibratingGraph(Graph):
    pass
