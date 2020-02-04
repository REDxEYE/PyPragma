from enum import IntFlag, auto, IntEnum
from typing import List, Dict, Tuple

from .byte_io_wmd import ByteIO
from .shared import PragmaVector3F, PragmaVector4F, PragmaVector2F, PragmaVector3H, PragmaVector3HF


class PragmaBase:
    model = None

    @classmethod
    def set_model(cls, model: 'PragmaModel'):
        cls.model = model


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

    def __str__(self):
        tmp = f'"{self.name}"'
        return f"{self.__class__.__name__}({tmp})<pos:{self.position} rot:{self.rotation}>"


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


class PragmaAttachment(PragmaBase):
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


class PragmaObjectAttachment(PragmaBase):
    def __init__(self):
        self.type = PragmaObjectAttachmentType(0)
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


class PragmaHitBox(PragmaBase):
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
        self.uvs = []
        self.weights = []
        self.additional_weights = []
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
        for _ in range(vertex_count):
            self.vertices.append(reader.read_fmt("3f"))
            self.normals.append(reader.read_fmt("3f"))
            self.uvs.append(reader.read_fmt("2f"))

        weight_count = reader.read_uint64()
        for _ in range(weight_count):
            self.weights.append((reader.read_fmt('4i'), reader.read_fmt('4f')))

        if self.model.version >= 27:
            weight_count = reader.read_uint64()
            for _ in range(weight_count):
                self.additional_weights.append((reader.read_fmt('4i'), reader.read_fmt('4f')))
        indices_count = reader.read_uint32()
        for _ in range(indices_count):
            self.indices.append(reader.read_fmt('3H'))


class PragmaMeshV24Plus(PragmaBase):
    def __init__(self):
        self.name = ''
        self.meshes = []  # type:List[List[PragmaSubMesh]]
        self.sub_meshes = []  # type: List[PragmaSubMesh]

    def __repr__(self):
        return f"Mesh<{self.name}>(sub meshes:{len(self.sub_meshes)})"

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        mesh_count = reader.read_uint8()
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


class PragmaMeshGroup(PragmaBase):
    def __init__(self):
        self.rb_min = PragmaVector3F()
        self.rb_max = PragmaVector3F()

        self.mesh_groups = []  # type:List[PragmaMeshV24Plus]
        self.bodygroups = {}  # type: Dict[str,List[PragmaMeshV24Plus]]

        self.group_ids = {}

    def from_file(self, reader: ByteIO):
        self.rb_min.from_file(reader)
        self.rb_max.from_file(reader)
        mesh_group_count = reader.read_uint32()
        for mesh_group_id in range(mesh_group_count):
            mesh = PragmaMeshV24Plus()
            mesh.from_file(reader)
            self.mesh_groups.append(mesh)
            pass

        base_mesh_count = reader.read_uint16()
        for i in range(base_mesh_count):
            self.group_ids[i] = []
        for i in range(base_mesh_count):
            self.group_ids[i].append(reader.read_uint32())

    def read_bodygroups(self, reader: ByteIO):
        bodygroup_count = reader.read_uint16()
        for _ in range(bodygroup_count):
            name = reader.read_ascii_string()
            self.bodygroups[name] = []
            mesh_count = reader.read_uint8()
            for _ in range(mesh_count):
                self.bodygroups[name].append(self.mesh_groups[reader.read_uint32()])


class PragmaLodInfo(PragmaBase):
    def __init__(self):
        self.lods = {}

    def from_file(self, reader: ByteIO):
        lod_count = reader.read_uint8()
        for _ in range(lod_count):
            lod_id = reader.read_uint8()
            self.lods[lod_id] = []
            replace_count = reader.read_uint8()
            for i in range(replace_count):
                self.lods[lod_id].append(reader.read_fmt('ii'))  # original,replacement


class PragmaConstraint(PragmaBase):
    def __init__(self):
        self.type = 0
        self.id_tgt = 0
        self.collide = 0
        self.key_value = {}

    def from_file(self, reader: ByteIO):
        self.type = reader.read_uint8()
        self.id_tgt = reader.read_uint32()
        self.collide = reader.read_uint8() == 1
        arg_count = reader.read_uint8()
        for _ in range(arg_count):
            self.key_value[reader.read_ascii_string()] = reader.read_ascii_string()


class PragmaCollisionMesh(PragmaBase):
    def __init__(self):
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

    def from_file(self, reader: ByteIO):
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


class PragmaSoftBodyInfo(PragmaBase):
    def __init__(self):
        pass

    def from_file(self, reader: ByteIO):
        softbody_data = reader.read_uint8() == 1
        if softbody_data:
            raise NotImplementedError('SoftBody physics not yet implemented')
        else:
            return


