from enum import IntFlag, auto, IntEnum
from typing import List, Dict, Tuple
from .modules import *

from .byte_io_wmd import ByteIO


class PragmaModelFlags(IntFlag):
    NONE = 0
    Static = auto()
    Inanimate = auto()
    Unused1 = auto()
    Unused2 = auto()
    Unused3 = auto()
    Unused4 = auto()
    Unused5 = auto()
    DontPrecacheTextureGroups = auto()

class PragmaModel(PragmaBase):
    def __init__(self):
        PragmaBase.set_model(self)
        self.name = ""
        self.version = 0
        self.flags = PragmaModelFlags(0)
        self.eye_offset = PragmaVector3F()

        self.offset_model_data = 0
        self.offset_meshes = 0
        self.offset_lod_data = 0
        self.offset_bodygroups = 0
        self.offset_collision_mesh = 0

        self.offset_bones = 0
        self.offset_animations = 0
        self.offset_vertex_animations = 0
        self.offset_flex_controllers = 0
        self.offset_flexes = 0
        self.offset_phoneme_map = 0
        self.index_offset_ik_controllers = 0
        self.index_offset_eyeballs = 0

        self.material_paths = []
        self.materials = []
        self.skins = []

        self.armature = PragmaArmature()

        self.attachments = []  # type: List[PragmaAttachment]
        self.object_attachments = []  # type: List[PragmaObjectAttachment]
        self.hitboxes = []  # type: List[PragmaHitBox]

        self.mesh = PragmaMeshGroup()
        self.lod_info = PragmaLodInfo()
        self.collision_mesh = PragmaCollisionMeshInfo()

        self.blend_controllers = []  # type:List[PragmaBlendController]
        self.ik_controllers = []  # type:List[PragmaIKController]
        self.animation_info = PragmaAnimationInfo()

        self.offsets_offset = 0
        self.skinned_data_offset = 0

        self.include_models = []  # type:List[str]

    @property
    def static(self):
        return bool(self.flags & PragmaModelFlags.Static)

    @property
    def skinned(self):
        return not self.static

    def from_file(self, reader: ByteIO):
        header = reader.read_ascii_string(3)
        assert header == 'WMD', "invalid header"
        self.version = reader.read_uint16()
        self.flags = PragmaModelFlags(reader.read_uint32())
        self.eye_offset.from_file(reader)

        self.offset_model_data = reader.read_uint64()
        self.offset_meshes = reader.read_uint64()
        self.offset_lod_data = reader.read_uint64()
        self.offset_bodygroups = reader.read_uint64()
        self.offset_collision_mesh = reader.read_uint64()

        if self.skinned:
            self.offset_bones = reader.read_uint64()
            self.offset_animations = reader.read_uint64()
            if self.version >= 21:
                self.offset_vertex_animations = reader.read_uint64()
                self.offset_flex_controllers = reader.read_uint64()
                self.offset_flexes = reader.read_uint64()
                self.offset_phoneme_map = reader.read_uint64()
            if self.version >= 22:
                self.index_offset_ik_controllers = reader.read_uint64()
            if self.version >= 28:
                self.index_offset_eyeballs = reader.read_uint64()

        material_path_count = reader.read_uint8()
        for i in range(material_path_count):
            self.material_paths.append(reader.read_ascii_string())

        # armature and attachments
        if self.skinned:
            self.armature.from_file(reader)

            attachment_count = reader.read_uint32()
            for _ in range(attachment_count):
                attachment = PragmaAttachment(self.armature)
                attachment.from_file(reader)
                self.attachments.append(attachment)

            if self.version >= 23:
                object_attachment_count = reader.read_uint32()
                for _ in range(object_attachment_count):
                    object_attachment = PragmaObjectAttachment()
                    object_attachment.from_file(reader)
                    self.object_attachments.append(object_attachment)
            hitbox_count = reader.read_uint32()
            for _ in range(hitbox_count):
                hitbox = PragmaHitBox(self.armature)
                hitbox.from_file(reader)
                self.hitboxes.append(hitbox)

        base_material_count = reader.read_uint16()
        material_count = reader.read_uint16()
        for _ in range(material_count):
            self.materials.append(reader.read_ascii_string())

        for skin_id in range(reader.read_int16()):
            skin = []
            for _ in range(base_material_count):
                skin.append(self.materials[reader.read_uint16()])
            self.skins.append(skin)

        self.mesh.from_file(reader)
        self.lod_info.from_file(reader)
        self.mesh.read_bodygroups(reader)
        self.collision_mesh.from_file(reader)

        if self.skinned:
            blend_controllers_count = reader.read_uint16()
            for _ in range(blend_controllers_count):
                controller = PragmaBlendController()
                controller.from_file(reader)
                self.blend_controllers.append(controller)
            if self.version >= 22:
                ik_controllers_count = reader.read_uint32()
                for _ in range(ik_controllers_count):
                    ik_controller = PragmaIKController()
                    ik_controller.from_file(reader)
                    self.ik_controllers.append(ik_controller)

            self.animation_info.from_file(self,reader)
        for _ in range(reader.read_uint8()):
            self.include_models.append(reader.read_ascii_string())

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string("WMD", False)
        writer.write_uint16(29)  # version
        writer.write_uint32(self.flags.value)
        self.eye_offset.to_file(writer)

        self.offsets_offset = offsets_offset = writer.tell()
        writer.write_uint64(0)
        writer.write_uint64(0)
        writer.write_uint64(0)
        writer.write_uint64(0)
        writer.write_uint64(0)

        self.skinned_data_offset = offsets_skinned_data = writer.tell()
        if self.skinned:
            writer.write_uint64(0)
            writer.write_uint64(0)

            writer.write_uint64(0)
            writer.write_uint64(0)
            writer.write_uint64(0)
            writer.write_uint64(0)

            writer.write_uint64(0)

        with writer.save_current_pos():
            model_data_offset = writer.tell()
            writer.seek(offsets_offset)
            writer.write_uint64(model_data_offset)

        writer.write_int8(len(self.material_paths))
        for path in self.material_paths:
            writer.write_ascii_string(path, True)

        if self.skinned:
            with writer.save_current_pos():
                armature_offset = writer.tell()
                writer.seek(offsets_skinned_data)
                writer.write_uint64(armature_offset)
            self.armature.to_file(writer)

            writer.write_uint32(len(self.attachments))
            for attachment in self.attachments:
                attachment.to_file(writer)

            writer.write_uint32(len(self.object_attachments))
            for attachment in self.object_attachments:
                attachment.to_file(writer)

            writer.write_uint32(len(self.hitboxes))
            for hitbox in self.hitboxes:
                hitbox.to_file(writer)

            writer.write_uint16(len(self.skins[0]))
            writer.write_uint16(len(self.materials))
            for material in self.materials:
                writer.write_ascii_string(material)

            writer.write_uint16(len(self.skins))
            for skin in self.skins:
                for mat in skin:
                    writer.write_uint16(self.materials.index(mat))

            mesh_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_offset + 8)
                writer.write_uint64(mesh_offset)
                # writer.write_uint64(0)

            self.mesh.to_file(writer)

            lod_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_offset + 16)
                writer.write_uint64(lod_offset)

            self.lod_info.to_file(writer)

            bodygroups_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_offset + 24)
                writer.write_uint64(bodygroups_offset)
            self.mesh.write_bodygroups(writer)

            collision_mesh_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_offset + 32)
                writer.write_uint64(collision_mesh_offset)

            self.collision_mesh.to_file(writer)

            writer.write_uint16(len(self.blend_controllers))
            for blend in self.blend_controllers:
                blend.to_file(writer)

            ik_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_skinned_data + 48)
                writer.write_uint64(ik_offset)

            writer.write_uint32(len(self.ik_controllers))
            for ik in self.ik_controllers:
                ik.to_file(writer)

            animations_offset = writer.tell()
            with writer.save_current_pos():
                writer.seek(offsets_skinned_data + 8)
                writer.write_uint64(animations_offset)

            self.animation_info.to_file(writer)

        writer.write_uint8(len(self.include_models))
        for s in self.include_models:
            writer.write_ascii_string(s)

    @staticmethod
    def check_header(reader: ByteIO):
        with reader.save_current_pos():
            header = reader.read_ascii_string(3)
            if header != "WMD":
                return False
            version = reader.read_uint16()
            if version < 20 or version > 27:
                return False
        return True

    def __str__(self):
        return f"{self.__class__.__name__}<{'static' if self.static else 'skinned'}>"

    def set_name(self, name):
        self.name = name
