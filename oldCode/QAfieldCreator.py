# ### add python modules folder in OS sensitive fashion
from os import path as osPath
# from sys import path as sysPath
# sysPath.append(osPath.join(osPath.split(sysPath[0])[0],'packages'))



#############################################################################
###  packages developed separately and included for this standalone



#############################################################################
###  My custom Dicom data handling class for easier plan manipulation


class PLANdata:
    def __init__(self):
        self.pName = ''  # the name of the plan
        self.numBeams = ''  # number of beams
        self.beam = []  # list container to expand for each beam

class BEAMdata:
    def __init__(self):
        self.bName = ''  # beam name
        self.type = ''  # beam type (TREATMENT or SETUP)
        self.gAngle = ''  # gantry angle for this beam
        self.cAngle = ''  # couch angle for this beam
        self.bMetersetUnit = ''  # what units the Meterset parameter corresponds to
        self.bMeterset = ''  # the beam meterset
        self.numCP = ''  # number of control points for the beam
                         # each pair CP is an energy layer
        self.CP = []

class SPOTdata:
    def __init__(self):
        self.En = ''  # energy for that CP (== layer)
        self.X = []  # X position for each spot in layer
        self.Y = []  # Y position for each spot in layer
        self.sizeX = []  # TPS X FWHM (mm)
        self.sizeY = []  # TPS Y FWHM (mm)
        self.sMeterset = []  # meterset value for each spot
        self.sMU = [] # spot MU, this is calculated later but required at initialisation

#############################################################################



#############################################################################
# usage:
# oPath = chooseDir(title='<optional message here>')

def chooseDir(title='Please navigate INTO desired directory'):

    import tkinter
    from tkinter import filedialog

    root = tkinter.Tk()
    dr = filedialog.askdirectory(title=title)
    root.destroy()

    return(dr)

#############################################################################



#############################################################################
# useage:
# if file == None:
#     file, fPath, fName = chooseFile()  # title='')
# else:
#     fPath, fName = osPath.split(file)[0], osPath.split(file)[1]
# # from os import chdir  #  optional
# # chdir(fPath)          #  optional

def chooseFile(title='Please select file'):

    import tkinter
    from tkinter import filedialog
    from os import path as osPath

    root = tkinter.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(title=title)
    root.destroy()
    fPath, fName = osPath.split(file)[0], osPath.split(file)[1]

    return(file, fPath, fName)

#############################################################################



#############################################################################
# useage:
# if oFile == None:
#     oFile, oPath, oName = chooseOutFile() # oPath=<directory>, oName=None)
# else:
#     fPath, fName = osPath.split(file)[0], osPath.split(file)[1]

def chooseOutFile(oPath=None, oName=None):

    from os import path as osPath
    from easygui import multenterbox

    if oPath == None:
        oPath = chooseDir()
    if oName == None:
        bxTitle = 'Output file'
        bxMsg = 'Please provide the output file location and name'
        bxOpts = ['file path', 'file name']
        oPath, oName = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=[oPath, oName])
    oFile = osPath.join(oPath, oName)

    return(oFile, oPath, oName)

#############################################################################



#############################################################################
# useage:
# ftype, data = fileRead(file=<filepath>)
''' want to extract the fileType part of the programme '''

