# Copyright (C) 2020:  Andrew J. Gosling

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


#  qaPlanGenerator
#  Produce custom plans for commissioning and QA
#  This effectively just calls a range of modules included alongside this file

# from planDefine import planType, spotParameters
from compactDICOM import spotConvert_new  # ,spotConvert
# from planPrepare import spotArrange
from writeDICOM import overwriteDICOM


if __name__ == '__main__':

    # type = planType()
    type = {}
    import os
    type['file'] = os.path.dirname(os.path.realpath(__file__))

    rangeShifter = None
    gantry = [0.0]
    repeats = 1
    energy = ([float(i) for i in range(70, 150+1, 10) for _ in range(repeats)])
    # energy = [float(_) for _ in range(160, 200+1, 5)]
    spots = 41
    space = 2.5
    MU = 10
    length = int(space*(spots-1)/10)
    # planName = "My_Plan"
    planName = f'Output_G{int(gantry[0])}_E{int(energy[0])}to{int(energy[-1])}_{length}x{length}_{MU}MU_RS{rangeShifter}x{repeats}'

    # doseRate = MU

    data = [[] for _ in range(len(energy))]

    for ga in gantry:
        for e, en in enumerate(energy):
            for x in range(spots):
                for y in range(spots):
                    if x % 2:  # if x is odd as any value > 0 is True
                        data[e].append([ga, en, (x-((spots-1)/2))*space,
                                        (y-((spots-1)/2))*space, MU]
                                       )
                    else:
                        data[e].append([ga, en, (x-((spots-1)/2))*space,
                                        (((spots-1)/2)-y)*space, MU ]
                                       )
                    #  trying to get scanning in Y to be back and forth




    dcmData = spotConvert_new(planName=planName, data=data, rangeShifter=rangeShifter)



    #  passing the template file to the write programme
    iFile = os.path.join( os.path.dirname( os.path.realpath(__file__) ), \
                            'data', 'RN.template-wRS.dcm' )
    overwriteDICOM(spotData=dcmData, iFile=iFile, oFile=type['file'])
