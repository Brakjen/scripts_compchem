#!/usr/bin/env python

from class_mrchem import MrchemOut
import glob
import sys
import pandas as pd

# Get all relevant output files in a list
files = glob.glob("*_*_*_*_.out")
error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)

 Test if all jobs terminated normally
#assert len(error_files) == 0, "Error! These jobs did not terminate normally: {}".format(' '.join([MrchemOut(f).filename for f in files if not MrchemOut(f).normaltermination()]))

# now we construct the dict and fill with information from filenames
data = {}
data["molecule"] =    [f.split("_")[0] for f in files if f not in error_files]
data["functional"] = [f.split("_")[1] for f in files if f not in error_files]
data["field"] =       [f.split("_")[3] for f in files if f not in error_files]
data["energy"] = []
data["dipole"] = []
data["filename"] = []
data["precision"] = []

# now collect the energies, dipoles, filenames, and precisions from output 
# and add them to the dict
for f in files:
    output = MrchemOut(f)
    if f not in error_files:
        data["energy"].append(output.energy_pot())
        data["dipole"].append(output.dipole_au())
        data["filename"].append(output.filename)
        data["precision"].append(output.precision())
    
# now write raw data to CSV file using a useful pandas command
pd.DataFrame(data).to_csv("rawdata.csv")

# to minimize manual manipulation in Excel, we should transform the raw data to the following format:

# molecule   field_strength    E^+     E^-     dipole_ref

# this means we need to pair up certain files. For instance, all jobs with +-field_strengths must be paired
# and the corresponding dipole_ref also need to be there. Thus we need to construct "triplets" of files:

# triplet = [(positive field, negative_field, dipole_ref), (triplet2), (triplet3), ..., (triplet_n)]


