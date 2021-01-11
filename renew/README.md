# QAplans

This package will create QA plans to use during commissioning.

Plans will be based on the test patients

- zzz_PBT_comm_Something
- zzz_PBT_comm_SomethingElse
- etc.

_BADGES_ - can add badges of metadata such as version info ([shields.io](https://shields.io/) gives many good options).

## Components

**qaPlanInput.py** - collects the information used to define the list of spots to be generated.

- **_qaPlanType_** - gets the user to define the type of plan to create
- **_qaSpotDefine_** - uses input from qaPlanType to produce a list of spots
- **_qaSpotArrange_** - takes the list of spots and populates teh pbtDICOM classes

**qaSpotGenerate.py** - checks spot list and make deliverable, write out to an appropriate DICOM file.

- **_qaSpotPrepare_** - check the supplied spots are within the deliverable range
- **_qaPlanWrite_** - using a template `.dcm` plan, write out a new plan file

## Installation

Steps to take to install

### Requirements

Any specifics, dependencies, use of PipEnv/requirements files

```python
copy
datetime
easygui
pysimplegui
random
re


There are template files stored in the `/doc` folder associated with this repo that should connect the plans to an appropriate phantom. It may be advisable to export an example plan from the patient you wish to import to for best results.

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
