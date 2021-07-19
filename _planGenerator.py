<<<<<<< HEAD
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

import os

from planDefine import planType, spotParameters
from compactDICOM import spotConvert
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM







if __name__ == '__main__':

    type = planType()

    planName, data, doseRate, rangeShifter = spotParameters(type)

    dcmData = spotConvert(planName=planName, data=data, rangeShifter=rangeShifter)

    dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)

    #  passing the template file to the write programme
    # iFile = os.path.join( os.path.dirname( os.path.realpath(__file__) ), \
    #                         'data', 'RN.template-wRS.dcm' )
    # overwriteDICOM(spotData=dcmData, iFile=iFile, oFile=type['file'])
    overwriteDICOM(spotData=dcmData, oFile=type['file'])
=======
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

import os

from planDefine import planType, spotParameters
from compactDICOM import spotConvert
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM







if __name__ == '__main__':

    type = planType()

    planName, data, doseRate, rangeShifter = spotParameters(type)

    dcmData = spotConvert(planName=planName, data=data, rangeShifter=rangeShifter)

    dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)

    #  passing the template file to the write programme
    # iFile = os.path.join( os.path.dirname( os.path.realpath(__file__) ), \
    #                         'data', 'RN.template-wRS.dcm' )
    overwriteDICOM(spotData=dcmData, iFile=iFile, oFile=type['file'])
>>>>>>> 7d4302a4df75213aa0bcb630e4313b40a106422f
