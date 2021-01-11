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







#  flag for different dose rate that will be implemented
#  Orders the spots to scan in the correct manner (invariate on start point)
#  Adds intermediate spots for large energy jumps
#  uses the final spot on a plan to dictate the dose rate if that flag used







###  Take a given set of spots in the pbtDICOM class
  #  re-arrange the beams, energy layers, and spots into the most deliverable
  #    order to best efficiency
  #  Also add in intermediate spots for large energy jumps
  #  Will also be worth double checking the validation for things like energy
  #    range and spot position
def qaSpotPrepare(data=None, doseRate=None):

    ###  Basic settings to translate into variables
      #  These dictate how plans are delivered
    #  gantry angle
    Alim = [0.0, 360.0, -180.0]  #  for angles given in 0 - 360 range
    #  beam energy
    Elim = [70.0, 244.0]
    Ejump = 10.0
    #  field size
    Xlim = [-20.0, 20.0]
    Ylim = [-30.0, 30.0]
    # dose rate
    minD = 5.0

    if not data:
        print('no spot data supplied'); raise SystemExit()

    if not doseRate:
        #  probably good to add something here to ask for the doseRate
        raise SystemExit()


    ###  check the data supplied is deliverable
    for b in data.beam:
        if (Alim[0] <= b.gAngle < Alim[1]) or b.gAngle == Alim[2]:
            pass
        else:  print('Gantry angle out of range\nAngles should be in the range \
                      0 - 360 and/or -180'); raise SystemExit()
        for c in b.CP:
            if Elim[0] <= c.En <= Elim[1]:
                pass
            else:  print('Energy out of range'); raise SystemExit()
            for s in c.X:
                if Xlim[0] <= s <= Xlim[1]:
                    pass
                else:  print('X position out of range'); raise SystemExit()
            for s in c.Y:
                if Ylim[0] <= s <= Ylim[1]:
                    pass
                else:  print('Y position out of range'); raise SystemExit()
            for s in c.sMeterset:
                if s >= minD:
                    pass
                else:  print('spot MU too low'); raise SystemExit()


    ###  Now work through all the data and make sure most effective setup

    ###  order the beams CCW from 180 post
    def beamE(beam):
        return beam.gAngle
    print([_.gAngle for _ in data.beam])
    data.beam.sort(key=beamE)
    print([_.gAngle for _ in data.beam])

    # print(sorted(data.beam))
    for bm in data.beam:
        pass

    ### order the energy layers from highest to lowest
    for bm in data.beam:
        for cp in bm.CP:
            pass

    ### order the spots in a raster pattern scanning primarily in Y direction
    for bm in data.beam:
        for cp in bm.CP:
            # for sp in <something>:
                pass



















###  Write out an appropriate QA plan .dcm file
  #  input must be in the pbtDICOM class
  #  uses a selection of template plans from the TPS as a basis

