import pathlib
import typing as tp
from datetime import datetime

from src.definitions import get_project_root
from src.framework.graph.CalibratingGraph import CalibratingGraph, SubCalibratingGraph, SubCalibratingNode, \
    SubCalibratingEdge, CalibratingNode, CalibratingEdge
from src.framework.graph.Graph import SubGraph, SubNode, Edge, Node
from src.framework.graph.types.database import database


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
            file: pathlib.Path,
            reference: tp.Optional[SubCalibratingGraph] = None
    ) -> SubGraph:
        graph = CalibratingGraph()

        print(
            f"framework/GraphParser: Loading '{graph.to_unique()}' from:\n    '{file}'"
        )

        graph.set_path(file)

        reader: tp.TextIO = file.open('r')
        lines: tp.List[str] = reader.readlines()

        element: tp.Union[SubCalibratingNode, SubCalibratingEdge]
        num_edges: int = 0
        line: str
        for i, line in enumerate(lines):
            # read line
            assert line != '\n', f'Line {i} is empty.'
            line = line.strip()
            words: tp.List[str] = line.split()

            # interpret tag
            tag: str = words[0]
            if tag == 'FIX':
                id_: int = int(words[1])
                node = graph.get_node(id_)
                node.fix()
            else:
                element = cls._database.from_tag(tag)

                # parse node
                if isinstance(element, Node):
                    # read node
                    id_: int = int(words[1])
                    element.set_id(id_)
                    assert not element.read(words[2:])

                    if reference is not None:
                        # copy reference content
                        reference_node = reference.get_node(id_)
                        element = reference_node.copy_to(element)

                    # add node
                    graph.add_node(element)

                # parse edge
                elif isinstance(element, CalibratingEdge):
                    # read edge
                    cardinality: int = element.get_cardinality()
                    node_ids: tp.List[int] = [int(id_) for id_ in words[1: 1 + cardinality]]
                    for id_ in node_ids:
                        node: SubCalibratingNode = graph.get_node(id_)
                        element.add_node(node)
                    assert not element.read(words[1 + cardinality:])

                    if reference is not None:
                        # add reference content
                        reference_edge = reference.get_edge(num_edges)
                        element = reference_edge.copy_to(element)

                    # add edge
                    graph.add_edge(element)
                    num_edges += 1
        return graph
