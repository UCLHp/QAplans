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







#  these are a subset of a full DICOM plan file
#  these make it easier to handle only the most relevant fields

from pbtDICOM import PLANdata, BEAMdata, SPOTdata







###  From a list of spots in the simple list format:
  #  gantry angle, energy, x, y, MU
  #  convert to the pre-generated pbtDICOM classes
def qaSpotConvert(data=None):

    if not data:
        print('no input data supplied');  raise SystemExit()



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
            FWHM = 28.9 - (0.338*energy) + ((2.32e-3)*energy**2) \
                    - ((7.39e-6)*energy**3) + ((9.04e-9)*energy**4)
            for sp in spotData:
                qaPlan.beam[an].CP[en].sizeX.append(FWHM)
                qaPlan.beam[an].CP[en].sizeY.append(FWHM)
                qaPlan.beam[an].CP[en].X.append(sp[2])
                qaPlan.beam[an].CP[en].Y.append(sp[3])
                qaPlan.beam[an].CP[en].sMeterset.append(sp[4])

    return(qaPlan)







if __name__ == '__main__':

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
