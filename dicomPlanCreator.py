### add python modules folder in OS sensitive fashion
from os import path as osPath
from sys import path as sysPath
sysPath.append(osPath.join(osPath.split( sysPath[0])[0],'packages'))




'''
###   creates a dicom file from generated spot data
# requires a template dicom plan from which all data is stripped
# input should be in the dcmDATA format (see dicomClass.py) def
'''





# useage:   dcmPlanCreator(spotData=<dcmDATA class spots>, file=<template dicom file>, oFile=<output file location and name>)
def dicomPlanCreator(spotData=None, file=None, oFile=None):
    from fileOps import chooseFile
    from fileOps import chooseOutFile
    from dicomOps import dicomRead
    import datetime
    from random import randint
    from copy import deepcopy




    # if no dataset passed, request user input
    if spotData == None:
        spotData = qaSpotGenerator()




    # obtain the template plan, and read in the data
    ''' see if any way to store this within the plan but still give option '''
    if file == None:
        file, fPath, fName = chooseFile(title='select the template DICOM file to convert')
    else:
        fPath, fName = osPath.split(file)[0], osPath.split(file)[1]




    # obtain the output file location
    if oFile == None:
        oFile, oPath, oName = chooseOutFile() # dir=<directory>, fname=None)
    else:
        oPath, oName = osPath.split(oFile)[0], osPath.split(oFile)[1]




    fullDCMdata = dicomRead(file=file, title='select template dicom file')





    #  adjusting the date and time of plan creation to now
    fullDCMdata.RTPlanLabel = spotData.pName  # (300a,0002)
    fullDCMdata.RTPlanDate = datetime.datetime.now().strftime('%Y%m%d')  # (300a,0006)
    fullDCMdata.RTPlanTime = datetime.datetime.now().strftime('%H%M%S.%f')  # (300a,0007)



    #  SOPInstanceUID is the unique identifier for each plan
    #  Final 2 sections are a generated ID number and date/time stamp
    sopInstUID = fullDCMdata.SOPInstanceUID.rsplit('.',2)
    fullDCMdata.SOPInstanceUID = sopInstUID[0] + '.' + str(randint(10000, 99999)) + '.' + fullDCMdata.RTPlanDate + fullDCMdata.RTPlanTime.rsplit('.')[0]



    #  ReferencedBeamNumber and BeamMeterset
    #  Need one for each beam in plan, so multiply if separating energy layers
    fullDCMdata.FractionGroupSequence[0].NumberOfBeams = spotData.numBeams
    # setting all elements in ReferencedBeam Sequence to same as 1st
    # to duplicate a class object and all elements within need copy.deepcopy
    # deepcopy ensures there isn't inheritance so changes to one doesn't affect others
    fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence = [deepcopy(fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[0]) for _ in range(spotData.numBeams)]
    # now changing each BeamMeterset to sum of all sMeterset within beam
    for _ in range(spotData.numBeams):
        fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].BeamMeterset = sum([sum(c.sMeterset) for c in spotData.beam[_].CP])
        fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber = _+1



    # need a PatientSetupSequence for each beam
    fullDCMdata.PatientSetupSequence = [deepcopy(fullDCMdata.PatientSetupSequence[0]) for _ in range(spotData.numBeams)]
    for _ in range(spotData.numBeams):
        fullDCMdata.PatientSetupSequence[_].PatientSetupNumber = _+1



    # The meat and potatoes of it all
    # have to create correct sized array of dicom structures before copying
    # https://stackoverflow.com/questions/28963354/typeerror-cant-pickle-generator-objects
    fullDCMdata.IonBeamSequence = [fullDCMdata.IonBeamSequence[0] for _ in range(spotData.numBeams)]
    # then use copy.deepcopy([]) to populate each time
    for b in range(spotData.numBeams):
        fullDCMdata.IonBeamSequence[b] = deepcopy(fullDCMdata.IonBeamSequence[0])



    for b in range(spotData.numBeams):
        fullDCMdata.IonBeamSequence[b].BeamNumber = b+1
        fullDCMdata.IonBeamSequence[b].BeamName = spotData.beam[b].bName + '-' + str(b+1)
        fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight = sum([sum(c.sMeterset) for c in spotData.beam[b].CP])
        fullDCMdata.IonBeamSequence[b].NumberOfControlPoints = 2*spotData.beam[b].numCP
        # Here is where the Range Shifter data needs to be added if included - DO LATER
        # Creating Control Point entries
        # 2 for each position as need a 'start' and 'end for each point'
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence = [fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0], fullDCMdata.IonBeamSequence[b].IonControlPointSequence[1]]
        # again, need to use copy.deepcopy otherwise end up with inheritance!!!
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence.extend([deepcopy(fullDCMdata.IonBeamSequence[b].IonControlPointSequence[1]) for _ in range(2*(spotData.beam[b].numCP-1))])
        # filling in the Control Point information
        # first control point in each beam contains additional data such as gantry angle etc.
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].GantryAngle = spotData.beam[b].gAngle
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[-1].CumulativeMetersetWeight = 0
        fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].CumulativeMetersetWeight = 0
        # fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].SnoutPosition
        # more range shifter settings
        # fullDCMdata.IonBeamSequence[b].IonControlPointSequence[0].Range Shifter Settings Sequence

        for c in range(0, 2*spotData.beam[b].numCP, 2):
            # Indexing
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ControlPointIndex = c
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ControlPointIndex = c+1

            # number of spots used regularly enough to warrant for typing efficiency
            nSpots = len(spotData.beam[b].CP[c//2].X)

            # spot energies
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].NominalBeamEnergy = spotData.beam[b].CP[c//2].En
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].NominalBeamEnergy = spotData.beam[b].CP[c//2].En

            # number of spots at this energy
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].NumberOfScanSpotPositions = nSpots
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].NumberOfScanSpotPositions = nSpots

            # setting spot position map, is a list of x, y coordinates all together
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotPositionMap = [coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair]
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotPositionMap = [coord for pair in zip(spotData.beam[b].CP[c//2].X, spotData.beam[b].CP[c//2].Y) for coord in pair]

            # Meterset weighting of each spot
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanSpotMetersetWeights = spotData.beam[b].CP[c//2].sMeterset
            # Meterset weight for every second CP is 0.0, acts as end point for each spot
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanSpotMetersetWeights = [0.0 for _ in range(nSpots)]

            # the size of the spot at isocentre
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ScanningSpotSize = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ScanningSpotSize = [spotData.beam[b].CP[c//2].sizeX, spotData.beam[b].CP[c//2].sizeY]

            # sum of previous control points
            # a CP with meterset listed doesn't add, the following with meterset 0.0 does add
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c-1].CumulativeMetersetWeight
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight + sum(spotData.beam[b].CP[c//2].sMeterset)
            # and as a ratio of the total plane meterset
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c].CumulativeMetersetWeight / fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight
            fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient = fullDCMdata.IonBeamSequence[b].IonControlPointSequence[c+1].CumulativeMetersetWeight / fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight
        fullDCMdata.IonBeamSequence[b].ReferencedPatientSetupNumber = b+1


    fullDCMdata.save_as(oFile)
