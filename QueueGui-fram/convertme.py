import Tkinter as tk
import tkFileDialog
import os
from datetime import datetime

class ConvertMe(tk.Toplevel):
    def __init__(self, parent, workdir): # here 'parent' is a reference to the class MainWindow, from which ConvertMe is called
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Convert-Me")
        self.workdir = workdir

        self["bg"] = self.parent.maincolor

        self.place_widgets()
            
        # move into the directory provided
        os.chdir(self.workdir)
        
        self.log_update("Welcome to Convert-Me!")
        self.log_update("You are in {}".format(os.getcwd()))

    def place_widgets(self):
        
        self.top = tk.Frame(self, bg=self.parent.maincolor)
        self.bot = tk.Frame(self, bg=self.parent.maincolor)
        
        self.top.grid(row=0, column=0, sticky="nsew")
        self.bot.grid(row=1, column=0, sticky="nsew")

        self.top.grid_columnconfigure(0, weight=1)

        # top frame widgets
        b_xyzcom = tk.Button(self.bot, text=".xyz -> .com", font=self.parent.buttonfont, width=10, command=self.xyz_to_com)
        b_xyzcom.grid(row=0, column = 0, pady=5, padx=5)

        b_comxyz = tk.Button(self.bot, text=".com -> .xyz", font=self.parent.buttonfont, width=10, command=self.com_to_xyz)
        b_comxyz.grid(row=0, column = 1, pady=5, padx=5)

        b_angbohr = tk.Button(self.bot, text=".ang -> .bohr", font=self.parent.buttonfont, width=10, command=self.ang_to_bohr)
        b_angbohr.grid(row=0, column = 2, pady=5, padx=5)

        b_bohrang = tk.Button(self.bot, text=".bohr -> .ang", font=self.parent.buttonfont, width=10, command=self.bohr_to_ang)
        b_bohrang.grid(row=0, column = 3, pady=5, padx=5)

        b_browse = tk.Button(self.top, text="Browse File", font=self.parent.buttonfont, width=10, command=self.browse_file)
        b_browse.grid(row=0, column = 1, sticky="e", pady=5, padx=5)

        b_quit = tk.Button(self.bot, text="Quit", font=self.parent.buttonfont, width=10, bg="black", fg="red", command=self.destroy)
        b_quit.grid(row=1, column=0, pady=5, padx=5)

        b_clearlog = tk.Button(self.bot, text="Clear Log", font=self.parent.buttonfont, width=10, command=self.clear_log)
        b_clearlog.grid(row=1, column=1, pady=5, padx=5)

        # create the entry filed and place it in the mainframe
        self.entry_file = tk.Entry(self.top)
        self.entry_file.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        # crate a vertical scrollbar and log window
        yscrollbar = tk.Scrollbar(self.top)
        yscrollbar.grid(row=1, column=4, pady=2, padx=2, sticky="ns")
        
        self.log = tk.Text(self.top, height=10, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        self.log.grid(row=1, columnspan=2, pady=5, padx=5, sticky="ew")

        yscrollbar.config(command=self.log.yview)
        
    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see(tk.END)

    def xyz_to_com(self):
        """Convert an XYZ file format to a Gaussian input format (.com). The input file
           contains only the bare minimum to be opened with GaussView, essentially only the coordinates.
           The new filename is the same as the given XYZ file, but with '.com' extension, so beware
           that you don't overwrite any files."""
        
        xyzfile = self.entry_file.get()
        if not self.filecheck():
            self.log_update("Error: File Not Found!")
            return

        job = xyzfile.split(".")[0]
        ext = xyzfile.split(".")[-1]
        if ext != "xyz":
            self.log_update("Error: You must specify an XYZ file!")
            return


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
        self.log_update("New file written: {}".format(job+"_test.com"))
        return None

    def com_to_xyz(self):
        """Extract the coordinates from a Gaussian input file, and save them as an XYZ file.
           The new filename is the same as the given XYZ file, but with '.com' extension, so beware
           that you don't overwrite any files."""
        comfile = self.entry_file.get()
        if not self.filecheck():
            self.log_update("Error: File Not Found!")
            return

        job = comfile.split(".")[0]
        ext = comfile.split(".")[-1]
        if ext != "com":
            self.log_update("Error: You must specify a COM file!")
            return
        
        with open(comfile, "r") as infile:
            coords = infile.read().split("\n\n")[2].split("\n")[1:]

        # get rid of special characters such as tabs and newlines
        coords = map(lambda x: ' '.join(x.strip().split()), coords)

        with open(job+".xyz", "w") as o:
            o.write("{}\n".format(len(coords)))
            o.write("\n")
            for atom in coords:
                o.write(atom+"\n")
        self.log_update("New file written: {}".format(job+"_test.xyz"))
        return None

    def ang_to_bohr(self):
        """Convert the XYZ coordinates in an XYZ file from Angstrom to Bohr.
           Only works with XYZ files."""
        xyzfile = self.entry_file.get()
        if not self.filecheck():
            self.log_update("Error: File Not Found!")
            return

        job = xyzfile.split(".")[0]
        ext = xyzfile.split(".")[-1]
        if ext != "xyz":
            self.log_update("Error: You must specify an XYZ file!")
            return

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
                o.write("{} {}\n".format(atom, ' '.join(coords[i])))
        self.log_update("New coordinates written to: {}".format(job+"_bohr.xyz"))
        return None

    def bohr_to_ang(self):
        """Convert the XYZ coordinates in an XYZ file from Bohr to Angstrom.
           Only works with XYZ files."""
        xyzfile = self.entry_file.get()
        if not self.filecheck():
            self.log_update("Error: File Not Found!")
            return

        job = xyzfile.split(".")[0]
        ext = xyzfile.split(".")[-1]
        if ext != "xyz":
            self.log_update("Error: You must specify an XYZ file!")
            return

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
                o.write("{} {}\n".format(atom, ' '.join(coords[i])))
        self.log_update("New coordinates written to: {}".format(job+"_ang.xyz"))
        return None

    def filecheck(self):
        try:
            t = open(self.entry_file.get(), "r")
            t.close()
            return True
        except IOError:
            return False

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to Convert-Me!")
        self.log_update("You are in {}".format(os.getcwd()))

    def browse_file(self):
        ftypes = [("All files", "*"),
                  ("XYZ files", "*.xyz"),
                  ("Gaussian input files", "*.com")]

        self.entry_file.delete(0, tk.END)
        self.entry_file.insert(0, tkFileDialog.askopenfilenames(initialdir=self.workdir, parent=self, title ="Select File", filetypes=ftypes))
