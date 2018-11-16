
# coding: utf-8

# # TO DO LIST
# ### Allow to set "option" as argument to program.py and automatically run the script?
# ### Get Gaussian trajectory with energies (energies missing)

# In[1]:


#! /usr/bin/env python

from utilities import *

option = None
while option != "0":
    print("|=======================================|")
    print("| What do you want to do? \t \t|")
    print("| For help, add 'h' to your option \t|")
    print("| (e.g. '3h') \t\t\t\t|")
    print("|---------------------------------------|")
    print("| 0: Exit \t\t\t\t|")
    print("|---------------------------------------|")
    print("| 1: Get ORCA optimized geometry \t|")
    print("| 2: Get Gaussian optimized geometry \t|")
    print("| 3: Get normal modes from .hess        |")
    print("| 4: Extract residues from .pdb\t\t|")
    print("| 5: .xyz -> .com \t\t\t|")
    print("| 6: .com -> .xyz \t\t\t|")
    print("| 7: Quick check convergence\t\t|")
    print("| 8: Align XYZ to 5HZ2 (.xyz)\t\t|")
    print("| 9: Summarize ORCA job\t\t\t|")
    print("|10: Check ORCA convergence\t\t|")
    print("|11: Fetch PDB file from internet\t|")
    print("|12: Check PDB resolution\t\t|")
    print("|13: Small, random displacements (.xyz) |")
    print("|14: Wiggle those constraints           |")
    print("|15: Generate ORCA templates            |")
    print("|16: Generate scan trajectory           |")
    print("|17: Generate IRC start geom Gaussian   |")
    print("|18: Wiggle those constraints (G)       |")
    print("|=======================================|")
    
    option = raw_input()

#####################################################################################    
    if option == "1":
        print("You have selected option {}.".format(option))
        get_optgeom_orca(raw_input("Please give name of ORCA output file: "))
        sys.exit()
    elif option == "1h":
        help_title_section()
        msg = """
        This script extracts the last optimized geometry from the ORCA output file.
        Beware that this is not necessarily the final optimized geometry!
        """
        sys.exit(msg)
#####################################################################################
    if option == "2":
        print("You have selected option {}.".format(option))
        get_opt_geom_gaussian(raw_input("Please give name of output file: "))
        sys.exit()
    elif option == "2h":
        help_title_section()
        msg = """
        This script extracts the last optimized geometry from the Gaussian output file.
        Beware that this is not necessarily the final optimized geometry!
        """
        sys.exit(msg)
#####################################################################################
    if option == "3":
        print("You have selected option {}.".format(option))
        print("Give name of ORCA .hess file:")
        get_normalmodes_orca(raw_input())
        sys.exit()
    elif option == "3h":
        help_title_section()
        msg = """
        This script generates a molden readable frequency file from an ORCA .hess file,
        which results from a frequency calculation. (The vibrations do not visualize
        very well when the .out file is opened in Molden (only two frames per vibration).)
        
        You need to specify the name/path of the .hess file. Note, the .hess file is
        not necessarily copied back to the submit directory, so make sure you save this
        file.
        """
        sys.exit(msg)
#####################################################################################
    if option == "4":
        print("You have selected option {}.".format(option))
        print("Give PDB entry code:")
        get_residues(raw_input())
        print("Done")
        sys.exit()
    elif option == "4h":
        help_title_section()
        msg = """
        This script downloads the PDB file for the given PDB entry code, and then extracts 
        the cartesian coordinates for the residues you give as input (HETATM also supported, 
        given you know their "sequence ID". You need to give the residues in a space-separated 
        list in the following format:
        
        "<chain><res_number1> <chain><res_number2> <chain><res_number3>"
        
        or, for example
        
        "A319 A480 A509 B38 C125"
        
        The coordinates are written to files with extensions .com and .xyz.
        """
        sys.exit(msg)
##################################################################################### 
    if option == "5":
        print("You have selected option {}.".format(option))
        print("Please give name of XYZ file:")
        convert_xyz_com(raw_input())
        print("Done")
        sys.exit()
    elif option == "5h":
        help_title_section()
        msg = """
        This script converts an XYZ file to a Gaussian input file.
        """
        sys.exit(msg)
#####################################################################################  
    if option == "6":
        print("You have selected option {}.".format(option))
        print("Please give name of Gaussian input file:")
        convert_com_xyz(raw_input())
        print("Done")
        sys.exit()
    elif option == "6h":
        help_title_section()
        msg = """
        This script converts a Gaussian input file to an XYZ file.
        """
        sys.exit(msg)