def fileRead(file=None):

    # from fileOps.selectFile import chooseFile
    # from dicomOps.dicomFile import dicomRead
    from easygui import buttonbox

    if file == None:
        file, fpath, fname = chooseFile()
    else:
        fpath, fname = file.rsplit('/', 1)[0], file.rsplit('/', 1)[1]

    ###  for specific file formats call appropriate functions  ###
    if 'w2cad' in fname:
        ftype = 'w2cad'
        data = w2cadRead(file=file)
    if 'csv' in fname:
        ftype = 'csv'
        param = fileParam(param=['#', ',', 'n', 'n'])
        data = dataRead(file=file, param=param)
    if 'dcm' in fname:
        ftype = 'dicom'
        data = dicomRead(file=file)

    else:
        ###  or if there is no indicator of the file type
        ###  ask user to identify the file type
        if ftype == None:
            bxTitle = 'Select file type'
            bxMsg = 'Select file type if known'
            bxChoice = ['Don\'t know', 'w2cad', 'csv', '1D data', '2D data']
            ftype = buttonbox(title=bxTitle, msg=bxMsg, choices=bxChoice, default_choice=bxChoice[0], cancel_choice=bxChoice[0])
        # if no selection or 'Don't know' selected then exit
        if ftype == bxChoice[0]:
            print('unknown file type, now exiting')
            exit()
        if param == None:
            param = fileParam()
        # otherwise call the appropriate data reading function
        elif ftype == 'w2cad':
            ftype, data = w2cadRead(file=file)
        elif ftype == '1D data':
            data = dataRead(file=file, param=param)
        elif ftype == '2D data':
            data = dataRead(file=file, param=param)
        elif ftype == 'csv':
            param = fileParam(param=['#', ',', 'n', 'n'])
            data = dataRead(file=file, param=param)

    return(ftype, data)
#############################################################################



#############################################################################
# useage:
# data = dataRead(file=<filepath>, param=[<header>, <delimiter>, <Col Title>, <Row Title>])

def dataRead(file=None, param=None):

    from fileOps.dataClass import TWODdata

    # check a file has been passed to the subprogramme
    if file == None:
        print('sub-programme dataRead requires a file string for input')
        exit()
    if param == None:
        print('no paramters supplied for header, delimiter, and title indicators\nneed to call fileOps/fileParam and pass to dataRead')
        exit()

    data = TWODdata()

    with open(file) as f:
        for line in f:
            # assign header lines
            if line.startswith(param[0]):
                data.head.append(line.lstrip(param[0]).strip())
            else:
                # separate values and remove white space
                ln = [l.strip() for l in line.strip().split(str(param[1]))]
                # for files with titles to the columns
                if param[2] == 'y':
                    if param[3] == 'y': data.colTitle = ln[1:]
                    else: data.colTitle = ln
                    param[2] = 'n'
                else:
                    # for files with row titles
                    if param[3] == 'y':
                        data.rowTitle.append(ln[0])
                        data.row.append(ln[1:])
                    else:
                        data.row.append(ln)
    # transpose the row data to columns
    data.col = list(map(list, zip(*data.row)))
    return(data)
#############################################################################



#############################################################################
def dicomRead(file=None, title=None):
    # from fileOps import chooseFile
    from pydicom.filereader import dcmread

    if file == None:
        file, fpath, fname = chooseFile(title)
    else:
        fPath, fName = osPath.split(file)[0], osPath.split(file)[1]

    dcmFullData=dcmread(file)
    return(dcmFullData)
#############################################################################



#############################################################################
# identify the type of QA plan to generate and type of output to create
# qaType = [['SS-ME', 'SG-SE', 'SG-ME', 'CSV'], ['TPS', 'MC', 'both']]


def qaPlanType(qaType=[None, None]):
    from easygui import buttonbox

    # finding out what type of plan file the user wishes to create
    if qaType[0] == None:
        bxTitle = 'QA plan file stucture'
        bxMsg = 'Select the QA file type you wish to create\n\n\
                      SS-SE:  Single Spot at a Single Energy\n\
                      SS-ME:  Single Spot at Multiple Energies\n\
                     SS-MGA:  Single Spot at Multiple Gantry Angles\n\
                      SG-SE:  Spot Grid (dose plane) at a Single Energy\n\
                      SG-ME:  Spot Grid (dose plane) at Multiple Energies\n\
                  SG-ME-MGA:  Spot Grid (dose plane) at Multiple Energies and Multiple Gantry Angles\n\
                        CSV:  Create a plan file from a pre-made .csv file of spot positions, energies, and MUs'
        bxOpts = ['SS-SE', 'SS-ME', 'SS-MGA', 'SG-SE', 'SG-ME', 'SG-ME-MGA', 'CSV']
        qaType[0] = buttonbox(title=bxTitle, msg=bxMsg, choices=bxOpts, cancel_choice=None)
        if qaType[0] == None:  exit()

    # is the output intended for the TPS or MC, or both
    if qaType[1] == None:
        bxTitle = 'TPS or MC'
        bxMsg = 'Do you need a QA file for the TPS, Monte-Carlo, or both'
        bxOpts = ['TPS', 'MC', 'both']
        qaType[1] = buttonbox(title=bxTitle, msg=bxMsg, choices=bxOpts, default_choice='TPS', cancel_choice=None)
        if qaType[1] == None:  exit()


    return(qaType)

