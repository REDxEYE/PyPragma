from typing import List

from . import *
from .vector import *


class PragmaBone(PragmaBase):
    def __init__(self, armature, name="ERROR"):
        self._armature = armature  # type:PragmaArmature
        self.name = name
        self.position = PragmaVector3F()
        self.rotation = PragmaVector4F()
        self.childs = []  # type: List[PragmaBone]
        self.parent = None  # type: PragmaBone

    def from_file(self, reader: ByteIO):
        self.rotation.from_file(reader)
        self.position.from_file(reader)

    def read_childs(self, reader: ByteIO):
        child_count = reader.read_uint32()
        for _ in range(child_count):
            child = self._armature.bones[reader.read_uint32()]  # type: PragmaBone
            child.parent = self
            self.childs.append(child)
            child.read_childs(reader)

    def write_childs(self, writer: ByteIO):
        writer.write_uint32(len(self.childs))
        for child in self.childs:
            writer.write_uint32(self._armature.bones.index(child))
            child.write_childs(writer)

    def __str__(self):
        tmp = f'"{self.name}"'
        return f"{self.__class__.__name__}({tmp})<pos:{self.position} rot:{self.rotation}>"

    def to_file(self, writer):
        self.rotation.to_file(writer)
        self.position.to_file(writer)
        pass


class PragmaArmature(PragmaBase):
    def __init__(self):
        self.bones = []  # type: List[PragmaBone]
        self.roots = []  # type: List[PragmaBone]
        self._bone_names = []  # type: List[str]

    def from_file(self, reader: ByteIO):
        bone_count = reader.read_uint32()
        for _ in range(bone_count):
            self._bone_names.append(reader.read_ascii_string())
        for i in range(bone_count):
            bone = PragmaBone(self, self._bone_names[i])
            bone.from_file(reader)
            self.bones.append(bone)

        root_bone_count = reader.read_uint32()
        for _ in range(root_bone_count):
            root_bone = self.bones[reader.read_uint32()]
            root_bone.read_childs(reader)
            self.roots.append(root_bone)

        pass

    def to_file(self, writer: ByteIO):
        writer.write_uint32(len(self.bones))
        for bone in self.bones:
            writer.write_ascii_string(bone.name, True)
        for bone in self.bones:
            bone.to_file(writer)
        writer.write_uint32(len(self.roots))
        for root in self.roots:
            writer.write_uint32(self.bones.index(root))
            root.write_childs(writer)
