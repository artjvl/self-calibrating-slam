import pathlib
import typing as tp
from typing import TextIO

from src.framework.graph.Database import Database
from src.framework.graph.FactorGraph import FactorNode, FactorEdge, SubGraph, SubNode, SubEdge
from src.framework.graph.Graph import Graph


class GraphParser(object):

    def __init__(self, database: Database):
        self._database = database

    def save(
            self,
            graph: SubGraph,
            file: pathlib.Path
    ) -> None:
        writer: TextIO = file.open('w')

        node: SubNode
        for node in graph.get_nodes():
            tag: str = self._database.from_element(node)
            id_: str = f'{node.get_id()}'
            data: str = ' '.join(node.write())
            writer.write(f'{tag} {id_} {data}\n')
            if node.is_fixed():
                writer.write(f'FIX {id_}\n')

        edge: SubEdge
        for edge in graph.get_edges():
            tag: str = self._database.from_element(edge)
            ids: str = ' '.join([f'{id_}' for id_ in edge.get_node_ids()])
            data: str = ' '.join(edge.write())
            writer.write(f'{tag} {ids} {data}\n')

    def load(
            self,
            file: pathlib.Path
    ) -> SubGraph:
        graph = Graph()

        reader: TextIO = file.open('r')
        lines = reader.readlines()

        line: str
        for i, line in enumerate(lines):
            assert line != '\n', f'Line {i} is empty.'
            line = line.strip()
            words: tp.List[str] = line.split()

            tag: str = words[0]
            if tag == 'FIX':
                id_: int = int(words[1])
                node = graph.get_node(id_)
                node.fix()
            else:
                element = self._database.from_tag(tag)
                if isinstance(element, FactorNode):
                    id_: int = int(words[1])
                    element.set_id(id_)
                    element.read(words[2:])
                    graph.add_node(element)
                elif isinstance(element, FactorEdge):
                    cardinality: int = element.get_cardinality()
                    node_ids: tp.List[int] = [int(id_) for id_ in words[1: 1 + cardinality]]
                    for id_ in node_ids:
                        node: SubNode = graph.get_node(id_)
                        element.add_node(node)
                    element.read(words[1 + cardinality:])
                    graph.add_edge(element)
        return graph
