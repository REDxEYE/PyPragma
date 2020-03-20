from PyPragma.shared.modules.base import PragmaBase
from PyPragma.byte_io_wmd import ByteIO


class IKController(PragmaBase):
    def __init__(self):
        self.name = ""
        self.type = ""
        self.chain_len = 0
        self.method = 0
        self.key_values = {}

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.type = reader.read_ascii_string()
        self.chain_len = reader.read_uint32()
        self.method = reader.read_uint32()
        for _ in range(reader.read_uint32()):
            key = reader.read_ascii_string()
            self.key_values[key] = reader.read_ascii_string()

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_ascii_string(self.type)
        writer.write_uint32(self.chain_len)
        writer.write_uint32(self.method)
        writer.write_uint32(len(self.key_values))
        for k, v in self.key_values.items():
            writer.write_ascii_string(k)
            writer.write_ascii_string(v)

    pass
