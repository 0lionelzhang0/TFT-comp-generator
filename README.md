# TFT-comp-generator

![screenshot](https://i.imgur.com/HVQXqsB.png)

## How to use

You can either run the pygui.py script or if you don't have Python installed you can run the pygui.exe under the dist folder. The two json files in the dist folder need to be in the same folder as the executable for it to work.

The tool calculates semi brute force the possible team compositions and assigns score based on the number of total synergies. It only tries adding a potential unit if it has a direct synergy with a unit already in the comp.

Calculations may take a long time if the total number of units is set greater than 4 more than the number of selected units.

If you want to select multiple starting units, it is best to select units that have at least one synergy link for best results.

