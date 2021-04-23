# QAplans

This package will create QA plans to use during commissioning.

Plans will be based on the template:

- `data/RN.template-wRS.dcm`

_BADGES_ - can add badges of metadata such as version info ([shields.io](https://shields.io/) gives many good options).

## Components

**_planGenerator.py** - the primary programme - calls the other modules to build a custom plan.

**planDefine.py** - collects the information used to define the list of spots to be generated.

- **_planType_** - gets the user to define the type of plan to create
- **_spotParameters_** - uses input from qaPlanType to request the required data from the user to create the plan, then generates the spots

**compactDICOM.py** - takes a list input data and converts it to the trimmed down DICOM class contained in pbtDICOM.py

- **_PLANdata_** - plan name, number of beams, and a list of beams
- **_BEAMdata_** - beam name, type, gantry angle, couch angle, Meterset unit, number of control-points (each CP is an energy layer)
- **_SPOTdata_** - energy, x and y position, x and y spot size, spot meterset
- **_spotConvert_** - takes the input data list and populates the above classes
- **_spotConvert_new_** - an adaption of the above used in `.outputPlans`, will make plans with multiple beams based on a more complex structure of data list, will migrate to this version in future releases

**qaPlanPrepare.py** - checks spot list and make deliverable, write out to an appropriate DICOM file.

- **_spotArrange_** - check the supplied spots are within the deliverable range, order the gantry angles, energy layers, and spot scanning for delivery. Also setup spots to control dose rate.
- **_spotPrepare_** - prepare the spot data for writing out, add intermediary spots at minimum dose rate to allow smooth stepping between energy layers, split beams into individual energy layers if required.

**writeDICOM.py** - takes data in the compact DICOM class defined in pbtDICOM and writes it over a template `.dcm` file

- **_overwriteDICOM_** - using a template `.dcm` plan, write out a new plan file

**_multipyBeams.py** - quick script to duplicate beams within an existing plan to be able to repeat delivery without reloading the patient.

## Installation

Clone this repo from github:

```console
git clone https://github.com/UCLHp/QAplans.git
```

Create an environment in which the code will run (these instructions use the basic python environment builder included with most Python installs). Open a command terminal and type the following  (you can exclude the parts in `[ ]` for directory paths if you are in the repo directory):

```console
cd <path to github repo>/QAplans
mkdir env
python -m venv [<path to github repo>/QAplans/]env/
```

This creates the environment. To activate the environment either use `activate.bat` on Windows or source `activate` on Linux/Mac

```console
##  Windows
[<path to github repo>/QAplans/]env/Scripts/activate.bat

##  Linux/Mac
source [<path to github repo>/QAplans/]env/Scripts/activate
```

Install the required packages as instructed in the **Requirements** section below.

To deactivate the virtual environment, simply type `deactivate`, and to remove the virtual environment delete the folder `env`.

### Requirements

The following dependency packages will need to be installed. They are as listed in the `requirements.txt` file within this package.<br>
To install from `requirements.txt`, within your environment, navigate back to `<path to github repo>/TPSprepare/` and run the following command:

```python
python -m pip install -r requirements.txt
```

`requirements.txt`:

```python
easygui==0.98.1
pydicom==2.1.2
```

There are template files stored in the `/data` folder associated with this repo that should connect the plans to an appropriate phantom. It may be advisable to export an example plan from the patient you wish to import to for best results.

### Tests

Included tests, how to use them, what results to expect

Some template DICOM files are indcluded in the folder `data/` from which you can build your plans. There is also a `test.csv` file that can be used to demonstrate how to create a `.csv` file that can be read by the programme for ultimate control of spot placement.

## Usage

The primary package is `_qaPlanGenerator.py`

This will allow the generation of plans either from a custom `.csv` file or define a set of spot grids.

There is a sub-package called `_multiplyBeams.py` which will take an existing plan and multiply each beam within the plan by a given amount. Appends `xN` to the plan name where `N` is the number of repeats of each beam. **BEWARE** PTC cannot handle more than 50 or so beams before struggling.

## Limitations / Known Bugs

The UI needs an overhaul that I plan to do when I can find some time.

I intend to overhaul the method of data input to add more flexibility and the ability to create multiple beams within a plan at the same gantry angle.

## Contribute

Pull requests are welcome.<br>
For major changes, please open a ticket first to discuss desired changes: [[repo-name]/issues](http://github.com/UCLHp/QAplans/issues)

If making changes, please check all tests and add if required.

## Licence

All code within this package distributed under [GNU GPL-3.0 (or higher)](https://opensource.org/licenses/GPL-3.0).

Full license text contained within the file LICENCE.

### (C) License for all programmes

```
### Copyright (C) 2021: Andrew J. Gosling

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
