# create a post ISM plan that delivers logos 4000 spot grids with output layers and a separate chevron plan

import os
import sys
import json
import matplotlib.pyplot as plt
from easygui import fileopenbox

from compactDICOM import PLANdata, BEAMdata, SPOTdata
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM


def chevron_field(data=None, spacer_step=None, spot=None, field_name=None):
    ''' Chevron spot parameters
        input:
            data            Nx6 list to which spot parameters will be appended     
            spacer_step     Spacer step size (MeV) between chevron energies
            spot            Specification dict 
            field_name      Name of chevron field
        
        output
            data            Nx6 list
    '''
    
    #for plotting
    # i = []
    # j = []    
    ChevEns = sorted(spot['ChevronEns'], reverse=True)  # Sort chevron energies
    an = float(spot['gAngle'])  # gantry angle should be zero
    for n,cen in enumerate(ChevEns):
        print("# Chevron Energy Layer: "+str(cen))
        for x in range(spot['chevronNx']):
            for y in range(spot['chevronNy']):
                if (x % 2) == 0:
                    data.append( [an, cen, \
                                (x-((spot['chevronNx']-1)/2))*spot['ChevronSep'], \
                                ((y-((spot['chevronNy']-1)/2))*spot['ChevronSep']), spot['chevronMU'], field_name] )
                    # i.extend([ (x-((spot['chevronNx']-1)/2))*spot['ChevronSep'] ])
                    # j.extend([ ((y-((spot['chevronNy']-1)/2))*spot['ChevronSep']) ])
                else:
                    data.append( [an, cen, \
                                (x-((spot['chevronNx']-1)/2))*spot['ChevronSep'], \
                                ((((spot['chevronNy']-1)/2)-y)*spot['ChevronSep']), spot['chevronMU'], field_name] )
                    # i.extend([ (x-((spot['chevronNx']-1)/2))*spot['ChevronSep'] ])
                    # j.extend([ ((((spot['chevronNy']-1)/2)-y)*spot['ChevronSep']) ])
        # energy spacer layers every spacer_step MeV
        if spacer_step:
            spacer_step = int(abs(spacer_step))
            if n+1<len(ChevEns):
                for stepen in range(int(cen)-spacer_step,round(ChevEns[n+1]),-1*spacer_step):
                    if stepen>70 and int(cen)>min(ChevEns):
                        print("  energy spacer: "+str(stepen))
                        for spotx, spoty in zip(spot['chevron_spacer_x'], spot['chevron_spacer_y']):
                            data.append( [an, stepen, spotx, spoty, spot['chevronMU'], field_name] )
                        # i.extend([spotx])
                        # j.extend([spoty])
    
    print(f"Number of Chevron Spots: {len(data)*int(spot['Reps'])}")

    # plt.plot(i,j,'k.')
    # plt.axis('equal')
    # plt.plot([-200,200],[0,0],'b-')
    # plt.plot([0,0],[-200,200],'b-')
    # plt.xlim([-200, 200])
    # plt.ylim([-200, 200])
    # plt.savefig('test.png')
    # plt.show()
    return data

def pre_irradiation(data=None, spot=None, energy=170, field_name=None):
    # pre-irradiation layer
    an = float(spot['gAngle'])  # gantry angle should be zero
    en = int(energy)
    print("# Pre-irradiation Layer: "+str(en))
    for x in range(spot['outputNx']):
        for y in range(spot['outputNy']):
            if (x % 2) == 0:
                data.append( [an, en, \
                            (x-((spot['outputNx']-1)/2))*spot['OutputSep'], \
                            ((y-((spot['outputNy']-1)/2))*spot['OutputSep'])+spot['yoffset'], spot['outputMU'], field_name] )
            else:
                data.append( [an, en, \
                            (x-((spot['outputNx']-1)/2))*spot['OutputSep'], \
                            ((((spot['outputNy']-1)/2)-y)*spot['OutputSep'])+spot['yoffset'], spot['outputMU'], field_name] )
    print(f"Number of Pre-irradiation Spots: {len(data)}")
    return(data)


