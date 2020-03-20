import typing

from ...byte_io_wmd import ByteIO


class PragmaBase:
    base = None

    @classmethod
    def set_base(cls, model):
        from ...wmd.wmd_file import Model
        from ...wld.wld_file import World
        cls.base: typing.Union[Model, World] = model

    def to_file(self, writer: ByteIO):
        raise NotImplemented

    def from_file(self, reader: ByteIO):
        raise NotImplemented