#####################################################################################
    if option == "7":
        print("You have selected option {}.".format(option))
        print("Please give name of Gaussian output file:")
        quick_convergence_check_orca(raw_input())
        sys.exit()
    elif option == "7h":
        help_title_section()
        msg = """
        This script generates a single plot that visualizes the various convergences
        of an ORCA geometry optimization. Values < 1 means not converged yet, 
        and values > 1 means converged."""
        sys.exit(msg)
#####################################################################################      
    if option == "8":
        print("You have selected option {}.".format(option))
        print("Please give name of XYZ file:")
        translate_xyz(raw_input())
        sys.exit()
    elif option == "8h":
        help_title_section()
        msg = """
        This script takes as input the index (1-indexed, as seen in Molden) of the atom corresponding
        to the Calpha of His508 in 5HZ2. The 5HZ2 coordinates of this atom is stored in the script, 
        and based on the coordinates of the model Calpha the amount of translation is calculated. Then
        all atomic coordinates are translated such that the Calpha of model and enzyme become the same.
        This means the model and enzyme can be overlayed in PyMOL for easy inspection.
        
        The aligned coordinates are written to a new file.
        
        Keep in mind that here only one atom is actually aligned with the enzyme, but since more than one
        atomic coordinate has been kept fixed throughout all calculations, then this procedure should
        perfectly align the model with the enzyme."""
        sys.exit(msg)
#####################################################################################
    if option == "9":
        print("You have selected option {}.".format(option))
        print("Please give name of ORCA output file:")
        orca_output = raw_input()
        if get_normal_termination_orca(orca_output) is False:
            sys.exit("Hmm, ORCA did not terminate normally. Check for error messages in output file.")
        else:
            print("------------------------------")
            print("Orca terminated normally :D")
            print("------------------------------")
            print(get_elapsed_time_orca(orca_output))
            print("------------------------------")
        
        
        if get_calc_type_orca(orca_output) == [1,0,0]:
            print("Job type:\t\t\t\t Geometry optimization")
        elif get_calc_type_orca(orca_output) == [1,1,0]:
            print("Job type:\t\t\t\t Geometry optimization + frequencies")
        elif get_calc_type_orca(orca_output) == [1,0,1]:
            print("Job type:\t\t\t\t Transition state optimization")
        elif get_calc_type_orca(orca_output) == [1,1,1]:
            print("Job type:\t\t\t\t Transition state optimization + frequencies")
        else:
            print("I have no idea what type of calculation this is...")
        
        
        print("# of atoms:\t\t\t\t {}".format(get_number_of_atoms_orca(orca_output)))
        print("# of geometry optimization cycles:\t {}".format(get_number_of_geometry_cycles_orca(orca_output)))
        
        if get_energy_orca(orca_output)[0][0] == 1:
            print("Final single point energy:\t\t {}".format(get_energy_orca(orca_output)[1][0]))
        if get_energy_orca(orca_output)[0][1] == 1:
            print("Empirical dispersion energy:\t\t {}".format(get_energy_orca(orca_output)[1][1]))
        
        
        print("Done")
        sys.exit()
    elif option == "9h":
        help_title_section()
        msg = """
        This script collects some basic information about a job, and determines the job type, determines if
        ORCA terminated normally, prints some energies, etc.
        """
        sys.exit(msg)
