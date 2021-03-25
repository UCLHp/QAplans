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

import numpy as np
import datetime
from random import randint
from copy import deepcopy
from pydicom.filereader import dcmread


# import configparser
from easygui import fileopenbox, filesavebox, enterbox







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


    ofile = os.path.join( os.path.splitext(ifile)[0] + '_stp' + str(space[0]) + '.dcm' )
    opath, oname = os.path.split(ofile)[0], os.path.split(ofile)[1]




    fullDCMdata = dcmread(ifile)

    newDCMdata = dcmread(ifile)





    # to duplicate a class object and all elements within need copy.deepcopy
    # deepcopy ensures there isn't inheritance so changes to one doesn't affect others





    #  adjusting the date and time of plan creation to now
    newDCMdata.RTPlanLabel = deepcopy(fullDCMdata.RTPlanLabel + '_stp' + str(space[0]))

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


    # print(fullDCMdata.FractionGroupSequence[0].NumberOfBeams)
    ##  step through each beam in the plan
    for b,ibseq in enumerate(fullDCMdata.IonBeamSequence):
        # print(ibseq.BeamNumber)
        # print(ibseq.NumberOfControlPoints)
        # print(ibseq.FinalCumulativeMetersetWeight)


        ##  creating new sets of control points to expand
        new_ion_cp_seq = []
        new_cp = 0
        new_mtst = 0.0

        for c in range(0, ibseq.NumberOfControlPoints-2, 2):
            new_ion_cp_seq.extend( [ deepcopy(ibseq.IonControlPointSequence[c]), \
                                     deepcopy(ibseq.IonControlPointSequence[c+1]) ] )

            ##  change the values in the copied CPs for the new order
            new_ion_cp_seq[new_cp].ControlPointIndex = new_cp
            new_ion_cp_seq[new_cp].CumulativeMetersetWeight = new_mtst

            new_mtst = new_mtst +  sum(new_ion_cp_seq[new_cp].ScanSpotMetersetWeights)

            new_ion_cp_seq[new_cp+1].ControlPointIndex = new_cp+1
            new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight = new_mtst
            # print(new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight)

            #   step forward the CP count for the two just written
            new_cp = new_cp+2


            ##  Now adding in the additional control points
            # print(np.arange(ibseq.IonControlPointSequence[c].NominalBeamEnergy-space[0], ibseq.IonControlPointSequence[c+2].NominalBeamEnergy, -1*space[0]))
            for en in np.arange(ibseq.IonControlPointSequence[c].NominalBeamEnergy-space[0], ibseq.IonControlPointSequence[c+2].NominalBeamEnergy, -1*space[0]):
                new_ion_cp_seq.extend( [ deepcopy(ibseq.IonControlPointSequence[1]), \
                                         deepcopy(ibseq.IonControlPointSequence[1]) ] )

                ##  change the values in the copied CPs for the new order
                new_ion_cp_seq[new_cp].ControlPointIndex = new_cp
                new_ion_cp_seq[new_cp].NominalBeamEnergy = float(en)
                new_ion_cp_seq[new_cp].CumulativeMetersetWeight = new_mtst
                # v1
                # new_ion_cp_seq[new_cp].NumberOfScanSpotPositions = space[1]
                # new_ion_cp_seq[new_cp].ScanSpotPositionMap = ibseq.IonControlPointSequence[c].ScanSpotPositionMap[:2*space[1]]
                # new_ion_cp_seq[new_cp].ScanSpotMetersetWeights = [float(space[2]) for _ in range(space[1])]
                # v2
                new_ion_cp_seq[new_cp].NumberOfScanSpotPositions = 8
                new_ion_cp_seq[new_cp].ScanSpotPositionMap = [-50.0,-50.0,-50.0,0.0,-50.0,50.0,0.0,50.0,50.0,50.0,50.0,0.0,50.0,-50.0,0.0,-50.0]
                new_ion_cp_seq[new_cp].ScanSpotMetersetWeights = [10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0]
                new_ion_cp_seq[new_cp].ScanningSpotSize = [28.9 - (0.338*en) + ((2.32e-3)*en**2) - ((7.39e-6)*en**3) + ((9.04e-9)*en**4), 28.9 - (0.338*en) + ((2.32e-3)*en**2) - ((7.39e-6)*en**3) + ((9.04e-9)*en**4)]

                new_mtst = new_mtst +  sum(new_ion_cp_seq[new_cp].ScanSpotMetersetWeights)

                new_ion_cp_seq[new_cp+1].ControlPointIndex = new_cp+1
                new_ion_cp_seq[new_cp+1].NominalBeamEnergy = float(en)
                new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight = new_mtst
                # v1
                # new_ion_cp_seq[new_cp+1].NumberOfScanSpotPositions = space[1]
                # new_ion_cp_seq[new_cp+1].ScanSpotPositionMap = ibseq.IonControlPointSequence[c+1].ScanSpotPositionMap[:2*space[1]]
                # new_ion_cp_seq[new_cp+1].ScanSpotMetersetWeights = [0.0 for _ in range(space[1])]
                # v2
                new_ion_cp_seq[new_cp+1].NumberOfScanSpotPositions = 8
                new_ion_cp_seq[new_cp+1].ScanSpotPositionMap = [-50.0,-50.0,-50.0,0.0,-50.0,50.0,0.0,50.0,50.0,50.0,50.0,0.0,50.0,-50.0,0.0,-50.0]
                new_ion_cp_seq[new_cp+1].ScanSpotMetersetWeights = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                new_ion_cp_seq[new_cp+1].ScanningSpotSize = [28.9 - (0.338*en) + ((2.32e-3)*en**2) - ((7.39e-6)*en**3) + ((9.04e-9)*en**4), 28.9 - (0.338*en) + ((2.32e-3)*en**2) - ((7.39e-6)*en**3) + ((9.04e-9)*en**4)]
                # print(new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight)

                #   step forward the CP count for the two just written
                new_cp = new_cp+2

        new_ion_cp_seq.extend( [ deepcopy(ibseq.IonControlPointSequence[-2]), \
                                 deepcopy(ibseq.IonControlPointSequence[-1]) ] )
        ##  change the values in the copied CPs for the new order
        new_ion_cp_seq[new_cp].ControlPointIndex = new_cp
        new_ion_cp_seq[new_cp].CumulativeMetersetWeight = new_mtst

        new_mtst = new_mtst +  sum(new_ion_cp_seq[new_cp].ScanSpotMetersetWeights)

        new_ion_cp_seq[new_cp+1].ControlPointIndex = new_cp+1
        new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight = new_mtst
        # print(new_ion_cp_seq[new_cp+1].CumulativeMetersetWeight)

        ##  Having added in control points and extra MU, go back and set
         #  the number of CP and MU for the beam
        newDCMdata.FractionGroupSequence[0].ReferencedBeamSequence[b].BeamMeterset = new_mtst
        newDCMdata.IonBeamSequence[b].FinalCumulativeMetersetWeight = new_mtst
        newDCMdata.IonBeamSequence[b].NumberOfControlPoints = new_cp+2
        newDCMdata.IonBeamSequence[b].IonControlPointSequence = new_ion_cp_seq
        # print(ibseq.NumberOfControlPoints, len(ibseq.IonControlPointSequence), new_cp+2, len(new_ion_cp_seq))

        ##  Finally need to reset the ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient
        for cp in newDCMdata.IonBeamSequence[b].IonControlPointSequence:
            cp.ReferencedDoseReferenceSequence[0].CumulativeDoseReferenceCoefficient = round(cp.CumulativeMetersetWeight / new_mtst,7)





    newDCMdata.save_as(ofile)







if __name__ == '__main__':

    # config = configparser.ConfigParser()
    # config.read('energy_spacer.ini')

    # mev_steps = 2
    # spots_per_layer = 4
    # mev_per_spot = 10

    # i_file = 'C:\\Users\\agoslin2\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\IndividualFolders\\AG\\planGeneration\\outputs\\RN.OP_10x10_10MeVs_RS0.dcm'
    spacing = [2, 1, 10]

    energy_spacer(space=spacing)
