import Tkinter as tk
import tkFileDialog
import tkSimpleDialog
import os
from datetime import datetime
import Gaussian as G
import Orca as O

class ToolBox(tk.Toplevel):
    def __init__(self, parent, workdir):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("ToolBox")
        self.workdir = workdir

        self["bg"] = self.parent.maincolor

        self.grid_columnconfigure(0, weight=1)

        self.place_widgets()
        os.chdir(self.workdir)

        self.log_update("Welcome to The ToolBox!")
        self.log_update("You are in {}".format(os.getcwd()))

        # defining some variables
        self.thefile = tk.StringVar()
        self.thefile.set(self.entry.get())
        
    def place_widgets(self):
        self.top = tk.Frame(self, bg=self.parent.maincolor)
        self.mid = tk.Frame(self, bg=self.parent.maincolor)
        self.bot = tk.Frame(self, bg=self.parent.maincolor)

        self.top.grid(row=0, column=0, sticky="nsew")
        self.mid.grid(row=1, column=0, sticky="nsew")
        self.bot.grid(row=2, column=0, sticky="nsew")
        self.mid.grid_columnconfigure(0, weight=1)
        self.bot.grid_columnconfigure(0, weight=1)

        b_exit = tk.Button(self.top, text="Quit", bg="black", fg="red", command=self.destroy)
        b_exit.grid(row=0, column=0, pady=5, padx=5)

        b_clearlog = tk.Button(self.top, text="Clear log", command=self.clear_log)
        b_clearlog.grid(row=0, column=1, pady=5, padx=5)

        yscrollbar = tk.Scrollbar(self.mid)
        yscrollbar.grid(row=0, column=1, padx=2, pady=2, sticky="ns")
        self.log = tk.Text(self.mid, height=10, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        self.log.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        yscrollbar.configure(command=self.log.yview)

        self.entry = tk.Entry(self.bot)
        self.entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        b_browse = tk.Button(self.bot, text="Browse", command=self.browse_files)
        b_browse.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        b_getgeom = tk.Button(self.bot, text="Get Optimized Geometry", command=self.get_optimized_geometry)
        b_getgeom.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        b_alignxyz = tk.Button(self.bot, text="Align XYZ file with 5HZ2", command=self.align_xyz_to_5hz2)
        b_alignxyz.grid(row=2, column=0, pady=5, padx=5, sticky="ew")

        b_orcamodes = tk.Button(self.bot, text="Get ORCA normal modes", command=self.get_normalmodes_orca)
        b_orcamodes.grid(row=3, column=0, pady=5, padx=5, sticky="ew")

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see(tk.END)

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to The ToolBox!")

    def browse_files(self):
        ftypes = [("All files", "*"),
                  ("XYZ files", "*.xyz"),
                  ("Gaussian input files", "*.com"),
                  ("Gaussian/ORCA output files", "*.out"),
                  ("ORCA input files", "*.inp")]

        self.entry.delete(0, tk.END)
        self.entry.insert(0, tkFileDialog.askopenfilenames(initialdir=self.workdir, parent=self, title ="Select File", filetypes=ftypes))

    def get_optimized_geometry(self):
        self.thefile.set(self.entry.get())
        gaussian, orca = False, False
        files = self.thefile.get().split()
        if len(files) > 1:
            self.log_update("Entering batch mode")


        # determine if file is from Gaussian or from ORCA
        for outputfile in files:
            self.log_update("{}".format(outputfile))
            try:
                output = G.GaussianOut(outputfile)
                if "Gaussian" in output.content().next():
                    gaussian = True
                    self.log_update("Gaussian file detected")
            except IOError:
                self.log_update("File not found. ErrorCode_teq18")
                return
            try:
                output = O.OrcaOut(outputfile)
                if "Program Version" in list(output.content())[20]:
                    orca = True
                    self.log_update("ORCA file detected.")
    
                elif "An Ab Initio, DFT and Semiempirical electronic structure package" in list(output.content())[5]:
                    orca = True
                    self.log_update("ORCA file detected")
                elif "TOTAL RUN TIME" in list(output.content())[-1]:
                    orca = True
                    self.log_update("ORCA file detected")
            except IOError:
                self.log_update("File not found. ErrorCode_cax18")
                return
    
            # Returning if neither Gaussian or ORCA file was detected,
            if gaussian == False and orca == False:
                self.log_update("Neither Gaussian or ORCA output file type was detected. ErrorCode_xud25")
                return
    
            ### GETTING GAUSSIAN OPT GEOM ###
            if gaussian:
                output = G.GaussianOut(outputfile)
                self.log_update("Getting Gaussian optimized geometry.")
                optgeom = output.geometry_trajectory()[-1]
    
                with open(output.filename.split(",")[-1] + "_optimized.xyz", "w") as f:
                    f.write("{}\n".format(output.no_atoms()))
                    f.write("Generated by the ToolBox\n")
                    for atom in optgeom:
                        f.write(' '.join(atom) + "\n")
                self.log_update("File written to {}".format(output.filename.split(",")[-1] + "_optimized.xyz"))


            ### GETTING OFCA OPT GEOM ###
            elif orca:
                output = O.OrcaOut(outputfile)
                self.log_update("Getting ORCA optimized geometry.")
                optgeom = output.geometry_trajectory()[-1]
                with open(output.filename.replace(".out", "_optimized.xyz"), "w") as f:
                    f.write(str(output.no_atoms()) + "\n")
                    f.write("Generated by the ToolBox\n")
                    for atom in optgeom:
                        f.write(atom + "\n")
                self.log_update("File written to {}".format(output.filename.replace(".out", "_optimized.xyz")))


    def align_xyz_to_5hz2(self):
        """
        This method aligns the given XYZ file to the published crystal structure given in
        PDB code '5HZ2'. The method uses the X,Y,Z coordinates of the C_alpha in His508,
        and translates all atoms in the provided XYZ file such that this C_alpha atom 
        fully overlaps with that in 5HZ2. This way the XYZ file can be visualized in PyMOL
        overlapped with the full protein, which is useful when analyzing whether the 
        calcuation has induced bad structural orientations on the model residues.

        This method expects as input the (1-indexed) atom number in the XYZ file.
        """
        self.thefile.set(self.entry.get())
        files = self.thefile.get().split()
        if len(files) > 1:
            self.log_update("Entering batch mode")

        for xyzfile in files:
        
            # make sure an XYZ file is given based on the extension
            if xyzfile.split(".")[-1] != "xyz":
                self.log_update("Using {}".format(xyzfile))
                self.log_update("You must select an XYZ file. ErrorCode_his262")
                continue
            jobname = xyzfile.split(".")[0]
            
            # Now open the xyzfile
            with open(xyzfile, "r") as infile:
                inlines = infile.readlines()
            
                
            # Remove the top two lines (number of atoms and comment line)
            coord = inlines[2:]
            no_atoms = len(coord)
            # Now split each line into strings of its elements
            coord = [line.split() for line in coord]
            
            # Define the XYZ coordinates of His508 Calpha from PDB ID 5HZ2 (used as reference)
            xref = float(41.023)
            yref = float(14.601)
            zref = float(56.605)
            

            # Now ask for the C_alpha index by opening a pop-up window with an entry field.
            atomid = tkSimpleDialog.askinteger("Input Required!", "Using {} \n Please give the atom index of the C_alpha atom in your XYZ file:".format(xyzfile))

            # Get the XYZ coordinates of the atom in the XYZ file to be translated
            x = float(coord[atomid][1])
            y = float(coord[atomid][2])
            z = float(coord[atomid][3])
            
            # Now compute the XYZ translations
            xtr = x - xref
            ytr = y - yref
            ztr = z - zref
            
            # Now translate each coordinate by the given value
            for atom in range(no_atoms):
                coord[atom][1] = str(float(coord[atom][1]) - xtr)
                coord[atom][2] = str(float(coord[atom][2]) - ytr)
                coord[atom][3] = str(float(coord[atom][3]) - ztr)

            # Now write translated coordiates to new file
            with open(jobname + "_aligned" + ".xyz", "w") as outfile:
                outfile.write("{}\n".format(no_atoms))
                outfile.write("Generated by The ToolBox\n")
                for el in coord:
                    outfile.write(" ".join(el) + "\n")
                
            self.log_update("Aligned coordinates written to {}".format(jobname + "_aligned" + ".xyz"))
            self.log_update("")

    def get_normalmodes_orca(self):
        """
        Extracts the normal modes from an ORCA Hessian file (.hess), and writes them
        to a new file with name <jobname_normalmodes.molden>. It works only for 
        analytical frequency jobs, since otherwise the normalmodes are scattered
        acrodd multiple Hessian files.
        """

        self.thefile.set(self.entry.get())
        files = self.thefile.get().split()
        if len(files) > 1:
            self.log_update("Entering batch mode")

        for hess in files:
            # get the jobname (without extension). Assumes only one "." is used in the
            # filename
            jobname = hess.split(".")[0]
            with open(hess, "r") as infile:
                inlines = infile.readlines()
        
            # Initialize some variables
            no_of_freq = None
            freqs      = []
            modes      = []
            geom       = []
            # Extract the number of frequencies and all frequencies
            for i,line in enumerate(inlines):
                
                # Now get the number of frequencies
                if line.startswith("$vibrational_frequencies"):
                    no_of_freq = int(inlines[i+1])
                    for j in range(no_of_freq):
                        freqs.append(float(inlines[i+j+2].split()[1]))
        
                # Now get all normal modes
                if line.startswith("$normal_modes"):
                    # index where the normal mode data starts
                    start = i+3
                    # the number of columns containing normal modes
                    cols = len(inlines[start].split()) - 1
                    # the number of times the columns are repeated
                    rows = int(float(no_of_freq)/float(cols)) + 1
                    # the number of columns in the last "line" of normal mode data
                    rest = no_of_freq - (cols * (rows - 1))
        
                    # minus 1 to not include the "rest" row
                    for r in range(rows-1):
                        # define each line where the data starts
                        # i: start of normal mode section, 3: to get to where the data
                        # starts, r*(nfreq+1): move down in r multiples of nfreq (must add
                        # one due to the extra label line inbetween each normal mode)
                        start = i + 3 + r*(no_of_freq+1)
                        for c in range(cols):
                            for f in range(no_of_freq):
                                modes.append(float(inlines[start+f].split()[c+1]))
        
                    # Now pick up the "rest" normal mode
                    # move down to the last "line" of normal mode data
                    start = i + 3 + (rows-1)*(no_of_freq+1)
                    for r in range(rest):
                        for f in range(no_of_freq):
                            modes.append(float(inlines[start + f].split()[r+1]))
                
                    # Now split the normal mode data into their x, y, and z components, as
                    # this will make it easier to write to file
                    mode_x = modes[::3]
                    mode_y = modes[1::3]
                    mode_z = modes[2::3]
        
        
                # Now get the geometry
                if line.startswith("$atoms"):
                    no_atoms = int(inlines[i+1])
                    start = i+2
                    for atom in range(no_atoms):
                        for k in range(5):
                            # we do not want the "mass" column in the table, so we exclude
                            # index 1 from the loop
                            if k != 1:
                                geom.append(inlines[start+atom].split()[k])
            # Now format geom into something which is easier to write (list of lists)
            coord = [[] for i in range(no_atoms)]
            for i in range(no_atoms):
                coord[i] = geom[i*4:i*4+4]
        
            # Define the output name as jobname_normalmodes.molden
            output=jobname + "_normalmodes.molden"
            # Now we write all of our data to file
            with open(output, "w") as o:
                o.write("[MOLDEN FORMAT]\n")
                o.write("[N_FREQ]\n")
                o.write("{}\n".format(no_of_freq))
                o.write("[FREQ]\n")
            
                for f in freqs:
                    o.write(str(f) + "\n")
        
                o.write("[NATOM]\n")
                o.write(str(no_atoms) + "\n")
                o.write("[FR-COORD]\n")
            
                for c in coord:
                    o.write("\t".join(c) + "\n")
        
                o.write("[FR-NORM-COORD]\n")
        
                for m in range(len(modes)):
                    if float(m) % no_of_freq == 0:
                        o.write("vibration {}\n".format(str(m/no_of_freq + 1)))
        
                    if float(m) % 3 == 0:
                        o.write("".join(str(mode_x[m/3]) + " " + str(mode_y[m/3]) + " " + str(mode_z[m/3])) + "\n")
                o.close()
            self.log_update("Normal modes written to {}_normalmodes.molden".format(jobname))
            
