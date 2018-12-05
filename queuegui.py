#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import subprocess as sub

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
        b_refresh.grid(row=1, column=1, sticky="ew", pady=5, padx=5)


        self.status_menu = tk.OptionMenu(self.topframe, self.status, *self.status_options)
        self.status_menu.grid(row=0, column=2, sticky="ew", pady=5, padx=5)

        b_cpu = tk.Button(self.topframe, text="Check CPU usage", command=self.cpu_usage, font=self.buttonfont)
        b_cpu.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        b_statusfilter = tk.Button(self.topframe, text="Filter by status", font=self.buttonfont)
        b_statusfilter.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

        self.entry_user = tk.Entry(self.topframe, width=10)
        self.entry_user.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        
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


    def get_q(self):
        
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
        oftotal = map(lambda x: float(x) / cpu_stallo_total * 100, cpu_running)
        
        # adding arrow to username.. First convert from tuple to list
        user = [u for u in user]
        choco = ["ambr", "mobst", "ljilja", "diego", "kathrin"]
        for i,u in enumerate(user):
            if u in choco:
                user[i] += " <<<<<<"
        
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, "-----------------------------------------------------------------")
        self.txt.insert(tk.END, "User \t\t Running CPUs \t % of total \t Pending CPUs")
        self.txt.insert(tk.END, "-----------------------------------------------------------------")
        
        for i in range(len(user)):
            if len(user[i]) > 6:
                self.txt.insert(tk.END, "{} \t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
            elif len(user[i]) < 7:
                self.txt.insert(tk.END, "{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
            elif len(user[i]) > 16:
                self.txt.insert(tk.END, "{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
        self.txt.insert(tk.END, "-----------------------------------------------------------------")
        self.txt.insert(tk.END, "SUM: \t\t {} \t\t {} \t\t {}".format(sum(cpu_running[:num]), str(sum(oftotal[:num]))[0:5], sum(cpu_pending[:num])))
        self.txt.insert(tk.END, "-----------------------------------------------------------------")
        self.txt.config(state=tk.DISABLED)

    def quepasa(self):
        pass



##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    master.geometry("1000x500")
    master.title("QueueGui")
    app = QueueGui(master)
    master.mainloop()
