from byte_io_wmd import ByteIO


class Vector:
    sanitize = True  # disable for speedup
    size = 0
    value_type = "x"

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

    @property
    def values(self):
        return self._values

    def __eq__(self, other: 'Vector'):
        return self.size == other.size and self.value_type == other.value_type and self.values == other.values

    def __repr__(self):
        values = ','.join([str(value) for value in self.values])
        return f"{self.__class__.__name__}({values})"


class Vector2F(Vector):
    size = 2
    value_type = 'f'

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]


class Vector3F(Vector):
    size = 3
    value_type = 'f'

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]

    @property
    def z(self):
        return self.values[2]


class Vector4F(Vector):
    size = 4
    value_type = 'f'

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]

    @property
    def z(self):
        return self.values[2]

    @property
    def w(self):
        return self.values[2]


if __name__ == '__main__':
    # TESTING STUFF
    assert Vector2F(1, 2) == Vector2F([1, 2])
    assert Vector2F(1, 2).x == Vector2F([1, 2]).x
