from PyWMD.pragma_model import PragmaModel
from PyWMD.byte_io_wmd import ByteIO

if __name__ == '__main__':
    reader = ByteIO(path=r"test_data\medic.wmd")
    # reader = ByteIO(path=r"F:\SteamLibrary\steamapps\common\Pragma\addons\imported\models\mark2580\mass_effect_3\misc\weaponmodtable.wmd")
    if PragmaModel.check_header(reader):
        model = PragmaModel()
        model.from_file(reader)
        print(model)
