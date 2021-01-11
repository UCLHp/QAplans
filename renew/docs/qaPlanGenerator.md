# qaPlanGenerator

## Scope

Code to take a list of spot values and convert them into a more usable format. Initially convert the data into the `pbtDICOM` format that is a subset of a full DICOM plan with the useful parts. Another function to convert a set of spots into something that can be delivered including changing the order of the spots and adding intervening spots for energies and positions.

## Plan design

The first stage is the preparation for conversion to DICOM, this involves:

- Organising by beam angle from 179 -> 181.
- Then stacking the energy layers from highest to lowest.

  - Also adding in intermediate energy layers with single spots if jumps between layers are larger than a given number of MeV to be decided.

- Then arranging the spots to scan back and forth from a given corner of the field.

  - currently will presume that the plan can achieve any size of position jump but this may need to be corrected in the future

- Finally, if a different dose rate has been requested, for the final spot in the final energy layer deliver the requested dose rate and then the remaining MU.

- Converter to fill in the gaps to create a deliverable plan

  - arrange spots in a layer to scan properly
  - add in intermediary spots for large lateral jumps at a minimum MU value – may be redundant
  - add intermediate spots every 2 MeV for large energy layer jumps

- Write out the plan based on a given template (either a cylindrical or cubic phantom)

  - write out plans that contain all energies for a given gantry angle into a single beam, and a plan with each energy layer delivered as a single beam
  - For a plan with a single spot at many energies and gantry angles (expecting to be for XRV work) offer the option to also do a plan with a plan for each energy setting with all the gantry angles in so can test isocentricity of each energy separately.

## Elements

### qaPlanGenerator.py

**qaSpotPrepare**

Starts with various limits such as limits on gantry angles, energies, energy spacing, X and Y field sizes, and minimum dose deliverable<br>
Will check that each element is acceptable for delivery<br>
Then will work through beam by beam and order and arrange to produce a dataset that would be considered deliverable if written directly to a .dcm file

**qaPlanWrite**

Good to add in a way of passing the plan type parameters that are passed from qaPlanType to then be added as the plan name.<br>
Writes the full plan data out based on a template file. Currently doesn't handle range shifter which will need to be added as well as back compatible to all the other elements of this process.

## To Develop

Things to be added into the programme.

1. Currently assumes can jump to whatever position desired in the field as we have been told this is possible by Varian. May need to implement this in the future if we find that it doesn't work.

2. Have a flag for if the angles are -180 - 180 rather than 0 - 360, will need to do some internal consistency checking using this but need to develop later.

3. Need to add in range shifters as an option for all elements of the plan production process.

## Testing

Any testing to be performed and/or files included to test the fucntions.

## Issues

Things that are a problem that need to be updated and/or fixed.

# Appendix: DEV NOTES

Here are notes taken as the project develops, not neat and tidy
