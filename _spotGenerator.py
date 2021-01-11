### add python modules folder in OS sensitive fashion
from os import path as osPath
from sys import path as sysPath
# sysPath.append(osPath.join(osPath.split( sysPath[0])[0],'packages'))
# subtlety, as already in packages directory, just need to remove subdir name
sysPath.append(osPath.split(sysPath[0])[0])



'''
# generate a spot pattern based on the user input
# calculates the spot FWHM based on the match to SPTC data (2019-04-12)
# format matchs structure of dcmDATA format (dicomDataExtract in dataOps.py)
# but is a limited subset of that information - rest needs generating on fly
# qaPlanVals = [pname, numBeams, [beam]]
#              |_   [bName, gAngle, numCP, [CP]]
#                   |_   [En, [X], [Y], sizeX, sizeY, [sMeterset]]
'''





def spotGenerator(qaType=None):
    from _qaType import qaPlanType
    from easygui import fileopenbox, multenterbox
    from _pbtDICOM import PLANdata, BEAMdata, SPOTdata


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
        bxVals = ['SG-SE', 270, 240, 5, 5, 7, 50]

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
        bxVals = ['SG-ME-MGA', '0, 90, 180, 270', 70, 240, 5, 3, 3, 7, 50]

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

        csvFile = fileopenbox(title='Choose the .csv file containg the desired spot list')
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






if __name__ == '__main__':
    # from qaPlanCreator.qaType import qaPlanType
    # qaType = qaPlanType()
    # print(qaType)
    qaSpotGenerator(qaType=['CSV', 'TPS'])  # , 'Combined'])
