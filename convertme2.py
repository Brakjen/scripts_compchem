#! /bin/usr/env python

import Tkinter as tk
from datetime import datetime
import os
import sys

class ConvertMe(object):
    """Docstring"""

    buttonfont = ("Arial", 10)

    def __init__(self, master):
        self.master = master

        # frame which will contain buttons and entry field
        self.topframe = tk.Frame()
        self.topframe.pack(side="top", fill="both", expand=True)

        self.topframe.grid_rowconfigure(0, weight=1)
        self.topframe.grid_rowconfigure(1, weight=1)
        self.topframe.grid_columnconfigure(0, weight=1)

        self.bottomframe = tk.Frame()
        self.bottomframe.pack(side="top", fill="both", expand=False)

        # create the buttons and place them in the mainframe
        b_xyzcom = tk.Button(self.bottomframe, text=".xyz -> .com", font=self.buttonfont, width=10, command=self.xyz_to_com)
        b_xyzcom.grid(row=0, column = 0, pady=5, padx=5)

        b_comxyz = tk.Button(self.bottomframe, text=".com -> .xyz", font=self.buttonfont, width=10, command=self.com_to_xyz)
        b_comxyz.grid(row=0, column = 1, pady=5, padx=5)

        b_angbohr = tk.Button(self.bottomframe, text=".ang -> .bohr", font=self.buttonfont, width=10, command=self.ang_to_bohr)
        b_angbohr.grid(row=0, column = 2, pady=5, padx=5)

        b_bohrang = tk.Button(self.bottomframe, text=".bohr -> .ang", font=self.buttonfont, width=10, command=self.bohr_to_ang)
        b_bohrang.grid(row=0, column = 3, pady=5, padx=5)

        b_browse = tk.Button(self.topframe, text="Browse File", font=self.buttonfont, width=10, command=self.file_browse)
        b_browse.grid(row=0, column = 1, sticky="e", pady=5, padx=5)

        b_quit = tk.Button(self.bottomframe, text="Quit", font=self.buttonfont, width=10, bg="black", fg="red", command=master.destroy)
        b_quit.grid(row=1, column=0, pady=5, padx=5)

        b_clearlog = tk.Button(self.bottomframe, text="Clear Log", font=self.buttonfont, width=10, command=self.clear_log)
        b_clearlog.grid(row=1, column=1, pady=5, padx=5)

        # create the entry filed and place it in the mainframe
        self.entry_file = tk.Entry(self.topframe)
        self.entry_file.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        # crate a vertical scrollbar and log window
        yscrollbar = tk.Scrollbar(self.topframe)
        yscrollbar.grid(row=1, column=4, pady=2, padx=2, sticky="ns")
        
        self.log = tk.Text(self.topframe, height=10, yscrollcommand=yscrollbar.set, wrap=tk.NONE)
        self.log.grid(row=1, columnspan=2, pady=5, padx=5, sticky="ew")
        self.log_update("Welcome to ConvertMe!")
        self.log_update("You are in {}".format(os.getcwd()))

        yscrollbar.config(command=self.log.yview)

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see("end")

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

        with open(xyzfile,"r") as infile:
           inlines = infile.readlines()[2:]

        # get rid of special characters such as tabs and newlines
        coords = map(lambda x: ' '.join(x.strip().split()), inlines)

        with open(job+"_test.com","w") as o:
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
        with open(comfile, "r") as infile:
            coords = infile.read().split("\n\n")[2].split("\n")[1:]

        # get rid of special characters such as tabs and newlines
        coords = map(lambda x: ' '.join(x.strip().split()), coords)

        with open(job+"_test.xyz", "w") as o:
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


    def file_browse(self):
        self.log_update("Browsing for file...")

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to ConvertMe!")
        self.log_update("You are in {}".format(os.getcwd()))
        return None


##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    master.title("ConvertMe")
    #master.geometry("700x350")
    app = ConvertMe(master)
    master.mainloop()
        
