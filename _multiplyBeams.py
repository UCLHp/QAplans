###  Copyright (C) 2021:  Andrew J. Gosling

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







import os
from easygui import fileopenbox, filesavebox, enterbox
import datetime
from random import randint
from copy import deepcopy
from pydicom.filereader import dcmread







###  Take a given plan and multiply every beam in that plan by a given value
def multiplyBeams(iFile=None, oFile=None, factor=None):


    # iFile = 'C:\\Users\\andrew\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\QAandCommissioning\\Gantry 1\\Commissioning\\Data\\Outputs\\RN.IDD-G0-E70-20x20-50MU.dcm'
    # iFile = 'C:\\Users\\andrew\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\QAandCommissioning\\Gantry 1\\Commissioning\\Data\\Outputs\\RN.Output-G0-E70-245-10x10-10MU.dcm'
    if not iFile:
        iFile = fileopenbox( title='Original plan', \
                             msg='Template file for which beams to be multiplied', \
                             default=os.path.dirname(os.path.realpath(__file__)), \
                             filetypes='*.dcm' )
    iPath, iName = os.path.split(iFile)[0], os.path.split(iFile)[1]


    # factor = 3
    if not factor:
        factor = enterbox( title='Multiplication factor', \
                            msg='How many times to multiply each beam', \
                            default='10', strip=True )
        factor = int(factor)


    oFile = os.path.join( os.path.splitext(iFile)[0] + '_x' + str(factor) + '.dcm' )
    if not oFile:
        oFile = filesavebox( title='Output plan', \
                             default=os.path.join( os.path.splitext(iFile)[0] \
                                                    + '_x' + str(factor) + '.dcm' ), \
                             filetypes='*.dcm' )
    oPath, oName = os.path.split(oFile)[0], os.path.split(oFile)[1]




    fullDCMdata = dcmread(iFile)

    newDCMdata = dcmread(iFile)





    # to duplicate a class object and all elements within need copy.deepcopy
    # deepcopy ensures there isn't inheritance so changes to one doesn't affect others





    #  adjusting the date and time of plan creation to now
    newDCMdata.RTPlanLabel = deepcopy(fullDCMdata.RTPlanLabel + '_x' + str(factor))

    newDCMdata.RTPlanDate = datetime.datetime.now().strftime('%Y%m%d')

    newDCMdata.RTPlanTime = datetime.datetime.now().strftime('%H%M%S.%f')




    #  SOPInstanceUID is the unique identifier for each plan
    #  Final 2 sections are a generated ID number and date/time stamp
    sopInstUID = fullDCMdata.SOPInstanceUID.rsplit('.',2)

    newDCMdata.SOPInstanceUID = sopInstUID[0] + '.' \
                                + str(randint(10000, 99999)) + '.' \
                                + fullDCMdata.RTPlanDate \
                                + fullDCMdata.RTPlanTime.rsplit('.')[0]




    #  ReferencedBeamNumber and BeamMeterset
    #  Need one for each beam in plan, so multiply by factor increase in beams
    newDCMdata.FractionGroupSequence[0].NumberOfBeams = \
      deepcopy(fullDCMdata.FractionGroupSequence[0].NumberOfBeams*factor)

    #  making copies of ReferencedBeamSequence for each new beam
    newDCMdata.FractionGroupSequence[0].ReferencedBeamSequence = []
    for refBmSeq in fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence:
        newDCMdata.FractionGroupSequence[0].ReferencedBeamSequence.extend( [ deepcopy(refBmSeq) for _ in range(factor) ] )
    #  and changing the beam numbers
    #  use old sequencing in case orders are reversed later in plan
    for n in range(len(fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence)):
        for f in range(factor):
            newDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[n*factor+f].ReferencedBeamNumber = (fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[n].ReferencedBeamNumber-1)*factor+f+1




    #  Patient setup sequence
    #  require a PatientSetupSequence for each beam
    newDCMdata.PatientSetupSequence = []
    for ptSetSeq in fullDCMdata.PatientSetupSequence:
        newDCMdata.PatientSetupSequence.extend( [ deepcopy(ptSetSeq) for _ in range(factor) ] )
    #  and changing the beam numbers
    #  use old sequencing in case orders are reversed later in plan
    for n in range(len(fullDCMdata.PatientSetupSequence)):
        for f in range(factor):
            newDCMdata.PatientSetupSequence[n*factor+f].PatientSetupNumber = (fullDCMdata.PatientSetupSequence[n].PatientSetupNumber-1)*factor+f+1




    #  Ion Beam Sequence
    newDCMdata.IonBeamSequence = []
    for ionBmSeq in fullDCMdata.IonBeamSequence:
        newDCMdata.IonBeamSequence.extend( [ deepcopy(ionBmSeq) for _ in range(factor) ] )
    #  and changing the beam numbers
    #  use old sequencing in case orders are reversed later in plan
    for n in range(len(fullDCMdata.IonBeamSequence)):
        for f in range(factor):
            newDCMdata.IonBeamSequence[n*factor+f].BeamNumber = (fullDCMdata.IonBeamSequence[n].BeamNumber-1)*factor+f+1
            newDCMdata.IonBeamSequence[n*factor+f].BeamName = fullDCMdata.IonBeamSequence[n].BeamName + '-' + str(f+1)



    newDCMdata.save_as(oFile)







if __name__ == '__main__':

    multiplyBeams()