#############################################################################



#############################################################################
###  generate a spot pattern based on the user input
  #  calculates the spot FWHM based on the match to SPTC data (2019-04-12)
  #  format matchs structure of dcmDATA format (dicomDataExtract in dataOps.py)
  #  but is a limited subset of that information - rest needs generating on fly
  #  qaPlanVals = [pname, numBeams, [beam]]
  #               |_   [bName, gAngle, numCP, [CP]]
  #                    |_   [En, [X], [Y], sizeX, sizeY, [sMeterset]]


def qaSpotGenerator(qaType=None):
    # from qaPlanCreator import qaPlanType
    from easygui import multenterbox
    # from fileOps import chooseFile, fileRead
    # from dicomOps import PLANdata, BEAMdata, SPOTdata


    if qaType == None:
        print('function requires a plan type to create a spot list')
        exit()


    bxTitle = 'Field Parameters'
    bxMsg = 'Please enter the values to define the field\n\n'

    ''' consider creating a dictionary for the various input parameters
        May make it easier for calling at a later time '''
    ''' Also need to add functionality to control dose rate in spots '''

    if qaType[0] == 'SS-SE':
        bxMsg = bxMsg + 'A single spot on the isocentre\n\nEnergy should be given in MeV\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Spot Energy', 'tMU per spot']
        bxVals = ['SS-SE', 270, 70, 50]

        planName, gAngle, Emax, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emax, sMU = ([float(gAngle)], float(Emax), float(sMU))
        Emin, delE, Nx, Ny, Sep = (Emax+1.0, 10.0, 1, 1, 0.0)


    elif qaType[0] == 'SS-ME':
        bxMsg = bxMsg + 'A series of spots on the isocentre\n\nAll energies should be given in MeV\nEnergy spacing greater than ~2 MeV will require the placement of out of field spots to allow the ESS to adjust\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'tMU per spot']
        bxVals = ['SS-ME', 270, 70, 240, 5, 50]

        planName, gAngle, Emin, Emax, delE, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emin, Emax, delE, sMU = ([float(gAngle)], float(Emin), float(Emax), float(delE), float(sMU))
        Nx, Ny, Sep = (1, 1, 0.0)


    elif qaType[0] == 'SS-MGA':
        bxMsg = bxMsg + 'A single spot on the isocentre, repeated at multiple gantry angles\n\nEnergy should be given in MeV\n\nGantry angles should be a comma separated list\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Spot Energy', 'tMU per spot']
        bxVals = ['SS-MGA', '0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330', 70, 50]

        planName, gAngle, Emax, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emax, sMU = ([float(_) for _ in gAngle.split(',')], float(Emax), float(sMU))  # gAngle = [float(_) for _ in gAngle.split(',')]
        Emin, delE, Nx, Ny, Sep = (Emax+1.0, 10.0, 1, 1, 0.0)


    elif qaType[0] == 'SG-SE':
        bxMsg = bxMsg + 'A grid of spots at a single energy\nCan be used to either create a grid or dose plane\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Layer Energy', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
        bxVals = ['SG-SE', 270, 240, 41, 41, 2.5, 10]

        planName, gAngle, Emax, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emax, Nx, Ny, Sep, sMU = ([float(gAngle)], float(Emax), int(Nx), int(Ny), float(Sep), float(sMU))
        Emin, delE = (Emax+1.0, 10.0)


    elif qaType[0] == 'SG-ME':
        bxMsg = bxMsg + 'A grid of spots at multiple energies\nCan be used to either create a series of grids, dose planes, or a dose cube\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
        bxVals = ['SG-ME', 270, 70, 240, 5, 3, 3, 7, 50]

        planName, gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = ([float(gAngle)], float(Emin), float(Emax), float(delE), int(Nx), int(Ny), float(Sep), float(sMU))


    elif qaType[0] == 'SG-ME-MGA':
        bxMsg = bxMsg + 'A grid of spots at multiple energies and multiple gantry angles\nCan be used to either create a series of grids, dose planes, or a dose cube\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\nGantry angles should be a comma separated list\n\ntMU is the technical MU used by Varian'
        bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
        bxVals = ['SG-ME-MGA', '0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330', 70, 240, 5, 3, 3, 7, 50]

        planName, gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
        gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = ([float(_) for _ in gAngle.split(',')], float(Emin), float(Emax), float(delE), int(Nx), int(Ny), float(Sep), float(sMU))


    elif qaType[0] == 'CSV':
        # this next bit I'm using in testing, still need to do a CSV setup
        ###  format for input
          #  plan name
          #  [BLANK], beam name, gantry angle
          #  [BLANK], [BLANK], [BLANK], energy (MeV), X position (mm from isocentre), Y position (mm from isocentre), tMU
          #  [BLANK], beam name, gantry angle
          #  ....... (repeat for each desired beam)

        csvFile = chooseFile(title='Choose the .csv file containg the desired spot list')
        line = [l.strip().split(',') for l in open(csvFile[0]) if '#' not in l]

        #  populate the plan data structure from the CSV file
        qaPlanVals = []
        planN=-1

        cpN = -1
        for ln in line:
            if len(ln) == 1:
                qaPlanVals.append(PLANdata())
                planN += 1
                beamN=-1
                qaPlanVals[planN].pName = str(ln[0])
                qaPlanVals[planN].numBeams = 0
            if len(ln) == 3:
                qaPlanVals[planN].beam.append(BEAMdata())
                qaPlanVals[planN].numBeams += 1
                beamN += 1
                cpN = -1
                qaPlanVals[planN].beam[beamN].bName = str(ln[1])
                qaPlanVals[planN].beam[beamN].gAngle = float(ln[2])
                qaPlanVals[planN].beam[beamN].numCP = 0
            if len(ln) == 7:
                qaPlanVals[planN].beam[beamN].CP.append(SPOTdata())
                qaPlanVals[planN].beam[beamN].numCP += 1
                cpN += 1
                qaPlanVals[planN].beam[beamN].CP[cpN].En = float(ln[3])
                FWHM = 28.9 - (0.338*float(ln[3])) + (2.32e-3)*(float(ln[3])**2) - (7.39e-6)*(float(ln[3])**3) + (9.04e-9)*(float(ln[3])**4)
                qaPlanVals[planN].beam[beamN].CP[cpN].sizeX = FWHM
                qaPlanVals[planN].beam[beamN].CP[cpN].sizeY = FWHM
                qaPlanVals[planN].beam[beamN].CP[cpN].X = float(ln[4])
                qaPlanVals[planN].beam[beamN].CP[cpN].Y = float(ln[5])
                qaPlanVals[planN].beam[beamN].CP[cpN].sMeterset = float(ln[6])
            elif len(ln) not in {1, 3, 7}:
                print('CSV file not properly formatted, incorrect number of datapoints\nexiting')
                exit()


    ''' perhaps a visualisation of the spot distribution as a check '''


    if 'CSV' not in qaType[0]:
        #  based on the plan setup values obtained, create spot grid
        #  creates each plan with a beam for each gantry angle
        #  energy layers are not separated within the beam
        qaPlanVals = PLANdata()

        qaPlanVals.pName = planName
        qaPlanVals.numBeams = len(gAngle)

        ''' for the energy, need to adjust to fill in the energy gaps\
            between layers for TPS '''
        qaPlanVals.beam = [BEAMdata() for _ in range(qaPlanVals.numBeams)]  # will need to expand if doing multiple beams
        for b, beam in enumerate(qaPlanVals.beam):
            beam.bName = 'G' + str(gAngle[b]) + '--' + qaType[0]
            beam.gAngle = gAngle[b]
            beam.CP = [SPOTdata() for _ in range(int(Emin), int(Emax)+int(delE), int(delE))]
            beam.numCP = len(beam.CP)

            for c,controlPoint in enumerate(beam.CP):
                ''' need to also add in intervening energy layers so not\
                    jumping too far in energy between layers '''
                controlPoint.En = float(Emax - c*delE)
                # equation from fitting SPTC data in google drive
                FWHM = 28.9 - (0.338*controlPoint.En) + (2.32e-3)*(controlPoint.En**2) - (7.39e-6)*(controlPoint.En**3) + (9.04e-9)*(controlPoint.En**4)
                controlPoint.sizeX = FWHM
                controlPoint.sizeY = FWHM
                ''' need to adjust writing order to achieve back and\
                    forth scanning of spots for better delivery '''
                for x in range(Nx):
                    for y in range(Ny):
                        controlPoint.X.append((x-((Nx-1)/2))*Sep)
                        controlPoint.Y.append((y-((Ny-1)/2))*Sep)
                        controlPoint.sMeterset.append(float(sMU))


    ###  Need to add in a whole slew of error handling to catch bad input  ###
    ###  Error handling and spot data ordering  ###
      #  Check a plan actually contains beams


    return(qaPlanVals)

