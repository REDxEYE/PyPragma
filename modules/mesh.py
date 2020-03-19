from enum import IntEnum
from typing import List, Dict

from . import *
from ..byte_io_wmd import ByteIO


class PragmaSubMeshGeometryType(IntEnum):
    Triangles = 0
    Lines = 1
    Points = 2


class PragmaSubMesh(PragmaBase):
    def __init__(self):
        self.pos = PragmaVector3F()
        self.rot = PragmaVector4F()
        self.scale = PragmaVector3F()

        self.material_id = 0

        self.geometry_type = PragmaSubMeshGeometryType(0)

        self.vertices = []
        self.normals = []
        self.uv_sets = {}
        self.weights = []
        self.additional_weights = []
        self.alpha_count = 0
        self.alphas = []  # type:List[PragmaVector2F]
        self.indices = []
        self.flexes = {}

    def from_file(self, reader: ByteIO):
        if self.model.version >= 26:
            self.pos.from_file(reader)
            self.rot.from_file(reader)
            self.scale.from_file(reader)
        self.material_id = reader.read_uint16()
        if self.model.version >= 27:
            self.geometry_type = PragmaSubMeshGeometryType(reader.read_uint8())

        vertex_count = reader.read_uint64()
        if self.model.version < 30:
            self.uv_sets["base"] = []
        for _ in range(vertex_count):
            self.vertices.append(reader.read_fmt("3f"))
            self.normals.append(reader.read_fmt("3f"))
            if self.model.version < 30:
                self.uv_sets["base"].append(reader.read_fmt("2f"))

        if self.model.version >= 30:
            uv_set_count = reader.read_uint8()
            for _ in range(uv_set_count):
                uv_set_name = reader.read_ascii_string()
                self.uv_sets[uv_set_name] = []
                for _ in range(vertex_count):
                    self.uv_sets[uv_set_name].append(reader.read_fmt("2f"))

        weight_count = reader.read_uint64()
        for _ in range(weight_count):
            self.weights.append((reader.read_fmt('4i'), reader.read_fmt('4f')))

        if self.model.version >= 27:
            weight_count = reader.read_uint64()
            for _ in range(weight_count):
                self.additional_weights.append((reader.read_fmt('4i'), reader.read_fmt('4f')))

        if self.model.version >= 30:
            self.alpha_count = reader.read_uint8()
            if self.alpha_count > 0:
                for _ in range(vertex_count):
                    alpha = PragmaVector2F()
                    alpha.x = reader.read_float()
                    if self.alpha_count > 1:
                        alpha.y = reader.read_float()
                    self.alphas.append(alpha)

        indices_count = reader.read_uint32()
        if self.model.version < 30:
            indices_count *= 3
        for _ in range(indices_count):
            self.indices.append(reader.read_fmt('1H'))

    def to_file(self, writer: ByteIO):
        self.pos.to_file(writer)
        self.rot.to_file(writer)
        self.scale.to_file(writer)

        writer.write_uint16(self.material_id)
        writer.write_uint8(self.geometry_type.value)

        writer.write_uint64(len(self.vertices))
        for v, n in zip(self.vertices, self.normals):
            writer.write_fmt('3f', *v)
            writer.write_fmt('3f', *n)

        writer.write_uint8(len(self.uv_sets))
        for uv_set_name, uv_set in self.uv_sets.items():
            writer.write_ascii_string(uv_set_name)
            for u in uv_set:
                writer.write_fmt("2f", *u)

        writer.write_uint64(len(self.weights))
        for (b, w) in self.weights:
            writer.write_fmt('4i', *b)
            writer.write_fmt('4f', *w)

        writer.write_uint64(len(self.additional_weights))
        for (b, w) in self.additional_weights:
            writer.write_fmt('4i', *b)
            writer.write_fmt('4f', *w)

        writer.write_uint8(self.alpha_count)
        if self.alphas:
            for alpha in self.alphas:
                writer.write_float(alpha.x)
                if self.alpha_count > 1:
                    writer.write_float(alpha.y)

        writer.write_uint32(len(self.indices))
        for ind in self.indices:
            writer.write_fmt('H', *ind)


class PragmaMeshV24Plus(PragmaBase):
    def __init__(self):
        self.name = ''
        self.meshes = []  # type:List[List[PragmaSubMesh]]
        self.sub_meshes = []  # type: List[PragmaSubMesh]

    def __repr__(self):
        return f"Mesh<{self.name}>(sub meshes:{len(self.sub_meshes)})"

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        if self.model.version < 30:
            mesh_count = reader.read_uint8()
        else:
            mesh_count = reader.read_uint32()
        for _ in range(mesh_count):
            meshes = []
            if self.model.version <= 23:
                pass  # TODO
            else:
                sub_mesh_count = reader.read_uint32()
                for _ in range(sub_mesh_count):
                    sub_mesh = PragmaSubMesh()
                    sub_mesh.from_file(reader)
                    self.sub_meshes.append(sub_mesh)
                    meshes.append(sub_mesh)
            self.meshes.append(meshes)

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_uint32(len(self.meshes))
        for mesh in self.meshes:
            writer.write_uint32(len(mesh))
            for sub_mesh in mesh:
                sub_mesh.to_file(writer)


class PragmaMeshGroup(PragmaBase):
    def __init__(self):
        self.rb_min = PragmaVector3F()
        self.rb_max = PragmaVector3F()

        self.mesh_groups = []  # type:List[PragmaMeshV24Plus]
        self.bodygroups = {}  # type: Dict[str,List[PragmaMeshV24Plus]]

        self.group_ids = []

    def from_file(self, reader: ByteIO):
        self.rb_min.from_file(reader)
        self.rb_max.from_file(reader)
        mesh_group_count = reader.read_uint32()
        for _ in range(mesh_group_count):
            mesh = PragmaMeshV24Plus()
            mesh.from_file(reader)
            self.mesh_groups.append(mesh)
            pass

        base_mesh_count = reader.read_uint16()
        for i in range(base_mesh_count):
            self.group_ids.append(reader.read_uint32())

    def to_file(self, writer: ByteIO):
        self.rb_min.to_file(writer)
        self.rb_max.to_file(writer)
        writer.write_uint32(len(self.mesh_groups))
        for mesh_group in self.mesh_groups:
            mesh_group.to_file(writer)

        writer.write_uint16(len(self.group_ids))
        for group_id in self.group_ids:
            writer.write_uint32(group_id)

    def read_bodygroups(self, reader: ByteIO):
        bodygroup_count = reader.read_uint16()
        for _ in range(bodygroup_count):
            name = reader.read_ascii_string()
            self.bodygroups[name] = []
            mesh_count = reader.read_uint8()
            for _ in range(mesh_count):
                self.bodygroups[name].append(self.mesh_groups[reader.read_uint32()])

    def write_bodygroups(self, writer: ByteIO):
        writer.write_uint16(len(self.bodygroups))
        for name, bodygroup in self.bodygroups.items():
            writer.write_ascii_string(name)
            writer.write_uint8(len(bodygroup))
            for body in bodygroup:
                writer.write_uint32(self.mesh_groups.index(body))
