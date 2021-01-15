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







###  Get a set of spot data in pbtDICOM format ready for deliver
  #  Arrange beams, energy layers, and spots for easiest deliver
  #  add in the necessary extras for delivery to avoid interlocks







###  Take a given set of spots in the pbtDICOM class
  #  re-arrange the beams, energy layers, and spots into the most deliverable
  #    order to best efficiency
  #  Also add in intermediate spots for large energy jumps
  #  Will also be worth double checking the validation for things like energy
  #    range and spot position
def qaSpotArrange(data=None, doseRate=None):

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
