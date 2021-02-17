import os
import sys
#  as body of code is one directory up from this test directory
fPath = os.path.dirname(os.path.realpath(__file__))  #  path of current file
sys.path.append(os.path.split(fPath)[0])  #  add parent directory to $PATH



# from QAplans import qaPlanType, qaSpotParameters
from qaPlanDefine import qaPlanType, qaSpotParameters
from convert2compactDICOM import qaSpotConvert
from qaPlanPrepare import qaSpotArrange
from writeDICOM import overwriteDICOM



#  data taken from pbtMod/docs/test.csv
#  [gAngle, energy, X, Y, MU]
# data = [[0.0, 70.0, 10.0, 10.0, 100.0], [0.0, 70.0, 20.0, 20.0, 100.0], [0.0, 100.0, -10.0, -10.0, 200.0], [0.0, 100.0, -15.0, 20.0, 250.0], [0.0, 100.0, 10.0, 10.0, 80.0], [80.0, 70.0, 10.0, 10.0, 100.0], [80.0, 70.0, 20.0, 20.0, 100.0], [80.0, 100.0, -10.0, -10.0, 200.0], [310.0, 70.0, 20.0, 20.0, 100.0], [310.0, 100.0, -10.0, -10.0, 200.0], [310.0, 100.0, -15.0, 20.0, 250.0], [-180.0, 100.0, 10.0, 10.0, 80.0]]
# doseRate = 50.0



###  perhaps need to find a way to pass values to this as a test
# type = qaPlanType(qaType={})
# print(type)

type = {}
type['type']='CSV'
type['output'] = 'TPS'
type['file'] = 'C:\\Users\\andrew\\coding\\QAplans\\test\\test.csv'
# # debugging the energy ordering issue at home
# type['file'] = 'C:\\Users\\andrew\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\QAplans\\spots.csv'
# # debugging the energy ordering issue at work
type['file'] = 'C:\\Users\\agoslin2\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\QAplans\\spots.csv'



data, doseRate = qaSpotParameters(type)
# order is preserved when convrted to 'data'

dcmData = qaSpotConvert(data)
# for b in dcmData.beam:
#     print(b.gAngle)
#     for c in b.CP:
#         print(c.En)
#  turns out this is where the energies get disordered
#  almost certainly due to the use of 'sets'

dcmData, doseRate = qaSpotArrange(data=dcmData, doseRate=doseRate)
# for b in dcmData.beam:
#     print(b.gAngle)
#     for c in b.CP:
#         print(c.En)


iFile = 'C:\\Users\\agoslin2\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\QAplans\\RN.deliverable_template.dcm'
oFile = 'C:\\Users\\agoslin2\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\QAplans\\profiles\\RN.qaPlan.dcm'
overwriteDICOM(dcmData, iFile, oFile)





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
