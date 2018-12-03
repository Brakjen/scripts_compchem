#! /usr/bin/env python

def xyz_to_com(xyzfile):
    """Convert an XYZ file format to a Gaussian input format (.com). The input file 
       contains only the bare minimum to be opened with GaussView, essentially only the coordinates.
       The new filename is the same as the given XYZ file, but with '.com' extension, so beware
       that you don't overwrite any files."""
    job = xyzfile.split(".")[0]
    with open(xyzfile,"r") as infile:
        inlines = infile.readlines()[2:]

    # get rid of special characters such as tabs and newlines
    coords = map(lambda x: ' '.join(x.strip().split()), inlines)
    
    with open(job+".com","w") as o:
        o.write("#\n")
        o.write("\n")
        o.write("Number of atoms: {}\n".format(len(coords)))
        o.write("\n")
        o.write("0 1\n")

        for atom in coords:
            o.write(atom+"\n")
        o.write('\n')
    return None

def com_to_xyz(comfile):
    """Extract the coordinates from a Gaussian input file, and save them as an XYZ file. 
       The new filename is the same as the given XYZ file, but with '.com' extension, so beware
       that you don't overwrite any files."""
    job = comfile.split(".")[0]
    with open(comfile, "r") as infile:
        coords = infile.read().split("\n\n")[2].split("\n")[1:]

    # get rid of special characters such as tabs and newlines
    coords = map(lambda x: ' '.join(x.strip().split()), coords)
    
    with open(job+".xyz", "w") as o:
        o.write("{}\n".format(len(coords)))
        o.write("\n")
        for atom in coords:
            o.write(atom+"\n")


def ang_to_bohr(xyzfile):
    """Convert the XYZ coordinates in an XYZ file from Angstrom to Bohr. 
       Only works with XYZ files."""
    job = xyzfile.split(".")[0]
    with open(xyzfile, "r") as infile:
        coords = infile.readlines()[2:]
    elements = map(lambda x: x.split()[0], coords)
    coords   = map(lambda x: x.split()[1:], coords)
    
    for i,atom in enumerate(coords):
        for j,c in enumerate(atom):
            coords[i][j] = str(float(coords[i][j]) * 1.889726)
    
    with open(job+"_bohr.xyz", "w") as o:
        o.write("{}\n".format(len(coords)))
        o.write("Geometry in Bohr\n")
        for i,atom in enumerate(elements):
            o.write("{} \t {}\n".format(atom, ' '.join(coords[i])))
    return None

def bohr_to_ang(xyzfile):
    """Convert the XYZ coordinates in an XYZ file from Bohr to Angstrom. 
       Only works with XYZ files."""
    job = xyzfile.split(".")[0]
    with open(xyzfile, "r") as infile:
        coords = infile.readlines()[2:]
    elements = map(lambda x: x.split()[0], coords)
    coords   = map(lambda x: x.split()[1:], coords)
    
    for i,atom in enumerate(coords):
        for j,c in enumerate(atom):
            coords[i][j] = str(float(coords[i][j]) / 1.889726)
    
    with open(job+"_ang.xyz", "w") as o:
        o.write("{}\n".format(len(coords)))
        o.write("Geometry in Angstrom\n")
        for i,atom in enumerate(elements):
            o.write("{} \t {}\n".format(atom, ' '.join(coords[i])))
    return None