def qaPlanWrite(spotData=None, tmpFile=None, oFile=None):

    import datetime

    from copy import deepcopy
    from random import randint

    from pydicom.filereader import dcmread



    #  sanitising and checking for all the necessary data
    if not spotData:
        print('require spot data to write'); raise SystemExit()

    if not tmpFile:
        from easygui import fileopenbox
        tmpFile = fileopenbox(title='Template file',
                              msg='Select the template DICOM file\n \
                                    Results will be better if the template is \
                                    exported from the patient to which the \
                                    created plan will be added',
                              default='*', filetypes='*.dcm')

    if not oFile:
        from easygui import filesavebox
        oFile = filesavebox(title='Output file',
                            default=osPath.split(tmpFile)[0]+str(data.pName)+'.dcm',
                            filetypes='*.dcm')


    fullDCM = dcmread(tmpFile)

    #  adjusting the date and time of plan creation to now
    fullDCM.RTPlanLabel = spotData.pName  # (300a,0002)
    fullDCM.RTPlanDate = datetime.datetime.now().strftime('%Y%m%d')  # (300a,0006)
    fullDCM.RTPlanTime = datetime.datetime.now().strftime('%H%M%S.%f')  # (300a,0007)

    #  SOPInstanceUID is the unique identifier for each plan
    #  Final 2 sections are a generated ID number and date/time stamp
    sopInstUID = fullDCM.SOPInstanceUID.rsplit('.',2)  # (0008,0018)
    fullDCM.SOPInstanceUID = sopInstUID[0] + '.' + str(randint(10000, 99999)) + '.' + fullDCM.RTPlanDate + fullDCM.RTPlanTime.rsplit('.')[0]

    #  to duplicate a class object and all elements within need copy.deepcopy
    #  this ensures there isn't inheritance, changes to one don't affect others

    #  ReferencedBeamNumber and BeamMeterset
    #  Need one for each beam in plan, so multiply if separating energy layers
    fullDCM.FractionGroupSequence[0].NumberOfBeams = spotData.numBeams  # (300A,0080)
    # setting all elements in ReferencedBeam Sequence to same as 1st
    fullDCM.FractionGroupSequence[0].ReferencedBeamSequence = [deepcopy(fullDCM.FractionGroupSequence[0].ReferencedBeamSequence[0]) for _ in range(spotData.numBeams)]
    # now changing each BeamMeterset to sum of all sMeterset within beam
    for _ in range(spotData.numBeams):
        fullDCM.FractionGroupSequence[0].ReferencedBeamSequence[_].BeamMeterset = sum([sum(c.sMeterset) for c in spotData.beam[_].CP])
        fullDCM.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber = _+1

    #  PatientSetupSequence for each beam
    fullDCM.PatientSetupSequence = [deepcopy(fullDCM.PatientSetupSequence[0]) for _ in range(spotData.numBeams)]
    for _ in range(spotData.numBeams):
        fullDCM.PatientSetupSequence[_].PatientSetupNumber = _+1

    # create correct sized array of dicom structures before copying
    # https://stackoverflow.com/questions/28963354/typeerror-cant-pickle-generator-objects
    fullDCM.IonBeamSequence = [fullDCM.IonBeamSequence[0] for _ in range(spotData.numBeams)]
    for b in range(spotData.numBeams):
        fullDCM.IonBeamSequence[b] = deepcopy(fullDCM.IonBeamSequence[0])

    #  populate through all the beams with all the data
    for b in range(spotData.numBeams):
        fullDCM.IonBeamSequence[b].BeamNumber = b+1
        fullDCM.IonBeamSequence[b].BeamName = spotData.beam[b].bName + '-' + str(b+1)
        fullDCM.IonBeamSequence[b].FinalCumulativeMetersetWeight = sum([sum(c.sMeterset) for c in spotData.beam[b].CP])
        fullDCM.IonBeamSequence[b].NumberOfControlPoints = 2*spotData.beam[b].numCP

        ''' Where the Range Shifter data needs to be added if included - TO DO '''

        #  Creating Control Point entries
        #  2 for each position as need a 'start' and 'end for each point'
        fullDCM.IonBeamSequence[b].IonControlPointSequence = [fullDCM.IonBeamSequence[b].IonControlPointSequence[0], fullDCM.IonBeamSequence[b].IonControlPointSequence[1]]
        fullDCM.IonBeamSequence[b].IonControlPointSequence.extend([deepcopy(fullDCM.IonBeamSequence[b].IonControlPointSequence[1]) for _ in range(2*(spotData.beam[b].numCP-1))])

        #  filling in the Control Point information
        #  first control point in each beam contains additional data
        #  such as gantry angle etc.
        fullDCM.IonBeamSequence[b].IonControlPointSequence[0].GantryAngle = spotData.beam[b].gAngle
        fullDCM.IonBeamSequence[b].IonControlPointSequence[-1].CumulativeMetersetWeight = 0
        fullDCM.IonBeamSequence[b].IonControlPointSequence[0].CumulativeMetersetWeight = 0

        '''  more range shifter settings '''
        # fullDCM.IonBeamSequence[b].IonControlPointSequence[0].SnoutPosition
        # fullDCM.IonBeamSequence[b].IonControlPointSequence[0].Range Shifter Settings Sequence

        #  work through the control point sequences (2 control points for each energy)
        #  do start and finish element of each energy layer together for completeness
        for c in range(0, 2*spotData.beam[b].numCP, 2):
            #  Indexing
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].ControlPointIndex = c
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].ControlPointIndex = c+1

            #  number of spots in the layer
            #  used regularly enough to warrant for typing efficiency
            nSpots = len(spotData.beam[b].CP[c//2].X)

            #  spot energies
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].NominalBeamEnergy = spotData.beam[b].CP[c//2].En
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].NominalBeamEnergy = spotData.beam[b].CP[c//2].En

            #  number of spots at this energy
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].NumberOfScanSpotPositions = nSpots
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].NumberOfScanSpotPositions = nSpots

            #  setting spot position map, is a list of x, y coordinates all together
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotPositionMap = [coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair]
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotPositionMap = [coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair]

            #  Meterset weighting of each spot
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotMetersetWeights = spotData.beam[b].CP[c//2].sMeterset
            # Meterset weight for every second CP is 0.0, acts as end point for each spot
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotMetersetWeights = [0.0 for _ in range(nSpots)]

            #  the size of the spot at isocentre
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].ScanningSpotSize = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].ScanningSpotSize = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]

            #  sum of previous control points
            #  a CP with meterset listed doesn't add,
            #  the following with meterset 0.0 does add
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight = fullDCM.IonBeamSequence[b].IonControlPointSequence[c-1].CumulativeMetersetWeight
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight = fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight + sum(spotData.beam[b].CP[c//2].sMeterset)
            # and as a ratio of the total plane meterset
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient = fullDCM.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight / fullDCM.IonBeamSequence[b].FinalCumulativeMetersetWeight
            fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient = fullDCM.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight / fullDCM.IonBeamSequence[b].FinalCumulativeMetersetWeight

        fullDCM.IonBeamSequence[b].ReferencedPatientSetupNumber = b+1


    ###  finally output the new data to the output file
    fullDCM.save_as(oFile)







if __name__ == '__main__':
    #  data taken from pbtMod/docs/test.csv
    #  [gAngle, energy, X, Y, MU]
    data = [[0.0, 70.0, 10.0, 10.0, 100.0], [0.0, 70.0, 20.0, 20.0, 100.0], [0.0, 100.0, -10.0, -10.0, 200.0], [0.0, 100.0, -15.0, 20.0, 250.0], [0.0, 100.0, 10.0, 10.0, 80.0], [80.0, 70.0, 10.0, 10.0, 100.0], [80.0, 70.0, 20.0, 20.0, 100.0], [80.0, 100.0, -10.0, -10.0, 200.0], [310.0, 70.0, 20.0, 20.0, 100.0], [310.0, 100.0, -10.0, -10.0, 200.0], [310.0, 100.0, -15.0, 20.0, 250.0], [-180.0, 100.0, 10.0, 10.0, 80.0]]
    doseRate = 50.0

    from qaPlanInput import qaSpotArrange
    data = qaSpotArrange(data)
    '''
    becomes:
    {'pName': 'qaPlan', 'numBeams': 4, 'beam': [<dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E2E0>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E280>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E2B0>, <dataMod.dataClass.pbtDICOM.BEAMdata object at 0x000001D53F88E3A0>]}
    {'bName': 'G0.0', 'type': 'TREATMENT', 'gAngle': 0.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 730.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C70>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880CA0>]}
    {'En': 50.0, 'X': [10.0, 20.0], 'Y': [10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0, 100.0], 'sMU': []}
    {'En': 100.0, 'X': [-10.0, -15.0, 10.0], 'Y': [-10.0, 20.0, 10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0, 250.0, 80.0], 'sMU': []}
    {'bName': 'G-130.0', 'type': 'TREATMENT', 'gAngle': -130.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 80.0, 'numCP': 1, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C10>]}
    {'En': 100.0, 'X': [10.0], 'Y': [10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [80.0], 'sMU': []}
    {'bName': 'G80.0', 'type': 'TREATMENT', 'gAngle': 80.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 400.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880700>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880C40>]}
    {'En': 50.0, 'X': [10.0, 20.0], 'Y': [10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0, 100.0], 'sMU': []}
    {'En': 100.0, 'X': [-10.0], 'Y': [-10.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0], 'sMU': []}
    {'bName': 'G310.0', 'type': 'TREATMENT', 'gAngle': 310.0, 'cAngle': 0.0, 'bMetersetUnit': '', 'bMeterset': 550.0, 'numCP': 2, 'CP': [<dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F880670>, <dataMod.dataClass.pbtDICOM.SPOTdata object at 0x000001D53F8806D0>]}
    {'En': 50.0, 'X': [20.0], 'Y': [20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [100.0], 'sMU': []}
    {'En': 100.0, 'X': [-10.0, -15.0], 'Y': [-10.0, 20.0], 'sizeX': [], 'sizeY': [], 'sMeterset': [200.0, 250.0], 'sMU': []}
    '''

    qaSpotPrepare(data=data, doseRate=doseRate)
