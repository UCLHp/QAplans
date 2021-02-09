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







###  Obtain the input for creating custom QA plans
  #  To be determined for this
  #   - QA file type (single spot, energy plane, SOBP)
  #   - CSV input
  #   - Single angle or range of angles
  #   - Cubic or cylindrical phantom










###  Generate qaType which contains
  #  the spot patter - a single spot (SS), grid of spots (SG),
  #  or a custom pattern defined in a .csv file (CSV)
def qaPlanType(qaType={}):

    import os
    from easygui import buttonbox, fileopenbox



    # finding out what type of plan file the user wishes to create
    bxTitle = 'QA plan file stucture'
    # bxMsg = 'Select the QA file type you wish to create\n\n\
    #               SS-SE:  Single Spot at a Single Energy\n\
    #               SS-ME:  Single Spot at Multiple Energies\n\
    #              SS-MGA:  Single Spot at Multiple Gantry Angles\n\
    #               SG-SE:  Spot Grid (dose plane) at a Single Energy\n\
    #               SG-ME:  Spot Grid (dose plane) at Multiple Energies\n\
    #           SG-ME-MGA:  Spot Grid (dose plane) at Multiple Energies and Multiple Gantry Angles\n\
    #                 CSV:  Create a plan file from a pre-made .csv file of format:\n\
    #                       Gantry Angle, Energy, X, Y, MU'
    bxMsg = 'Select the QA file type you wish to create\n\n\
                  SG-SE:  Spot Grid (dose plane) at a Single Energy\n\
                  SG-ME:  Spot Grid (dose plane) at Multiple Energies\n\
                    CSV:  Create a plan file from a pre-made .csv file of format:\n\
                          Gantry Angle, Energy, X, Y, MU'
    # bxOpts = ['SS-SE', 'SS-ME', 'SS-MGA', 'SG-SE', 'SG-ME', 'SG-ME-MGA', 'CSV']
    bxOpts = ['SG-SE', 'SG-ME', 'CSV']
    qaType['type'] = buttonbox( title=bxTitle, msg=bxMsg, \
                                choices=bxOpts, cancel_choice=None )
    if qaType['type'] == None:
        print('Requires a defined spot pattern');  raise SystemExit()

    if qaType['type'] == 'CSV':
        #  request the CSV file
        qaType['file'] = fileopenbox( title='select .csv spot file', msg=None,
                                        default=os.getcwd(), filetypes='*.csv' )



    '''
    # is the output intended for the TPS or MC, or both
    bxTitle = 'TPS or MC'
    bxMsg = 'Do you need a QA file for the TPS, Monte-Carlo, or both'
    bxOpts = ['TPS', 'MC', 'both']
    qaType['output'] = buttonbox( title=bxTitle, msg=bxMsg, \
                                    choices=bxOpts, default_choice='TPS', \
                                    cancel_choice=None )
    if qaType['output'] == None:
        print('Output type must be defined');  raise SystemExit()
    '''



    return(qaType)







