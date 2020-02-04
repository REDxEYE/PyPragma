from .byte_io_wmd import ByteIO


class PragmaVector:
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
                # case where PragmaVector initialized as PragmaVector(X,Y,Z...) instead of PragmaVector([X,Y,Z...])
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

    def __eq__(self, other: 'PragmaVector'):
        return self.size == other.size and self.value_type == other.value_type and self.values == other.values

    def __repr__(self):
        values = ','.join([str(value) for value in self.values])
        return f"{self.__class__.__name__}({values})"


class PragmaVector2F(PragmaVector):
    size = 2
    value_type = 'f'
    value_order = "xy"


class PragmaVector3F(PragmaVector):
    size = 3
    value_type = 'f'
    value_order = 'xyz'


class PragmaVector3H(PragmaVector3F):
    value_type = 'H'


class PragmaVector3HF(PragmaVector3F):
    value_type = 'x'

    def from_file(self, reader: ByteIO):
        self._values = [reader.read_float16() for _ in range(self.size)]


class PragmaVector4F(PragmaVector):
    size = 4
    value_type = 'f'
    value_order = 'wxyz'

    def from_file(self, reader: ByteIO):
        self._values = list(reader.read_fmt(self.value_type * self.size))


if __name__ == '__main__':
    # TESTING STUFF
    assert PragmaVector2F(1, 2) == PragmaVector2F([1, 2])
    assert PragmaVector2F(1, 2).x == PragmaVector2F([1, 2]).x
