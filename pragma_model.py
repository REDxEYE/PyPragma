from enum import IntFlag, auto, IntEnum
from typing import List

from byte_io_wmd import ByteIO
from shared import PragmaVector3F, PragmaVector4F


class PragmaModelFlags(IntFlag):
    NONE = auto()
    Static = auto()
    Inanimate = auto()
    Unused1 = auto()
    Unused2 = auto()
    Unused3 = auto()
    Unused4 = auto()
    Unused5 = auto()
    DontPrecacheTextureGroups = auto()


class PragmaBone:
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

    def __str__(self):
        tmp = f'"{self.name}"'
        return f"{self.__class__.__name__}({tmp})<pos:{self.position} rot:{self.rotation}>"


class PragmaArmature:
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


class PragmaAttachment:
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

    def __str__(self):
        tmp = f'"{self.name}"'
        tmp2 = f'"{self.bone.name}"'
        return f"{self.__class__.__name__}({tmp})<parent:{tmp2} offset:{self.offset} rot:{self.angles}>"


class PragmaObjectAttachmentType(IntEnum):
    Model = 0
    ParticleSystem = 1


class PragmaObjectAttachment:
    def __init__(self):
        self.type = 0
        self.name = ''
        self.attachment = ''
        self.key_values = {}

    def from_file(self, reader: ByteIO):
        self.type = PragmaObjectAttachmentType(reader.read_uint32())
        self.name = reader.read_ascii_string()
        self.attachment = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            self.key_values[reader.read_ascii_string()] = reader.read_ascii_string()

    def __str__(self):
        tmp = f'"{self.name}"'
        tmp2 = f'"{self.attachment}"'
        return f"{self.__class__.__name__}({tmp})<attachment:{tmp2} type:{self.type.name}>"


class PragmaHitBox:
    def __init__(self, armature):
        self._armature = armature
        self.bone = None
        self.group = 0
        self.min = PragmaVector3F()
        self.max = PragmaVector3F()

    def from_file(self, reader: ByteIO):
        self.bone = self._armature.bones[reader.read_uint32()]
        self.group = reader.read_uint32()
        self.min.from_file(reader)
        self.max.from_file(reader)


class PragmaModel:
    def __init__(self):
        self.version = 0
        self.flags = PragmaModelFlags(0)
        self.eye_offset = PragmaVector3F()

        self.offset_model_data = 0
        self.offset_meshes = 0
        self.offset_lod_data = 0
        self.offset_bodygroups = 0
        self.offset_collision_mesh = 0

        self.material_paths = []
        self.materials = []

        self.armature = PragmaArmature()

        self.attachments = []  # type: List[PragmaAttachment]
        self.object_attachments = []  # type: List[PragmaObjectAttachment]
        self.hitboxes = []  # type: List[PragmaHitBox]

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
            reader.skip(8 * 2)
            if self.version >= 21:
                reader.skip(8 * 4)
            if self.version >= 22:
                reader.skip(8 * 1)

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


    @staticmethod
    def check_header(reader: ByteIO):
        with reader.save_current_pos():
            header = reader.read_ascii_string(3)
            if header != "WMD":
                return False#, {"status": "ERROR", "msg": "invalid header"}
            version = reader.read_uint16()
            if version < 20:
                return False#, {"status": "ERROR", "msg": "invalid version(min supported 20)"}
        return True#, {"status": "OK", "msg": "no errors"}

    def __str__(self):
        return f"{self.__class__.__name__}<{'static' if self.static else 'skinned'}>"
