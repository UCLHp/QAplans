###  Copyright (C) 2020:  Andrew J. Gosling

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

import pydicom
import PySimpleGUI as sg







def ct_connector():
    """ Connect a plan to an existing CT dataset

    For quick connection of any generated treatment plan to a pre-exported
    CT and structure dataset
    CT files (CT.***.dcm) and an associated structure set (RS.***.dcm)
    should be copied into the same directory location as the plan
    """

    # ##  quick get a filename using pysimplegui
    # iplan = sg.popup_get_file('Select treatment plan')
    # sg.popup('Treatment plan:  ', filename)


    ##  get multiple file locations using pysimplegui
    # layout = [[sg.Text('Select files to connect')],
    #           [sg.Text('Plan file (RN.***.dcm)', size=(8, 1)), sg.Input(), sg.FileBrowse()],
    #           [sg.Text('Structure file (RS.***.dcm)', size=(8, 1)), sg.Input(), sg.FileBrowse()],
    #           [sg.Submit(), sg.Cancel()]]
    layout = [[sg.Text('Select files to connect')],
              [sg.Text('Plan file (RN.***.dcm)', size=(20, 1)), sg.Input(), sg.FileBrowse()],
              [sg.Text('Structure file (RS.***.dcm)', size=(20, 1)), sg.Input(), sg.FileBrowse()],
              [sg.Submit(), sg.Cancel()]]
    window = sg.Window('CT connector', layout)
    event, values = window.read()
    window.close()
    # print(f'You clicked {event}')
    # print(f'You chose filenames {values[0]} and {values[1]}')
    iplan, istruct = value[0], values[1]








if __name__ == '__main__':
    ct_connector()
