#!/usr/bin/env python

from MRChem import MrchemOut
import glob

# Get all relevant output files in a list
files = glob.glob("*_*_*_*_.out")
nullfield_files = filter(lambda f: f.split("_")[3] == "00", files)
error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)

#Test if all jobs terminated normally
assert len(error_files) == 0, "Error! These {} job(s) did not terminate normally: {}".format(len(error_files), ' '.join([MrchemOut(f).filename for f in files if not MrchemOut(f).normaltermination()]))

print("All jobs terminated normally")

# now we construct the dict and fill with information from filenames
# this dict will contain the raw data for each calculation
rawdata = {}
rawdata["molecule"] =    [f.split("_")[0] for f in files]
rawdata["functional"] = [f.split("_")[1] for f in files]
rawdata["field"] =       [f.split("_")[3] for f in files]
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
        if f.split("_")[0] == g.split("_")[0] and f.split("_")[1] == g.split("_")[1] and f.split("_")[2] == g.split("_")[2]:
            triplet.append([f, g, decimal(f.split("_")[3][1:])])

for f in filter(lambda f: f.split("_")[3] == "-0005", files):
    for g in filter(lambda f: f.split("_")[3] == "+0005", files):
        if f.split("_")[0] == g.split("_")[0] and f.split("_")[1] == g.split("_")[1] and f.split("_")[2] == g.split("_")[2]:
            triplet.append([f, g, decimal(f.split("_")[3][1:])])

for f in filter(lambda f: f.split("_")[3] == "-00025", files):
    for g in filter(lambda f: f.split("_")[3] == "+00025", files):
        if f.split("_")[0] == g.split("_")[0] and f.split("_")[1] == g.split("_")[1] and f.split("_")[2] == g.split("_")[2]:
            triplet.append([f, g, decimal(f.split("_")[3][1:])])


# now we need to append the appropriate null field files to each sublist along with molecule, functional, and precision
for f in nullfield_files:
    for trip in triplet:
        if f.split("_")[0] == trip[0].split("_")[0] and f.split("_")[1] == trip[0].split("_")[1] and f.split("_")[2] == trip[0].split("_")[2]:
            trip.append(f)
            trip.append(f.split("_")[0])
            trip.append(f.split("_")[1])
            trip.append(str(MrchemOut(f).precision()))


# first unzip the sorted list (the order has been triple checked)
minus, plus, field, null, mol, func, prec = (zip(*sorted(triplet)))

# then map the energy/diple moment to the list, and convert to string
plus = map(str, map(lambda f: MrchemOut(f).final_energy_pot(), plus))
minus = map(str, map(lambda f: MrchemOut(f).final_energy_pot(), minus))
null = map(str, map(lambda f: MrchemOut(f).dipole_au(), null))

# then zip back
triplet = zip(mol, func, prec, field, plus, minus, null)

# now insert header
triplet.insert(0, ("molecule", "functional", "precision", "field_strength", "e+", "e-", "dipole_null"))

# finally print to terminal in a format easily copied to Excel
for i in triplet:
    print(' '.join(i))