#############################################################################



#############################################################################
###   creates a dicom file from generated spot data
# requires a template dicom plan from which all data is stripped
# input should be in the dcmDATA format (see dicomClass.py) def


# useage:   dcmPlanCreator(spotData=<dcmDATA class spots>, file=<template dicom file>, oFile=<output file location and name>)
def dicomPlanCreator(spotData=None, file=None, oFile=None):
    # from fileOps import chooseFile
    # from fileOps import chooseOutFile
    # from dicomOps import dicomRead
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
        ''' I'm hoping this hack will fix the beam labelling issues '''
        ''' replacing all instances of _+1 with ReferencedBeamNumber+_ '''
        fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber = fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber+_



    # need a PatientSetupSequence for each beam
    fullDCMdata.PatientSetupSequence = [deepcopy(fullDCMdata.PatientSetupSequence[0]) for _ in range(spotData.numBeams)]
    for _ in range(spotData.numBeams):
        fullDCMdata.PatientSetupSequence[_].PatientSetupNumber = fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber+_



    # The meat and potatoes of it all
    # have to create correct sized array of dicom structures before copying
    # https://stackoverflow.com/questions/28963354/typeerror-cant-pickle-generator-objects
    fullDCMdata.IonBeamSequence = [fullDCMdata.IonBeamSequence[0] for _ in range(spotData.numBeams)]
    # then use copy.deepcopy([]) to populate each time
    for b in range(spotData.numBeams):
        fullDCMdata.IonBeamSequence[b] = deepcopy(fullDCMdata.IonBeamSequence[0])



    for b in range(spotData.numBeams):
        ''' I'm hoping this hack will fix the beam labelling issues '''
        ''' similarly replacing all instances of b+1 with ReferencedBeamNumber+b '''
        fullDCMdata.IonBeamSequence[b].BeamNumber = fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber+b
        fullDCMdata.IonBeamSequence[b].BeamName = spotData.beam[b].bName + '-' + str(fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber+b)
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
        fullDCMdata.IonBeamSequence[b].ReferencedPatientSetupNumber = fullDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[_].ReferencedBeamNumber+b


    fullDCMdata.save_as(oFile)

