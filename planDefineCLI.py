###  Copyright (C) 2021:  Alex Grimwood (based on code by Andrew Gosling)

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


###  Using the values from qaPlanType, obtain all the necessary spot details
def spotParameters(qaType=None):

    import os
    import re
    import numpy


    #  setup for custom .CSV file input
    #  input file should have a single line per spot
    #  each desired beam should be started with header lines starting with the '#' character
    #  within a beam are lines containing:
    #   - custom info such as DOSE RATE values within the header lines ie:
    #     # DOSE RATE, 20
    #  gantry angle, energy, X, Y, MU
    if qaType['PlanType'] == 'CSV':
        raise ValueError("CSV plan types not supported from json.")
    
    if qaType['PlanType'] not in ['CSV', 'Spot Grid']:
        raise ValueError("Unsupported plan type: "+str(qaType['type']))
    
    elif qaType['PlanType'] == 'Spot Grid':
        planName = qaType['PlanName']
        gAngle = qaType['GantryAngle']
        Ene = qaType['Energies']
        Nx = qaType['NspotX']
        Ny = qaType['NspotY']
        Sep = qaType['Spacing']
        sMU = qaType['tMU']
        rs = qaType['RangeShifter']
        gAngle, Ene, Nx, Ny, Sep, sMU, rs = ([float(gAngle)], [float(_) for _ in Ene], int(Nx), int(Ny), float(Sep), float(sMU), float(rs))

    
    data = []
    #  generate the spots
    for an in gAngle:
        for en in Ene: # numpy.arange(Emin, Emax+delE, delE):
            for x in range(Nx):
                for y in range(Ny):
                    if (x % 2) == 0:
                        data.append( [an, en, \
                                        (x-((Nx-1)/2))*Sep, \
                                        (y-((Ny-1)/2))*Sep, sMU] )
                    else:
                        data.append( [an, en, \
                                        (x-((Nx-1)/2))*Sep, \
                                        (((Ny-1)/2)-y)*Sep, sMU] )

    # if doseRate not already defined set to minimum MU
    try:
        doseRate
    except NameError:
        doseRate = min([_[4] for _ in data])

    if rs not in [0., 2., 3, 5.]:
        raise ValueError("Invalid range shifter: "+str(rs))
    else:
        rangeShifter = rs

    if rangeShifter is None:
        planName = planName + '_RS0'
    else:
        planName = planName + '_RS' + str(int(rangeShifter))

    return(planName, data, doseRate, rangeShifter)







if __name__ == '__main__':

    x = qaPlanType()
    print(x)

    y = qaSpotParameters()
