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







import os
from easygui import fileopenbox, filesavebox
import datetime
from random import randint
from copy import deepcopy
from pydicom.filereader import dcmread







def overwriteDICOM(spotData=None, iFile=None, oFile=None):

    # if no dataset passed, request user input
    if spotData == None:
        print('requires input data');  raise SystemExit()




    # obtain the template plan, and read in the data
    ''' see if any way to store this within the plan but still give option '''
    if not iFile:
        iFile = fileopenbox( title='Template file',
                             msg='Select the template DICOM file\n \
                                  Results will be better if the template is \
                                  exported from the patient to which the \
                                  created plan will be added',
                             default=os.path.join( os.path.dirname( \
                                        os.path.realpath(__file__) ), \
                                        'data', 'RN.template-wRS.dcm' ), \
                             filetypes='*.dcm' )
    iPath, iName = os.path.split(iFile)[0], os.path.split(iFile)[1]




    # obtain the output file location
    oFile = filesavebox( title='Output file',
                         msg='Select where to save the plan file produced', \
                         default=os.path.join( os.path.dirname(oFile), 'RN.' \
                                                + str(spotData.pName) + '.dcm' ), \
                         filetypes='*.dcm' )
    oPath, oName = os.path.split(oFile)[0], os.path.split(oFile)[1]



    fullDCMdata = dcmread(iFile)





    #  adjusting the date and time of plan creation to now
    fullDCMdata.RTPlanLabel = spotData.pName

    fullDCMdata.RTPlanDate = datetime.datetime.now().strftime('%Y%m%d')

    fullDCMdata.RTPlanTime = datetime.datetime.now().strftime('%H%M%S.%f')



    #  SOPInstanceUID is the unique identifier for each plan
    #  Final 2 sections are a generated ID number and date/time stamp
    sopInstUID = fullDCMdata.SOPInstanceUID.rsplit('.',2)

    fullDCMdata.SOPInstanceUID = sopInstUID[0] + '.' \
                                 + str(randint(10000, 99999)) + '.' \
                                 + fullDCMdata.RTPlanDate \
                                 + fullDCMdata.RTPlanTime.rsplit('.')[0]



    '''  Fraction Group Sequence '''



    #  ReferencedBeamNumber and BeamMeterset
    #  Need one for each beam in plan, so multiply if separating energy layers
    fullDCMdata.FractionGroupSequence[0].NumberOfBeams = spotData.numBeams

    # setting all elements in ReferencedBeam Sequence to same as 1st
    # to duplicate a class object and all elements within need copy.deepcopy
    # deepcopy ensures there isn't inheritance so changes to one doesn't affect others
    fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence \
      = [ deepcopy( fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[0]) \
          for _ in range(spotData.numBeams) ]

    # now changing each BeamMeterset to sum of all sMeterset within beam
    for _ in range(spotData.numBeams):

        fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].BeamMeterset \
          = sum([sum(c.sMeterset) for c in spotData.beam[_].CP])

        fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber = _+1



    '''  Patient Setup Sequence '''



    # need a PatientSetupSequence for each beam
    fullDCMdata.PatientSetupSequence = \
      [ deepcopy(fullDCMdata.PatientSetupSequence[0]) \
        for _ in range(spotData.numBeams) ]

    for _ in range(spotData.numBeams):
        fullDCMdata.PatientSetupSequence[_].PatientSetupNumber = _+1



    '''  Ion Beam Sequence '''



    # The meat and potatoes of it all
    # have to create correct sized array of dicom structures before copying
    # https://stackoverflow.com/questions/28963354/typeerror-cant-pickle-generator-objects
    fullDCMdata.IonBeamSequence = [ fullDCMdata.IonBeamSequence[0] \
                                    for _ in range(spotData.numBeams) ]

    # then use copy.deepcopy([]) to populate each time
    for b in range(spotData.numBeams):
        fullDCMdata.IonBeamSequence[b] = deepcopy(fullDCMdata.IonBeamSequence[0])



    for b in range(spotData.numBeams):

        fullDCMdata.IonBeamSequence[b].BeamNumber = b+1

        fullDCMdata.IonBeamSequence[b].BeamName = spotData.beam[b].bName

        fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight = \
          sum( [sum(c.sMeterset) for c in spotData.beam[b].CP] )

        fullDCMdata.IonBeamSequence[b].NumberOfControlPoints = \
          2*spotData.beam[b].numCP



        '''
        # Here is where the Range Shifter data needs to be added if included - DO LATER
        '''
        if spotData.beam[b].rs != None:
            fullDCMdata.IonBeamSequence[b].NumberOfRangeShifters = 1
            fullDCMdata.IonBeamSequence[b].RangeShifterSequence[0].RangeShifterNumber = 1
            if spotData.beam[b].rs == 2:
                fullDCMdata.IonBeamSequence[b].RangeShifterSequence[0].RangeShifterID = 'RS=2cm'
            if spotData.beam[b].rs == 3:
                fullDCMdata.IonBeamSequence[b].RangeShifterSequence[0].RangeShifterID = 'RS=3cm'
            if spotData.beam[b].rs == 5:
                fullDCMdata.IonBeamSequence[b].RangeShifterSequence[0].RangeShifterID = 'RS=5cm'
            fullDCMdata.IonBeamSequence[b].RangeShifterSequence[0].RangeShifterType = 'BINARY'
        else:
            fullDCMdata.IonBeamSequence[b].NumberOfRangeShifters = 0
            del fullDCMdata.IonBeamSequence[b].RangeShifterSequence


        # Creating Control Point entries
        # 2 for each position as need a 'start' and 'end for each point'
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence \
          = [ fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0], \
              fullDCMdata.IonBeamSequence[b].IonControlPointSequence[1] ]

        # again, need to use copy.deepcopy otherwise end up with inheritance!!!
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence.extend( \
          [ deepcopy(fullDCMdata.IonBeamSequence[b].IonControlPointSequence[1]) \
            for _ in range(2*(spotData.beam[b].numCP-1)) ] )

        # filling in the Control Point information
        # first control point in each beam contains additional data such as gantry angle etc.
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].GantryAngle \
          = spotData.beam[b].gAngle

        '''  more range shifter settings will have to go here'''
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].SnoutPosition \
          = 421.0
        if spotData.beam[b].rs != None:
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].RangeShifterSetting = 'IN'
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].IsocenterToRangeShifterDistance \
              = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].SnoutPosition + 4.9
            if spotData.beam[b].rs == 2:
                fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].RangeShifterWaterEquivalentThickness = 23.0
            if spotData.beam[b].rs == 3:
                fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].RangeShifterWaterEquivalentThickness = 34.0
            if spotData.beam[b].rs == 5:
                fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].RangeShifterWaterEquivalentThickness = 57.0
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence[0].ReferencedRangeShifterNumber = '1'
        else:
            del fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].RangeShifterSettingsSequence



        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[-1].CumulativeMetersetWeight = 0
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].CumulativeMetersetWeight = 0



        for c in range(0, 2*spotData.beam[b].numCP, 2):

            # print('c:  ', c//2, 'En:  ', spotData.beam[b].CP[c//2].En)

            # Indexing
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ControlPointIndex = c
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ControlPointIndex = c+1

            # number of spots used regularly enough to warrant for typing efficiency
            nSpots = len(spotData.beam[b].CP[c//2].X)

            # spot energies
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].NominalBeamEnergy \
              = spotData.beam[b].CP[c//2].En
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].NominalBeamEnergy \
              = spotData.beam[b].CP[c//2].En

            # number of spots at this energy
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].NumberOfScanSpotPositions = nSpots
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].NumberOfScanSpotPositions = nSpots

            # setting spot position map, is a list of x, y coordinates all together
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotPositionMap \
              = [ coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair ]
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotPositionMap \
              = [coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair]

            # Meterset weighting of each spot
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotMetersetWeights \
              = spotData.beam[b].CP[c//2].sMeterset
            # Meterset weight for every second CP is 0.0, acts as end point for each spot
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotMetersetWeights \
              = [0.0 for _ in range(nSpots)]

            # the size of the spot at isocentre
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanningSpotSize \
              = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanningSpotSize \
              = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]

            # sum of previous control points
            # a CP with meterset listed doesn't add, the following with meterset 0.0 does add
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight \
              = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c-1].CumulativeMetersetWeight
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight \
              = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight \
                + sum(spotData.beam[b].CP[c//2].sMeterset)

            # and as a ratio of the total plane meterset
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient \
              = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight \
                / fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient \
              = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight \
                / fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight

        fullDCMdata.IonBeamSequence[b].ReferencedPatientSetupNumber = b+1



    fullDCMdata.save_as(oFile)