#############################################################################





'''
#############################################################################
###   Create a QA plan file either for TPS or MC
# User input required to create either single spots of spot grids
# Will also later have ability to input CSV of spot positions and weights
#############################################################################
'''



# identify the type of QA plan to create
# from qaPlanCreator import qaPlanType
planType = qaPlanType([None, 'TPS'])
# for testing - setting to most complex scenario
# [['SS-SE', 'SS-ME', 'SS-MGA', 'SG-SE', 'SG-ME', 'SG-ME-MGA', 'CSV'], ['TPS', 'MC', 'both']]
# planType = qaType(['SG-SE', 'MC'])



# generate the spot data for the QA plan
# produced data in the format
# qaPlanVals = [pName, numBeams, [beam]]
#              |_   [bName, gAngle, numCP, [CP]]
#                   |_   [En, [X], [Y], sizeX, sizeY, [sMeterset]]
# from qaPlanCreator import qaSpotGenerator
spotData = qaSpotGenerator(planType)
# # to expand to a 3 beam plan for testing purposes
# spotData.numBeams = 3
# from copy import deepcopy
# spotData.beam = [deepcopy(spotData.beam[0]) for _ in range(spotData.numBeams)]





'''
# should the plan be split into individual energy layers
# if qaType[0] == None:
if 'ME' in qaType[0]:
    bxTitle = 'Separate plans?'
    # bxMsg = 'Do you wish to split each beam into separate energy layers?\n\nIf so, the plan will be split into MULITPLE PLANS\nEach plan will be a single energy layer for a single beam\n\nPlan naming convention will be:  <plan name>-<beam name>-<energy>.dcm\n\nOnly recommended for single beam QA plans'
    bxMsg = 'Do you wish to split the spots into MULTIPLE PLANS?\nEach plan will be a single energy layer or gantry angle\n\nOnly recommended for single beam QA plans'
    bxOpts = ['Separate', 'Combined']
    qaType.append(buttonbox(title=bxTitle, msg=bxMsg, choices=bxOpts, default_choice='Combined', cancel_choice=None))
    if qaType[2] == None:  exit()
'''



