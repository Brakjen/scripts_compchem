import sys
sys.path.append("/Users/abr121/Documents/github/computational_chemistry")
import os
from MRChem import MrchemOut
import glob
import pandas as pd
import os
import numpy as np
import shutil

# We will need a function that converts a string into a float. Example: "00025" -> 0.0025
def decimal(s):
    if "+" in s or "-" in s:
        return s[0] + s[1:2] + "." + s[2:]
    elif "Zero" in s:
        return "0"

#//////////////////////////////////////////////////////////////////////////////////////
suffix = sys.argv[1] # Used to define the naming for the particular job
#//////////////////////////////////////////////////////////////////////////////////////

root = os.getcwd()
datafiledir = os.path.join(root, "datafiles_{}".format(suffix))
if os.path.isdir(datafiledir):
    shutil.rmtree(datafiledir)
    os.mkdir(datafiledir)
else:
    os.mkdir(datafiledir)

# Must copy all necessary files into datafiledir
for f in glob.glob("{}/*.out".format(root)) + glob.glob("{}/*.inp".format(root)):
    shutil.copyfile(f, os.path.join(datafiledir, os.path.basename(f)))


# Get all relevant output files in a list
print("Aqcuiring output files...")
files = glob.glob("{}/*_*_*_*.out".format(datafiledir))
molecules = set(map(lambda x: os.path.basename(x).split("_")[0], files))
functionals = set(map(lambda x: os.path.basename(x).split("_")[1], files))

error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)

#Test if all jobs terminated normally
#print("Asserting...")
#assert len(error_files) == 0, "Error! These {} job(s) did not terminate normally: \n{}".format(len(error_files), '\n'.join([os.path.basename(MrchemOut(f).filename) for f in files if not MrchemOut(f).normaltermination()]))

#print(">>> All jobs terminated normally")
print("Initializing data structure...")

# now we construct the dict and fill with information from filenames
# this dict will contain the raw data for each calculation
skip_molecules = sys.argv[-1].split("=")[-1].split(",") # Skip these molecules (perhaps not all jobs are converged yet?)

rawdata = {}
rawdata["molecule"] =    [os.path.basename(f).split("_")[0] for f in files if os.path.basename(f).split("_")[0] not in skip_molecules]
rawdata["functional"] = [os.path.basename(f).split("_")[1] for f in files if os.path.basename(f).split("_")[0] not in skip_molecules]
rawdata["direction"] =       [os.path.basename(f).split("_")[3].split(".")[0] for f in files if os.path.basename(f).split("_")[0] not in skip_molecules]
rawdata["field"] = [decimal(os.path.basename(f).split("_")[2]) for f in files if os.path.basename(f).split("_")[0] not in skip_molecules]
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


# now collect the energies, dipoles, filenames, and precisions from output 
# and add them to the dict
for f in files:
    if os.path.basename(f).split("_")[0] in skip_molecules:
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
pd.DataFrame(rawdata).to_csv("rawdata_{}.csv".format(suffix))
print(">>>> Done!")


####################################################
### NOW MAKE NICE OUTPUT TO BE COPIED INTO EXCEL ###
####################################################

# we need to collect those files that will be part of the same calculation.
# get a tuple of the form:
# (molecule    functional    strength    direction    u+    u-    u0)

os.chdir(datafiledir)

# Initializing data list
data = []
skipped_molecules = [] # use as a control
for f in files:
    for mol in molecules:
        if mol in skip_molecules:
            skipped_molecules.append(mol)
            continue
        for func in functionals:
            if mol == os.path.basename(f).split("_")[0] and func == os.path.basename(f).split("_")[1]:
                
                # Get the multiplicity the input file
                with open(f.replace(".out", ".inp"), "r") as ipf:
                    lines = ipf.readlines()
                for line in lines:
                    if line.strip().startswith("multiplicity") or line.strip().startswith("Multiplicity"):
                        mult = line.strip().split()[-1]
                        break
                
                print("Generating nice data for: {}".format(os.path.basename(f)))
                if "_x.out" in f:
                    if "_Zero_" in f:
                        continue
                    else:
                        null  = "{}_{}_{}_{}.out".format(mol, func, "000", "x")
                        plus  = "{}_{}_{}_{}.out".format(mol, func, "+0001", "x")
                        minus = "{}_{}_{}_{}.out".format(mol, func, "-0001", "x")
                        if [mol, func, "x", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)] not in data:
                            data.append([mol, func, "x", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)])

                elif "_y.out" in f:
                    if "_Zero_" in f:
                        continue
                    else:
                        null = "{}_{}_{}_{}.out".format(mol, func, "000", "y")
                        plus  = "{}_{}_{}_{}.out".format(mol, func, "+0001", "y")
                        minus = "{}_{}_{}_{}.out".format(mol, func, "-0001", "y")
                        if [mol, func, "y", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)] not in data:
                            data.append([mol, func, "y", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)])

                elif "_z.out" in f:
                    if "_Zero_" in f:
                        continue
                    else:
                        null = "{}_{}_{}_{}.out".format(mol, func, "000", "z")
                        plus  = "{}_{}_{}_{}.out".format(mol, func, "+0001", "z")
                        minus = "{}_{}_{}_{}.out".format(mol, func, "-0001", "z")
                        if [mol, func, "z", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)] not in data:
                            data.append([mol, func, "z", mult, os.path.basename(null), os.path.basename(plus), os.path.basename(minus)])
print(">>> Done!")
# Now replace the file names with the values
for i, el in enumerate(data):
    print("Extracting dipole vector data for: {}".format(' '.join(el[:3])))

    if el[2] == "x":
        index = 0
    elif el[2] == "y": 
        index = 1
    elif el[2] == "z":
        index = 2

    data[i][4] = MrchemOut(data[i][4]).dipole_vector()[index]

    data[i][5] = MrchemOut(data[i][5]).dipole_vector()[index]

    data[i][6] = MrchemOut(data[i][6]).dipole_vector()[index]

print(">>> Done!")

fieldstrength = 0.001
bohr_to_ang = 1.8897162

# Now append the static polarizabilities
for job in data:
    job.append((job[5] - job[6]) / (2*fieldstrength) / (bohr_to_ang**3))

# map everything to strings for simpler writing to file
data = [map(str, i) for i in data]

os.chdir(root)
print("Writing nice data to file...")

header = "Molecule,Functional,Field Direction,Multiplicity,u_0,u_+,u_-,alpha (A^3)"
with open("nicedata_{}.csv".format(suffix), "w") as f:
    f.write(header + "\n")
    for job in data:
        f.write(','.join(job) + "\n")
print(">>> Done!")
print("These molecules were skipped: {}".format(', '.join(set(skipped_molecules))))
