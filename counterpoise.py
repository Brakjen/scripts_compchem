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
# The counterpoise-corrected reaction energy should be computed as follows:

# Delta_E(CP) = Delta_E + BSSE

# where BSSE is the energy obtained from running this job, and Delta_E
# is the uncorrected reaction energy.
# -----------------------------------------------------------------------------
# IMPORTANT!!!
# -------------
# The fragment xyz files should contain the coordinates of each fragment at the
# optimized complex geometry, and NOT the coordinates of each fragment optimized
# individually
#
# ALSO IMPORTANT!!!
# This script assumes you have used a dispersion correction, and will give error
# if this is not the case.
# -----------------------------------------------------------------------------
# Author:
# Anders Brakestad
# University of Tromso - The Arctic University of Norway
# PhD Candidate in Computational Chemistry
# -----------------------------------------------------------------------------
# Last edit: 2019-03-06
################################################################################


def counterpoise(fragment1,
                 fragment2,
                 charge_1=0,
                 charge_2=0,
                 mult_1=1,
                 mult_2=1,
                 keywords="!keywords",
                 jobname="counterpoise.inp",
                 raw_coordinates=False,
                 nprocs=16,
                 memory=800):

    # Read content of xyz and input files
    if raw_coordinates:
        fragment1_coord = fragment1
        fragment2_coord = fragment2
    else:
        with open(fragment1, "r") as f: fragment1_coord = f.readlines()[2:]
        with open(fragment2, "r") as f: fragment2_coord = f.readlines()[2:]

        # Convert coordinates to more practical format
        fragment1_coord = [i.strip() for i in fragment1_coord]
        fragment2_coord = [i.strip() for i in fragment2_coord]

    # Define the coordinate format necessary for the single point calculations
    # of each fragment but with the complex basis set
    # The coordinates containing ":" will be treated as dummy atoms by ORCA
    #fragment1_coord_complexbasis = fragment1_coord + map(lambda x: x.split()[0]+" : "+' '.join(x.split()[1:]), fragment2_coord)
    #fragment2_coord_complexbasis = fragment2_coord + map(lambda x: x.split()[0]+" : "+' '.join(x.split()[1:]), fragment1_coord)

    fragment1_coord_complexbasis = fragment1_coord + [x.split()[0]+" : "+' '.join(x.split()[1:]) for x in fragment2_coord]
    fragment2_coord_complexbasis = fragment2_coord + [x.split()[0]+" : "+' '.join(x.split()[1:]) for x in fragment1_coord]

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
        f.write("\tvariable D1, D2, D3, D4 end\n")
        f.write("\tvariable BSSE_AU end\n")
        f.write("\tvariable BSSE_KCALMOL end\n\n")

        f.write("\t# Calculation 1: fragment 1 @ complex geom with fragment 1 basis\n")
        f.write("\tNew_Step\n")
        f.write("\t\t{}\n".format(keywords))
        f.write("\t\t%Pal NProcs {} End\n".format(nprocs))
        f.write("\t\t%maxcore {}\n".format(memory))
        f.write("\t\t* xyz {} {}\n".format(charge_1, mult_1))
        for atom in fragment1_coord:
            f.write("\t\t"+atom + "\n")
        f.write("\t\t*\n")
        f.write("\tStep_End\n")
        f.write("\tRead D1 = VDW_CORRECTION[1] End\n")
        f.write("\tRead SP1 = SCF_ENERGY[1] End\n\n")


        f.write("\t# Calculation 2: fragment 1 @ complex geom with complex basis\n")
        f.write("\tNew_Step\n")
        f.write("\t\t{}\n".format(keywords))
        f.write("\t\t%Pal NProcs {} End\n".format(nprocs))
        f.write("\t\t%maxcore {}\n".format(memory))
        f.write("\t\t* xyz {} {}\n".format(charge_1, mult_2))
        for atom in fragment1_coord_complexbasis:
            f.write("\t\t"+atom + "\n")
        f.write("\t\t*\n")
        f.write("\tStep_End\n")
        f.write("\tRead D2 = VDW_CORRECTION[2] End\n")
        f.write("\tRead SP2 = SCF_ENERGY[2] End\n\n")


        f.write("\t# Calculation 3: fragment 2 @ complex geom with fragment 2 basis\n")
        f.write("\tNew_Step\n")
        f.write("\t\t{}\n".format(keywords))
        f.write("\t\t%Pal NProcs {} End\n".format(nprocs))
        f.write("\t\t%maxcore {}\n".format(memory))
        f.write("\t\t* xyz {} {}\n".format(charge_2, mult_2))
        for atom in fragment2_coord:
            f.write("\t\t"+atom + "\n")
        f.write("\t\t*\n")
        f.write("\tStep_End\n")
        f.write("\tRead D3 = VDW_CORRECTION[3] End\n")
        f.write("\tRead SP3 = SCF_ENERGY[3] End\n\n")


        f.write("\t# Calculation 4: fragment 2 @ complex geom with complex basis\n")
        f.write("\tNew_Step\n")
        f.write("\t\t{}\n".format(keywords))
        f.write("\t\t%Pal NProcs {} End\n".format(nprocs))
        f.write("\t\t%maxcore {}\n".format(memory))
        f.write("\t\t* xyz {} {}\n".format(charge_2, mult_2))
        for atom in fragment2_coord_complexbasis:
            f.write("\t\t"+atom + "\n")
        f.write("\t\t*\n")
        f.write("\tStep_End\n")
        f.write("\tRead D4 = VDW_CORRECTION[4] End\n")
        f.write("\tRead SP4 = SCF_ENERGY[4] End\n\n")


        f.write("\tAssign BSSE_AU = (SP1 - SP2) + (SP3 - SP4) + (D1 - D2) + (D3 - D4) End\n")
        f.write("\tAssign BSSE_KCALMOL = 627.509 * BSSE_AU End\n")

        f.write("End\n")


