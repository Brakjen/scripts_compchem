import sys
sys.path.append("/home/ambr/scripts_compchem")
import os
from MRChem import MrchemOut
import glob
import shutil
from pprint import pprint

# We will need a function that converts a string into a float. Example: "00025" -> 0.0025
def decimal(s):
    if "+" in s or "-" in s:
        return s[0] + s[1:2] + "." + s[2:]
    elif "Zero" in s:
        return "0"

#//////////////////////////////////////////////////////////////////////////////////////
suffix = sys.argv[1] # Used to define the naming for the particular job
#//////////////////////////////////////////////////////////////////////////////////////
fieldstrength = 0.001
bohr_to_ang = 1.8897162
#//////////////////////////////////////////////////////////////////////////////////////

root = os.getcwd()

# Get all relevant output files in a list
print("Aqcuiring output files...")
files = glob.glob("{}/*_*_*_*.out".format(root))
molecules = set(map(lambda x: os.path.basename(x).split("_")[0], files))
functionals = set(map(lambda x: os.path.basename(x).split("_")[1], files))

error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)
error_molecules = set(map(lambda x: os.path.basename(x).split("_")[0], error_files))

# now we construct the dict and fill with information from filenames
# this dict will contain the raw data for each MRChem calculation
print("Initializing data structure...")
rawdata = {}
rawdata["molecule"] =    [os.path.basename(f).split("_")[0] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
rawdata["functional"] = [os.path.basename(f).split("_")[1] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
rawdata["direction"] =       [os.path.basename(f).split("_")[3].split(".")[0] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
rawdata["field"] = [decimal(os.path.basename(f).split("_")[2]) for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
rawdata["energy"] = []
rawdata["u_norm"] = []
rawdata["u_x"] = []
rawdata["u_y"] = []
rawdata["u_z"] = []
rawdata["filename"] = []
rawdata["precision"] = []
rawdata["no_scf_cycles"] = []
rawdata["walltime"] = []
rawdata["property_threshold"] = []
rawdata["orbital_threshold"] = []


# now collect the remaining information
# and add them to the dict
print("Adding remainding data...")
for f in files:
    if os.path.basename(f).split("_")[0] in error_molecules:
        continue
    output = MrchemOut(f)
    rawdata["energy"].append(output.final_energy_pot())
    rawdata["u_norm"].append(output.dipole_norm_au())
    rawdata["u_x"].append(output.dipole_vector()[0])
    rawdata["u_y"].append(output.dipole_vector()[1])
    rawdata["u_z"].append(output.dipole_vector()[2])
    rawdata["filename"].append(os.path.basename(output.filename))
    rawdata["precision"].append(output.precision())
    rawdata["no_scf_cycles"].append(output.no_scfcycles())
    rawdata["walltime"].append(output.walltime())
    rawdata["property_threshold"].append(output.property_threshold())
    rawdata["orbital_threshold"].append(output.orbital_threshold())
    
print(">>> Done!")

# now write raw data to CSV file using a useful pandas command
print"Writing raw data to CSV,,,"

