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







###  A subset of the full pyDicom data class
  #  Built to work with the programme dicomRead.py

  #  Starts with PLANdata
  #  For each beam, extend plan.beam[] list filling each with BEAMdata
  #  For each control point, extend beam.CP[] filling each with SPOTdata





class PLANdata:
    def __init__(self):
        self.pName = ''  # the name of the plan
        self.numBeams = ''  # number of beams
        self.beam = []  # list container to expand for each beam



class BEAMdata:
    def __init__(self):
        self.bName = ''  # beam name
        self.type = ''  # beam type (TREATMENT or SETUP)
        self.gantry = 'Gantry 1'  # gantry name
        self.gAngle = ''  # gantry angle for this beam
        self.cAngle = ''  # couch angle for this beam
        self.rs = None  #  range shifter nominal thickness (2, 3, 5)
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








###  From a list of spots in the simple list format:
  #  Pass a list of lists
  #  each list within the list of lists represents a beam
  #  within each beam, an entry for each spot with the format:
     #  gantry angle, energy, x, y, MU
  #  convert to the pre-generated pbtDICOM classes
def spotConvert_new(planName=None, data=None, rangeShifter=None):

    if not data:
        print('no input data supplied');  raise SystemExit()

    #  check the integrity of the data
    for bm in data:
        angleSet = set([_[0] for _ in bm])
        if len(angleSet) > 1:
            print('cannot have two gantry angles in a single beam')
            raise SystemExit()



    qaPlan = PLANdata()
    qaPlan.pName = planName

    #  create a beam entry for each beam angle
    qaPlan.numBeams = len(data)
    qaPlan.beam = [BEAMdata() for _ in range(len(data))]

    for bm, beamData in enumerate(data):

        #  input various parameters for this beam angle
        qaPlan.beam[bm].bName = 'E '+str(beamData[0][1])
        qaPlan.beam[bm].type = 'TREATMENT'
        qaPlan.beam[bm].gAngle = beamData[0][0]
        qaPlan.beam[bm].cAngle = 0.0
        if rangeShifter != None:
            qaPlan.beam[bm].rs = rangeShifter
        qaPlan.beam[bm].bMeterset = sum(map(float,[_[4] for _ in beamData]))

        #  identify the number of energy layers at this angle
        energies = set([_[1] for _ in beamData])
        qaPlan.beam[bm].numCP = len(energies)
        #  create a control point (in protons each CP is an energy layer)
        #  for each energy
        qaPlan.beam[bm].CP = [SPOTdata() for _ in range(len(energies))]

        for en, energy in enumerate(energies):
            #  the data for spots in this energy layer
            spotData = [_ for _ in beamData if _[1] == energy]
            qaPlan.beam[bm].CP[en].En = energy
            FWHM = 28.9 - (0.338*energy) + ((2.32e-3)*energy**2) \
                    - ((7.39e-6)*energy**3) + ((9.04e-9)*energy**4)
            for sp in spotData:
                qaPlan.beam[bm].CP[en].sizeX = FWHM
                qaPlan.beam[bm].CP[en].sizeY = FWHM
                qaPlan.beam[bm].CP[en].X.append(sp[2])
                qaPlan.beam[bm].CP[en].Y.append(sp[3])
                qaPlan.beam[bm].CP[en].sMeterset.append(sp[4])

    return(qaPlan)








###  From a list of spots in the simple list format:
  #  gantry angle, energy, x, y, MU
  #  convert to the pre-generated pbtDICOM classes
def spotConvert(planName=None, data=None, rangeShifter=None, gantry=None):

    if not data:
        print('no input data supplied');  raise SystemExit()



    qaPlan = PLANdata()
    qaPlan.pName = planName

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
        qaPlan.beam[an].gantry = str(gantry)
        qaPlan.beam[an].gAngle = angle
        qaPlan.beam[an].cAngle = 0.0
        if rangeShifter != None:
            qaPlan.beam[an].rs = rangeShifter
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
            FWHM = 28.9 - (0.338*energy) + ((2.32e-3)*energy**2) \
                    - ((7.39e-6)*energy**3) + ((9.04e-9)*energy**4)
            for sp in spotData:
                qaPlan.beam[an].CP[en].sizeX = FWHM
                qaPlan.beam[an].CP[en].sizeY = FWHM
                qaPlan.beam[an].CP[en].X.append(sp[2])
                qaPlan.beam[an].CP[en].Y.append(sp[3])
                qaPlan.beam[an].CP[en].sMeterset.append(sp[4])

    return(qaPlan)







if __name__ == '__main__':

    #  data taken from pbtMod/docs/test.csv
    #  [gAngle, energy, X, Y, MU]
    data = [[0.0, 50.0, 10.0, 10.0, 100.0], [0.0, 50.0, 20.0, 20.0, 100.0], [0.0, 100.0, -10.0, -10.0, 200.0], [0.0, 100.0, -15.0, 20.0, 250.0], [0.0, 100.0, 10.0, 10.0, 80.0], [80.0, 50.0, 10.0, 10.0, 100.0], [80.0, 50.0, 20.0, 20.0, 100.0], [80.0, 100.0, -10.0, -10.0, 200.0], [310.0, 50.0, 20.0, 20.0, 100.0], [310.0, 100.0, -10.0, -10.0, 200.0], [310.0, 100.0, -15.0, 20.0, 250.0], [-130.0, 100.0, 10.0, 10.0, 80.0]]
    z = qaSpotConvert(data=data)
    print(z)
    print(vars(z))
    for b in z.beam:
        print(vars(b))
        for c in b.CP:
            print(vars(c))