if __name__ == "__main__":
    import argparse

    epilog = """
~~~~~~~~~~~~~~~~~~~~~~~
D E S C R I P T I O N
~~~~~~~~~~~~~~~~~~~~~~~
This script generates an ORCA compound job that performs the four necessary
single point calculations in order to get the counterpoise correction to the
binding energy. The final correction is defined as a variable in the compound
block, and is easily found at the end of the output file, along with its four
components.

~~~~~~~~~~~~~~~~~~~~~~~
H O W   T O   U S E
~~~~~~~~~~~~~~~~~~~~~~~
Call the script like this:
    python counterpoise.py <f1.xyz> <f2.xyz> --jobname <> --charge_1 <> etc...

or import the function into your script with

    from counterpoise import counterpoise

and call the function and pass your variables to it, e.g.

    counterpoise(fragment1,
                 fragment2,
                 charge_1=0,
                 charge_2=1,
                 mult_1=1,
                 mult_2=2,
                 jobname="something",
                 raw_coordinates=True,
                 keywords="! uks wb97x-v def2-qzvpp d3 grid5 finalgrid6 tightscf")
                 
                 
When using the 'raw_coordinates' option, you need to pass the coordinates in the
format this script expects. If you are reading a standard XYZ file, then the 
following code will obtain the coordinates in the format expected:

    with open("my_coordinates.xyz") as f:
        coords = f.readlines()[2:]
        
It is up to you to decide whether you want to generate the fragment XYZ manually
before using this script, or if you have some way of automatically extracting
the fragment coordinates from the optimized complex geometry. For example,
I have been in the situation where fragment2 always was located at the bottom
of the complex XYZ file. This could be exploited like this:

    natoms_f2 = 6
    with open("complex.xyz") as f:
        coords = f.readlines()[2:]
    
    f1 = coords[:-natoms_f2]
    f2 = coords[-natoms_f2:]
    
~~~~~~~~~~~~~~~~~~~~~~~
E N E R G E T I C S
~~~~~~~~~~~~~~~~~~~~~~~
The counterpoise-corrected energy should be computed as follows:
 Delta_E(CP) = Delta_E + BSSE
 where BSSE is the energy obtained from running this job, and Delta_E
is the non-corrected reaction energy.

~~~~~~~~~~~~~~~~~~~~~~~
I M P O R T A N T ! ! !
~~~~~~~~~~~~~~~~~~~~~~~
The fragment xyz coordiantes should be the coordinates of each fragment at the
optimized complex geometry, and NOT the coordinates of each fragment optimized
individually

~~~~~~~~~~~~~~~~~~~~~~~
A U T H O R
~~~~~~~~~~~~~~~~~~~~~~~
Anders Brakestad
University of Tromso - The Arctic University of Norway
PhD Candidate in Computational Chemistry

~~~~~~~~~~~~~~~~~~~~~~~
L A S T   E D I T
~~~~~~~~~~~~~~~~~~~~~~~
2010-04-27: clarified help text, and added dispersion correction to computed BSSE
2019-10-04: version 1
    """

    parser = argparse.ArgumentParser(description="Generate input file for performing a simple Counterpoise correction",
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fragment1", type=str,
                        help="Path to XYZ file for fragment1")
    parser.add_argument("fragment2", type=str,
                        help="Path to XYZ file for fragment2")
    parser.add_argument("--jobname", type=str, default="counterpoise.inp", metavar="<str>",
                        help="Name of the generated input file")
    parser.add_argument("--charge_1", type=int, default=0, metavar="<int>",
                        help="Charge of fragment 1 (default: 0)")
    parser.add_argument("--charge_2", type=int, default=0, metavar="<int>",
                        help="Charge of fragment 2 (default: 0)")
    parser.add_argument("--mult_1", type=int, default=1, metavar="<int>",
                        help="Multiplicity of fragment 1 (default: 1)")
    parser.add_argument("--mult_2", type=int, default=1, metavar="<int>",
                        help="Multiplicity of fragment 2 (default: 1)")
    parser.add_argument("--nprocs", type=int, default=16, metavar="<int>",
                        help="Number of parallel processes (default: 16)")
    parser.add_argument("--memory", type=int, default=800, metavar="<int>",
                        help="Maxcore memory (default: 800MB)")
    parser.add_argument("--keywords", type=str, default="!keywords", metavar="<str>",
                        help="ORCA keywords for defining computational protocol (default: '!keywords')")

    args = parser.parse_args()

    # Generate the input file
    counterpoise(args.fragment1,
                 args.fragment2,
                 jobname=args.jobname,
                 raw_coordinates=False,
                 charge_1=args.charge_1,
                 charge_2=args.charge_2,
                 mult_1=args.mult_1,
                 mult_2=args.mult_2,
                 nprocs=args.nprocs,
                 memory=args.memory,
                 keywords=args.keywords)
