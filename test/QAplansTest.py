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



###  perhaps need to find a way to pass values to this as a test
# type = qaPlanType(qaType={})
# print(type)

type = {}
type['type']='CSV'
type['output'] = 'TPS'
type['file'] = 'C:\\Users\\andrew\\coding\\QAplans\\test\\test.csv'

# debugging the energy ordering issue
type['file'] = 'C:\\Users\\andrew\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\QAplans\\spots.csv'

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

overwriteDICOM(dcmData)
