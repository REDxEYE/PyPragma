from . import *
from PyPragma.byte_io_wmd import ByteIO


class LodInfo(PragmaBase):
    def __init__(self):
        self.lods = {}

    def from_file(self, reader: ByteIO):
        lod_count = reader.read_uint8()
        for _ in range(lod_count):
            lod_id = reader.read_uint8()
            self.lods[lod_id] = []
            replace_count = reader.read_uint8()
            for i in range(replace_count):
                self.lods[lod_id].append(reader.read_fmt('ii'))  # original,replacement

    def to_file(self, writer: ByteIO):
        writer.write_uint8(len(self.lods))
        for lod_id, lod in self.lods.items():
            writer.write_uint8(lod_id)
            writer.write_uint8(len(lod))
            for l in lod:
                writer.write_fmt('ii', *l)
