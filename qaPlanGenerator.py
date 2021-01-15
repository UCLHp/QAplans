import easygui as eg

from os import path as osPath

from _pbtDICOM import PLANdata, BEAMdata, SPOTdata
from _qaType import qaPlanType
from _spotGenerator import spotGenerator
from _writeDICOMplan import writeDICOMplan







planType = qaPlanType()
# for testing - setting to most complex scenario
# [['SS-SE', 'SS-ME', 'SS-MGA', 'SG-SE', 'SG-ME', 'SG-ME-MGA', 'CSV'], ['TPS', 'MC', 'both']]
# planType = qaPlanType(qaType=['SG-ME', 'both'])



spotData = spotGenerator(planType)
# # to expand to a 3 beam plan for testing purposes
# spotData.numBeams = 3
# from copy import deepcopy
# spotData.beam = [deepcopy(spotData.beam[0]) for _ in range(spotData.numBeams)]





if planType[1] in ('TPS', 'both'):
    #  create TPS plan files
    #  options to create:
    #   - plan as if was from TPS, all layers combined
    #   - if from a single beam angle:
    #       - each energy layer in a separate beam
    #       - If 'Separate' selected, each energy layer in a separate plan
    #   - if from multiple beam angles:
    #       - if only a single energy layer will already be covered by stock
    #       - if multiple energy layers, separate plans both for each gantry angle with all energy layers (separate beams), and each energy layer with all gantry angles



    #  location of the template DICOM file to amend
    iFile = eg.fileopenbox(title='template DICOM', msg='select the template \
                          DICOM file for conversion', filetypes=['*.dcm'])
    iPath, iName = osPath.split(iFile)[0], osPath.split(iFile)[1]



    # selecting an output location and then creating dicom files
    oPath = eg.diropenbox(title='output Directory', msg='Navigate INTO the \
                          output directory', default=str(iPath))



    #  add spotData into qaPlans as a list to be passed when creating DICOM plans - this is the basic minimum dataset
    qaPlans = [spotData]



    ###  determine next step on whether a single or multiple gantry angles

    #  if a single gantry angle and tf single beam
    if qaPlans[0].numBeams == 1:
        qaPlans.append(PLANdata())

        ### creating plan with each energy layer in its own beam

        #  set the plan name and setup beam containers
        qaPlans[1].pName = qaPlans[0].pName + '--sepE'
        #  each CP represents an energy layer, spotGenerator only creates one CP per energy layer, reading from TPS has 2, the second of each needs to be excluded.
        qaPlans[1].beam = [BEAMdata() for _ in range(qaPlans[0].beam[0].numCP)]
        qaPlans[1].numBeams = len(qaPlans[1].beam)

        #  creating individual beams for each energy layer
        # for b,beam in enumerate(qaPlans[0].beam):
        b = 0
        for layer in qaPlans[0].beam[0].CP:
            qaPlans[1].beam[b].bName = qaPlans[0].beam[0].bName.split('--')[0] + '--E' + str(layer.En)
            qaPlans[1].beam[b].gAngle = qaPlans[0].beam[0].gAngle
            qaPlans[1].beam[b].numCP = 1
            qaPlans[1].beam[b].CP = [layer]
            b += 1

    elif qaPlans[0].numBeams > 1:
        ''' doing something strange with beam naming\
            see Issue raised in GitHub and try to fix later '''
        # check if more than one energy layer for each gantry angle
        # and all gantry angles have same number of energy layers
        if all(_ > 1 for _ in [beam.numCP for beam in qaPlans[0].beam]) and all(_ == _ for _ in [beam.numCP for beam in qaPlans[0].beam]):

            p = 1
            # one plan per energy layer with each gantry angle in a beam
            qaPlans.extend([PLANdata() for _ in range(qaPlans[0].beam[0].numCP)])
            for e in range(qaPlans[0].beam[0].numCP):
                qaPlans[p].pName = qaPlans[0].pName + '--E' + str(qaPlans[0].beam[0].CP[e].En)
                qaPlans[p].beam = [BEAMdata() for _ in range(qaPlans[0].numBeams)]
                qaPlans[p].numBeams = len(qaPlans[p].beam)
                for b, beam in enumerate(qaPlans[p].beam):
                    beam.bName = qaPlans[0].beam[0].bName
                    beam.gAngle = qaPlans[0].beam[b].gAngle
                    beam.numCP = 1
                    beam.CP = [qaPlans[0].beam[b].CP[e]]
                p += 1

            # one plan per gantry angle with each energy level in a beam
            qaPlans.extend([PLANdata() for _ in range(qaPlans[0].numBeams)])
            for b,beam in enumerate(qaPlans[0].beam):
                qaPlans[p].pName = qaPlans[0].pName + '--G' + str(beam.gAngle)
                qaPlans[p].beam = [BEAMdata() for _ in range(beam.numCP)]
                qaPlans[p].numBeams = len(qaPlans[p].beam)

                #  creating individual beams for each energy layer
                for e,layer in enumerate(beam.CP):
                    qaPlans[p].beam[e].bName = qaPlans[0].beam[0].bName.split('--')[0] + '--E' + str(layer.En)
                    qaPlans[p].beam[e].gAngle = qaPlans[0].beam[b].gAngle
                    qaPlans[p].beam[e].numCP = 1
                    qaPlans[p].beam[e].CP = [layer]
                p +=1

        # if not and only single energy layer
        elif all(_ == 1 for _ in [beam.numCP for beam in qaPlans[0].beam]):
            # the standard dataset will cover the required plans
            pass


        ''' I think I need some error handling here if\
            mixed energy layers and gantry angles '''

    else:
        print('No beams????')
        exit()





    #  writing out to dicom files
    # useage:   dcmPlanCreator(spotData=<dcmDATA class spots>, file=<template dicom file>, oFile=<output file location and name>)
    for plan in qaPlans:
        oFile = osPath.join(oPath, str(plan.pName) + '.dcm')
        # print('oFile: ', oFile)
        writeDICOMplan(spotData=plan, iFile=iFile, oFile=oFile)





'''  Still need to work on this in the new architecture\
     - currently less important so will deal with later  ''
if planType[1] in ('MC', 'both'):
    #  create MC plan files

    # selecting an output location and then creating dicom files
    from fileOps import chooseDir
    oPath = chooseDir(title='Navigate INTO the output directory for MC')

    # useage:   mcSourceCreator(spotData=<dcmDATA class spots>, oFile=<output file location and name, output will be separate file for each beam with name appended>)
    from qaPlanCreator import mcSourceCreator
    for plan in qaPlans:
        if planType[2] == 'Separate':
            oName = plan.pName.rsplit('--')[0] + '.mac'
        elif planType[2] == 'Combined':
            oName = plan.pName + '.mac'
        oFile = osPath.join(oPath, oName)
        # print('Com:  ', oFile)
        # # assuming next line works - UNTESTED
        mcSourceCreator(spotData=plan, oFile=oFile)
'''
