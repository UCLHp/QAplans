# QA plan creator script

## Scope

A script to generate custom fields on the fly for use in commissioning.

Ideally will be able to run whenever needed and produce something that can be delivered (without needing to calculate in the TPS (look to flags that may enable this) but if not without any more info).

Will need to create the following types of fields:

- Single spots at any gantry angle desired, for single or multiple energies
- Spot grids (energy layers) at any gantry angle and for any range of energies
- Custom spot patterns fed in in some user friendly format
- Ability to control the dose rate for a given energy layer Additional features
- Generate all plans so they can be delivered either as a single delivery, or as each energy layer and gantry angle as a single beam for manual control
- Limits on how far the spot can move spatially, and how large an energy jump can be achieved
- Scanning directions/raster for the X-Y motion for optimum delivery

## Plan design

Building modules into the pbtMod set of packages

Approximate structure, each element is a separate function:

- Obtain all the input values
- Convert the input values into a list containing an entry for each spot containing gantry angle, energy, x, y, mu, dose rate
- Take list in the above format, and build the stripped down `DICOMplan` format established previously organising by gantry angle and energy layer etc.

Then convert a list of values into the `pbtDICOM` format including splitting the list into the required beams for each gantry angle and energy layers dependent on what is supplied.

The dose rate application is not applied at this stage as it is not necessary and without knowing the delivery order is not applicable.

## Elements

### qaPlanInput.py

**qaPlanType**

Asks if want a single spot, spot grid, or plan type defined as a list supplied in .csv format.

Then asks if not a .csv input, does the user want single or multiple energies and gantry angles These are stored into a library to be passed as the definitions for generating the spot lists

**qaSpotDefine**

If the type is a CSV, extract the data out of the csv file.<br>
Also extract from any header lines that should be indicated by a leading `#`.<br>
Find the entry for DOSE RATE in the file and extract following entry.

If not a .csv file, then get the user to generate the values for the data.

If it is a single spot plan, ask about on- or off-axis, if on-axis then generate the spot positions either 0,0 or whatever supplied.

If it is a spot grid plan, offer a few standard field sizes, or ask the user to define the grid size, also request the spot spacing for either.

Ask for the energy layers, if a single energy convert to a float, if a list convert to a list of floats extracting based on various delimeters (`,` `;` `[space]` `\n`).

The same process but asking for gantry angles.

Finally ask for the dose per spot and a doserate value if a specific dose rate is required.

Generate a list of lists in which the data is contained in the format: `[ [Gantry Angle, Spot Energy, X position, Y position, spot MU], [...], ... ]`

**qaSpotArrange**

Takes the spot data in list format and then populates the pbtDICOM data format.

## To Develop

1. Consider how to offer option to define either by grid size or number of spots Then generate a list of lists containing the X and Y cords of the spots, always do an odd number of spots for each axis so there will be a spot on 0,0 no matter what

2. If doing a grid by number of spots, may need to handle if even number of spots and surrounding 0,0

## Testing

Stored in the `docs/` folder is the file `test.csv` which contains a series of spot values to be input into the .csv input option. Used to test that the programme will correctly parse a .csv file if formatted properly.

## Issues

Lots and lots of popups - would be much better with `PySimpleGUI` so will have to learn that and combine all input into a single/few windows

# Appendix: DEV NOTES

Here are notes taken as the project develops, not neat and tidy

## qaSpotArrange

First need to find the unique gantry angles to split by beam direction<br>
Using `set` to find unique values

```python
print([_[0] for _ in data])
angleSet = set([_[0] for _ in data])
print(list(angleSet))
```
