##  small script to change the gantry

#   First looks for an .ini file that gives a list of gantry options
#   if not present, will offer the 4 gantries at UCLH



import configparser
import logging
import re

import PySimpleGUI as sg



logging.basicConfig(filename='gantry_changer.log', level=logging.DEBUG)



def gantry_changer(ifile=None, ofile=None, gantry=None):

    """ Script to change the gantry / beam model

        ifile is either a single file or list of file names
        ofile is an output file or list, if not given will simply append new gantry to end of ifile
        gantry is the gantry to change the plan to
    """



    logging.warning('Starting gantry_changer script\n')

    logging.info('Checking for .ini config file')
    change = configparser.ConfigParser()
    try:
        logging.debug('try')
        change.read('gantry.ini')
        gantries = list( re.split( ', ', change['OPT']['gantries'] ) )
    except:
        logging.debug('except')
        ##  input goes here
        gantries = [ 'Gantry 1', 'Gantry 2', 'Gantry 3' ]
        pass
    # else:
    #     logging.debug('else')
    #     logging.error('no input recorded - exiting')
    #     print()
    #     input('Press enter to close window')
    #     raise SystemExit()



    logging.warning('Identifying files')

    if not ifile:
        layout = [  [ sg.T('') ], 
                    [ sg.Text('Plan to change: '), 
                      sg.Input(), 
                      sg.FilesBrowse(key='-IN-') ],
                    [ sg.Text('If no output location selected, each plan will have\n_Gtr<N> appended (where <N> is gantry number)') ],
                    [ sg.Text('Output location:'),
                      sg.Input(),
                      sg.FileBrowse(key='-OUT-') ],
                    [ sg.T('') ],
                    [ sg.OK(), sg.Cancel() ]
                                            ]
        window = sg.Window('Choose plan for gantry change', layout)#, size=(600,150))
        event, values = window.read()
        print(ifile)



    if isinstance(ifile, list):
        pass
    else:
        ifile = [ifile]





if __name__ == '__main__':

    gantry_changer()