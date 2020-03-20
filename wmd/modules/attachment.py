from enum import IntEnum

from . import *
from PyWMD.byte_io_wmd import ByteIO


class PragmaObjectAttachmentType(IntEnum):
    Model = 0
    ParticleSystem = 1


class PragmaObjectAttachment(PragmaBase):
    def __init__(self):
        self.type = PragmaObjectAttachmentType(0)
        self.name = ''
        self.attachment = ''
        self.key_values = {}

    def from_file(self, reader: ByteIO):
        self.type = PragmaObjectAttachmentType(reader.read_uint32())
        self.name = reader.read_ascii_string()
        self.attachment = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            key = reader.read_ascii_string()
            self.key_values[key] = reader.read_ascii_string()

    def to_file(self, writer: ByteIO):
        writer.write_uint32(self.type.value)
        writer.write_ascii_string(self.name)
        writer.write_ascii_string(self.attachment)
        writer.write_uint32(len(self.key_values))
        for k, v in self.key_values.items():
            writer.write_ascii_string(k)
            writer.write_ascii_string(v)

    def __str__(self):
        tmp = f'"{self.name}"'
        tmp2 = f'"{self.attachment}"'
        return f"{self.__class__.__name__}({tmp})<attachment:{tmp2} type:{self.type.name}>"


class PragmaAttachment(PragmaBase):
    def __init__(self, armature):
        self._armature = armature
        self.name = ''
        self.bone = None  # type: PragmaBone
        self.offset = PragmaVector3F()
        self.angles = PragmaVector3F()

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.bone = self._armature.bones[reader.read_uint32()]
        self.offset.from_file(reader)
        self.angles.from_file(reader)

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_uint32(self._armature.bones.index(self.bone))
        self.offset.to_file(writer)
        self.angles.to_file(writer)

    def __str__(self):
        tmp = f'"{self.name}"'
        tmp2 = f'"{self.bone.name}"'
        return f"{self.__class__.__name__}({tmp})<parent:{tmp2} offset:{self.offset} rot:{self.angles}>"
