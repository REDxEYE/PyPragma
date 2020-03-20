from enum import IntFlag, IntFlag
from typing import List

from ..byte_io_wmd import ByteIO
from ..shared import PragmaBase
from .modules import BSPTree, Entity

MAX_SUPPORTED_VERSION = 11


class DataFlags(IntFlag):
    NONE = 0
    HasLightmapAtlas = 1
    HasBSPTree = HasLightmapAtlas << 1


class World(PragmaBase):
    class Offsets(PragmaBase):
        def __init__(self):
            self.materials_offset = 0
            self.entities_offset = 0
            self.bsp_tree_offset = 0
            self.lightmap_data_offset = 0
            self.face_vertex_data_offset = 0

        def from_file(self, reader: ByteIO):
            self.materials_offset = reader.read_uint64()
            self.entities_offset = reader.read_uint64()
            self.bsp_tree_offset = reader.read_uint64()
            self.lightmap_data_offset = reader.read_uint64()
            self.face_vertex_data_offset = reader.read_uint64()

        def to_file(self, writer: ByteIO):
            writer.write_uint64(self.materials_offset)
            writer.write_uint64(self.entities_offset)
            writer.write_uint64(self.bsp_tree_offset)
            writer.write_uint64(self.lightmap_data_offset)
            writer.write_uint64(self.face_vertex_data_offset)

    def __init__(self):
        PragmaBase.set_base(self)
        self.version = 0
        self.flags = DataFlags(0)
        self.offsets = self.Offsets()
        self.materials = []  # type:List[str]
        self.bsp_tree = BSPTree()
        self.entities = []  # type:List[Entity]

    def from_file(self, reader: ByteIO):
        reader.read_ascii_string(3)
        self.version = reader.read_int32()
        self.flags = DataFlags(reader.read_int64())
        self.offsets.from_file(reader)
        reader.seek(self.offsets.materials_offset)
        for _ in range(reader.read_uint32()):
            self.materials.append(reader.read_ascii_string())
        reader.seek(self.offsets.bsp_tree_offset)
        if self.flags.HasBSPTree:
            self.bsp_tree.from_file(reader)
            pass
        reader.seek(self.offsets.entities_offset)
        for _ in range(reader.read_uint32()):
            entity = Entity()
            entity.from_file(reader, 0)
            self.entities.append(entity)

    @staticmethod
    def check_header(reader: ByteIO):
        with reader.save_current_pos():
            header = reader.read_ascii_string(3)
            if header != "WLD":
                return False
            version = reader.read_uint16()
            if version < 10 or version > MAX_SUPPORTED_VERSION:
                return False
        return True
