import typing
from enum import IntFlag

from ...shared import PragmaBase, Vector3F
from ...byte_io_wmd import ByteIO


class EntityFlags(IntFlag):
    NONE = 0
    Clientside_only = 1


class Output(PragmaBase):
    def __init__(self):
        self.name = ""
        self.target = ""
        self.input = ""
        self.param = ""
        self.delay = 0.0
        self.times = 0

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.target = reader.read_ascii_string()
        self.input = reader.read_ascii_string()
        self.param = reader.read_ascii_string()
        self.delay = reader.read_float()
        self.times = reader.read_uint32()


class Entity(PragmaBase):
    global_map_index = 1

    @classmethod
    def next_map_index(cls):
        val = cls.global_map_index
        cls.global_map_index += 1
        return val

    def __init__(self):
        self.flags = EntityFlags(0)
        self.map_index = 0
        self.class_name = ""
        self.origin = Vector3F()
        self.kv = {}
        self.outputs = []
        self.components = []
        self.leaves = []
        pass

    def from_file(self, reader: ByteIO, flag_mask: EntityFlags):
        start_offset = reader.tell()
        end_offset = start_offset + reader.read_uint64()
        mesh_offset = reader.tell() + reader.read_uint64()

        leaves_offset = reader.tell() + reader.read_uint64()

        self.flags = EntityFlags(reader.read_uint64())

        if flag_mask != 0 and self.flags & flag_mask == 0:
            return
        self.map_index = self.next_map_index()
        self.class_name = reader.read_ascii_string()
        self.origin.from_file(reader)

        for _ in range(reader.read_uint32()):
            key = reader.read_ascii_string()
            self.kv[key] = reader.read_ascii_string()

        for _ in range(reader.read_uint32()):
            output = Output()
            output.from_file(reader)
            self.outputs.append(output)

        for _ in range(reader.read_uint32()):
            self.components.append(reader.read_ascii_string())

        for _ in range(reader.read_uint32()):
            self.leaves.append(reader.read_uint16())

        reader.seek(end_offset)
