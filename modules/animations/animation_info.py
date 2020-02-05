from typing import List, Tuple

from .. import PragmaBase, PragmaArmatureAnimation, PragmaVertexAnimation, PragmaFlexInfo, PragmaPhoneme
from ...byte_io_wmd import ByteIO


class PragmaAnimationInfo(PragmaBase):
    def __init__(self):
        self.armature_animations = []  # type:List[PragmaArmatureAnimation]
        self.vertex_animations = []  # type:List[PragmaVertexAnimation]
        self.flex_controllers = []  # type:List[Tuple[str,float,float]] # name,min,max
        self.flex_infos = []  # type:List[PragmaFlexInfo]
        self.phonemes = []  # type:List[PragmaPhoneme]

    def from_file(self, reader: ByteIO):
        armature_animation_count = reader.read_uint32()
        for _ in range(armature_animation_count):
            arm_anim = PragmaArmatureAnimation()
            arm_anim.from_file(reader)
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

    def to_file(self, writer: ByteIO):
        writer.write_uint32(len(self.armature_animations))
        for arm_anim in self.armature_animations:
            arm_anim.to_file(writer)

        writer.write_uint32(len(self.vertex_animations))
        for vert_anim in self.vertex_animations:
            vert_anim.to_file(writer)