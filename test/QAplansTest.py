import os
import sys
#  as body of code is one directory up from this test directory
fPath = os.path.dirname(os.path.realpath(__file__))  #  path of current file
sys.path.append(os.path.split(fPath)[0])  #  add parent directory to $PATH



# from QAplans import qaPlanType, qaSpotParameters
from qaPlanDefine import qaPlanType, qaSpotParameters
# from convert2compactDICOM import qaSpotConvert
# from qaPlanPrepare import qaSpotArrange
# from writeDICOM import overwriteDICOM



###  perhaps need to find a way to pass values to this as a test
# type = qaPlanType(qaType={})

type = {}
type['type']='CSV'
type['output'] = 'TPS'

data, doseRate = qaSpotParameters(type)

# dcmData = qaSpotConvert(data)

# overwriteDICOM(dcmData)