#####################################################################################
    if option == "10":
        print("You have selected option {}.".format(option))
        print("Please give name of ORCA output file:")
        orca_output = raw_input()
        
        print("Getting variables from ORCA output...")
        # Get variables to be plotted
        cycles     = get_no_of_scfsteps_orca(orca_output)
        n_of_steps = get_number_of_geometry_cycles_orca(orca_output)
        ec         = get_energy_change_orca(orca_output)[0]
        rmsgrad    = get_energy_change_orca(orca_output)[1]
        maxgrad    = get_energy_change_orca(orca_output)[2]
        rmsstep    = get_energy_change_orca(orca_output)[3]
        maxstep    = get_energy_change_orca(orca_output)[4]
        drmsg      = get_energy_change_orca(orca_output)[5]
        dmaxg      = get_energy_change_orca(orca_output)[6]
        tole       = get_energy_change_orca(orca_output)[7]
        tolmaxg    = get_energy_change_orca(orca_output)[8]
        tolrmsg    = get_energy_change_orca(orca_output)[9]
        tolmaxd    = get_energy_change_orca(orca_output)[10]
        tolrmsd    = get_energy_change_orca(orca_output)[11]
        energies   = get_energy_change_orca(orca_output)[12]
        print("Done!")
        
        # Define the x axis with appropriate length:
        ec_idx             = [i+1 for i in range(len(ec))]
        grad_and_step_idx  = [i+1 for i in range(len(rmsstep))]
        cycle_idx          = [i+1 for i in range(len(cycles))]
        energies_idx       = [i+1 for i in range(len(energies))]
        delta_gradient_idx = [i+1 for i in range(len(drmsg))]
        
        
        # Make constant list of the tolerances with appropriate length:
        tole_list     = [tole for i in range(len(ec_idx))]
        tole_list_neg = [-1 * tole for i in range(len(ec_idx))]
        tolmaxg_list  = [tolmaxg for i in range(len(grad_and_step_idx))]
        tolrmsg_list  = [tolrmsg for i in range(len(grad_and_step_idx))]
        tolmaxd_list  = [tolmaxd for i in range(len(grad_and_step_idx))]
        tolrmsd_list  = [tolrmsd for i in range(len(grad_and_step_idx))]
        
        
        fig = plt.figure(figsize=(40, 30), dpi=50)
        
        plt.subplot(5, 3, 1)
        plt.plot(energies_idx,energies)
        plt.ylabel("Energy")
        plt.title("Energies")
        plt.grid(True)
        
        plt.subplot(5, 3, 2)
        plt.plot(grad_and_step_idx,rmsgrad, grad_and_step_idx, tolrmsg_list, "r--")
        plt.ylabel("RMS grad")
        plt.title("RMS grad")
        plt.grid(True)
        
        plt.subplot(5, 3, 3)
        plt.plot(grad_and_step_idx,maxgrad, grad_and_step_idx, tolmaxg_list, "r--")
        plt.ylabel("MAX grad")
        plt.title("MAX grad")
        plt.grid(True)
        
        plt.subplot(5, 3, 4)
        plt.plot(ec_idx,ec)
        plt.ylabel("Energy change")
        plt.title("Energy change")
        plt.grid(True)
        
        plt.subplot(5, 3, 5)
        plt.plot(delta_gradient_idx, drmsg)
        plt.ylabel("Delta RMSD grad")
        plt.title("Delta RMSD grad")
        plt.grid(True)
        
        plt.subplot(5, 3, 6)
        plt.plot(delta_gradient_idx, dmaxg)
        plt.ylabel("Delta MAX grad")
        plt.title("Delta MAX grad")
        plt.grid(True)
        
        plt.subplot(5, 3, 7)
        plt.plot(ec_idx,ec, ec_idx, tole_list, "r--", ec_idx, tole_list_neg, "r--")
        plt.ylim(-1*tole-2*tole, tole+2*tole)
        plt.ylabel("Energy change")
        plt.title("Energy change ultra zoom")
        plt.grid(True)
        
        
        plt.subplot(5, 3, 8)
        plt.plot(grad_and_step_idx,rmsgrad, grad_and_step_idx, tolrmsg_list, "r--")
        plt.ylim(0, 0.001)
        plt.ylabel("RMSD grad")
        plt.title("RMS grad zoom")
        plt.grid(True)
        
        
        plt.subplot(5, 3, 9)
        plt.plot(grad_and_step_idx,maxgrad, grad_and_step_idx, tolmaxg_list, "r--")
        plt.ylim(0, 0.01)
        plt.ylabel("MAX grad")
        plt.title("MAX grad zoom")
        plt.grid(True)
        
        plt.subplot(5, 3, 10)
        plt.plot(ec_idx,ec, ec_idx, tole_list, "r--", ec_idx, tole_list_neg, "r--")
        plt.ylim(-0.003, 0.003)
        plt.ylabel("Energy change")
        plt.title("Energy change zoom")
        plt.grid(True)
        
        plt.subplot(5, 3, 11)
        plt.plot(delta_gradient_idx, drmsg)
        plt.ylim(-0.0002, 0.0002)
        plt.ylabel("Delta RMSD grad")
        plt.title("Delta RMSD grad zoom")
        plt.grid(True)
        
        plt.subplot(5, 3, 12)
        plt.plot(delta_gradient_idx, dmaxg)
        plt.ylim(-0.002, 0.002)
        plt.ylabel("Delta MAX grad")
        plt.title("Delta MAX grad zoom")
        plt.grid(True)
        
        plt.subplot(5, 3, 13)
        plt.plot(grad_and_step_idx,rmsstep, grad_and_step_idx, tolrmsd_list, "r--")
        plt.ylabel("RMS step")
        plt.title("RMS step")
        plt.grid(True)
        
        plt.subplot(5, 3, 14)
        plt.plot(grad_and_step_idx,maxstep, grad_and_step_idx, tolmaxd_list, "r--")
        plt.ylabel("MAX step")
        plt.title("MAX step")
        plt.grid(True)
        
        plt.subplot(5, 3, 15)
        plt.plot(cycle_idx,cycles)
        plt.title("# SCF cyc b4 conv")
        plt.grid(True)
        
        plt.show()
        sys.exit()
    elif option == "10h":
        help_title_section()
        msg = """
        This script collects convergence information from an ORCA output file - energy, energy change,
        step info, and gradient info - and plots them for inspection.
        """
        sys.exit(msg)
