import Tkinter as tk
import tkFileDialog
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

        self.log_update("Welcome to the ToolBox!")
        self.log_update("You are in {}".format(os.getcwd()))

        # defining some variables
        self.thefile = tk.StringVar()
        self.thefile.set(self.entry.get())
        
    def place_widgets(self):
        self.top = tk.Frame(self, bg=self.parent.maincolor)
        self.bot = tk.Frame(self, bg=self.parent.maincolor)

        self.top.grid(row=0, column=0, sticky="nsew")
        self.bot.grid(row=1, column=0, sticky="nsew")
        self.top.grid_columnconfigure(0, weight=1)
        self.bot.grid_columnconfigure(0, weight=1)

        yscrollbar = tk.Scrollbar(self.top)
        yscrollbar.grid(row=0, column=1, padx=2, pady=2, sticky="ns")
        self.log = tk.Text(self.top, height=10, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        self.log.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        yscrollbar.configure(command=self.log.yview)

        self.entry = tk.Entry(self.bot)
        self.entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        b_browse = tk.Button(self.bot, text="Browse", command=self.browse_files)
        b_browse.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        b_getgeom = tk.Button(self.bot, text="Get Optimized Geometry", command=self.get_optimized_geometry)
        b_getgeom.grid(row=1, column=0, pady=5, padx=5, sticky="w")

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see(tk.END)

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

        # determine if file is from Gaussian or from ORCA
        try:
            output = G.GaussianOut(self.thefile.get())
            if "Gaussian" in output.content().next():
                gaussian = True
                self.log_update("Gaussian file detected")
                self.parent.log_update(list(output.content()))
        except IOError:
            self.log_update("File not found. ErrorCode_teq18")
            return
        try:
            output = O.OrcaOut(self.thefile.get())
            if "Program Version" in list(output.content())[20]:
                orca = True

            elif "An Ab Initio, DFT and Semiempirical electronic structure package" in list(output.content())[5]:
                orca = True
                self.log_update("ORCA file detected")
            elif "TOTAL RUN TIME" in list(output.content())[-1]:
                orca = True
                self.log_update("ORCA file detected")
        except IOError:
            self.log_update("File not found. ErrorCode_cax18")
            return

        if gaussian == False and orca == False:
            self.log_update("Neither Gaussian or ORCA file type was detected. ErrorCode_xud25")
            return

        if gaussian:
            self.log_update("Getting Gaussian optimized geometry.")
        if orca:
            self.log_update("Getting ORCA optimized geometry.")


        





