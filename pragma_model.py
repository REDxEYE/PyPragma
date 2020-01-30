from enum import IntFlag, auto

from byte_io_wmd import ByteIO
from shared import Vector3F, Vector4F


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
    def __init__(self):
        self.position = Vector3F()
        self.rotation = Vector4F()

    def from_file(self,reader:ByteIO):
        self.rotation.from_file(reader)
        self.position.from_file(reader)


class PragmaArmature:
    def __init__(self):
        self.bones = []

    def from_file(self, reader: ByteIO):
        bone_count = reader.read_uint32()
        pass


class PragmaModel:
    def __init__(self):
        self.version = 0
        self.flags = PragmaModelFlags(0)
        self.eye_offset = Vector3F()

        self.offset_model_data = 0
        self.offset_meshes = 0
        self.offset_lod_data = 0
        self.offset_bodygroups = 0
        self.offset_collision_mesh = 0

        self.material_paths = []

        self.armature = PragmaArmature()

    @property
    def static(self):
        return self.flags & PragmaModelFlags.Static

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

        if self.skinned:
            self.armature.from_file(reader)
        pass

    @staticmethod
    def check_header(reader: ByteIO):
        with reader.save_current_pos():
            header = reader.read_ascii_string(3)
            if header != "WMD":
                return False, {"status": "ERROR", "msg": "invalid header"}
            version = reader.read_uint16()
            if version < 20:
                return False, {"status": "ERROR", "msg": "invalid version(min supported 20)"}
        return True, {"status": "OK", "msg": "no errors"}

    def __str__(self):
        return f"{self.__class__.__name__}<{'static' if self.static else 'skinned'}>"
