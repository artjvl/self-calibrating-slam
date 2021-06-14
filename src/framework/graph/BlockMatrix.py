import typing as tp

import numpy as np
from src.framework.math.matrix.Matrix import SubMatrix, Matrix

SubBlockMatrix = tp.TypeVar('SubBlockMatrix', bound='BlockMatrix', covariant=True)
SubSparseBlockMatrix = tp.TypeVar('SubSparseBlockMatrix', bound='SparseBlockMatrix', covariant=True)


class BlockMatrix(object):

    _row_block_sizes: tp.List[int]
    _column_block_sizes: tp.List[int]
    _blocks: tp.List[tp.List[tp.Optional[SubMatrix]]]

    def __init__(
            self,
            block_sizes: tp.List[int],
            column_block_sizes: tp.Optional[tp.List[int]] = None
    ):
        super().__init__()
        if column_block_sizes is None:
            column_block_sizes = block_sizes
        self._row_block_sizes = block_sizes
        self._column_block_sizes = column_block_sizes

        self._blocks = [
            [None for _ in range(len(self._column_block_sizes))] for __ in range(len(self._row_block_sizes))
        ]

    def __setitem__(self, key: tp.Tuple[int, int], block: SubMatrix) -> None:
        assert isinstance(key, tuple)
        a, b = key
        assert block.shape()[0] == self._row_block_sizes[a]
        assert block.shape()[1] == self._column_block_sizes[b]
        self._blocks[a][b] = block

    def __getitem__(self, key: tp.Tuple[int, int]) -> SubMatrix:
        assert isinstance(key, tuple)
        a, b = key
        block: tp.Optional[SubMatrix] = self._blocks[a][b]
        return block

    def __bool__(self) -> bool:
        return not self.is_empty()

    def shape(self) -> tp.Tuple[int, int]:
        return len(self._row_block_sizes), len(self._column_block_sizes)

    def get_row_sizes(self) -> tp.List[int]:
        return self._row_block_sizes

    def get_column_sizes(self) -> tp.List[int]:
        return self._column_block_sizes

    def is_empty(self) -> bool:
        empty: bool = True
        for i, _ in enumerate(self._row_block_sizes):
            for j, __ in enumerate(self._column_block_sizes):
                if self._blocks[i][j] is not None:
                    empty = False
                    break
        return empty

    def array(self) -> np.ndarray:
        row_size: int = sum(self._row_block_sizes)
        column_size: int = sum(self._column_block_sizes)
        array: np.ndarray = np.zeros((row_size, column_size))
        for i, row in enumerate(self._row_block_sizes):
            for j, column in enumerate(self._column_block_sizes):
                row_index = sum(self._row_block_sizes[:i])
                column_index = sum(self._column_block_sizes[:j])
                block: SubMatrix = self[i, j]
                assert block is not None
                for ii in range(row):
                    for jj in range(column):
                        array[row_index + ii, column_index + jj] = block[ii, jj]
        return array

    def matrix(self) -> SubMatrix:
        return Matrix(self.array())

    def inverse(self) -> np.ndarray:
        array = self.array()
        return np.linalg.pinv(array)

    @classmethod
    def from_array(
            cls,
            array: np.ndarray,
            block_sizes: tp.List[int],
            column_block_sizes: tp.Optional[tp.List[int]] = None
    ):
        if column_block_sizes is None:
            column_block_sizes = block_sizes
        assert array.shape == (sum(block_sizes), sum(column_block_sizes))
        matrix = cls(block_sizes, column_block_sizes)
        for i, row in enumerate(block_sizes):
            for j, column in enumerate(column_block_sizes):
                row_index = sum(block_sizes[:i])
                column_index = sum(column_block_sizes[:j])
                matrix[i, j] = Matrix(
                    array[
                        row_index: row_index + block_sizes[i],
                        column_index: column_index + column_block_sizes[j]
                    ]
                )
        return matrix


class SparseBlockMatrix(BlockMatrix):

    def __init__(
            self,
            block_sizes: tp.List[int],
            column_block_sizes: tp.Optional[tp.List[int]] = None
    ):
        super().__init__(block_sizes, column_block_sizes)

    def __getitem__(self, key: tp.Tuple[int, int]) -> SubMatrix:
        block: tp.Optional[SubMatrix] = super().__getitem__(key)
        if block is None:
            a, b = key
            array: np.ndarray = np.zeros((self._row_block_sizes[a], self._column_block_sizes[b]))
            block = Matrix(array)
        return block
