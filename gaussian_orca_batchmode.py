#! /usr/bin/env python

from gaussian_orca_functions import *

option = sys.argv[1]

if option == "help":
    help_title_section ()
    print("|=======================================|")
    print("| Below are the implemented batch  ")
    print("| functions. To run batch processing, ")
    print("| run\n  ")
    print("| python dobatch.py <val> <files>\n")
    print("| where <val> is the menu number.")
    print("|---------------------------------------|")
    print("| 1: Get ORCA optimized geometry \t|")
    print("| 3: Get normalmodes from .hess \t|")
    print("| 5: Convert .xyz to .com \t\t|")
    print("| 6: Convert .com to .xyz \t\t|")
    print("|=======================================|")
    sys.exit()
    
filename = sys.argv[2]

if option == "1":
    get_optgeom_orca(filename)
    sys.exit()
    
if option == "3":
    get_normalmodes_orca(filename)
    sys.exit()

if option == "5":
    convert_xyz_com(filename)
    sys.exit()

if option == "6":
    convert_com_xyz(filename)
    sys.exit()
