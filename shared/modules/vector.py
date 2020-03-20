import typing

from PyPragma.byte_io_wmd import ByteIO
import numpy as np



class Vector:
    VECTOR_OF_SCALAR = typing.Union["Vector", int, float]

    sanitize = True  # disable for speedup
    size = 0
    value_type = "x"
    value_order = "x"

    def __getattr__(self, item):
        if item in self.value_order:
            return self.values[self.value_order.index(item)]
        else:
            return self.__dict__[item]

    def __setattr__(self, key, value):
        if key in self.value_order:
            self.values[self.value_order.index(key)] = value
        else:
            self.__dict__[key] = value

    @staticmethod
    def validate_input(values):
        assert type(values) in [list, set, tuple], "input values for vector are not list/set/tuple type"

    def __init__(self, initial_values=None, *args):
        if initial_values is not None:
            if type(initial_values) in [int, float] and args:
                # case where Vector initialized as Vector(X,Y,Z...) instead of Vector([X,Y,Z...])
                initial_values = [initial_values, ] + list(args)
            if self.sanitize:
                self.validate_input(initial_values)
            self._values = list(initial_values)
        else:
            self._values = []

    def from_file(self, reader: ByteIO):
        self._values = list(reader.read_fmt(self.value_type * self.size))

    def to_file(self, writer: ByteIO):
        for value in self.values:
            writer.write(self.value_type, value)

    @property
    def values(self):
        return self._values

    def __eq__(self, other: 'Vector'):
        return self.size == other.size and self.value_type == other.value_type and self.values == other.values

    def __repr__(self):
        values = ','.join([str(value) for value in self.values])
        return f"{self.__class__.__name__}({values})"

    def __len__(self):
        return len(self._values)

    def __neg__(self):
        return self * -1

    def __sub__(self, other: VECTOR_OF_SCALAR):
        return self.__class__(np.subtract(self.values, other.values))

    def __add__(self, other: VECTOR_OF_SCALAR):
        return self.__class__(np.add(self.values, other.values))

    def __mul__(self, other: VECTOR_OF_SCALAR):
        return self.__class__(np.multiply(self.values, other.values))

    def __div__(self, other: VECTOR_OF_SCALAR):
        return self.__class__(np.multiply(self.values, other.values))

    def dot(self, other: VECTOR_OF_SCALAR):
        return np.dot(self.values, other.values)


class Vector2F(Vector):
    size = 2
    value_type = 'f'
    value_order = "xy"


class Vector3F(Vector):
    size = 3
    value_type = 'f'
    value_order = 'xyz'


class Vector3H(Vector3F):
    value_type = 'H'


class Vector3HF(Vector3F):
    value_type = 'x'

    def from_file(self, reader: ByteIO):
        self._values = [reader.read_float16() for _ in range(self.size)]

    def to_file(self, writer: ByteIO):
        for v in self._values:
            writer.write_float16(v)


class Vector4F(Vector):
    size = 4
    value_type = 'f'
    value_order = 'wxyz'

    def from_file(self, reader: ByteIO):
        self._values = list(reader.read_fmt(self.value_type * self.size))


if __name__ == '__main__':
    # TESTING STUFF
    assert Vector2F(1, 2) == Vector2F([1, 2])
    assert Vector2F(1, 2).x == Vector2F([1, 2]).x
