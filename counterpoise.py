#! /usr/bin/env python
#################################################################################
# This script generates an ORCA compound job that performs the four necessary
# single point calculations in order to get the counterpoise correction to the
# binding energy. The final correction is defined as a variable in the compound
# block, and is easily found at the end of the output file, along with its four
# components.
# -----------------------------------------------------------------------------
# This script takes two mandatory arguments and one optional one:

# 1) XYZ file of fragment 1
# 2) XYZ file of fragment 2
# 3) [optional] name for the generated input file (wthout extension)

# The input file will be saved with the arbitrary name "counterpoise.inp",
# unless the third argument is used to specify the name.
# -----------------------------------------------------------------------------
# Call the script like this:
# python counterpoise.py <fragment1.xyz> <fragment2.xyz> <filename>
# -----------------------------------------------------------------------------
# The counterpoise-corrected energy should be computed as follows:

# E = Delta_E + E_counterpoise

# where E_counterpoise is the energy obtained from running this job, and Delta_E
# is the dissociation or association energy.
# -----------------------------------------------------------------------------
# IMPORTANT!!!
# -------------
# The fragment xyz files should contain the coordinates of each fragment at the
# optimized complex geometry, and NOT the coordinates of each fragment optimized
# individually
# -----------------------------------------------------------------------------
# Author:
# Anders Brakestad
# University of Tromso - The Arctic University of Norway
# PhD Candidate in Computational Chemistry
# -----------------------------------------------------------------------------
# Last edit: 2019-03-06
################################################################################

import sys

# Separate the arguments
fragment1 = sys.argv[1]
fragment2 = sys.argv[2]
try:
    jobname = sys.argv[3]+".inp"
except IndexError:
    jobname = "counterpoise.inp"

# Read content of xyz and input files
with open(fragment1, "r") as f: fragment1_coord = f.readlines()[2:]
with open(fragment2, "r") as f: fragment2_coord = f.readlines()[2:]

# Convert coordinates to more practical format
fragment1_coord = [i.strip() for i in fragment1_coord]
fragment2_coord = [i.strip() for i in fragment2_coord]

# Define the coordinate format necessary for the single point calculations
# of each fragment but with the complex basis set
# The coordinates containing ":" will be treated as dummy atoms by ORCA
fragment1_coord_complexbasis = fragment1_coord + map(lambda x: x.split()[0]+" : "+' '.join(x.split()[1:]), fragment2_coord)
fragment2_coord_complexbasis = fragment2_coord + map(lambda x: x.split()[0]+" : "+' '.join(x.split()[1:]), fragment1_coord)

# Now we are ready to start making the input file.
with open(jobname, "w") as f:
    # We need an arbitrary initial structure for the Compound method to work.
    # However, this structure will be overwrittne once we provide out actual coordinates
    f.write("# We need to insert a dummy structure to satisfy ORCA, as it is expected with the compound method\n")
    f.write("* xyz 0 1\n")
    f.write("H 0 0 0\n")
    f.write("*\n\n")

    f.write("%Compound\n")

    f.write("\tvariable SP1, SP2, SP3, SP4 end\n")
    f.write("\tvariable COUNTERPOISE_CORRECTION_AU end\n\n")
    f.write("\tvariable COUNTERPOISE_CORRECTION_KCALMOL end\n\n")

    f.write("\t# Calculation 1: fragment 1 @ complex geom with fragment 1 basis\n")
    f.write("\tNew_Step\n")
    f.write("\t\t!keywords\n")
    f.write("\t\t%Pal NProcs 16 End\n")
    f.write("\t\t* xyz charge multiplicity\n")
    for atom in fragment1_coord:
        f.write("\t\t"+atom + "\n")
    f.write("\t\t*\n")
    f.write("\tStep_End\n")
    f.write("\tRead SP1 = SCF_ENERGY[1] End\n\n")
    

    f.write("\t# Calculation 2: fragment 1 @ complex geom with complex basis\n")
    f.write("\tNew_Step\n")
    f.write("\t\t!keywords\n")
    f.write("\t\t%Pal NProcs 16 End\n")
    f.write("\t\t* xyz charge multiplicity\n")
    for atom in fragment1_coord_complexbasis:
        f.write("\t\t"+atom + "\n")
    f.write("\t\t*\n")
    f.write("\tStep_End\n")
    f.write("\tRead SP2 = SCF_ENERGY[2] End\n\n")


    f.write("\t# Calculation 3: fragment 2 @ complex geom with fragment 2 basis\n")
    f.write("\tNew_Step\n")
    f.write("\t\t!keywords\n")
    f.write("\t\t%Pal NProcs 16 End\n")
    f.write("\t\t* xyz charge multiplicity\n")
    for atom in fragment2_coord:
        f.write("\t\t"+atom + "\n")
    f.write("\t\t*\n")
    f.write("\tStep_End\n")
    f.write("\tRead SP3 = SCF_ENERGY[3] End\n\n")


    f.write("\t# Calculation 4: fragment 2 @ complex geom with complex basis\n")
    f.write("\tNew_Step\n")
    f.write("\t\t!keywords\n")
    f.write("\t\t%Pal NProcs 16 End\n")
    f.write("\t\t* xyz charge multiplicity\n")
    for atom in fragment2_coord_complexbasis:
        f.write("\t\t"+atom + "\n")
    f.write("\t\t*\n")
    f.write("\tStep_End\n")
    f.write("\tRead SP4 = SCF_ENERGY[4] End\n\n")


    f.write("\tAssign COUNTERPOISE_CORRECTION_AU = -(SP2 - SP1 + SP4 - SP3) End\n")
    f.write("\tAssign COUNTERPOISE_CORRECTION_KCALMOL = 627.509 * COUNTERPOISE_CORRECTION_AU End\n")

    f.write("End\n")
