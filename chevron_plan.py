from post_ism_plan import *
import os
import json

chevron_json = "O:\\protons\Work in Progress\\AlexG\\QAplans\\ChevLayers.json"

def chevron_define(json_file=None):
    '''
        Initialise POST ISM spot parameters from jscon-derived dict
    '''

    f = open(json_file)
    spot = json.load(f)
    
    # extract params from json dict
    planName = spot['planName']
    gantryAngle = float(spot['gAngle'])

    #  generate spot properties as Nx6 list
    data = []
    #spot['ChevronEns'] = [200,195,190,185,180,175,170,165,160,155,150]
    spot['ChevronEns'] = [199.5,194.5,189.5,184.5,179.5,174.5,169.5,164.5,159.5,154.5,149.5]
    data = chevron_field(data=data, spacer_step=10, spot=spot, field_name='ChevronHi')  # Chevron spots
    #spot['ChevronEns'] = [145,140,135,130,125,120,115,110,105,100]
    spot['ChevronEns'] = [144.5,139.5,134.5,129.5,124.5,119.5,114.5,109.5,104.5,99.5]
    data = chevron_field(data=data, spacer_step=10, spot=spot, field_name='ChevronLo')  # Chevron spots

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

planName, data, doseRate, rangeShifter, gAngle = chevron_define(json_file=chevron_json)
dcmData = spotConvertByField(gAngle=gAngle, planName=planName, data=data, rangeShifter=rangeShifter)
dcmData, doseRate = spotArrange(data=dcmData, doseRate=doseRate)
overwriteDICOM(spotData=dcmData, oFile=f'..{os.sep}{planName}')
