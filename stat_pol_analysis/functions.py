import sys, os, glob, pandas, operator, yaml, shutil
from pprint import pprint
sys.path.append("/Users/{}/Documents/github/computational_chemistry".format(os.getenv("USER")))
from MRChem import MrchemOut
from Orca import OrcaOut

def get_HG_data(datafile, functionals=[]):
    """
    Collect data for the functionals we are interested in,
    and convert to yaml format. 
    Return the yaml data file name.
    Give name of wanted functionals in list as kwarg to function
    """
    with open(datafile, "r") as ref:
        raw_data = ref.readlines()[:133]
    
    raw_data = map(lambda x: x.split(","), raw_data)
    
    # Initialize the dict which will contains the data
    # and a dict for storing the column indeces of the 
    # functionals we are intersted in
    data = {}
    indeces = {}
    # Convert to upper case
    functionals = map(lambda x: x.upper(), functionals)
    for i, mol in enumerate(raw_data):
        # Determine the column index for the functionals we want
        if i == 0:
            for col, func in enumerate(mol):
                if func in functionals:
                    indeces[func.lower()] = col
        
        else:
            # Initialize sub-dict
            molecule = mol[0].lower()
            data[molecule] = {}
            
    
            # Insert the data we want
            data[molecule]["spin"] = mol[1]
            for func, idx in indeces.items():
                data[molecule][func] = {"diagonal": [], "mean": ""}
                data[molecule][func]["diagonal"] = map(float, mol[idx+1:idx+4])
                data[molecule][func]["mean"] = sum(data[molecule][func]["diagonal"]) / 3


    with open("hg_data.yaml", "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
    return data


def decimal(s):
    """
    Perform the following conversions:
    +0001     ->   0.001
    -0001     ->   -0.001
    Zero      ->   0
    """
    if "+" in s or "-" in s:
        return s[0] + s[1:2] + "." + s[2:]
    else:
        return "0"

def stem(s):
    """
    Strip filename of its extension
    """
    if isinstance(s, str):
        return s.split(".")[0]
    else:
        raise TypeError("You did not pass a string to the stem function")

def get_pol_data(datadir):
    """
    Extract information about each MRChem calculation, and store as a CSV file.
    Return the CSV filename.

    Parameters:
    datadir       name of dir where output and input files are stored (not full path)
    """
    # Get all relevant output files in a list
    datafiles = os.path.join(os.getcwd(), datadir)

    files = glob.glob("{}/*.out".format(datafiles))
    molecules = set(map(lambda x: os.path.basename(x).split("_")[0], files))
    functionals = set(map(lambda x: os.path.basename(x).split("_")[1], files))
    
    error_files = filter(lambda f: not MrchemOut(f).normaltermination(), files)
    error_molecules = set(map(lambda x: os.path.basename(x).split("_")[0], error_files))
    print("Skipping these due to bad termination: {}".format(", ".join(error_molecules)))
    
    # now we construct the dict and fill with information from filenames
    # this dict will contain the raw data for each MRChem calculation
    rawdata = {}
    rawdata["molecule"] =    [os.path.basename(f).split("_")[0] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["functional"] = [os.path.basename(f).split("_")[1] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["direction"] =  [stem(os.path.basename(f)).split("_")[3] if len(stem(os.path.basename(f)).split("_")) == 4 else "non" for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["field"] = [decimal(stem(os.path.basename(f)).split("_")[2]) for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
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
    rawdata["multiplicity"] = []
    
    
    # now collect the remaining information
    # and add them to the dict
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

        # Get multiplicity from input file
        with open(f.replace(".out", ".inp"), "r") as inputfile: inputlines = inputfile.readlines()
        for line in inputlines:
            if line.strip().startswith("multiplicity") or line.strip().startswith("Multiplicity"):
                mult = int(line.split("=")[-1])
                break
        rawdata["multiplicity"].append(mult)
        
    
    # now write raw data to CSV file using a useful pandas command
    pandas.DataFrame(rawdata).to_csv("mw_rawdata.csv")
    return rawdata
   

def get_mw_pol_fdu(rawdatafile, fieldstrength=0.001, bohr_to_ang=1.8897162):
    """
    Extract relavant pol information from rawdata, and construct a dictionary to store
    the alpha_xx, alpha_yy, and alpha_zz values, for each molecule and each functional used.

    Parameters:
    rawdatafile       name of CSV file containing all raw data
    fieldstrength     the absolute value of the static electric field strength used
    bohr_to_ang       Conversion factor for converting 1 Bohr to Angstrom
    """
    
    # String representation of the positive and negative fields used
    # and the field directions
    fields = ["+"+''.join(str(fieldstrength).split(".")), "-"+''.join(str(fieldstrength).split("."))]
    directions = ["x", "y", "z"]
    
    with open(rawdatafile, "r") as raw:
        jobs = raw.readlines()
    
    # identify the correct column indeces for data we need
    index = {}
    headers = ["molecule", "functional", "direction", "field", "u_x", "u_y", "u_z", "filename", "multiplicity"]
    for i, raw_header in enumerate(jobs[0].split(",")):
        if raw_header in headers:
            index[raw_header] = i
    
    # Sort the raw data to make data extraction possible
    jobs = sorted(map(lambda x: x.strip().split(","), jobs), key=operator.itemgetter(index["functional"], index["molecule"], index["direction"], index["field"]))
    
    # Get all unique molecules and functionals from rawdata
    molecules = set([job[index["molecule"]] for i, job in enumerate(jobs) if i>0])
    functionals = set([job[index["functional"]] for i, job in enumerate(jobs) if i>0])
    
    # Initialize data structure
    data = {}
    for mol in molecules:
        data[mol] = {}
        data[mol]["multiplicity"] = ""
        for func in functionals:
            data[mol][func] = {"diagonal": ["", "", ""],
                               "mean": ""}
            
            # Now we need to add the correct information to the initialized lists
            for field in fields:
                for dirr in directions:
                    # We will compare an ID to the job filename to make sure we get the correct data
                    ID = "_".join([mol, func, field, dirr]) + ".out"

                    # Avoid duplicates by making sure 'ID' is only the positive field jobs
                    if fields[1] in ID:
                        continue
   
                    # Now loop over the rawdata and compute the diagonal elements
                    # We only need to get the multiplicity once
                    # Due to the way the rawdata is sorted, we know that if the positive field job
                    # is on line 'i', then the corresponding negative field job is on line 'i+1'
                    for i, job in enumerate(jobs):
                        if ID == job[index["filename"]] and "_x" in ID:
                            data[mol][func]["diagonal"][0] = (float(jobs[i][index["u_x"]]) - float(jobs[i+1][index["u_x"]])) / 2 / fieldstrength / bohr_to_ang**3
                            try:
                                data[mol]["multiplicity"] = int(jobs[i][index["multiplicity"]])
                            except KeyError:
                                data[mol]["multiplicity"] = "na"
                        elif ID == job[index["filename"]] and "_y" in ID:
                            data[mol][func]["diagonal"][1] = (float(jobs[i][index["u_y"]]) - float(jobs[i+1][index["u_y"]])) / 2 / fieldstrength / bohr_to_ang**3
                        elif ID == job[index["filename"]] and "_z" in ID:
                            data[mol][func]["diagonal"][2] = (float(jobs[i][index["u_z"]]) - float(jobs[i+1][index["u_z"]])) / 2 / fieldstrength / bohr_to_ang**3
            
            # Now store the mean of the polarizability tensor diagonal
            data[mol][func]["mean"] = sum(data[mol][func]["diagonal"]) / 3
    # Now write the data to yaml file format
    with open("mw_data.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    return data

def get_mw_pol_fde(rawdatafile, fieldstrength=0.001, bohr_to_ang=1.8897162):
    """
    Extract relavant pol information from rawdata, and construct a dictionary to store
    the alpha_xx, alpha_yy, and alpha_zz values, for each molecule and each functional used.

    Parameters:
    rawdatafile       name of CSV file containing all raw data
    fieldstrength     the absolute value of the static electric field strength used
    bohr_to_ang       Conversion factor for converting 1 Bohr to Angstrom
    """
    
    # String representation of the positive and negative fields used
    # and the field directions
    fields = ["+"+''.join(str(fieldstrength).split(".")), "-"+''.join(str(fieldstrength).split("."))]
    directions = ["x", "y", "z"]
    
    with open(rawdatafile, "r") as raw:
        jobs = raw.readlines()
    
    # identify the correct column indeces for data we need
    index = {}
    headers = ["energy", "molecule", "functional", "direction", "field", "u_x", "u_y", "u_z", "filename", "multiplicity"]
    for i, raw_header in enumerate(jobs[0].split(",")):
        if raw_header in headers:
            index[raw_header] = i
    
    # Sort the raw data to make data extraction possible
    jobs = sorted(map(lambda x: x.strip().split(","), jobs), key=operator.itemgetter(index["functional"], index["molecule"], index["direction"], index["field"]))
    
    # Get all unique molecules and functionals from rawdata
    molecules = set([job[index["molecule"]] for i, job in enumerate(jobs) if i>0])
    functionals = set([job[index["functional"]] for i, job in enumerate(jobs) if i>0])
    
    # Initialize data structure
    data = {}
    for mol in molecules:
        data[mol] = {}
        data[mol]["multiplicity"] = ""
        for func in functionals:
            data[mol][func] = {"diagonal": ["", "", ""],
                               "mean": ""}
            
            # Now we need to add the correct information to the initialized lists
            for field in fields:
                for dirr in directions:
                    # We will compare an ID to the job filename to make sure we get the correct data
                    ID = "_".join([mol, func, field, dirr]) + ".out"

                    # Avoid duplicates by making sure 'ID' is only the positive field jobs
                    if fields[1] in ID:
                        continue
   
                    # Now loop over the rawdata and compute the diagonal elements
                    # We only need to get the multiplicity once
                    # Due to the way the rawdata is sorted, we know that if the positive field job
                    # is on line 'i', then the corresponding negative field job is on line 'i+1'
                    # and that the zero-field job is at the "top" for each block of molecule jobs
                    for i, job in enumerate(jobs):
                        if ID == job[index["filename"]] and "_x" in ID:

                            data[mol][func]["diagonal"][0] = -(float(jobs[i][index["energy"]]) + float(jobs[i+1][index["energy"]]) - 2*float(jobs[i-1][index["energy"]])) / fieldstrength**2 / bohr_to_ang**3
                            try:
                                data[mol]["multiplicity"] = int(jobs[i][index["multiplicity"]])
                            except KeyError:
                                data[mol]["multiplicity"] = "na"

                        elif ID == job[index["filename"]] and "_y" in ID:
                            data[mol][func]["diagonal"][1] = -(float(jobs[i][index["energy"]]) + float(jobs[i+1][index["energy"]]) - 2*float(jobs[i-3][index["energy"]])) / fieldstrength**2 / bohr_to_ang**3
                        elif ID == job[index["filename"]] and "_z" in ID:
                            data[mol][func]["diagonal"][2] = -(float(jobs[i][index["energy"]]) + float(jobs[i+1][index["energy"]]) - 2*float(jobs[i-5][index["energy"]])) / fieldstrength**2 / bohr_to_ang**3
            
            # Now store the mean of the polarizability tensor diagonal
            data[mol][func]["mean"] = sum(data[mol][func]["diagonal"]) / 3
    # Now write the data to yaml file format
    with open("mw_data.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    return data

def get_mw_pol_response(datadir, bohr_to_ang=1.8897162):
    """
    Extracts polarizabilities from MRChem output files.
    
    Parameters:
    - datadir        path to directory containing all output files
    - bohr-to-ang    conversion factor from bohr to angstrom (default: 1.8897162)
    """
    
    outputfiles = glob.glob(datadir+"/"+"*.out")
    data = {}
    for job in outputfiles:
        if not MrchemOut(job).normaltermination():
            continue

        # Get molecule
        mol  = os.path.basename(job).split(".")[0]
        data[mol] = {}

        with open(job.replace(".out", ".inp")) as f: lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("$functionals"):
                func = lines[i+1].strip().lower()
        
        data[mol][func] = {}
        data[mol][func]["diagonal"] = map(lambda x: x / bohr_to_ang**3, MrchemOut(job).polarizability_diagonal(unit="au"))
        data[mol][func]["mean"] = sum(data[mol][func]["diagonal"]) / 3
        
    return data


def get_pol_data_orca(datadir):
    """
    Extract information about each Orca calculation, and store as a CSV file.
    Return the CSV filename.

    Parameters:
    datadir       name of dir where output and input files are stored (not full path)
    """
    cwd = os.getcwd()
    # Get all relevant output files in a list
    datafiles = os.path.join(os.getcwd(), datadir)

    files = glob.glob("{}/*.out".format(datafiles))
    molecules = set(map(lambda x: os.path.basename(x).split("_")[0], files))
    functionals = set(map(lambda x: os.path.basename(x).split("_")[1], files))
    
    error_files = filter(lambda f: not OrcaOut(f).normaltermination(), files)
    error_molecules = set(map(lambda x: os.path.basename(x).split("_")[0], error_files))
    print("Skipping these due to bad termination: {}".format(", ".join(error_molecules)))
    
    # now we construct the dict and fill with information from filenames
    # this dict will contain the raw data for each MRChem calculation
    rawdata = {}
    rawdata["molecule"] =    [os.path.basename(f).split("_")[0] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["functional"] = [os.path.basename(f).split("_")[1] for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["direction"] =  [stem(os.path.basename(f)).split("_")[3] if len(stem(os.path.basename(f)).split("_")) == 4 else "non" for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["field"] = [decimal(stem(os.path.basename(f)).split("_")[2]) for f in files if os.path.basename(f).split("_")[0] not in error_molecules]
    rawdata["energy"] = []
    rawdata["u_x"] = []
    rawdata["u_y"] = []
    rawdata["u_z"] = []
    rawdata["filename"] = []
    rawdata["no_scf_cycles"] = []
    rawdata["walltime"] = []
    
    
    # now collect the remaining information
    # and add them to the dict
    for f in files:
        if os.path.basename(f).split("_")[0] in error_molecules:
            continue
        output = OrcaOut(f)
        rawdata["energy"].append(output.scf_energy()[-1])
        rawdata["u_x"].append(output.dipole_vector()[0])
        rawdata["u_y"].append(output.dipole_vector()[1])
        rawdata["u_z"].append(output.dipole_vector()[2])
        rawdata["filename"].append(os.path.basename(output.filename))
        rawdata["no_scf_cycles"].append(output.no_scfcycles())
        rawdata["walltime"].append(output.walltime())

    # now write raw data to CSV file using a useful pandas command
    pandas.DataFrame(rawdata).to_csv(os.path.join(cwd, "orca_rawdata.csv"))
    return rawdata
