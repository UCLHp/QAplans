'''
Alex Grimwood 2022

GUI-based plan file creator for Dose Linearity and Dose Rate Linearity checks on the UCLH ProBeam
Gantry 1.

Based upon previous code in QAPlans repository.

'''
from easygui import multenterbox, ynbox
from compactDICOM import PLANdata, BEAMdata, SPOTdata
from planPrepare import spotArrange
from writeDICOM import overwriteDICOM

def create_spots(muSet=None, Nx=None, Ny=None, gantry_angle=None, energy=None, Sep=None, throttle_weights=False):
    ''' construct spot data as a stacked list i.e.: [[GA, E, x1, y1, MU, field1]...[GA, E, xn, yn, MU, fieldn]]
    Params:
        muSet:              float list of MU spot weights per field
        Nx:                 int number of spots along x-axis (total spots = Nx x Ny)
        Ny:                 int number of spots along y-axis (total spots = Nx x Ny)
        gantry_angle:       float degrees, constant across all fields
        energy:             float MeV, constant across all fields
        Sep:                float mm spacing between spots 
        throttle_weights:   float MU list of low MU spot added to each field, controls dose rate
    
    Output:
        data:               list of spot data defining a single energy layer per field
    '''
    data = []
    for n, sMU in enumerate(muSet):
        for x in range(Nx):
            for y in range(Ny):
                if (x % 2) == 0:
                    data.append( [gantry_angle, energy, \
                                    (x-((Nx-1)/2))*Sep, \
                                    (y-((Ny-1)/2))*Sep, sMU, n] )
                else:
                    data.append( [gantry_angle, energy, \
                                    (x-((Nx-1)/2))*Sep, \
                                    (((Ny-1)/2)-y)*Sep, sMU, n] )
        if throttle_weights and throttle_weights[n]!=sMU and throttle_weights[n]*2<=sMU:
            data[-1][4]=sMU-throttle_weights[n]
            data.append( [gantry_angle, energy, \
                                    (x-((Nx-1)/2))*Sep, \
                                    (((Ny-1)/2)-y)*Sep, throttle_weights[n], n] )

    return data


def field_spot_data(plan_name=None, mu_list=None, spot_data=None, g_angle=None, rs=None, en=None, field_prefix='MU'):
    ''' convert spot data list to DICOM-style data struct
    Params:
        plan_name:      string plan name
        mu_list:        float list must reflect the fixed MU spot weights of each field
        spot_data:      list of spot weight data
        g_angle:        float degrees gantry angle, must reflect value in spot data list
        rs:             range shifter (None, 2.0, 3.0, or 5.0)
        en:             float energy, must be constant across fields and reflect spot data list
        field_prefix:   string field name prefix
    
    Output:
        planData:       DICOM-like class struct
    '''
        
    # plan-level info
    planData = PLANdata()
    planData.pName = plan_name

    # number of beams
    planData.numBeams = len(mu_list)
    #  create field for each MU
    planData.beam = [BEAMdata() for _ in range(len(mu_list))]

    for n, s in enumerate(mu_list):
        #  spot_data for every field
        beamspot_data = [_ for _ in spot_data if _[5] == n]
        #  field parameters
        planData.beam[n].bName = field_prefix+str(s)
        planData.beam[n].type = 'TREATMENT'
        planData.beam[n].gAngle = g_angle
        planData.beam[n].cAngle = 0.0
        if rs != None:
            planData.beam[n].rs = rs
        planData.beam[n].bMeterset = sum(map(float,[_[4] for _ in beamspot_data]))

        #  one energy layer per field
        planData.beam[n].numCP = 1
        #  one control point (in protons each CP is an energy layer)
        planData.beam[n].CP = [SPOTdata()]
        planData.beam[n].CP[0].En = en
        FWHM = 28.9 - (0.338*en) + ((2.32e-3)*en**2) \
                - ((7.39e-6)*en**3) + ((9.04e-9)*en**4)
        for sp in beamspot_data:
            planData.beam[n].CP[0].sizeX = FWHM
            planData.beam[n].CP[0].sizeY = FWHM
            planData.beam[n].CP[0].X.append(sp[2])
            planData.beam[n].CP[0].Y.append(sp[3])
            planData.beam[n].CP[0].sMeterset.append(sp[4])
        
    return planData


