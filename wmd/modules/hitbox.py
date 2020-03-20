from . import *
from ...byte_io_wmd import ByteIO


class HitBox(PragmaBase):
    def __init__(self, armature):
        self._armature = armature
        self.bone = None
        self.group = 0
        self.min = Vector3F()
        self.max = Vector3F()

    def from_file(self, reader: ByteIO):
        self.bone = self._armature.bones[reader.read_uint32()]
        self.group = reader.read_uint32()
        self.min.from_file(reader)
        self.max.from_file(reader)

    def to_file(self, writer: ByteIO):
        writer.write_uint32(self._armature.bones.index(self.bone))
        writer.write_uint32(self.group)
        self.min.to_file(writer)
        self.max.to_file(writer)
