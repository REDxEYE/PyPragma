from . import PragmaBase
from ...byte_io_wmd import ByteIO


class Constraint(PragmaBase):
    def __init__(self):
        self.type = 0
        self.id_tgt = 0
        self.collide = 0
        self.key_value = {}

    def from_file(self, reader: ByteIO):
        self.type = reader.read_uint8()
        self.id_tgt = reader.read_uint32()
        self.collide = reader.read_uint8() == 1
        arg_count = reader.read_uint8()
        for _ in range(arg_count):
            key = reader.read_ascii_string()
            self.key_value[key] = reader.read_ascii_string()

    def to_file(self, writer: ByteIO):
        writer.write_uint8(self.type)
        writer.write_uint32(self.id_tgt)
        writer.write_uint8(self.collide)
        writer.write_uint8(len(self.key_value))
        for k, v in self.key_value.items():
            writer.write_ascii_string(k)
            writer.write_ascii_string(v)
