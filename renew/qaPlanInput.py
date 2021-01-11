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
    from easygui import buttonbox

    #  User to define the spot pattern to produce
    bxTitle = 'Spot pattern'
    bxMsg = 'Select the spot pattern you wish:\n\n\
                  SS:  Single spot on central axis\n\
                  SG:  Grid of spots\n\
                 CSV:  A pre-made spot pattern stored as .csv'#\n\
                # SOBP:  Spread Out Bragg Peak\n\
    bxOpts = ['SS', 'SG', 'CSV']# , 'SOBP']
    qaType['type'] = buttonbox(title=bxTitle, msg=bxMsg, \
                               choices=bxOpts, cancel_choice=None)
    #  if cancelled the choice, give error message and exit the programme
    if not qaType['type']:
        print('Requires a defined spot pattern')
        raise SystemExit()


    #  if CSV input then different process
    if qaType['type'] != 'CSV':


        #  User to define if single of multiple energy layers
        bxTitle = 'Energy layers'
        bxMsg = 'Select whether a single energy layer or multiple:\n\n\
                      SE:  Single energy\n\
                      ME:  Multiple energy layers'
        bxOpts = ['SE', 'ME']
        qaType['layer'] = buttonbox(title=bxTitle, msg=bxMsg, \
                                    choices=bxOpts, cancel_choice=None)
        #  if cancelled the choice, give error message and exit the programme
        if not qaType['layer']:
            print('Must select either single of multiple energy layers')
            raise SystemExit()


        #  User to define if single of multiple gantry angles
        bxTitle = 'Gantry angles'
        bxMsg = 'Select whether a single energy layer or multiple:\n\n\
                      SA:  Single angle\n\
                      MA:  Multiple angles'
        bxOpts = ['SA', 'MA']
        qaType['angle'] = buttonbox(title=bxTitle, msg=bxMsg, \
                                    choices=bxOpts, cancel_choice=None)
        #  if cancelled the choice, give error message and exit the programme
        if not qaType['angle']:
            print('Required to define at least one gantry angle')
            raise SystemExit()

    return(qaType)







