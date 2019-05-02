import os, sys, glob, pandas, operator
from pprint import pprint
sys.path.append("/Users/{}/Documents/github/computational_chemistry".format(os.getenv("USER")))
from MRChem import MrchemOut

#//////////////////////////////////////////////////////////////////////////////////////
fieldstrength = 0.001
bohr_to_ang = 1.8897162
fields = ["+0001", "-0001"]
directions = ["x", "y", "z"]
#//////////////////////////////////////////////////////////////////////////////////////

root = os.getcwd()
rawdata_filename = os.path.join(root, "mw_rawdata.csv")

with open(rawdata_filename, "r") as raw:
    jobs = raw.readlines()

# identify the correct column indeces for data we need
index = {}
headers = ["molecule", "functional", "direction", "field", "u_x", "u_y", "u_z", "filename"]
for i, raw_header in enumerate(jobs[0].split(",")):
    if raw_header in headers:
        index[raw_header] = i

jobs = sorted(map(lambda x: x.strip().split(","), jobs), key=operator.itemgetter(index["functional"], index["molecule"], index["direction"], index["field"]))

molecules = set([job[index["molecule"]] for i, job in enumerate(jobs) if i>0])
functionals = set([job[index["functional"]] for i, job in enumerate(jobs) if i>0])

# Initialize data structure
data = {}
IDS = []
for mol in molecules:
    data[mol] = {}
    for func in functionals:
        data[mol][func] = ["", "", ""]

        # Now we need to add the correct information to the initialized lists
        for field in fields:
            for dirr in directions:
                ID = "_".join([mol, func, field, dirr]) + ".out"
                if "-" in ID:
                    continue
                else:
                    ID2 = ID.replace("+", "-" )

                for i, job in enumerate(jobs):
                    if ID == job[index["filename"]] and "_x" in ID:
                        print(jobs[i][index["filename"]], jobs[i+1][index["filename"]])
                        print(jobs[i][index["u_x"]], jobs[i+1][index["u_x"]])
                        #data[mol][func][0] = (float(jobs[i][index["u_x"]]) - float(jobs[i+1][index["u_x"]])) / 2 / fieldstrength / bohr_to_ang**3
                    elif ID == job[index["filename"]] and "_y" in ID:
                        print(jobs[i][index["filename"]], jobs[i+1][index["filename"]])
                        print(jobs[i][index["u_y"]], jobs[i+1][index["u_y"]])
                        #data[mol][func][1] = (float(jobs[i+2][index["u_y"]]) - float(jobs[i+3][index["u_y"]])) / 2 / fieldstrength / bohr_to_ang**3
                    elif ID == job[index["filename"]] and "_z" in ID:
                        print(jobs[i][index["filename"]], jobs[i+1][index["filename"]])
                        print(jobs[i][index["u_z"]], jobs[i+1][index["u_z"]])
                        print("")
                        #data[mol][func][2] = (float(jobs[i+4][index["u_z"]]) - float(jobs[i+5][index["u_z"]])) / 2 / fieldstrength / bohr_to_ang**3
pprint(data["alf"])
