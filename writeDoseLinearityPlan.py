from easygui import multenterbox
from compactDICOM import PLANdata, BEAMdata, SPOTdata
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM

def dose_linearity_plan():
    planName = 'DoseLinearity'
    spot_MU = [5,10]
    rangeShifter = None
    gantry_angle = 0
    energy = 160.
    Nspots_x = 3
    Nspots_y = 3
    spot_spacing = 0.25

    Nx = Nspots_x
    Ny = Nspots_y
    Sep = spot_spacing

    bxTitle = 'Dose Linearity Plan Parameters'
    bxMsg = 'Please enter the values to define the fields\n\n'
    bxMsg = bxMsg + 'A series of monoenergetic fields. The number of fields is defined by the number of values in MU per spot'
    bxOpts = ['Plan Name', 'Gantry Angle', 'Energy', 'N spots X', 'N spots Y', 'Spot spacing (mm)', 'MU per spot']
    bxVals = ['DoseLinearity', 0, 160, 3, 3, 2.5, '5,10,20,30,40,50']

    planName, gantry_angle, energy, Nx, Ny, Sep, spot_MU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
    gantry_angle, energy, Nx, Ny, Sep, spot_MU = (float(gantry_angle), float(energy), int(Nx), int(Ny), float(Sep), list(float(_) for _ in spot_MU.split(',')))

    # construct spot data - a stacked list e.g.: [[GA, E, x1, y1, MU]...[GA, E, xn, yn, MU]]
    data = []
    for sMU in spot_MU:
        for x in range(Nx):
            for y in range(Ny):
                if (x % 2) == 0:
                    data.append( [gantry_angle, energy, \
                                    (x-((Nx-1)/2))*Sep, \
                                    (y-((Ny-1)/2))*Sep, sMU] )

                else:
                    data.append( [gantry_angle, energy, \
                                    (x-((Nx-1)/2))*Sep, \
                                    (((Ny-1)/2)-y)*Sep, sMU] )

    # construct plan data
    qaPlan = PLANdata()
    qaPlan.pName = planName

    #  identify the number of beams by MU list
    muSet = sorted(set([_[4] for _ in data]))
    qaPlan.numBeams = len(muSet)

    #  create a beam entry for each MU
    qaPlan.beam = [BEAMdata() for _ in range(len(muSet))]

    for n, s in enumerate(muSet):
        #  extract the data at this beam angle
        beamData = [_ for _ in data if _[4] == s]
        #  input various parameters for this beam angle
        qaPlan.beam[n].bName = 'MU'+str(s)
        qaPlan.beam[n].type = 'TREATMENT'
        qaPlan.beam[n].gAngle = gantry_angle
        qaPlan.beam[n].cAngle = 0.0
        if rangeShifter != None:
            qaPlan.beam[n].rs = rangeShifter
        qaPlan.beam[n].bMeterset = sum(map(float,[_[4] for _ in beamData]))

        #  identify the number of energy layers at this angle
        energies = set([_[1] for _ in beamData])
        qaPlan.beam[n].numCP = len(energies)
        #  create a control point (in protons each CP is an energy layer)
        #  for each energy
        qaPlan.beam[n].CP = [SPOTdata() for _ in range(len(energies))]

        for en, energy in enumerate(energies):
            #  the data for spots in this energy layer
            spotData = [_ for _ in beamData if _[1] == energy]
            qaPlan.beam[n].CP[en].En = energy
            FWHM = 28.9 - (0.338*energy) + ((2.32e-3)*energy**2) \
                    - ((7.39e-6)*energy**3) + ((9.04e-9)*energy**4)
            for sp in spotData:
                qaPlan.beam[n].CP[en].sizeX = FWHM
                qaPlan.beam[n].CP[en].sizeY = FWHM
                qaPlan.beam[n].CP[en].X.append(sp[2])
                qaPlan.beam[n].CP[en].Y.append(sp[3])
                qaPlan.beam[n].CP[en].sMeterset.append(sp[4])

    dcmData, _ = spotArrange(data=qaPlan, doseRate=spot_MU)
    overwriteDICOM(spotData=dcmData)

if __name__ == '__main__':
    dose_linearity_plan()