###  Copyright (C) 2020:  Andrew J. Gosling

  #  This program is free software: you can redistribute it and/or modify
  #  it under the terms of the GNU General Public License as published by
  #  the Free Software Foundation, either version 3 of the License, or
  #  (at your option) any later version.

  #  This program is distributed in the hope that it will be useful,
  #  but WITHOUT ANY WARRANTY; without even the implied warranty of
  #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  #  GNU General Public License for more details.

  #  You should have received a copy of the GNU General Public License
  #  along with this program.  If not, see <http://www.gnu.org/licenses/>.







###  qaPlanGenerator
  #  Produce custom plans for commissioning and QA
  #  This effectively just calls a range of modules included alongside this file

from qaPlanDefine import qaPlanType, qaSpotParameters
from convert2compactDICOM import qaSpotConvert
from qaPlanPrepare import qaSpotArrange
from writeDICOM import overwriteDICOM







if __name__ == '__main__':

    #  data taken from pbtMod/docs/test.csv
    #  [gAngle, energy, X, Y, MU]
    # data = [[0.0, 70.0, 10.0, 10.0, 100.0], [0.0, 70.0, 20.0, 20.0, 100.0], [0.0, 100.0, -10.0, -10.0, 200.0], [0.0, 100.0, -15.0, 20.0, 250.0], [0.0, 100.0, 10.0, 10.0, 80.0], [80.0, 70.0, 10.0, 10.0, 100.0], [80.0, 70.0, 20.0, 20.0, 100.0], [80.0, 100.0, -10.0, -10.0, 200.0], [310.0, 70.0, 20.0, 20.0, 100.0], [310.0, 100.0, -10.0, -10.0, 200.0], [310.0, 100.0, -15.0, 20.0, 250.0], [-180.0, 100.0, 10.0, 10.0, 80.0]]
    # doseRate = 50.0



    type = qaPlanType()

    data, doseRate = qaSpotParameters(type)

    dcmData = qaSpotConvert(data)

    overwriteDICOM(dcmData)



'''
    from qaPlanInput import qaSpotArrange
    data = qaSpotArrange(data)



    # becomes:
    # {'pName': 'qaPlan', 'numBeams': 4, 'beam': [<dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E2E0>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E280>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E2B0>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E3A0>]}
    # {'bName': 'G0.0', 'type': 'TREATMENT', 'gAngle': 0.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 730.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C70>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880CA0>]}
    # {'En': 50.0, 'X': [10.0, 20.0], 'Y': [10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0, 100.0], 'sMU': []}
    # {'En': 100.0, 'X': [-10.0, -15.0, 10.0], 'Y': [-10.0, 20.0, 10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0, 250.0, 80.0], 'sMU': []}
    # {'bName': 'G-130.0', 'type': 'TREATMENT', 'gAngle': -130.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 80.0, 'numCP': 1, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C10>]}
    # {'En': 100.0, 'X': [10.0], 'Y': [10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [80.0], 'sMU': []}
    # {'bName': 'G80.0', 'type': 'TREATMENT', 'gAngle': 80.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 400.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880700>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C40>]}
    # {'En': 50.0, 'X': [10.0, 20.0], 'Y': [10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0, 100.0], 'sMU': []}
    # {'En': 100.0, 'X': [-10.0], 'Y': [-10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0], 'sMU': []}
    # {'bName': 'G310.0', 'type': 'TREATMENT', 'gAngle': 310.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 550.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880670>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F8806D0>]}
    # {'En': 50.0, 'X': [20.0], 'Y': [20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0], 'sMU': []}
    # {'En': 100.0, 'X': [-10.0, -15.0], 'Y': [-10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0, 250.0], 'sMU': []}



    qaSpotPrepare(data=data, doseRate=doseRate)
'''
