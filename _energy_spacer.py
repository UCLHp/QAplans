###  Copyright (C) 2021:  Andrew J. Gosling

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
import configparser
from easygui import fileopenbox, filesavebox, enterbox
import datetime
from random import randint
from copy import deepcopy
from pydicom.filereader import dcmread







###  Take a given plan and multiply every beam in that plan by a given value
def energy_spacer(ifile=None, ofile=None, space=None):


    if not ifile:
        ifile = fileopenbox( title='Original plan', \
                             msg='Template file with all energies in a beam', \
                             default=os.path.dirname(os.path.realpath(__file__)), \
                             filetypes='*.dcm' )
        print(ifile)
    ipath, iname = os.path.split(ifile)[0], os.path.split(ifile)[1]


    if not space:
        raise SystemExit()


    ofile = os.path.join( os.path.splitext(ifile)[0] + '_stp.dcm' )
    opath, oname = os.path.split(ofile)[0], os.path.split(ofile)[1]




    fullDCMdata = dcmread(ifile)

    newDCMdata = dcmread(ifile)





    # to duplicate a class object and all elements within need copy.deepcopy
    # deepcopy ensures there isn't inheritance so changes to one doesn't affect others





    #  adjusting the date and time of plan creation to now
    newDCMdata.RTPlanLabel = deepcopy(fullDCMdata.RTPlanLabel + '_stp')

    newDCMdata.RTPlanDate = datetime.datetime.now().strftime('%Y%m%d')

    newDCMdata.RTPlanTime = datetime.datetime.now().strftime('%H%M%S.%f')




    #  SOPInstanceUID is the unique identifier for each plan
    #  Final 2 sections are a generated ID number and date/time stamp
    sopInstUID = fullDCMdata.SOPInstanceUID.rsplit('.',2)

    newDCMdata.SOPInstanceUID = sopInstUID[0] + '.' \
                                + str(randint(10000, 99999)) + '.' \
                                + fullDCMdata.RTPlanDate \
                                + fullDCMdata.RTPlanTime.rsplit('.')[0]


    ##  Number of beams in the plan
    # fullDCMdata.FractionGroupSequence[0].NumberOfBeams


    print(fullDCMdata.FractionGroupSequence[0].NumberOfBeams)
    ##  step through each beam in the plan
    for ibseq in fullDCMdata.IonBeamSequence:
        print(ibseq.BeamNumber)
        print(ibseq.NumberOfControlPoints)
        print(ibseq.FinalCumulativeMetersetWeight)


        ##  Having added in control points and extra MU, go back and set
         #  the number of CP and MU for the beam
        # fullDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight = #something
        # fullDCMdata.IonBeamSequence[b].NumberOfControlPoints = #something





    # newDCMdata.save_as(ofile)







if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('energy_spacer.ini')

    # mev_steps = 2
    # spots_per_layer = 4
    # mev_per_spot = 10

    i_file = 'C:\\Users\\agoslin2\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\planGeneration\\outputs\\RN.OP_10x10_10MeVs_RS0.dcm'
    spacing = [2, 4, 10]

    energy_spacer(ifile=i_file, space=spacing)