###  Using the values from qaPlanType, obtain all the necessary spot details
def qaSpotDefine(qaType=None):
    from easygui import buttonbox, multenterbox, fileopenbox
    import re

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
        #  request the CSV file
        file = fileopenbox(title='select .csv spot file', msg=None,
                              default='*', filetypes='*.csv')

        head = []
        data = []
        with open(file) as inFile:
            for line in inFile:
                if line.startswith('#'):
                    head.append(line.strip())
                    if 'DOSE RATE' in line:
                        doseRate = float(line.split(',')[1].strip())
                else:
                    data.append([float(_) for _ in line.strip().split(',')])


    #  if not a csv input then need to generate the dataset
    else:

        #  These lists will house the spot values
        spots = []
        layers = []
        angles = []


        #  User to define spot position either on the central axis
        #  or at some distance off-axis as defined in mm
        if qaType['type'] == 'SS':
            bxTitle = 'Spot position'
            bxMsg = 'Do you want on-axis or off-axis spot?'
            bxOpts = ['on-axis', 'off-axis']
            axis = buttonbox(title=bxTitle, msg=bxMsg, \
                             choices=bxOpts, cancel_choice=None)
            if not axis:
                print('Position for single spot required')
                raise SystemExit()

            if axis == 'on-axis':
                spots = [[0.0, 0.0]]
            elif axis == 'off-axis':
                bxTitle = 'Spot positions'
                bxMsg = 'Enter off-axis position of spot\n\n \
                         position given in mm at isocentre'
                bxNames = ['X position', 'Y position']
                bxValues = ['0.0', '0.0']  #  default values in box for on-axis
                vals = multenterbox(bxTitle, bxMsg, bxNames, bxValues)
                spots = [[float(_) for _ in vals]]

        #  User to define spot grid size in cm and spot spacing in mm
        if qaType['type'] == 'SG':
            bxTitle = 'Grid size'
            bxMsg = 'Select a pre-determined grid size (in cm)\n \
                      - or define a custom grid size (in cm)'
            bxOpts = ['5x5', '10x10', '15x15', '20x20', '30x40', 'custom']
            grid = buttonbox(title=bxTitle, msg=bxMsg, \
                             choices=bxOpts, cancel_choice=None)
            if not grid:
                print('Grid size must be selected')
                raise SystemExit()

            bxTitle = 'Grid size'
            bxMsg = 'Confirm or enter a different grid size (in cm) if desired\n\n \
                      - maximum X grid size:  30 cm\n \
                      - maximum Y grid size:  40 cm\n\n \
                     Also enter spot separation in mm'
            bxNames = ['X size (cm)', 'Y size (cm)', 'Separation (mm)']
            # pre-fill box size if preset values selected
            if grid != 'custom':
                bxValues = [float(_) for _ in grid.split('x')]
            else: bxValues = ['', '']
            bxValues.extend('5.0')
            vals = multenterbox(bxMsg, bxTitle, bxNames, bxValues)
            size = [float(_) for _ in vals]
            sep = size.pop()

            #  for info supplied, generate spots
            #  spots grid defined out from central spot
            #  everything from here in mm
            nx = int(((size[0]*10)/2)//sep)
            ny = int(((size[1]*10)/2)//sep)
            for x in range(-1*nx, nx):
                for y in range(-1*ny, ny):
                    spots.append([x*sep, y*sep])


        #  user to supply energy layers, first checking the layer value defined
        #  created to accept a list with verious separators
        if 'layer' in qaType.keys():

            bxTitle = 'Energy Layers'
            bxMsg = 'Please enter the required energy/energies\n\n \
                     Multiple energies should be entered as a single list'
            bxNames = ['Energy']
            vals = multenterbox(bxMsg, bxTitle, bxNames)

            if not vals:
                print('At least one energy layer value required')
                raise SystemExit()

            if qaType['layer'] == 'SE':
                layers = [float(vals[0])]

            #  split the input list text, split by various delimeters
            #  using regex to remove range of delimeters, 'if _' to ignore empty
            if qaType['layer'] == 'ME':
                layers = [float(_) for _ in re.split(',|;| |\n', vals[0]) if _]


        #  user to supply gantry angles, first checking the layer value is defined
        #  created to accept a list with verious separators
        if 'angle' in qaType.keys():

            bxTitle = 'Gantry Angles'
            bxMsg = 'Please enter the required gantry angle/s\n\n \
                     Multiple gantry angles should be entered as a single list'
            bxNames = ['Angles']
            vals = multenterbox(bxMsg, bxTitle, bxNames)

            if not vals:
                print('At least one gantry angle value required')
                raise SystemExit()

            if qaType['angle'] == 'SA':
                angles = [float(vals[0])]

            #  split the input list text, split by various delimeters
            #  using regex to remove range of delimeters, 'if _' to ignore empty
            if qaType['angle'] == 'MA':
                angles = [float(_) for _ in re.split(',|;| |\n', vals[0]) if _]


        #  Obtain a value for the dose per spot and a doserate if a different
        #  value desired
        bxTitle = 'Dose per spot'
        bxMsg = 'Please enter the required dose per spot\n\n \
                 If a specific dose rate is required, provide this\n \
                  - the spcified dose rate MUST be less than or equal to half \
                    of the dose per spot otherwise the delivered dose rate \
                    will be the remaining MU as the smaller element.'
        bxNames = ['Dose', 'Dose rate']
        (dose, doseRate) = multenterbox(bxMsg, bxTitle, bxNames)


        data = []
        #  now that have all the necessary values, generate the spots
        for an in angles:
            for en in layers:
                for sp in spots:
                    data.append([an, en, sp[0], sp[1], dose])

    return(data, doseRate)







###  From a list of spots in the simple list format:
  #  gantry angle, energy, x, y, MU
  #  convert to the pre-generated pbtDICOM classes
def qaSpotArrange(data=None):

    from pbtDICOM import PLANdata, BEAMdata, SPOTdata

    if not data:
        from pbtMod.qaPlanInput import qaSpotDefine
        data, doseRate = qaSpotDefine()


    qaPlan = PLANdata()
    qaPlan.pName = 'qaPlan'

    #  identify the number of unique beam angles
    angleSet = set([_[0] for _ in data])
    qaPlan.numBeams = len(angleSet)
    #  create a beam entry for each beam angle
    qaPlan.beam = [BEAMdata() for _ in range(len(angleSet))]

    for an, angle in enumerate(angleSet):
        #  extract the data at this beam angle
        beamData = [_ for _ in data if _[0] == angle]
        #  input various parameters for this beam angle
        qaPlan.beam[an].bName = 'G'+str(angle)
        qaPlan.beam[an].type = 'TREATMENT'
        qaPlan.beam[an].gAngle = angle
        qaPlan.beam[an].cAngle = 0.0
        qaPlan.beam[an].bMeterset = sum(map(float,[_[4] for _ in beamData]))

        #  identify the number of energy layers at this angle
        energies = set([_[1] for _ in beamData])
        qaPlan.beam[an].numCP = len(energies)
        #  create a control point (in protons each CP is an energy layer)
        #  for each energy
        qaPlan.beam[an].CP = [SPOTdata() for _ in range(len(energies))]

        for en, energy in enumerate(energies):
            #  the data for spots in this energy layer
            spotData = [_ for _ in beamData if _[1] == energy]
            qaPlan.beam[an].CP[en].En = energy
            for sp in spotData:
                qaPlan.beam[an].CP[en].X.append(sp[2])
                qaPlan.beam[an].CP[en].Y.append(sp[3])
                qaPlan.beam[an].CP[en].sMeterset.append(sp[4])

    return(qaPlan)







if __name__ == '__main__':

    x = qaPlanType()
    print(x)

    y = qaSpotDefine()
    print(y)

    #  data taken from pbtMod/docs/test.csv
    #  [gAngle, energy, X, Y, MU]
    data = [[0.0, 50.0, 10.0, 10.0, 100.0], [0.0, 50.0, 20.0, 20.0, 100.0], [0.0, 100.0, -10.0, -10.0, 200.0], [0.0, 100.0, -15.0, 20.0, 250.0], [0.0, 100.0, 10.0, 10.0, 80.0], [80.0, 50.0, 10.0, 10.0, 100.0], [80.0, 50.0, 20.0, 20.0, 100.0], [80.0, 100.0, -10.0, -10.0, 200.0], [310.0, 50.0, 20.0, 20.0, 100.0], [310.0, 100.0, -10.0, -10.0, 200.0], [310.0, 100.0, -15.0, 20.0, 250.0], [-130.0, 100.0, 10.0, 10.0, 80.0]]
    z = qaSpotArrange(data=data)
    print(z)
    print(vars(z))
    for b in z.beam:
        print(vars(b))
        for c in b.CP:
            print(vars(c))
