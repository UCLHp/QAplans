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
import sys
import json

from compactDICOM import spotConvert, spotConvert_ism, spotConvert_chevron
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM


if __name__ == '__main__':
    # load from json file if specified
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
      try:
        with open(sys.argv[1], 'r') as f:
          type = json.load(f)
      except:
        raise ValueError("Specify a valid json file.")
      
      from planDefineCLI import spotParameters
      from _multiplyBeams import *
      from _energy_spacer import *
      planName, data, doseRate, rangeShifter = spotParameters(type)
      dcmData = spotConvert(planName=planName, data=data, rangeShifter=rangeShifter)
      dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
      oFile=os.path.join(type['outdir'],planName)
      overwriteDICOM(spotData=dcmData, iFile=type['TemplateFile'], oFile=oFile)
      oPath, oFile = os.path.split(oFile)
      oFile = 'RN.'+oFile+'.dcm'
      oFile = os.path.join(oPath,oFile)
      oFile = os.path.abspath(oFile)
      if 'm' in sys.argv:
        beam_multiple = int(type['BeamMultiple'])
        multiplyBeams(ifile=[oFile], factor=beam_multiple)
        oPath, oExt = os.path.splitext(oFile)
        oFile = oPath + '_x' + str(beam_multiple) + oExt
      if 's' in sys.argv:
        space = int(type['EnergySpacer'])
        energy_spacer(ifile=[oFile], ofile=None, space=[space])
    elif '-ism' in sys.argv:
      from planDefine import planType, spotParameters
      type = planType()
      planName, data, doseRate, rangeShifter = spotParameters(type)
      dcmData = spotConvert_ism(planName=planName, data=data, rangeShifter=rangeShifter)
      dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
      overwriteDICOM(spotData=dcmData)
    elif '-chev' in sys.argv:
      from planDefine import planType, spotParameters
      type = planType()
      planName, data, doseRate, rangeShifter = spotParameters(type)
      dcmData = spotConvert_chevron(planName=planName, data=data, rangeShifter=rangeShifter)
      dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
      overwriteDICOM(spotData=dcmData)
    else:
      from planDefine import planType, spotParameters
      type = planType()
      planName, data, doseRate, rangeShifter = spotParameters(type)
      dcmData = spotConvert(planName=planName, data=data, rangeShifter=rangeShifter)
      dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
      overwriteDICOM(spotData=dcmData)
