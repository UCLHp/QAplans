# QAplans

This package will create QA plans to use during commissioning.

Plans will be based on the test patients

- zzz_PBT_comm_EnergyLayers
- zzz_PBT_comm_Isocentre

_BADGES_ - can add badges of metadata such as version info ([shields.io](https://shields.io/) gives many good options).

## Components

**pbtDICOM.py** - contains the trimmed down DICOM class

- **_PLANdata_** - plan name, number of beams, and a list of beams
- **_BEAMdata_** - beam name, type, gantry angle, couch angle, Meterset unit, number of control-points (each CP is an energy layer)
- **_SPOTdata_** - energy, x and y position, x and y spot size, spot meterset

**qaPlanDefine.py** - collects the information used to define the list of spots to be generated.

- **_qaPlanType_** - gets the user to define the type of plan to create
- **_qaSpotParameters_** - uses input from qaPlanType to request the required data from the user to create the plan, then generates the spots

**convert2compactDICOM.py** - takes a list input data and converts it to the trimmed down DICOM class contained in pbtDICOM.py

- **_qaSpotConvert_** - does this task

**qaPlanPrepare.py** - checks spot list and make deliverable, write out to an appropriate DICOM file.

- **_qaSpotArrange_** - check the supplied spots are within the deliverable range, order the gantry angles, energy layers, and spot scanning for delivery. Also setup spots to control dose rate.
- **_qaSpotPrepare_** - prepare the spot data for writing out, add intermediary spots at minimum dose rate to allow smooth stepping between energy layers, split beams into individual energy layers if required.

**writeDICOM.py** - takes data in the compact DICOM class defined in pbtDICOM and writes it over a template `.dcm` file

- **_overwriteDICOM_** - using a template `.dcm` plan, write out a new plan file

## Installation

Clone this repo from github:

```console
git clone https://github.com/UCLHp/QAplans.git
```

Create an environment in which the code will run (these instructions use the basic python environment builder included with most Python installs). Open a command terminal and type the following:

```console
cd <path to github repo>/QAplans
mkdir env
python -m <path to github repo>/QAplans/env/
```

This creates the environment. Next navigate into the directory `<path to github repo>/QAplans/env/Scripts` and activate the environment with either `Scripts.bat` on Windows or `<SOMETHING HERE>` on Linux/Mac

Finally, install the required packages. Navigate back to `<path to github repo>/QAplans` and run the following command which should install the packages and versions listed below.

```console
python -m pip install -r requirements.txt
```

To deactivate the virtual environment, simply type `deactivate`, and to remove the virtual environment delete the folder `env`.

### Requirements

Any specifics, dependencies, use of PipEnv/requirements files

```python
easygui==0.98.1
pydicom==2.1.2
```

There are template files stored in the `/data` folder associated with this repo that should connect the plans to an appropriate phantom. It may be advisable to export an example plan from the patient you wish to import to for best results.

### Tests

Included tests, how to use them, what results to expect

## Usage

How to use the programme, how to call the package

Examples of what it can do

## Limitations / Known Bugs

Sometimes the plans do not re-import into the current course open for the patient, this is under investigation.

## Contribute

Pull requests are welcome.<br>
For major changes, please open a ticket first to discuss desired changes: [[repo-name]/issues](http://github.com/UCLHp/QAplans/issues)

If making changes, please check all tests and add if required.

## Licence

All code within this package distributed under [GNU GPL-3.0 (or higher)](https://opensource.org/licenses/GPL-3.0).

Full license text contained within the file LICENCE.

### (C) License for all programmes

```

### Copyright (C) 2020: Andrew J. Gosling

# This program is free software: you can redistribute it and/or modify

# it under the terms of the GNU General Public License as published by

# the Free Software Foundation, either version 3 of the License, or

# (at your option) any later version.

# This program is distributed in the hope that it will be useful,

# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the

# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License

# along with this program. If not, see <http://www.gnu.org/licenses/>.
```