#####################################################################################  
    if option == "11":
        print("You have selected option {}.".format(option))
        print("Please give PDB entry code:")
        fetch_pdb(raw_input())
        print("Done")
        sys.exit()
    elif option == "11h":
        help_title_section()
        msg = """
        This script downloads a PDB file from the PDB and saves it in the current directory.
        """
        exit(msg)
#####################################################################################
    if option == "12":
        print("You have selected option {}.".format(option))
        print("Please give PDB entry code:")
        fetch_pdb_resolution(raw_input())
        print("Done")
        sys.exit()
    elif option == "12h":
        help_title_section()
        msg = """
        This script fetches the crystal structure resolution from the PDB of a given PDB file entry code.
        """
        sys.exit(msg)
#####################################################################################
    if option == "13":
        print("You have selected option {}.".format(option))
        print("Give name of XYZ file:")
        small_random_displacement(raw_input())
        print("Done")
        sys.exit()
    elif option == "13h":
        help_title_section()
        msg = """
        This script generates random displacements (+- 0.05 Angstrom) to all atoms in
        an XYZ file, EXCEPT for those involved in any constraints. The constrained atoms
        are identified by reading the ORCA input file in which the XYZ file is the
        starting geometry.
        """
        sys.exit(msg)
#####################################################################################
    if option == "14":
        print("You have selected option {}.".format(option))
        print("Give name of ORCA input file:")
        wiggle_constraints_orca(raw_input())
        print("Done")
        sys.exit()
    elif option == "14h":
        help_title_section()
        msg = """
        This script generates a molden readable "frequency" file, in which all forces are zero
        except for those atoms involved in constraints. The file serves as a quick way to make
        sure the correct atoms are constrained. Just give the name (or path) to the ORCA input
        file. 
        
        NOTE: The XYZ file linked in the input MUST be in the directory from which you run
        the script.
        """
        sys.exit(msg)
#####################################################################################
    if option == "15":
        subopt = None
        while subopt != "0":
            print("------------------------------------------------------------------")
            print("List of templates you can choose from:")
            print("------------------------------------------------------------------")
            print("\t 0: Exit to main menu")
            print("\t 1: Geometry optimization for different initial Hessian level")
            print("\t 2: Geometry optimization")
            print("\t 3: Frequency calculation")
            print("------------------------------------------------------------------")
            
            print("Please choose which template you want:")
            subopt = raw_input()
            
            if subopt == "1":
                orca_template_scaninitialhessian()
            if subopt == "2":
                orca_template_geometryoptimization()
            if subopt == "3":
                orca_template_frequencies()
            subopt = "0"
        sys.exit()
    
    elif option == "15h":
        help_title_section()
        msg = """This option opens a sub-menu where you can choose to generate different
        ORCA input file templates."""
        sys.exit(msg)
#####################################################################################
    if option == "16":        
        print("Please give the jobname and number of steps (in that order), separated by a space:")
        data = raw_input().split()
        make_scan_traj(data[0], data[1])
        sys.exit("Success")
        
    elif option == "16h":
        help_title_section()
        msg = """This script collects the optimized geometries and final single point
        energies from a TS scan, and writes the information to a molden readable trajectory
        file. 
        
        The script takes two mandatory inputs: the job name and the number of scan steps. 
        For example, if two scan files are 'm1v1_s1_step_i.out' and 'm1v1_s1_step_i_optimized.xyz',
        the the jobname you need to submit is 'm1v1_s1_step_', otherwise the script will not
        be able to open the necessary files."""
        sys.exit(msg)
#####################################################################################
    if option == "17":        
        outputfile = raw_input("Please give name of Gaussian output file: ")
        displace_tsmode_gaussian(outputfile)
        sys.exit("Done")
        
    elif option == "17h":
        help_title_section()
        msg = """This script displaces the optimized TS structure in the direction of
        the TS mode (imaginary frequency), and writes two new files to disk: 
        a forward direction (add TS mode) and a backward direction (substract TS mode). 
        In each case, the TS mode is scaled down by a factor of 0.05, so as to not
        move too far away from the TS structure. 
        
        The script assumes that the correct TS mode is the one with the highest imaginary
        frequency, because this is the first normal mode encountered in the Gaussian output file.
        The script also assumes that the optimized TS structure is the last structure in the Gaussian
        output file."""
        sys.exit(msg)        
#####################################################################################
    if option == "18":        
        inputfile = raw_input("Please give name of Gaussian output file: ")
        xyzfile = raw_input("Please give name of XYZ file: ")
        wiggle_constraints_gaussian(inputfile, xyzfile)
        sys.exit("Done")
        
    elif option == "18h":
        help_title_section()
        msg = """To be done..."""
        sys.exit(msg) 

        

