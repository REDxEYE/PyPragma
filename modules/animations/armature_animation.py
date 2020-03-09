from enum import IntFlag
from typing import List, Dict, Tuple

from .. import PragmaBase, PragmaVector2F, PragmaVector3F, PragmaVector4F
from ...byte_io_wmd import ByteIO


class PragmaBlendController(PragmaBase):
    def __init__(self):
        self.name = ''
        self.min = 0
        self.max = 0
        self.loop = False

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.min, self.max = reader.read_fmt('ii')
        self.loop = reader.read_uint8() == 1

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_fmt('ii', self.min, self.max)
        writer.write_uint8(self.loop)


class PragmaArmatureAnimationsFlags(IntFlag):
    NONE = 0
    Loop = 1
    NoRepeat = 2
    MoveX = 32
    MoveZ = 64
    Autoplay = 128
    Gesture = 256
    NoMoveBlend = 512


class PragmaArmatureAnimationFrame(PragmaBase):
    def __init__(self, anim: 'PragmaArmatureAnimation'):
        self._anim = anim
        self.pos = []  # type:List[PragmaVector3F]
        self.rot = []  # type:List[PragmaVector4F]
        self.events = {}  # type: Dict[str,List[str]]
        self.move = PragmaVector2F()

    def from_file(self, reader: ByteIO):
        for _ in self._anim.bones:
            pos = PragmaVector3F()
            pos.from_file(reader)
            quat = PragmaVector4F()
            quat.from_file(reader)
            self.pos.append(pos)
            self.rot.append(quat)
        for _ in range(reader.read_uint16()):
            name = reader.read_ascii_string()
            params = []
            for _ in range(reader.read_uint8()):
                params.append(reader.read_ascii_string())
            self.events[name] = params
        if self._anim.flags & PragmaArmatureAnimationsFlags.MoveX:
            self.move.x = reader.read_float()
        if self._anim.flags & PragmaArmatureAnimationsFlags.MoveZ:
            self.move.z = reader.read_float()

    def to_file(self, writer: ByteIO):
        for bone_id in range(len(self._anim.bones)):
            self.pos[bone_id].to_file(writer)
            self.rot[bone_id].to_file(writer)
        writer.write_uint16(len(self.events))
        for event_name, params in self.events.items():
            writer.write_ascii_string(event_name)
            writer.write_uint8(len(params))
            for param in params:
                writer.write_ascii_string(param)
        if self._anim.flags & PragmaArmatureAnimationsFlags.MoveX:
            writer.write_float(self.move.x)
        if self._anim.flags & PragmaArmatureAnimationsFlags.MoveZ:
            writer.write_float(self.move.z)


class PragmaArmatureAnimation(PragmaBase):
    def __init__(self):
        self.name = ""
        self.activity_name = ""
        self.activity_weight = ""
        self.flags = PragmaArmatureAnimationsFlags(0)
        self.fps = 0
        self.min = PragmaVector3F()
        self.max = PragmaVector3F()
        self.fade_in = False
        self.fade_in_time = 0.0
        self.fade_out = False
        self.fade_out_time = 0.0
        self.bones = []
        self.weights = []
        self.controller = PragmaBlendController()  # type:PragmaBlendController
        self.transitions = []  # type: List[Tuple[int,int]] #animationId,transition
        self.animation_post_blend_controller = -1
        self.animation_post_blend_target = -1

        self.frames = []  # type: List[PragmaArmatureAnimationFrame]

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.activity_name = reader.read_ascii_string()
        self.activity_weight = reader.read_uint8()
        self.flags = reader.read_uint32()
        self.fps = reader.read_uint32()
        self.min.from_file(reader)
        self.max.from_file(reader)
        self.fade_in = reader.read_uint8() == 1
        if self.fade_in:
            self.fade_in_time = reader.read_float()
        self.fade_out = reader.read_uint8() == 1
        if self.fade_out:
            self.fade_out_time = reader.read_float()

        for _ in range(reader.read_uint32()):
            self.bones.append(reader.read_uint32())

        if reader.read_uint8() == 1:
            for _ in range(len(self.bones)):
                self.weights.append(reader.read_float())

        if reader.read_uint8() == 1:
            self.controller = self.model.blend_controllers[reader.read_uint32()]
            for _ in range(reader.read_uint32()):
                if self.model.version >= 29:
                    self.transitions.append(reader.read_float())
                else:
                    self.transitions.append(reader.read_fmt('Ii'))
            if self.model.version >= 29:
                self.animation_post_blend_controller = reader.read_int32()
                self.animation_post_blend_target = reader.read_int32()

        for _ in range(reader.read_uint32()):
            frame = PragmaArmatureAnimationFrame(self)
            frame.from_file(reader)
            self.frames.append(frame)

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_ascii_string(self.activity_name)
        writer.write_uint8(self.activity_weight)

        writer.write_uint32(self.flags)
        writer.write_uint32(self.fps)

        self.min.to_file(writer)
        self.max.to_file(writer)

        writer.write_uint8(self.fade_in)
        if self.fade_in:
            writer.write_float(self.fade_in_time)

        writer.write_uint8(self.fade_out)
        if self.fade_out:
            writer.write_float(self.fade_out_time)

        writer.write_uint32(len(self.bones))
        for w in self.bones:
            writer.write_uint32(w)

        writer.write_int8(len(self.weights) > 0)
        if self.weights:
            writer.write_uint32(len(self.weights))
            for w in self.weights:
                writer.write_float(w)

        writer.write_uint8(self.controller.name != '')
        if self.controller.name != '':
            writer.write_uint32(self.model.blend_controllers.index(self.controller))
            writer.write_uint32(len(self.transitions))
            for t in self.transitions:
                writer.write_float(t)
            writer.write_int32(self.animation_post_blend_controller)
            writer.write_int32(self.animation_post_blend_target)

        writer.write_uint32(len(self.frames))
        for frame in self.frames:
            frame.to_file(writer)

    @property
    def has_movement(self):
        return self.flags & PragmaArmatureAnimationsFlags.MoveX or self.flags & PragmaArmatureAnimationsFlags.MoveZ