def spot_grid_field(data=None, output_field=None, spacer_step=None, spot=None, field_name=None):
    ''' Spot grid logos 4000 spot parameters
        input:
            data            Nx6 list to which spot parameters will be appended
            output_field    Boolean to indicate whether 10x10 output layer is generated
            spacer_step     Spacer step size (MeV) between chevron energies
            spot            Specification dict
            field_name      Name of chevron field
        
        output:
            data            Nx6 list
    '''
    Ens = sorted(spot['SpotEns'], reverse=True)  # sort spot energies
    gridMU = [None]*len(spot['SpotMU'])
    for i,en in enumerate(spot['SpotEns']):  # sort spot MUs
        idx = Ens.index(en)
        gridMU[idx] = spot['SpotMU'][i]
    an = float(spot['gAngle'])  # gantry angle should be zero

    for j,en in enumerate(Ens):
        print("# Spot Grid Layer: "+str(en))
        data.append( [an, en, -125.000000,-175.000000,gridMU[j],field_name] )
        data.append( [an, en, -125.000000,-125.000000,gridMU[j],field_name] )
        data.append( [an, en, -125.000000,0.000000,gridMU[j],field_name] )
        data.append( [an, en, -125.000000,125.000000,gridMU[j],field_name] )
        data.append( [an, en, -125.000000,175.000000,gridMU[j],field_name] )
        data.append( [an, en, 0.000000,175.000000,gridMU[j],field_name] )
        data.append( [an, en, 0.000000,125.000000,gridMU[j],field_name] )
        data.append( [an, en, 0.000000,0.000000,gridMU[j],field_name] )
        data.append( [an, en, 0.000000,-125.000000,gridMU[j],field_name] )
        data.append( [an, en, 0.000000,-175.000000,gridMU[j],field_name] )
        data.append( [an, en, 125.000000,-175.000000,gridMU[j],field_name] )
        data.append( [an, en, 125.000000,-125.000000,gridMU[j],field_name] )
        data.append( [an, en, 125.000000,0.000000,gridMU[j],field_name] )
        data.append( [an, en, 125.000000,125.000000,gridMU[j],field_name] )
        data.append( [an, en, 125.000000,175.000000,gridMU[j],field_name] )

        if output_field:
            print("  # Output: "+str(en))
            # output layers
            for x in range(spot['outputNx']):
                for y in range(spot['outputNy']):

                    if (x % 2) == 0:
                        data.append( [an, en, \
                                    (x-((spot['outputNx']-1)/2))*spot['OutputSep'], \
                                    ((y-((spot['outputNy']-1)/2))*spot['OutputSep'])+spot['yoffset'], spot['outputMU'], field_name] )
                    else:
                        data.append( [an, en, \
                                    (x-((spot['outputNx']-1)/2))*spot['OutputSep'], \
                                    ((((spot['outputNy']-1)/2)-y)*spot['OutputSep'])+spot['yoffset'], spot['outputMU'], field_name] )
            
        # energy spacer every spacer_step MeV
        spacer_step = int(abs(spacer_step))
        if j+1<len(Ens):
            for stepen in range(en-spacer_step,Ens[j+1],-1*spacer_step):
                if stepen>70 and en>min(Ens):
                    print("  energy spacer: "+str(stepen))
                    for spotx, spoty in zip(spot['spacer_x'], spot['spacer_y']):
                        data.append( [an, stepen, spotx, spoty, 10, field_name] )
                if stepen>70 and en>min(Ens) and en<=100:
                    print("  energy spacer: "+str(stepen))
                    for spotx, spoty in zip(spot['spacer_x'], spot['spacer_y']):
                        data.append( [an, stepen, spotx, spoty, 10, field_name] )

    print(f"Number of Grid Output Spots: {len(data)*int(spot['Reps'])}")
    return data


