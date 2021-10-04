import pathlib
import typing as tp
from datetime import datetime

from src.definitions import get_project_root
from src.framework.graph.CalibratingGraph import CalibratingGraph, SubCalibratingGraph, SubCalibratingEdge, \
    CalibratingEdge
from src.framework.graph.Graph import SubGraph, SubNode, Node
from src.framework.graph.types.database import database


class GraphParser(object):

    _database = database

    @classmethod
    def save(
            cls,
            graph: SubGraph,
            file: pathlib.Path,
            should_print: bool = True
    ) -> None:
        if should_print:
            print(f"framework/GraphParser: Saving '{graph.to_unique()}' to:\n    '{file}'")
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

        edge: SubCalibratingEdge
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
            add_date: bool = False,
            should_print: bool = True
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
        cls.save(graph, file, should_print=should_print)

    @classmethod
    def load(
            cls,
            file: pathlib.Path,
            reference: tp.Optional[SubCalibratingGraph] = None,
            should_sort: bool = False,
            should_print: bool = True
    ) -> SubGraph:
        nodes: tp.Dict[int, SubNode]
        edges: tp.List[SubCalibratingEdge]
        nodes, edges = cls.read_graph(file, should_print=should_print)

        graph: SubCalibratingGraph = CalibratingGraph()
        graph.set_path(file)
        graph.set_atol(1e-3)

        nodes_sorted: tp.List[SubNode]
        edges_sorted: tp.List[SubCalibratingEdge]
        if should_sort:
            nodes_sorted = [nodes[id_] for id_ in sorted(nodes)]
            edge_dict: tp.Dict[int, tp.List[SubCalibratingEdge]] = {}
            for edge in edges:
                max_id: int = max(edge.get_node_ids())
                if max_id not in edge_dict:
                    edge_dict[max_id] = []
                edge_dict[max_id].append(edge)
            edges_sorted = []
            for max_id in sorted(edge_dict):
                edges_sorted += edge_dict[max_id]
        else:
            nodes_sorted = list(nodes.values())
            edges_sorted = edges

        for node in nodes_sorted:
            if reference is not None:
                # copy reference content
                reference_node = reference.get_node(node.get_id())
                node = reference_node.copy_attributes_to(node)
            graph.add_node(node)

        for edge in edges_sorted:
            if reference is not None:
                # copy reference content
                reference_edge = reference.get_edge_from_ids(tuple(edge.get_node_ids()))
                edge = reference_edge.copy_attributes_to(edge)
            graph.add_edge(edge)

        if reference is not None:
            reference.copy_attributes_to(graph)
        return graph

    @classmethod
    def read_graph(
            cls,
            file: pathlib.Path,
            should_print: bool = True
    ) -> tp.Tuple[tp.Dict[int, SubNode], tp.List[SubCalibratingEdge]]:
        if should_print:
            print(f"framework/GraphParser: Reading:\n    '{file}'")

        nodes: tp.Dict[int, SubNode] = {}
        edges: tp.List[SubCalibratingEdge] = []

        reader: tp.TextIO = file.open('r')
        lines: tp.List[str] = reader.readlines()

        for i, line in enumerate(lines):
            # read line
            assert line != '\n', f'Line {i} is empty.'
            line = line.strip()
            words: tp.List[str] = line.split()

            # interpret tag
            tag: str = words[0]
            if tag == 'FIX':
                id_: int = int(words[1])
                assert id_ in nodes
                node: SubNode = nodes[id_]
                node.fix()
            else:
                element: tp.Union[SubNode, SubCalibratingEdge] = cls._database.from_tag(tag)

                # parse node
                if isinstance(element, Node):
                    node: SubNode = element
                    # read node
                    id_: int = int(words[1])
                    node.set_id(id_)
                    words = words[2:]
                    assert not any(word == 'nan' for word in words)
                    assert not node.read(words)

                    # add node
                    assert id_ not in nodes
                    nodes[id_] = node

                # parse edge
                elif isinstance(element, CalibratingEdge):
                    edge: SubCalibratingEdge = element

                    # read edge
                    cardinality: int = edge.get_cardinality()
                    node_ids: tp.List[int] = [int(id_) for id_ in words[1: 1 + cardinality]]
                    for id_ in node_ids:
                        assert id_ in nodes
                        node: SubNode = nodes[id_]
                        edge.add_node(node)
                    assert not edge.read(words[1 + cardinality:])

                    # add edge
                    edges.append(edge)
        return nodes, edges
