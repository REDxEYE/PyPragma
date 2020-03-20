import typing

from ...shared import PragmaBase, Vector3F
from ...byte_io_wmd import ByteIO


class BSPPlane:
    def __init__(self):
        self.normal = Vector3F()
        self.distance = 0.0
        self.pos = Vector3F()
        self.pos_center = Vector3F()

    def set_normal(self, normal):
        self.normal = normal

    def set_distance(self, distance):
        self.distance = distance

    def get_distance(self, pos: Vector3F):
        offset = pos - self.pos_center
        return offset.dot(self.normal, offset)

    def move_to_pose(self, pos: Vector3F):
        d_new = self.normal.dot(pos)
        self.distance = -d_new
        self.pos = self.normal * d_new
        self.pos_center = pos


class BSPNode(PragmaBase):
    def __init__(self):
        self.children = []  # type:typing.List['BSPNode']
        self.leaf = True
        self.min = Vector3F()
        self.max = Vector3F()
        self.original_node_index = -1
        self.first_face = 0
        self.face_count = 0
        self.cluster = 0xFF_FF

        self.min_visible = Vector3F()
        self.max_visible = Vector3F()

        self.plane = BSPPlane()


class BSPTree(PragmaBase):

    def __init__(self):
        self.nodes = []  # type:typing.List[BSPNode]
        self.root_node = self.create_node()
        self.cluster_count = 0
        self.compressed_cluster_count = 0
        self.compressed_cluster_data = b''

        pass

    def create_node(self):
        node = BSPNode()
        self.nodes.append(node)
        return node

    def read_node(self, reader: ByteIO, node: BSPNode):
        node.leaf = reader.read_uint8() == 1
        node.min.from_file(reader)
        node.max.from_file(reader)
        node.first_face = reader.read_uint32()
        node.face_count = reader.read_uint32()
        node.original_node_index = reader.read_uint32()
        if node.leaf:
            node.cluster = reader.read_uint16()
            node.min_visible.from_file(reader)
            node.max_visible.from_file(reader)
            return
        normal = Vector3F()
        normal.from_file(reader)
        d = reader.read_float()
        node.plane.set_normal(normal)
        node.plane.set_distance(d)
        node.children.append(self.create_node())
        node.children.append(self.create_node())
        self.read_node(reader, node.children[0])
        self.read_node(reader, node.children[1])

    def from_file(self, reader: ByteIO):
        self.read_node(reader, self.root_node)
        self.cluster_count = reader.read_uint64()
        self.compressed_cluster_count = self.cluster_count ** 2
        self.compressed_cluster_count = self.compressed_cluster_count // 8 + \
                                        1 if (self.compressed_cluster_count % 8) > 0 else 0
        self.compressed_cluster_data = reader.read_bytes(self.compressed_cluster_count * 1)
        pass