class PragmaCollisionMeshInfo(PragmaBase):
    def __init__(self):
        self.mass = 0
        self.meshes = []
        self.softbody_info = PragmaSoftBodyInfo()

    def from_file(self, reader: ByteIO):
        self.mass = reader.read_float()
        mesh_count = reader.read_uint8()
        for i in range(mesh_count):
            mesh = PragmaCollisionMesh()
            mesh.from_file(reader)
            self.meshes.append(mesh)
        if self.model.version >= 20:
            self.softbody_info.from_file(reader)


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


class PragmaIKController(PragmaBase):
    def __init__(self):
        self.name = ""
        self.type = ""
        self.chain_len = 0
        self.method = 0
        self.key_values = {}

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.type = reader.read_ascii_string()
        self.chain_len = reader.read_uint32()
        self.method = reader.read_uint32()
        for _ in range(reader.read_uint32()):
            self.key_values[reader.read_ascii_string()] = reader.read_ascii_string()

    pass


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
            self.move.y = reader.read_float()


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
                self.transitions.append(reader.read_fmt('Ii'))

        for _ in range(reader.read_uint32()):
            frame = PragmaArmatureAnimationFrame(self)
            frame.from_file(reader)
            self.frames.append(frame)

    @property
    def has_movement(self):
        return self.flags & PragmaArmatureAnimationsFlags.MoveX or self.flags & PragmaArmatureAnimationsFlags.MoveZ


class PragmaVertexMeshAnimationFrameFlags(IntFlag):
    NONE = 0
    HasDeltaValues = 1


class PragmaVertexMeshAnimation(PragmaBase):
    def __init__(self):
        self.meshgroup_id = 0
        self.mesh_id = 0
        self.submesh_id = 0
        self.frames = []
        self.target_submesh = PragmaSubMesh()

    def from_file(self, reader: ByteIO):
        self.meshgroup_id = reader.read_uint32()
        self.mesh_id = reader.read_uint32()
        self.submesh_id = reader.read_uint32()
        self.target_submesh = self.model.mesh.mesh_groups[self.meshgroup_id].meshes[self.mesh_id][self.submesh_id]

        for _ in range(reader.read_uint32()):
            flags = PragmaVertexMeshAnimationFrameFlags(0)
            if self.model.version >= 25:
                flags = PragmaVertexMeshAnimationFrameFlags(reader.read_uint8())
            verts = []
            for _ in range(reader.read_uint16()):
                idx = reader.read_uint16()
                v = PragmaVector3HF()
                v.from_file(reader)
                delta = 0
                if flags & PragmaVertexMeshAnimationFrameFlags.HasDeltaValues:
                    delta = reader.read_uint16()
                verts.append((idx, v, delta))
            self.frames.append(verts)

        pass


class PragmaVertexAnimation(PragmaBase):
    def __init__(self):
        self.name = ""
        self.mesh_animations = []  # type: List[PragmaVertexMeshAnimation]

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            mesh_anim = PragmaVertexMeshAnimation()
            mesh_anim.from_file(reader)
            self.mesh_animations.append(mesh_anim)

    def __repr__(self):
        return f"VertexAnimation<{self.name}>(meshes:{len(self.mesh_animations)})"


class PragmaFlexInfo(PragmaBase):
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

    def __repr__(self):
        return f"FlexInfo<{self.name}>(operators:{len(self.ops)})"


class PragmaPhoneme(PragmaBase):
    def __init__(self):
        self.name = ''
        self.flex_controllers = []

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        for _ in range(reader.read_uint32()):
            self.flex_controllers.append((reader.read_uint32(), reader.read_float()))

    def __repr__(self):
        return f"Phoneme<{self.name}>(flex controllers:{len(self.flex_controllers)})"


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

        self.material_paths = []
        self.materials = []
        self.skins = {}

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

        for skin_id in range(reader.read_int16()):
            skin = []
            for _ in range(base_material_count):
                skin.append(self.materials[reader.read_uint16()])
            self.skins[skin_id] = skin

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

            self.animation_info.from_file(reader)

    @staticmethod
    def check_header(reader: ByteIO):
        with reader.save_current_pos():
            header = reader.read_ascii_string(3)
            if header != "WMD":
                return False  # , {"status": "ERROR", "msg": "invalid header"}
            version = reader.read_uint16()
            if version < 20:
                return False  # , {"status": "ERROR", "msg": "invalid version(min supported 20)"}
        return True  # , {"status": "OK", "msg": "no errors"}

    def __str__(self):
        return f"{self.__class__.__name__}<{'static' if self.static else 'skinned'}>"

    def set_name(self, name):
        self.name = name