def dose_linearity_plan():
    ''' create dose linearity and dose rate linearity plans from GUI inputs and write to DICOM file
    '''
    # Set Parameters in GUI
    bxTitle = 'Dose Linearity Plan Parameters'
    bxMsg = 'Please enter the values to define the fields\n\n'
    bxMsg = bxMsg + 'A series of monoenergetic fields. The number of fields is defined by the number of values in MU per spot'
    bxOpts = ['Plan Name', 'Gantry Angle', 'Energy', 'N spots X', 'N spots Y', 'Spot spacing (mm)', 'MU per spot']
    bxVals = ['DoseLinearity', 0, 160, 3, 3, 2.5, '5,10,20,30,40,50']
    planName, ga, nrg, nx, ny, spacing, spot_MU = multenterbox(title=bxTitle, msg=bxMsg, fields=bxOpts, values=bxVals)
    pre_rad = ynbox('Add pre-irradiation field?', 'Title', ('Yes', 'No'))
    if pre_rad:
        f=1
    else:
        f=0
    ga, nrg, nx, ny, spacing, spot_MU = (float(ga), float(nrg), int(nx), int(ny), float(spacing), list(float(_) for _ in spot_MU.split(',')))
    muSorted = sorted(spot_MU)
    throttle = ynbox('Throttle Dose Rates?', 'Title', ('Yes', 'No'))
    throttle_weights = None
    if throttle:
        throttle_weights = multenterbox(title='Minimum Spot Weights',
                            msg='Throttle Dose Rate By Setting Minimum Spot Weight.\n Weights Must Be >= 3.0 and < MU/2',
                            fields=['Field '+str(int(i)+1+f)+', '+str(m)+' MU: ' for i,m in enumerate(muSorted)],
                            values=muSorted)
        throttle_weights = [float(_) for _ in throttle_weights]
        for t,m in zip(throttle_weights,muSorted):
            if t<3 or (m/2-t<0 and m-t!=0):
                raise ValueError("Minimum Spot Weight Out of Bounds")

    # construct spot data - a stacked list e.g.: [[GA, E, x1, y1, MU, field1]...[GA, E, xn, yn, MU, fieldn]]
    data = create_spots(muSet=muSorted, Nx=nx, Ny=ny, gantry_angle=ga, energy=nrg, Sep=spacing, throttle_weights=throttle_weights)
    
    if pre_rad:
        # construct pre-irradiation spot data
        pre_rad_MU = [10]
        pre_rad_en = 170
        pre_data = create_spots(muSet=pre_rad_MU, Nx=21, Ny=21, gantry_angle=ga, energy=pre_rad_en, Sep=spacing)
        # create plan data
        print('pre-irradiation')
        DLPlan = field_spot_data(plan_name='', mu_list=muSorted, spot_data=data, g_angle=ga, rs=None, en=nrg)
        qaPlan = field_spot_data(plan_name=planName, mu_list=pre_rad_MU, spot_data=pre_data, g_angle=ga, rs=None, en=pre_rad_en, field_prefix='PreIrradiation')
        qaPlan.beam.extend(DLPlan.beam)
        qaPlan.numBeams = qaPlan.numBeams + DLPlan.numBeams
    else:
        # create plan data
        qaPlan = field_spot_data(plan_name=planName, mu_list=muSorted, spot_data=data, g_angle=ga, rs=None, en=nrg)

    #write to DICOM file    
    dcmData, _ = spotArrange(data=qaPlan, doseRate=spot_MU)
    overwriteDICOM(spotData=dcmData)


if __name__ == '__main__':
    dose_linearity_plan()
