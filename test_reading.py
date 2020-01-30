from pragma_model import PragmaModel
from byte_io_wmd import ByteIO

if __name__ == '__main__':
    reader = ByteIO(path='test_data/medic.wmd')
    if PragmaModel.check_header(reader):
        model = PragmaModel()
        model.from_file(reader)
        print(model)
