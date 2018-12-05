#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import subprocess as sub
import glob

class QueueGui(object):
    """Docstring"""

    buttonfont = ("Arial", 10)
    qfont = ("Arial", 8)

    def __init__(self, master):
        self.master = master

        self.topframe = tk.Frame()
        self.topframe.pack(side="top", fill="both", expand=False)

        self.midframe = tk.Frame()
        self.midframe.pack(side="top", fill="both", expand=True)
        self.midframe.grid_columnconfigure(0, weight=1)
        self.midframe.grid_rowconfigure(0, weight=1)

        self.botframe = tk.Frame()
        self.botframe.pack(side="top", fill="both", expand=False)

        self.status_options = ("All jobs", "Running jobs", "Pending jobs")
        self.status = tk.StringVar()
        self.status.set(self.status_options[0]) # set default value to "All"

        self.user = tk.StringVar()
        self.user.set("ambr") # set default user to "ambr"

        self.place_widgets()

        self.get_q()

    def place_widgets(self):
        # top frame widgets

        b_refresh = tk.Button(self.topframe, text="Update Queue", width=10, command=self.get_q, font=self.buttonfont)
        b_refresh.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        b_openoutput = tk.Button(self.topframe, text="Open Output", width=10, command=self.open_output, font=self.buttonfont)
        b_openoutput.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        b_openinput = tk.Button(self.topframe, text="Open Input", width=10, command=self.open_input, font=self.buttonfont)
        b_openinput.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

        self.status_menu = tk.OptionMenu(self.topframe, self.status, *self.status_options)
        self.status_menu.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        b_cpu = tk.Button(self.topframe, text="Check CPU Usage", command=self.cpu_usage, font=self.buttonfont)
        b_cpu.grid(row=0, column=2, sticky="ew", pady=5, padx=5)
        
        b_quepasa = tk.Button(self.topframe, text="Que Pasa?", command=self.quepasa, font=self.buttonfont)
        b_quepasa.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        b_moldenout = tk.Button(self.topframe, text="Molden Output", command=self.molden_output, font=self.buttonfont)
        b_moldenout.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        self.entry_user = tk.Entry(self.topframe, width=10)
        self.entry_user.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        self.entry_user.bind("<Return>", self.get_q)
 

        yscroll_log = tk.Scrollbar(self.topframe)
        yscroll_log.grid(row=0, rowspan=2, column=5, pady=2, padx=2, sticky="ns")
        self.log = tk.Text(self.topframe, yscrollcommand=yscroll_log.set, bg="black", height=7, width=90)
        self.log.grid(row=0, rowspan=2, column=4, pady=5, padx=5, sticky="nsew")
        yscroll_log.config(command=self.log.yview)

        # mid frame widgets
        yscrollbar = tk.Scrollbar(self.midframe)
        yscrollbar.grid(row=0, column=1, sticky="ns", pady=2, padx=2)

        self.txt = tk.Text(self.midframe, wrap=tk.NONE, yscrollcommand=yscrollbar.set)
        self.txt.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        self.txt.config(state=tk.DISABLED)

        yscrollbar.config(command=self.txt.yview)

        # bottom frame widgets
        b_exit = tk.Button(self.botframe, text="Quit", bg="black", fg="red", command=self.master.destroy, font=self.buttonfont)
        b_exit.grid(row=0, column=0, pady=5, padx=5)

        b_killjob = tk.Button(self.botframe, text="Kill Selected Job", bg="black", fg="red", command=self.kill_job, font=self.buttonfont)
        b_killjob.grid(row=0, column=1, pady=5, padx=5)

    def get_q(self, *args):
        
        self.user.set(self.entry_user.get())

        if self.user.get().strip() == "":
            cmd = ["squeue", "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]
        else:
            cmd = ["squeue", "-u", "{}".format(self.user.get()), "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]

        process = sub.Popen(cmd, stdout=sub.PIPE)

        q_all = process.stdout.read().splitlines()
        header = q_all[0]
        q_run = filter(lambda x: x.split()[4] == "RUNNING", q_all)
        q_pen = filter(lambda x: x.split()[4] == "PENDING", q_all)

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        
        if self.status.get() == "All jobs":
            for line in q_all:
                self.txt.insert(tk.END, line + "\n")
        elif self.status.get() == "Running jobs":
            self.txt.insert(tk.END, header + "\n")
            for line in q_run:
                self.txt.insert(tk.END, line + "\n")
        elif self.status.get() == "Pending jobs":
            self.txt.insert(tk.END, header + "\n")
            for line in q_pen:
                self.txt.insert(tk.END, line + "\n")


        self.txt.config(state=tk.DISABLED)

    def cpu_usage(self):
        cmd = ["squeue", "-o", "%u %C %t"]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        q = process.stdout.read().splitlines()
        
        # Total number of CPU on Stallo, taken from
        # https://www.sigma2.no/content/stallo
        cpu_stallo_total = float(14116)
        
        # all jobs in queue
        q = map(lambda x: x.split(), q)
        # only running jobs
        r = filter(lambda x: x[-1] == "R", q)
        # only pending jobs
        p = filter(lambda x: x[-1] == "PD", q)
        
        # Initialize list to contain the users from all jobs
        users = []
        for job in q:
            for j,el in enumerate(job):
                if j == 0:
                    users.append(el)
        
        # Initialize a dict in which the sum of all CPUs will be accumulated
        cpu_running = {usr: 0 for usr in set(users)}
        cpu_pending = {usr: 0 for usr in set(users)}
        
        # perform the sum for running cpus
        for job in r:
            for u in cpu_running.keys():
                if u in job:
                    cpu_running[u] += int(job[1])
        # and for pending cpus. Getting users from same list as above, to keep the order consistent
        for job in p:
            for u in cpu_running.keys():
                if u in job:
                    cpu_pending[u] += int(job[1])
        
        
        # zipping and sorting
        zipped = sorted(zip(cpu_running.keys(), [c for user, c in cpu_running.items()], [c for user, c in cpu_pending.items()]), key=lambda x: x[1], reverse=True)
        
        # unzipping
        user, cpu_running, cpu_pending = zip(*zipped)
        # get ratio of running cpus to stallo's total
        oftotal = map(lambda x: str(float(x) / cpu_stallo_total * 100)[0:5], cpu_running)
        
        # adding arrow to username.. First convert from tuple to list
        user = [u for u in user]
        choco = ["ambr", "mobst", "ljilja", "diego", "kathrin"]
        for i,u in enumerate(user):
            if u in choco:
                user[i] += " <<<<<<"
        
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.insert(tk.END, "User Running CPUs % of total Pending CPUs\n")
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        

        maxlen = (max(len(x) for x in user) , max(len(str(x)) for x in cpu_running), max(len(str(x)) for x in oftotal), max(len(str(x)) for x in cpu_pending))
        for i in range(len(user)):
                self.txt.insert(tk.END, "{} {} {} {} {} {} {}\n".format(user[i], 
                                                                 (maxlen[0] - len(user[i])) * " ",
                                                                 cpu_running[i],
                                                                 (maxlen[1] - len(str(cpu_running[i]))) * " ",
                                                                 oftotal[i],
                                                                 (maxlen[2] - len(oftotal[i])) * " ",
                                                                 cpu_pending[i]))
                
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        
        # convert back to floats for the summation
        oftotal = map(float, oftotal)
        self.txt.insert(tk.END, "SUM: {} {} {}\n".format(sum(cpu_running), sum(oftotal), sum(cpu_pending)))
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.config(state=tk.DISABLED)

    def open_output(self):
        if self.txt.tag_ranges(tk.SEL):
            pid = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            return

        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)

        outputfile = glob.glob(workdir+"*.out")
        if len(outputfile) > 1:
            print("More than one output file found in work dir.")
            return
        
        try:
            lines = open(outputfile[0], "r").readlines()
        except (IOError, IndexError):
            print("File not found.")
            return
        
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_input(self):
        if self.txt.tag_ranges(tk.SEL):
            pid = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            return

        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)

        inputfile = glob.glob(workdir+"*.com")
        if len(inputfile) > 1:
            print("More than one input file found in work dir.")
            return
        
        try:
            lines = open(inputfile[0], "r").readlines()
        except (IOError, IndexError):
            print("File not found.")
            return
        
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def quepasa(self):
        if self.txt.tag_ranges(tk.SEL):
            pid = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            return

        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)

        outputfile = glob.glob(workdir+"*.out")
        if len(outputfile) > 1:
            print("More than one output file found in work dir.")
            return

        sub.call(["bash", "/home/ambr/bin/gaussian_howsitgoing.sh", "{}".format(outputfile[0])])

    def molden_output(self):
        if self.txt.tag_ranges(tk.SEL):
            pid = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            return

        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)

        outputfile = glob.glob(workdir+"*.out")
        if len(outputfile) > 1:
            print("More than one output file found in work dir.")
            return

        sub.call(["molden", "{}".format(outputfile[0])])

    def kill_job(self):
        if self.txt.tag_ranges(tk.SEL):
            pid = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            return

        sub.call(["scancel", "{}".format(pid)])




##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    master.geometry("1200x500")
    master.title("QueueGui")
    app = QueueGui(master)
    master.mainloop()
