import pathlib
import typing as tp
from datetime import datetime

from src.definitions import get_project_root
from src.framework.graph.CalibratingGraph import CalibratingGraph
from src.framework.graph.Graph import SubGraph, SubNode, Edge, Node
from src.framework.graph.types.scslam2d.database import database


class GraphParser(object):

    _database = database

    @classmethod
    def save(
            cls,
            graph: SubGraph,
            file: pathlib.Path
    ) -> None:
        print(
            f"framework/GraphParser: Saving '{graph.to_unique()}' to:\n    '{file}'"
        )
        graph.set_path(file)

        writer: tp.TextIO = file.open('w')

        node: SubNode
        for node in graph.get_nodes():
            tag: str = cls._database.from_element(node)
            id_: str = f'{node.get_id()}'
            data: str = ' '.join(node.write())
            writer.write(f'{tag} {id_} {data}\n')
            if node.is_fixed():
                writer.write(f'FIX {id_}\n')

        edge: SubEdge
        for edge in graph.get_edges():
            tag: str = cls._database.from_element(edge)
            ids: str = ' '.join([f'{id_}' for id_ in edge.get_node_ids()])
            data: str = ' '.join(edge.write())
            writer.write(f'{tag} {ids} {data}\n')

    @classmethod
    def save_path_folder(
            cls,
            graph: SubGraph,
            folder: str,
            name: tp.Optional[str] = None,
            relative_to_root: bool = True,
            add_date: bool = False
    ) -> None:

        # path
        path: pathlib.Path
        if relative_to_root:
            path = get_project_root()
        else:
            path = pathlib.Path(__file__).parent
        path = (path / folder).resolve()
        path.mkdir(parents=True, exist_ok=True)

        # file-name
        if name is None or add_date:
            date_string: str = datetime.now().strftime('%Y%m%d-%H%M%S')
            name: str = f'{name}_{date_string}'
            name = name.strip('_')
        file: pathlib.Path = (path / f'{name}.g2o').resolve()

        # save
        cls.save(graph, file)

    @classmethod
    def load(
            cls,
            file: pathlib.Path
    ) -> SubGraph:
        graph = CalibratingGraph()

        print(
            f"framework/GraphParser: Loading '{graph.to_unique()}' from:\n    '{file}'"
        )

        graph.set_path(file)

        reader: tp.TextIO = file.open('r')
        lines: tp.List[str] = reader.readlines()
        nodes: tp.Dict[int, SubNode] = {}

        line: str
        for i, line in enumerate(lines):
            assert line != '\n', f'Line {i} is empty.'
            line = line.strip()
            words: tp.List[str] = line.split()

            tag: str = words[0]
            if tag == 'FIX':
                id_: int = int(words[1])
                node = nodes[id_]
                node.fix()
            else:
                element = cls._database.from_tag(tag)
                if isinstance(element, Node):
                    id_: int = int(words[1])
                    element.set_id(id_)
                    element.read(words[2:])
                    nodes[id_] = element
                    # graph.add_node(element)
                elif isinstance(element, Edge):
                    cardinality: int = element.get_cardinality()
                    node_ids: tp.List[int] = [int(id_) for id_ in words[1: 1 + cardinality]]
                    for id_ in node_ids:
                        assert id_ in nodes
                        node: SubNode = nodes[id_]
                        if not graph.contains_node_id(id_):
                            graph.add_node(node)
                        element.add_node(node)
                    element.read(words[1 + cardinality:])
                    graph.add_edge(element)
        return graph
