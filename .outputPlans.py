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

from planDefine import planType, spotParameters
from compactDICOM import spotConvert, spotConvert_new
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM








if __name__ == '__main__':

    # type = planType()
    type={}
    import os
    type['file'] = os.path.dirname(os.path.realpath(__file__))



    # planName, data, doseRate, rangeShifter = spotParameters(type)
    planName = 'Output-G0-E70-245-10x10-10MU'
    # planName = 'Output-G0-E70-245-10x10-50MU'
    # planName = 'IDD-G0-E70-10x10-50MU'
    # planName = 'IDD-G0-E70-20x20-50MU'
    # data =
    rangeShifter = None

    gantry = [0.0]
    energy = [float(_) for _ in range(70, 245+1, 5)]
    spots = 41
    space = 2.5
    MU = 10

    doseRate = MU

    data = [[] for _ in range(len(energy))]

    for ga in gantry:
        for e, en in enumerate(energy):
            for x in range(spots):
                for y in range(spots):
                    data[e].append([ ga, en, (x-((spots-1)/2))*space, (y-((spots-1)/2))*space, MU ])



    dcmData = spotConvert_new(planName=planName, data=data, rangeShifter=rangeShifter)



    overwriteDICOM(spotData=dcmData, iFile=None, oFile=type['file'])