###  Using the values from qaPlanType, obtain all the necessary spot details
def qaSpotParameters(qaType=None):

    import os
    import re
    import numpy
    from easygui import buttonbox, multenterbox, fileopenbox



    # if the qaPlanType code has not been run and passed then call
    if not qaType:
        qaType=qaPlanType()



    #  setup for custom .CSV file input
    #  input file should have a single line per spot containing:
    #  header line starting with the '#' character
    #   - contain custom info such as DOSE RATE values ie:
    #     # DOSE RATE, 20
    #  gantry angle, energy, X, Y, MU
    if qaType['type'] == 'CSV':
        if qaType['file'] == None:
            #  request the CSV file
            qaType['file'] = fileopenbox( title='select .csv spot file', msg=None,
                                default=os.getcwd(), filetypes='*.csv' )

        planName = os.path.splitext(os.path.split(qaType['file'])[1])[0]

        head = []
        data = []
        with open(qaType['file']) as inFile:
            for line in inFile:
                if line.startswith('#'):
                    head.append(line.strip())
                    if 'DOSE RATE' in line:
                        doseRate = float(line.split(',')[1].strip())
                    if 'RS' in line:
                        rangeShifter = float(line.split(',')[1].strip())
                else:
                    data.append([float(_) for _ in line.strip().split(',')])



    #  if not a csv input then need to generate the dataset
    else:

        bxTitle = 'Field Parameters'
        bxMsg = 'Please enter the values to define the field\n\n'

        ''' consider creating a dictionary for the various input parameters
            May make it easier for calling at a later time '''
        ''' Also need to add functionality to control dose rate in spots '''

        if qaType['type'] == 'SS-SE':
            bxMsg = bxMsg + 'A single spot on the isocentre\n\nEnergy should be given in MeV\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Spot Energy', 'tMU per spot']
            bxVals = ['SS-SE', 270, 70, 50]

            planName, gAngle, Emin, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, sMU = ([float(gAngle)], float(Emin), float(sMU))
            Emax, delE, Nx, Ny, Sep = (Emin+1.0, 10.0, 1, 1, 0.0)


        elif qaType['type'] == 'SS-ME':
            bxMsg = bxMsg + 'A series of spots on the isocentre\n\nAll energies should be given in MeV\nEnergy spacing greater than ~2 MeV will require the placement of out of field spots to allow the ESS to adjust\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'tMU per spot']
            bxVals = ['SS-ME', 270, 70, 240, 5, 50]

            planName, gAngle, Emin, Emax, delE, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, Emax, delE, sMU = ([float(gAngle)], float(Emin), float(Emax), float(delE), float(sMU))
            Nx, Ny, Sep = (1, 1, 0.0)


        elif qaType['type'] == 'SS-MGA':
            bxMsg = bxMsg + 'A single spot on the isocentre, repeated at multiple gantry angles\n\nEnergy should be given in MeV\n\nGantry angles should be a comma separated list\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Spot Energy', 'tMU per spot']
            bxVals = ['SS-MGA', '0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330', 70, 50]

            planName, gAngle, Emin, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, sMU = ([float(_) for _ in gAngle.split(',')], float(Emin), float(sMU))  # gAngle = [float(_) for _ in gAngle.split(',')]
            Emax, delE, Nx, Ny, Sep = (Emin+1.0, 10.0, 1, 1, 0.0)


        elif qaType['type'] == 'SG-SE':
            bxMsg = bxMsg + 'A grid of spots at a single energy\nCan be used to either create a grid or dose plane\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Layer Energy', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
            bxVals = ['SG-SE', 270, 240, 5, 5, 7, 50]

            planName, gAngle, Emin, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, Nx, Ny, Sep, sMU = ([float(gAngle)], float(Emin), int(Nx), int(Ny), float(Sep), float(sMU))
            Emax, delE = (Emin+1.0, 10.0)


        elif qaType['type'] == 'SG-ME':
            bxMsg = bxMsg + 'A grid of spots at multiple energies\nCan be used to either create a series of grids, dose planes, or a dose cube\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
            bxVals = ['SG-ME', 270, 70, 240, 5, 3, 3, 7, 50]

            planName, gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = ([float(gAngle)], float(Emin), float(Emax), float(delE), int(Nx), int(Ny), float(Sep), float(sMU))


        elif qaType['type'] == 'SG-ME-MGA':
            bxMsg = bxMsg + 'A grid of spots at multiple energies and multiple gantry angles\nCan be used to either create a series of grids, dose planes, or a dose cube\n\nEnergy should be given in MeV\nCentral spot on beam-axis\nOdd number of spots required for symmetric fields\nGantry angles should be a comma separated list\n\ntMU is the technical MU used by Varian'
            bxOpts = ['Plan Name', 'Gantry Angle', 'Lowest Energy', 'Highest Energy', 'Energy spacing', 'Nspot X', 'Nspot Y', 'Spot spacing (mm)', 'tMU per spot']
            bxVals = ['SG-ME-MGA', '0, 90, 180, 270', 70, 240, 5, 3, 3, 7, 50]

            planName, gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
            gAngle, Emin, Emax, delE, Nx, Ny, Sep, sMU = ([float(_) for _ in gAngle.split(',')], float(Emin), float(Emax), float(delE), int(Nx), int(Ny), float(Sep), float(sMU))



        data = []
        #  now that have all the necessary values, generate the spots
        for an in gAngle:
            for en in numpy.arange(Emin, Emax, delE):
                for x in range(Nx):
                    for y in range(Ny):
                        data.append( [an, en, \
                                      (x-((Nx-1)/2))*Sep, \
                                      (y-((Ny-1)/2))*Sep, sMU] )



    # print(data)



    # if doseRate not already defined set to minimum MU
    try:
        doseRate
    except NameError:
        doseRate = min([_[4] for _ in data])


    try:
        rangeShifter
    except NameError:
        bxTitle = 'Range Shifter'
        bxMsg = 'Choose a Range Shifter if desired'
        bxOpts = ['None', '2 cm', '3 cm', '5 cm']
        rs = buttonbox( title=bxTitle, msg=bxMsg, choices=bxOpts, \
                        cancel_choice=None )
        if rs == 'None':  rangeShifter = None
        if rs == '2 cm':  rangeShifter = 2.0
        if rs == '3 cm':  rangeShifter = 3.0
        if rs == '5 cm':  rangeShifter = 5.0





    return(planName, data, doseRate, rangeShifter)







if __name__ == '__main__':

    x = qaPlanType()
    print(x)

    y = qaSpotParameters()
    print(y)
