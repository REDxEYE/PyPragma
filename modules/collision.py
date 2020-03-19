from enum import IntFlag
from typing import List

from . import PragmaVector3F, PragmaBase, PragmaConstraint, PragmaBone
from ..byte_io_wmd import ByteIO


class PragmaCollisionMeshFlags(IntFlag):
    NONE = 0
    SoftBody = 1
    Convex = SoftBody << 1


class PragmaCollisionMesh(PragmaBase):
    def __init__(self):
        self.flags = PragmaCollisionMeshFlags(0)
        self.parent_bone = None  # type:PragmaBone
        self.origin = PragmaVector3F()
        self.surface_materials = ""
        self.min_bounds = PragmaVector3F()
        self.max_bounds = PragmaVector3F()
        self.vertices = []
        self.indices = []
        self.volume = 0
        self.center_of_mass = PragmaVector3F()
        self.constraints = []  # type:List[PragmaConstraint]
        self.softbody_info = PragmaSoftBodyInfo(self)

    def from_file(self, reader: ByteIO):
        if self.model.version >= 30:
            self.flags = PragmaCollisionMeshFlags(reader.read_uint64())
        self.parent_bone = reader.read_int32()
        if self.parent_bone == -1:
            self.parent_bone = 0
        self.origin.from_file(reader)
        self.surface_materials = reader.read_ascii_string()
        self.min_bounds.from_file(reader)
        self.max_bounds.from_file(reader)
        vert_count = reader.read_uint64()
        for _ in range(vert_count):
            self.vertices.append(reader.read_fmt('3f'))
        index_count = reader.read_uint64()
        for _ in range(index_count // 3):
            self.indices.append(reader.read_fmt('3H'))
        self.volume = reader.read_double()
        self.center_of_mass.from_file(reader)
        constraint_count = reader.read_uint8()
        for _ in range(constraint_count):
            constraint = PragmaConstraint()
            constraint.from_file(reader)
            self.constraints.append(constraint)
        if self.model.version >= 20:
            self.softbody_info.from_file(reader)

    def to_file(self, writer: ByteIO):
        writer.write_uint64(self.flags.value)
        writer.write_int32(self.parent_bone)
        self.origin.to_file(writer)
        writer.write_ascii_string(self.surface_materials)
        self.min_bounds.to_file(writer)
        self.max_bounds.to_file(writer)
        writer.write_uint64(len(self.vertices))
        for v in self.vertices:
            writer.write_fmt('3f', *v)
        writer.write_uint64(len(self.indices) * 3)
        for v in self.indices:
            writer.write_fmt('3H', *v)

        writer.write_double(self.volume)
        self.center_of_mass.to_file(writer)

        writer.write_uint8(len(self.constraints))
        for constaint in self.constraints:
            constaint.to_file(writer)
        self.softbody_info.to_file(writer)


class PragmaSoftBodyInfo(PragmaBase):
    def __init__(self, collision_mesh: PragmaCollisionMesh):
        self._collision_mesh = collision_mesh
        pass

    def from_file(self, reader: ByteIO):
        if self.model.version < 30:
            softbody_data = reader.read_uint8() == 1
        else:
            softbody_data = (self._collision_mesh.flags & PragmaCollisionMeshFlags.SoftBody) != 0
        if softbody_data:
            raise NotImplementedError('SoftBody physics not yet implemented')
        else:
            return

    def to_file(self, writer: ByteIO):
        pass


class PragmaCollisionMeshInfo(PragmaBase):
    def __init__(self):
        self.mass = 0.0
        self.meshes = []  # type:List[PragmaCollisionMesh]

    def from_file(self, reader: ByteIO):
        self.mass = reader.read_float()
        if self.model.version < 30:
            mesh_count = reader.read_uint8()
        else:
            mesh_count = reader.read_uint32()
        for i in range(mesh_count):
            mesh = PragmaCollisionMesh()
            mesh.from_file(reader)
            self.meshes.append(mesh)

    def to_file(self, writer: ByteIO):
        writer.write_float(self.mass)
        writer.write_uint32(len(self.meshes))
        for mesh in self.meshes:
            mesh.to_file(writer)
