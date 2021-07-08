##  small script to link a plan to a structure set

#   First looks for an .ini file that gives a list of gantry options
#   if not present, will offer the 4 gantries at UCLH



import configparser
import logging
import pydicom
import re

import PySimpleGUI as sg



logging.basicConfig(filename='gantry_changer.log', level=logging.DEBUG)



def link_structure_set(pfile=None, sfile=None, ofile=None):

    """ Script to link a plan to a structure set

        pfile is the treatment plan
        sfile is the structure set
        ofile is the output file, if not supplied _lnk will be appended to pfile
        """



    if not pfile or sfile:
        layout = [  [ sg.T('') ],
                    [ sg.Text('Plan(s) to change: '),
                      sg.Input(),
                      sg.FileBrowse(key='-IN-') ],
                    [ sg.Text('If no output location selected, each plan will have\n_Gtr<N> appended (where <N> is gantry number)') ],
                    [ sg.Text('Output location:'),
                      sg.Input(),
                      sg.FileBrowse(key='-OUT-') ],
                    [ sg.T('') ],
                    [ sg.OK(), sg.Cancel() ]
                                            ]
        window = sg.Window('Choose plan for gantry change - MULTIPLE selection possible', layout)#, size=(600,150))
        event, values = window.read()
        logging.debug(values['-IN-'])
        logging.debug(values['-OUT-'])
        ifile = list(values['-IN-'].split(';'))
        ofile = list(values['-OUT-'].split(';'))
        logging.debug(str(ifile))
        logging.debug(str(ofile))