# splitting the data if necessary to create multiple plans
# from dicomOps import PLANdata, BEAMdata, SPOTdata



#  options to create:
#   - plan as if was from TPS, all layers combined
#   - if from a single beam angle:
#       - each energy layer in a separate beam
#       - If 'Separate' selected, each energy layer in a separate plan
#   - if from multiple beam angles:
#       - if only a single energy layer will already be covered by stock
#       - if multiple energy layers, separate plans both for each gantry angle
#         with all energy layers (separate beams),
#         and each energy layer with all gantry angles



#  add spotData into qaPlans as a list to be passed when creating DICOM plans - this is the basic minimum dataset
qaPlans = [spotData]

#  if a single gantry angle and tf single beam
if qaPlans[0].numBeams == 1:
    qaPlans.append(PLANdata())

    ### creating plan with each energy layer in its own beam

    #  set the plan name and setup beam containers
    qaPlans[1].pName = qaPlans[0].pName + '--sepE'
    #  each CP represents an energy layer, spotGenerator only creates one CP per energy layer, reading from TPS has 2, the second of each needs to be excluded.
    qaPlans[1].beam = [BEAMdata() for _ in range(qaPlans[0].beam[0].numCP)]
    qaPlans[1].numBeams = len(qaPlans[1].beam)

    #  creating individual beams for each energy layer
    # for b,beam in enumerate(qaPlans[0].beam):
    b = 0
    for layer in qaPlans[0].beam[0].CP:
        qaPlans[1].beam[b].bName = qaPlans[0].beam[0].bName.split('--')[0] + '--E' + str(layer.En)
        qaPlans[1].beam[b].gAngle = qaPlans[0].beam[0].gAngle
        qaPlans[1].beam[b].numCP = 1
        qaPlans[1].beam[b].CP = [layer]
        b += 1

