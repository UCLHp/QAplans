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



###  A subset of the full pyDicom data class
  #  Built to work with the programme dicomRead.py

  #  Starts with PLANdata
  #  For each beam, extend plan.beam[] list filling each with BEAMdata
  #  For each control point, extend beam.CP[] filling each with SPOTdata





class PLANdata:
    def __init__(self):
        self.pName = ''  # the name of the plan
        self.numBeams = ''  # number of beams
        self.beam = []  # list container to expand for each beam



class BEAMdata:
    def __init__(self):
        self.bName = ''  # beam name
        self.type = ''  # beam type (TREATMENT or SETUP)
        self.gAngle = ''  # gantry angle for this beam
        self.cAngle = ''  # couch angle for this beam
        self.bMetersetUnit = ''  # what units the Meterset parameter corresponds to
        self.bMeterset = ''  # the beam meterset
        self.numCP = ''  # number of control points for the beam
                         # each pair CP is an energy layer
        self.CP = []



class SPOTdata:
    def __init__(self):
        self.En = ''  # energy for that CP (== layer)
        self.X = []  # X position for each spot in layer
        self.Y = []  # Y position for each spot in layer
        self.sizeX = []  # TPS X FWHM (mm)
        self.sizeY = []  # TPS Y FWHM (mm)
        self.sMeterset = []  # meterset value for each spot
        self.sMU = [] # spot MU, this is calculated later but required at initialisation
