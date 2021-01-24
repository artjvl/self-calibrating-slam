from abc import ABC, abstractmethod


class Group(ABC):

    # operators
    def __mul__(self, other):
        assert isinstance(other, Group)
        product = self.matrix() @ other.matrix()
        return self.from_matrix(product)

    # public methods
    def algebra(self):
        vector = self.vector()
        algebra = type(self).vector_to_algebra(vector)
        return algebra

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def _dim(cls) -> int:
        """ number of dimensions """
        pass

    @property
    @classmethod
    @abstractmethod
    def _dof(cls) -> int:
        """ number of degrees of freedom """
        pass

    # abstract methods
    @abstractmethod
    def matrix(self):
        """ returns the matrix representation """
        pass

    def vector(self):
        """ returns the vector representation """
        pass

    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix):
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_vector(cls, vector):
        """ generates group element from vector """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args, **kwargs):
        """ generates group element from vector elements """
        pass

    @staticmethod
    @abstractmethod
    def vector_to_algebra(vector):
        """ returns the algebra corresponding to the vector """
        pass

    @staticmethod
    @abstractmethod
    def algebra_to_vector(algebra):
        """ returns the vector corresponding to the algebra """
        pass