#  else if multiple gantry angles and tf multiple beams

elif qaPlans[0].numBeams > 1:
    ''' doing something strange with beam naming\
        see Issue raised in GitHub and try to fix later '''
    # check if more than one energy layer for each gantry angle
    # and all gantry angles have same number of energy layers
    if all(_ > 1 for _ in [beam.numCP for beam in qaPlans[0].beam]) and all(_ == _ for _ in [beam.numCP for beam in qaPlans[0].beam]):

        p = 1
        # one plan per energy layer with each gantry angle in a beam
        qaPlans.extend([PLANdata() for _ in range(qaPlans[0].beam[0].numCP)])
        for e in range(qaPlans[0].beam[0].numCP):
            qaPlans[p].pName = qaPlans[0].pName + '--E' + str(qaPlans[0].beam[0].CP[e].En)
            qaPlans[p].beam = [BEAMdata() for _ in range(qaPlans[0].numBeams)]
            qaPlans[p].numBeams = len(qaPlans[p].beam)
            for b, beam in enumerate(qaPlans[p].beam):
                beam.bName = qaPlans[0].beam[0].bName
                beam.gAngle = qaPlans[0].beam[b].gAngle
                beam.numCP = 1
                beam.CP = [qaPlans[0].beam[b].CP[e]]
            p += 1

        # one plan per gantry angle with each energy level in a beam
        qaPlans.extend([PLANdata() for _ in range(qaPlans[0].numBeams)])
        for b,beam in enumerate(qaPlans[0].beam):
            qaPlans[p].pName = qaPlans[0].pName + '--G' + str(beam.gAngle)
            qaPlans[p].beam = [BEAMdata() for _ in range(beam.numCP)]
            qaPlans[p].numBeams = len(qaPlans[p].beam)

            #  creating individual beams for each energy layer
            for e,layer in enumerate(beam.CP):
                qaPlans[p].beam[e].bName = qaPlans[0].beam[0].bName.split('--')[0] + '--E' + str(layer.En)
                qaPlans[p].beam[e].gAngle = qaPlans[0].beam[b].gAngle
                qaPlans[p].beam[e].numCP = 1
                qaPlans[p].beam[e].CP = [layer]
            p +=1

    # if not and only single energy layer
    elif all(_ == 1 for _ in [beam.numCP for beam in qaPlans[0].beam]):
        # the standard dataset will cover the required plans
        pass


    ''' I think I need some error handling here if\
        mixed energy layers and gantry angles '''

else:
    print('No beams????')
    exit()



###  Writing out depending on the selected output
# from fileOps import chooseFile

if planType[1] in ('TPS', 'both'):
    #  location of the template DICOM file to amend
    file, fPath, fName = chooseFile(title='select the template DICOM file to convert')

    # selecting an output location and then creating dicom files
    # from fileOps import chooseDir
    oPath = chooseDir(title='Navigate INTO the output directory for TPS')

    #  writing out to dicom files
    # useage:   dcmPlanCreator(spotData=<dcmDATA class spots>, file=<template dicom file>, oFile=<output file location and name>)
    # from dicomOps import dicomPlanCreator
    for plan in qaPlans:
        oFile = osPath.join(oPath, str(plan.pName) + '.dcm')
        # print('oFile: ', oFile)
        dicomPlanCreator(spotData=plan, file=file, oFile=oFile)



# if planType[1] in ('MC', 'both'):
#     #  selecting an output location for the MC files
#     from fileOps import chooseDir
#     oPath = chooseDir(title='Navigate INTO the output directory for MC')
#
#     #  writing out to MC macros
#     from qaPlanCreator import mcSourceCreator
#     for plan in qaPlans:
#         oFile = osPath.join(oPath, str(plan.pName) + '.mac')
#         mcSourceCreator(spotData=plan, oFile=oFile)
