from enum import IntFlag
from typing import List

from .. import PragmaBase, SubMesh, Vector3HF
from PyPragma.byte_io_wmd import ByteIO


class VertexMeshAnimationFrameFlags(IntFlag):
    NONE = 0
    HasDeltaValues = 1


class VertexMeshAnimation(PragmaBase):
    def __init__(self):
        self.meshgroup_id = 0
        self.mesh_id = 0
        self.submesh_id = 0
        self.frames = []
        self.flags = []  # TODO: remove it
        self.target_submesh = SubMesh()

    def from_file(self, reader: ByteIO):
        self.meshgroup_id = reader.read_uint32()
        self.mesh_id = reader.read_uint32()
        self.submesh_id = reader.read_uint32()
        self.target_submesh = self.base.mesh.mesh_groups[self.meshgroup_id].meshes[self.mesh_id][self.submesh_id]

        for _ in range(reader.read_uint32()):
            flags = VertexMeshAnimationFrameFlags(0)
            if self.base.version >= 25:
                flags = VertexMeshAnimationFrameFlags(reader.read_uint8())
            self.flags.append(flags)
            verts = []
            for _ in range(reader.read_uint16()):
                idx = reader.read_uint16()
                v = Vector3HF()
                v.from_file(reader)
                delta = 0
                if flags & VertexMeshAnimationFrameFlags.HasDeltaValues:
                    delta = reader.read_uint16()
                verts.append((idx, v, delta))
            self.frames.append(verts)

        pass

    def to_file(self, writer: ByteIO):
        writer.write_fmt('III', self.meshgroup_id, self.mesh_id, self.submesh_id)
        writer.write_uint32(len(self.frames))
        for flag, frame in zip(self.flags, self.frames):
            writer.write_uint8(flag)
            writer.write_uint16(len(frame))
            for (idx, v, delta) in frame:
                writer.write_uint16(idx)
                v.to_file(writer)
                if flag & VertexMeshAnimationFrameFlags.HasDeltaValues:
                    writer.write_uint16(delta)


class VertexAnimation(PragmaBase):
    def __init__(self):
        self.name = ""
        self.mesh_animations = []  # type: List[VertexMeshAnimation]

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            mesh_anim = VertexMeshAnimation()
            mesh_anim.from_file(reader)
            mesh_anim.target_submesh.flexes[self.name] = mesh_anim
            self.mesh_animations.append(mesh_anim)

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_uint32(len(self.mesh_animations))
        for mesh_anim in self.mesh_animations:
            mesh_anim.to_file(writer)

    def __repr__(self):
        return f"VertexAnimation<{self.name}>(meshes:{len(self.mesh_animations)})"


class FlexInfo(PragmaBase):
    def __init__(self):
        self.name = ''
        self.vert_anim_ind = 0
        self.mesh_ind = 0
        self.frame_ind = 0
        self.ops = []  # type:List[Tuple[int,float]]

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.vert_anim_ind = reader.read_uint32()
        self.mesh_ind = reader.read_uint32()
        self.frame_ind = reader.read_uint32()
        for _ in range(reader.read_uint32()):
            self.ops.append((reader.read_uint32(), reader.read_float()))

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_uint32(self.vert_anim_ind)
        writer.write_uint32(self.mesh_ind)
        writer.write_uint32(self.frame_ind)
        writer.write_uint32(len(self.ops))
        for op in self.ops:
            writer.write_fmt('If', *op)

    def __repr__(self):
        return f"FlexInfo<{self.name}>(operators:{len(self.ops)})"


class Phoneme(PragmaBase):
    def __init__(self):
        self.name = ''
        self.flex_controllers = []

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            self.flex_controllers.append((reader.read_uint32(), reader.read_float()))

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_uint32(len(self.flex_controllers))
        for flex in self.flex_controllers:
            writer.write_fmt('If', *flex)

    def __repr__(self):
        return f"Phoneme<{self.name}>(flex controllers:{len(self.flex_controllers)})"
