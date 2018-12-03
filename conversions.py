#! /usr/bin/env python

from Gaussian import *
from Orca import *

def xyz_to_com(xyzfile):
    job = xyzfile.split(".")[0]
    with open(xyzfile,"r") as infile:
        inlines = infile.readlines()[2:]

    elements = filter(lambda x: x.split()[0], inlines)
    coords =   filter(lambda x: x.split()[1:], inlines)

    with open(job+"_test.com","w") as o:
        o.write('{}\n'.format(len(coords)))
        o.write("XYZ file")
        for i,atom in enumerate(elements):
            o.write('{} \t {}\n'.format(atom, ' '.join(coords[i])))
            o.write('\n')
    return None

def com_to_xyz(comfile):
    pass

def ang_to_bohr(xyzfile):
    job = xyzfile.split(".")[0]
    with open(xyzfile, "r") as infile:
        coords = infile.readlines()[2:]
    elements = map(lambda x: x.split()[0], coords)
    coords   = map(lambda x: x.split()[1:], coords)
    
    for i,atom in enumerate(coords):
        for j,c in enumerate(atom):
            coords[i][j] = str(float(coords[i][j]) * 1.889726)
    
    with open(job+"_au.xyz", "w") as o:
        o.write("{}\n".format(len(coords)))
        o.write("Geometry in Bohr\n")
        for i,atom in enumerate(elements):
            o.write("{} \t {}\n".format(atom, ' '.join(coords[i])))
    return None

def bohr_to_ang(xyzfile):
    job = xyzfile.split(".")[0]
    with open(xyzfile, "r") as infile:
        coords = infile.readlines()[2:]
    elements = map(lambda x: x.split()[0], coords)
    coords   = map(lambda x: x.split()[1:], coords)
    
    for i,atom in enumerate(coords):
        for j,c in enumerate(atom):
            coords[i][j] = str(float(coords[i][j]) / 1.889726)
    
    with open(job+"_au.xyz", "w") as o:
        o.write("{}\n".format(len(coords)))
        o.write("Geometry in Bohr\n")
        for i,atom in enumerate(elements):
            o.write("{} \t {}\n".format(atom, ' '.join(coords[i])))
    return None
