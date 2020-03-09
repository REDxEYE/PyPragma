from typing import List, Tuple

from .. import PragmaBase, PragmaArmatureAnimation, PragmaVertexAnimation, PragmaFlexInfo, PragmaPhoneme
from ...byte_io_wmd import ByteIO

class PragmaEyeball(PragmaBase):
    def __init__(self):
        self.name = ''
        self.bone_index = -1
        self.origin = PragmaVector3F()
        self.zOffset = 0.0
        self.radius = 0.0
        self.up = PragmaVector3F()
        self.forward = PragmaVector3F()
        self.irisMaterialIndex = -1
        self.maxDilationFactor = 1.0
        self.irisUvRadius = 0.2
        self.irisScale = 0.0
        self.upperFlexDesc = [0,0,0]
        self.lowerFlexDesc = [0,0,0]
        self.upperTarget = [0.0,0.0,0.0]
        self.lowerTarget = [0.0,0.0,0.0]
        self.upperLidFlexDesc = -1
        self.lowerLidFlexDesc = -1

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.bone_index = reader.read_int32()
        self.origin.from_file(reader)
        self.zOffset = reader.read_float()
        self.radius = reader.read_float()
        self.up.from_file(reader)
        self.forward.from_file(reader)
        self.irisMaterialIndex = reader.read_int32()
        self.maxDilationFactor = reader.read_float()
        self.irisUvRadius = reader.read_float()
        self.irisScale = reader.read_float()
        self.upperFlexDesc = [reader.read_int32(),reader.read_int32(),reader.read_int32()]
        self.lowerFlexDesc = [reader.read_int32(),reader.read_int32(),reader.read_int32()]
        self.upperTarget = [reader.read_float(),reader.read_float(),reader.read_float()]
        self.lowerTarget = [reader.read_float(),reader.read_float(),reader.read_float()]
        self.upperLidFlexDesc = reader.read_int32()
        self.lowerLidFlexDesc = reader.read_int32()

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_int32(self.bone_index)
        self.origin.to_file(writer)
        writer.write_float(self.zOffset)
        writer.write_float(self.radius)
        self.up.to_file(writer)
        self.forward.to_file(writer)
        writer.write_int32(self.irisMaterialIndex)
        writer.write_float(self.maxDilationFactor)
        writer.write_float(self.irisUvRadius)
        writer.write_float(self.irisScale)
        writer.write_int32(self.upperFlexDesc[0])
        writer.write_int32(self.upperFlexDesc[1])
        writer.write_int32(self.upperFlexDesc[2])
        writer.write_int32(self.lowerFlexDesc[0])
        writer.write_int32(self.lowerFlexDesc[1])
        writer.write_int32(self.lowerFlexDesc[2])
        writer.write_float(self.upperTarget[0])
        writer.write_float(self.upperTarget[1])
        writer.write_float(self.upperTarget[2])
        writer.write_float(self.lowerTarget[0])
        writer.write_float(self.lowerTarget[1])
        writer.write_float(self.lowerTarget[2])
        writer.write_int32(self.upperLidFlexDesc)
        writer.write_int32(self.lowerLidFlexDesc)

class PragmaAnimationInfo(PragmaBase):
    def __init__(self):
        self.armature_animations = []  # type:List[PragmaArmatureAnimation]
        self.vertex_animations = []  # type:List[PragmaVertexAnimation]
        self.flex_controllers = []  # type:List[Tuple[str,float,float]] # name,min,max
        self.flex_infos = []  # type:List[PragmaFlexInfo]
        self.phonemes = []  # type:List[PragmaPhoneme]
        self.eyeballs = [] # type: List[PragmaEyeball]
        self.maxEyeDeflection = 30.0 # Degree

    def from_file(self, mdl, reader: ByteIO):
        armature_animation_count = reader.read_uint32()
        for _ in range(armature_animation_count):
            arm_anim = PragmaArmatureAnimation()
            arm_anim.from_file(mdl,reader)
            self.armature_animations.append(arm_anim)
        if self.model.version >= 21:
            vertex_anim_count = reader.read_uint32()
            for _ in range(vertex_anim_count):
                vert_anim = PragmaVertexAnimation()
                vert_anim.from_file(reader)
                self.vertex_animations.append(vert_anim)

            for _ in range(reader.read_uint32()):
                self.flex_controllers.append((reader.read_ascii_string(), reader.read_float(), reader.read_float()))

            for _ in range(reader.read_uint32()):
                flex_info = PragmaFlexInfo()
                flex_info.from_file(reader)
                self.flex_infos.append(flex_info)

            for _ in range(reader.read_uint32()):
                phoneme = PragmaPhoneme()
                phoneme.from_file(reader)
                self.phonemes.append(phoneme)

            if self.model.version >= 28:
                self.maxEyeDeflection = reader.read_float()
                for _ in range(reader.read_uint32()):
                    eyeball = PragmaEyeball()
                    eyeball.from_file(reader)
                    self.eyeballs.append(eyeball)

    def to_file(self, writer: ByteIO):
        writer.write_uint32(len(self.armature_animations))
        for arm_anim in self.armature_animations:
            arm_anim.to_file(writer)

        vert_anim_offset = writer.tell()
        with writer.save_current_pos():
            writer.seek(self.model.skinned_data_offset + 16)
            writer.write_uint64(vert_anim_offset)

        writer.write_uint32(len(self.vertex_animations))
        for vert_anim in self.vertex_animations:
            vert_anim.to_file(writer)

        flex_controllers_offset = writer.tell()
        with writer.save_current_pos():
            writer.seek(self.model.skinned_data_offset + 24)
            writer.write_uint64(flex_controllers_offset)

        writer.write_uint32(len(self.flex_controllers))
        for flex, a, b in self.flex_controllers:
            writer.write_ascii_string(flex)
            writer.write_fmt('ff', a, b)

        flex_infos_offset = writer.tell()
        with writer.save_current_pos():
            writer.seek(self.model.skinned_data_offset + 32)
            writer.write_uint64(flex_infos_offset)

        writer.write_uint32(len(self.flex_infos))
        for info in self.flex_infos:
            info.to_file(writer)

        phonemes_offset = writer.tell()
        with writer.save_current_pos():
            writer.seek(self.model.skinned_data_offset + 40)
            writer.write_uint64(phonemes_offset)

        writer.write_uint32(len(self.phonemes))
        for phoneme in self.phonemes:
            phoneme.to_file(writer)

        writer.write_float(self.maxEyeDeflection)
        writer.write_uint32(len(self.eyeballs))
        for eyeball in self.eyeballs:
            eyeball.to_file(writer)