def pism_define(json_file=None):
    ''' Initialise POST ISM spot parameters from jscon-derived dict
        input:
            json_file       Boolean. If true, user selects a json file

    '''
    if json_file:
        fname = fileopenbox( title='select .json spot parameters file',
                             msg=None,
                             default=os.path.dirname(os.path.realpath(__file__)),
                             filetypes=['*.json'] )
        f = open(fname) 
        spot = json.load(f)
    else:
        spot = {
        'planName': "xxxxxxxxx",
        'OutputSep': 2.5,  # spot spacing (mm) for output field
        'ChevronSep': 2.5,  # spot spacing (mm) for output field
        'chevronNx': 61,  # number of x spots for chevron
        'chevronNy': 81,  # number of y spots for chevron
        'outputNx': 41,  # number of x spots for outputs
        'outputNy': 41,  # number of y spots for outputs
        'ChevronEns': [210,190,170,150,130,110,90,70],  # chevron energy layers (MeV)
        'SpotEns': [240,200,150,100,70], # spot grid energies
        'SpotMU': [40,50,70,105,150],  # spot grid weights
        'outputMU': 10, # spot weighting for outputs
        'chevronMU': 10,  # spot weighting for chevron
        'gAngle': 0,  # gantry angle must be zero
        'yoffset': -100,  # output field y-offset from centre (mm)
        'chevron_spacer_x': [-50.0,-50.0,-50.0,0.0,50.0,50.0,50.0,0.0], # chevron energy x spacer coords
        'chevron_spacer_y': [-150.0,-100.0,-50.0,-50.0,-50.0,-100.0,-150.0,-150.0], # chevron energy y spacer coords
        'spacer_x': [-50.0,-50.0,-50.0,0.0,50.0,50.0,50.0,0.0], # energy x spacer coords
        'spacer_y': [-150.0,-100.0,-50.0,-50.0,-50.0,-100.0,-150.0,-150.0], # energy y spacer coords
        'outputSpacerStep': [5], # output spacer energy step in MeV
        'Reps': 2,  # multiply each field by Reps
        'Patterns': ['Chevron','Spots','Outputs'],  # state which plan elements are generated
        'RangeShifter': ['None']
        }

    # extract params from json dict
    planName = spot['planName']
    patterns = spot['Patterns']
    Reps = spot['Reps']
    gantryAngle = float(spot['gAngle'])

    #  generate spot properties as Nx6 list
    data = []

    # Outputs flag
    if 'Outputs' in spot['Patterns']:  
        op = True
    else:
        op = False

    # Fields
    if op:
        data = pre_irradiation(data=data, spot=spot, energy=170, field_name='0 PreIrrad')  # pre-irradiation field
    n=0
    for i in range(0,Reps):  # create spots for each field
        if 'Spots' in spot['Patterns']:
            n+=1
            data = spot_grid_field(data=data, output_field=op, spacer_step=spot['outputSpacerStep'], spot=spot, field_name=str(n)+' SpotOP '+str(i+1))  # Spot grids w optional outputs
    for i in range(0,Reps):  # create spots for each field
        if 'Chevron' in spot['Patterns']:
            n+=1
            data = chevron_field(data=data, spacer_step=None, spot=spot, field_name=str(n)+' Chevron '+str(i+1))  # Chevron spots

    # set doseRate to minimum MU
    doseRate = min([_[4] for _ in data])

    # set rangeShifter
    try:
        rangeShifter = spot['RangeShifter']
    except:
        rangeShifter = None
    
    if rangeShifter == 'None':
        rangeShifter = None

    return(planName, data, doseRate, rangeShifter, gantryAngle)


def spotConvertByField(gAngle=0.0, planName=None, data=None, rangeShifter=None):
    qaPlan = PLANdata()
    qaPlan.pName = planName

    #  identify the number of unique fields
    fieldSet = set([_[-1] for _ in data])
    fieldSet = sorted(fieldSet)
    qaPlan.numBeams = len(fieldSet)

    #  create a beam entry for each field
    qaPlan.beam = [BEAMdata() for _ in range(len(fieldSet))]

    # write spot data for each field
    for n, field_name in enumerate(fieldSet):
        #  write spot data
        beamData = [_ for _ in data if _[-1] == field_name]
        #  write field parameters
        qaPlan.beam[n].bName = field_name
        qaPlan.beam[n].type = 'TREATMENT'
        qaPlan.beam[n].gAngle = 0.0
        qaPlan.beam[n].cAngle = gAngle
        if rangeShifter != None:
            qaPlan.beam[n].rs = rangeShifter
        qaPlan.beam[n].bMeterset = sum(map(float,[_[4] for _ in beamData]))

        #  identify the number of energy layers
        energies = set([_[1] for _ in beamData])
        qaPlan.beam[n].numCP = len(energies)

        #  create a control point for each energy
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

    return(qaPlan)



if __name__ == '__main__':
      planName, data, doseRate, rangeShifter, gAngle = pism_define(True)
      dcmData = spotConvertByField(gAngle=gAngle, planName=planName, data=data, rangeShifter=rangeShifter)
      dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
      overwriteDICOM(spotData=dcmData, oFile=f'..{os.sep}{planName}')


