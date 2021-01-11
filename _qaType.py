# identify the type of QA plan to generate and type of output to create
# qaType = [['SS-ME', 'SG-SE', 'SG-ME', 'CSV'], ['TPS', 'MC', 'both']]


def qaPlanType(qaType=[None, None]):
    from easygui import buttonbox

    # finding out what type of plan file the user wishes to create
    if qaType[0] == None:
        bxTitle = 'QA plan file stucture'
        bxMsg = 'Select the QA file type you wish to create\n\n\
                      SS-SE:  Single Spot at a Single Energy\n\
                      SS-ME:  Single Spot at Multiple Energies\n\
                     SS-MGA:  Single Spot at Multiple Gantry Angles\n\
                      SG-SE:  Spot Grid (dose plane) at a Single Energy\n\
                      SG-ME:  Spot Grid (dose plane) at Multiple Energies\n\
                  SG-ME-MGA:  Spot Grid (dose plane) at Multiple Energies and Multiple Gantry Angles\n\
                        CSV:  Create a plan file from a pre-made .csv file of spot positions, energies, and MUs'
        bxOpts = ['SS-SE', 'SS-ME', 'SS-MGA', 'SG-SE', 'SG-ME', 'SG-ME-MGA', 'CSV']
        qaType[0] = buttonbox(title=bxTitle, msg=bxMsg, choices=bxOpts, cancel_choice=None)
        if qaType[0] == None:  exit()

    # is the output intended for the TPS or MC, or both
    if qaType[1] == None:
        bxTitle = 'TPS or MC'
        bxMsg = 'Do you need a QA file for the TPS, Monte-Carlo, or both'
        bxOpts = ['TPS', 'MC', 'both']
        qaType[1] = buttonbox(title=bxTitle, msg=bxMsg, choices=bxOpts, default_choice='TPS', cancel_choice=None)
        if qaType[1] == None:  exit()



    return(qaType)
