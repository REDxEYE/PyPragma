from . import PragmaBase, Vector3F
from ...byte_io_wmd import ByteIO


class Eyeball(PragmaBase):
    def __init__(self):
        self.name = ''
        self.bone_index = -1
        self.origin = Vector3F()
        self.z_offset = 0.0
        self.radius = 0.0
        self.up = Vector3F()
        self.forward = Vector3F()
        self.iris_material_index = -1
        self.max_dilation_factor = 1.0
        self.iris_uv_radius = 0.2
        self.iris_scale = 0.0
        self.upper_flex_desc = [0, 0, 0]
        self.lower_flex_desc = [0, 0, 0]
        self.upper_target = [0.0, 0.0, 0.0]
        self.lower_target = [0.0, 0.0, 0.0]
        self.upper_lid_flex_desc = -1
        self.lower_lid_flex_desc = -1

    def from_file(self, reader: ByteIO):
        self.name = reader.read_ascii_string()
        self.bone_index = reader.read_int32()
        self.origin.from_file(reader)
        self.z_offset = reader.read_float()
        self.radius = reader.read_float()
        self.up.from_file(reader)
        self.forward.from_file(reader)
        self.iris_material_index = reader.read_int32()
        self.max_dilation_factor = reader.read_float()
        self.iris_uv_radius = reader.read_float()
        self.iris_scale = reader.read_float()
        self.upper_flex_desc = [reader.read_int32(), reader.read_int32(), reader.read_int32()]
        self.lower_flex_desc = [reader.read_int32(), reader.read_int32(), reader.read_int32()]
        self.upper_target = [reader.read_float(), reader.read_float(), reader.read_float()]
        self.lower_target = [reader.read_float(), reader.read_float(), reader.read_float()]
        self.upper_lid_flex_desc = reader.read_int32()
        self.lower_lid_flex_desc = reader.read_int32()

    def to_file(self, writer: ByteIO):
        writer.write_ascii_string(self.name)
        writer.write_int32(self.bone_index)
        self.origin.to_file(writer)
        writer.write_float(self.z_offset)
        writer.write_float(self.radius)
        self.up.to_file(writer)
        self.forward.to_file(writer)
        writer.write_int32(self.iris_material_index)
        writer.write_float(self.max_dilation_factor)
        writer.write_float(self.iris_uv_radius)
        writer.write_float(self.iris_scale)
        writer.write_int32(self.upper_flex_desc[0])
        writer.write_int32(self.upper_flex_desc[1])
        writer.write_int32(self.upper_flex_desc[2])
        writer.write_int32(self.lower_flex_desc[0])
        writer.write_int32(self.lower_flex_desc[1])
        writer.write_int32(self.lower_flex_desc[2])
        writer.write_float(self.upper_target[0])
        writer.write_float(self.upper_target[1])
        writer.write_float(self.upper_target[2])
        writer.write_float(self.lower_target[0])
        writer.write_float(self.lower_target[1])
        writer.write_float(self.lower_target[2])
        writer.write_int32(self.upper_lid_flex_desc)
        writer.write_int32(self.lower_lid_flex_desc)
