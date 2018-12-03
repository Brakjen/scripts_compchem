#! /usr/bin/env python

from Tkinter import *

class convertme(object):
    def __init__(self, root):
        root.title("ConvertMe")
        self.frame = Frame(root)
        self.frame.pack()
        
        self.title = Label(self.frame, text="Ready to be converted?", font=("Helvetica", 16))
        self.title.grid(row=0, column=0)

        self.button_xyzcom =  Button(self.frame, text=".xyz ->.com", width=20)
        self.button_comxyz =  Button(self.frame, text=".com ->.xyz", width=20)
        self.button_angbohr = Button(self.frame, text="Angstrom -> Bohr", width=20)
        self.button_bohrang = Button(self.frame, text="Bohr -> Angstrom", width=20)
        self.button_filecheck = Button(self.frame, text="Does file exist?", width=20)

        self.button_xyzcom.grid(row=1, column=0)
        self.button_comxyz.grid(row=2, column=0)
        self.button_angbohr.grid(row=3, column=0)
        self.button_bohrang.grid(row=4, column=0)
        self.button_filecheck.grid(row=5, column=0)

        self.button_xyzcom.bind("<Button-1>", self.xyz_to_com)
        self.button_comxyz.bind("<Button-1>", self.com_to_xyz)
        self.button_angbohr.bind("<Button-1>", self.ang_to_bohr)
        self.button_bohrang.bind("<Button-1>", self.bohr_to_ang)
        self.button_filecheck.bind("<Button-1>", self.filecheck)

        self.entry_filename = Entry(self.frame, width=50)
        self.entry_filename.grid(row=6, column=0)

    def filecheck(self, f):
        f = self.entry_filename.get()
        try:
            t = open(f, "r")
            t.close()
            status = Label(root, text="File Exists :)")
            status.pack()
            root.after(1000, status.destroy)
            return True
        except IOError:
            status = Label(root, text="File Not Found :(")
            status.pack()
            root.after(1000, status.destroy)
            return None

    def xyz_to_com(self, xyzfile):
        """Convert an XYZ file format to a Gaussian input format (.com). The input file
           contains only the bare minimum to be opened with GaussView, essentially only the coordinates.
           The new filename is the same as the given XYZ file, but with '.com' extension, so beware
           that you don't overwrite any files."""
        xyzfile = self.entry_filename.get()
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
        print("File converted!")
        return None

    def com_to_xyz(self, comfile):
        """Extract the coordinates from a Gaussian input file, and save them as an XYZ file.
           The new filename is the same as the given XYZ file, but with '.com' extension, so beware
           that you don't overwrite any files."""
        comfile = self.entry_filename.get()
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
        print("File converted!")
        return None



    def ang_to_bohr(self, xyzfile):
        """Convert the XYZ coordinates in an XYZ file from Angstrom to Bohr.
           Only works with XYZ files."""
        xyzfile = self.entry_filename.get()
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
        print("File converted!")
        return None



    def bohr_to_ang(self, xyzfile):
        """Convert the XYZ coordinates in an XYZ file from Bohr to Angstrom.
           Only works with XYZ files."""
        xyzfile = self.entry_filename.get()
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
        print("File converted!")
        return None


root = Tk()
root.geometry("500x230")
app = convertme(root)
root.mainloop()
