#!/usr/bin/env python

from MRChem import MrchemOut
import glob
import sys
import pandas as pd

# Get all relevant output files in a list
files = glob.glob("*_*_*_*.out")
error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)
# Get rid of extension
filenames = map(lambda x: x.split(".")[0], files)

#Test if all jobs terminated normally
assert len(error_files) == 0, "Error! These {} job(s) did not terminate normally: {}".format(len(error_files), ' '.join([MrchemOut(f).filename for f in files if not MrchemOut(f).normaltermination()]))

print("All jobs terminated normally")

# now we construct the dict and fill with information from filenames
# this dict will contain the raw data for each calculation
rawdata = {}
rawdata["molecule"] =    [f.split("_")[0] for f in filenames]
rawdata["functional"] = [f.split("_")[1] for f in filenames]
rawdata["field"] =       [f.split("_")[3] for f in filenames]
rawdata["direction"] = [f.split("_")[4] for f in filenames]
rawdata["energy"] = []
rawdata["dipole"] = []
rawdata["filename"] = []
rawdata["precision"] = []

# now collect the energies, dipoles, filenames, and precisions from output 
# and add them to the dict
for f in files:
    output = MrchemOut(f)
    rawdata["energy"].append(output.final_energy_pot())
    rawdata["dipole"].append(output.dipole_au())
    rawdata["filename"].append(output.filename)
    rawdata["precision"].append(output.precision())
    
# now write raw data to CSV file using a useful pandas command
pd.DataFrame(rawdata).to_csv("rawdata.csv")


# We will need a function that converts a string into a float. Example: "00025" -> 0.0025
def decimal(s):
    return s[0:1] + "." + s[1:]

# now collect the jobs on same molecule with same functional at same precision, but with fields of opposite signs
# appending filenames and absolute value of field strength
triplet = []
for f in filter(lambda f: f.split("_")[3] == "-001", files):
    for g in filter(lambda f: f.split("_")[3] == "+001", files):
        if f.split("_")[0] == g.split("_")[0] and f.split("_")[1] == g.split("_")[1] and f.split("_")[2] == g.split("_")[2] and f.split("_")[4] == g.split("_")[4]:
            triplet.append([f, g, decimal(f.split("_")[3][1:])])

for i, trip in enumerate([el for trip in triplet for el in trip if "+" in el]):
    triplet[i].append(trip.split("_")[0])
    triplet[i].append(trip.split("_")[1])
    triplet[i].append(str(MrchemOut(trip).precision()))
    triplet[i].append(str(MrchemOut(trip).filename))
    triplet[i].append(trip.split("_")[4].split(".")[0])


# first unzip the sorted list (the order has been triple checked)
minus, plus, field, mol, func, prec, direction = (zip(*sorted(triplet)))

# then map the energy/diple moment to the list, and convert to string
#plus = map(str, map(lambda f: MrchemOut(f).dipole_au(), plus))
#minus = map(str, map(lambda f: MrchemOut(f).dipole_au(), minus))

# then zip back
triplet = zip(mol, func, prec, field, direction, plus, minus)

# now insert header
triplet.insert(0, ("molecule", "functional", "precision", "field_strength", "direction", "u+", "u-"))

# finally print to terminal in a format easily copied to Excel
for i in triplet:
    print(' '.join(i))



