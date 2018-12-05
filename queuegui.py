#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import subprocess as sub
import glob
from datetime import datetime

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

        self.log_update("Welcome to QueueGui!")






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
        b_quepasa.grid(row=1, column=3, sticky="ew", pady=5, padx=5)
        
        b_moldenout = tk.Button(self.topframe, text="Molden Output", command=self.molden_output, font=self.buttonfont)
        b_moldenout.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        self.entry_user = tk.Entry(self.topframe, width=10)
        self.entry_user.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        self.entry_user.bind("<Return>", self.get_q)
 

        yscroll_log = tk.Scrollbar(self.topframe)
        yscroll_log.grid(row=0, rowspan=2, column=5, pady=2, padx=2, sticky="ns")
        self.log = tk.Text(self.topframe, yscrollcommand=yscroll_log.set, bg="black", fg="white", height=7, width=90)
        self.log.grid(row=0, rowspan=2, column=4, pady=5, padx=5, sticky="nsew")
        yscroll_log.config(command=self.log.yview)

        # mid frame widgets
        yscrollbar = tk.Scrollbar(self.midframe)
        yscrollbar.grid(row=0, column=1, sticky="ns", pady=2, padx=2)

        self.txt = tk.Text(self.midframe, wrap=tk.NONE, yscrollcommand=yscrollbar.set, bg="black", fg="white")
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
        self.txt.insert(tk.END, "User    Run     %     Pending\n")
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
        self.txt.insert(tk.END, "SUM: {} {} {} {} {} {}\n".format((maxlen[0] - 4) * " ",
                                                                  sum(cpu_running),
                                                                  (maxlen[1] - len(str(sum(cpu_running)))) * " ",
                                                                  sum(oftotal),
                                                                  (maxlen[2] - len(str(sum(oftotal)))) * " ",
                                                                  sum(cpu_pending)))
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.config(state=tk.DISABLED)

    def open_output(self):
        outputfile = self.eval_workfile("out")
        f = open(outputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_input(self):
        inputfile = self.eval_workfile("com")
        f = open(inputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def quepasa(self):
        outputfile = self.eval_workfile("out")
        if outputfile == "error":
            return "error"
        self.log_update("Que Pasa? {}".format(outputfile))
        sub.call(["bash", "/home/ambr/bin/gaussian_howsitgoing.sh", "{}".format(outputfile)])

    def molden_output(self):
        outputfile = self.eval_workfile("out")
        if outputfile == "error":
            return "error"
        self.log_update("molden {}".format(outputfile))
        sub.call(["molden", "{}".format(outputfile)])

    def select_text(self):
        if self.txt.tag_ranges(tk.SEL):
            return self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            self.log_update("No PID selected. Please select a job PID with the cursor.")
            return "error"

    def eval_workfile(self,ext):
        pid = self.select_text()
        workdir = "/global/work/{}/{}".format(self.user.get(), pid)
        f = glob.glob("{}/*.{}".format(workdir, ext))

        if len(f) > 1: # might be several files with relevant extension in workdir
            self.log_update("More than one {} file found in work dir. I don't know which one to use.".format(ext))
            return "error"

        try:
            int(pid)
        except ValueError:
            self.log_update("Selected PID not valid. PID must be integer.")
            return "error"

        try:
            s = open(f[0], "r")
            s.close()
            return f[0]
        except (IOError, IndexError):
            self.log_update("File not found!")
            return "error"

    def kill_job(self):
        pid = self.select_text()
        sub.call(["scancel", "{}".format(pid)])

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to QueueGui!")
        return None

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see("end")
        return None


##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    master.geometry("1200x500")
    master.title("QueueGui")
    app = QueueGui(master)
    master.mainloop()
