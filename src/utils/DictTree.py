from __future__ import annotations

from typing import Optional, List, TypeVar, Generic, Dict, Type, Tuple
import warnings

K = TypeVar('K')  # key type
D = TypeVar('D')  # data type


class DictTree(Generic[K, D]):

    # constructor
    def __init__(self, value: Optional[D] = None):
        self._children: Dict[K, DictTree] = {}
        # data:
        self._value: D = value

    # public methods
    def get_value(self) -> D:
        """ returns the node's data entry """
        return self._value

    def set_value(self, data: D):
        """ sets the node's data entry """
        self._value = data

    def get_child(self, key: K) -> DictTree:
        """ returns the child at <key> """
        assert key in self._children
        return self._children[key]

    def set_child(self, key: K, child: Optional[DictTree] = None) -> DictTree:
        """ returns the replaced <child> at <key> """
        assert key in self._children
        if child is None:
            child = type(self)()
        self._children[key] = child
        return child

    def add_child(self, key: K, child: Optional[DictTree] = None) -> DictTree:
        """ returns the newly added <child> at <key> """
        if key in self._children:
            warnings.warn('Child with key {} already present in DictTree {}'.format(key, self))
        if child is None:
            child = type(self)()
        self._children[key] = child
        return child

    def remove_child(self, key: K):
        """ removes the child at <key> """
        assert key in self._children
        self._children.pop(key)

    def add_value(self, key: K, data: D) -> DictTree:
        """ returns the newly added child at <key> with <data> promptly initialised """
        child: DictTree = type(self)()
        child.set_value(data)
        self._children[key] = child
        return child

    def get_children(self) -> List[DictTree]:
        """ returns all children as a list """
        return list(self._children.values())

    # printing
    @classmethod
    def pretty(cls, tree: DictTree[K, D], indent: int):
        string: str = '<{}>'.format(tree.get_value())
        if tree._children:
            string += ', {{{}\n{}}}'.format(
                ','.join(['\n{}{}: {}'.format(
                        '\t' * (indent + 1),
                        repr(key),
                        cls.pretty(child, indent + 1)
                    ) for key, child in tree._children.items()]
                ),
                '\t' * indent
            )
        return string

    # default dict methods
    def key_values(self) -> List[Tuple[K, D]]:
        """ returns the keys and data entries of all children as a list """
        return [(key, child.get_value()) for key, child in self._children.items()]

    def keys(self) -> List[K]:
        """ returns all keys as a list """
        return list(self._children.keys())

    def values(self) -> List[D]:
        """ returns all data entries as a list """
        return [child.get_value() for child in self.get_children()]

    # object methods
    def __getitem__(self, key: K) -> DictTree:
        return self.get_child(key)

    def __setitem__(self, key: K, value: DictTree):
        self.add_child(key, value)

    def __contains__(self, key: K):
        return key in self._children

    def __iter__(self):
        return iter(self._children)

    def __next__(self):
        return next(self._children)

    def __str__(self):
        return type(self).pretty(self, indent=0)

    def __repr__(self) -> str:
        string: str = '<{}>'.format(self.get_value())
        if self._children:
            string += ', {{{}}}'.format(
                ', '.join(['{}: {}'.format(repr(key), repr(child)) for key, child in self._children.items()])
            )
        return string
