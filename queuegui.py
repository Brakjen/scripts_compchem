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

        self.status_options = ("All", "Running", "Pending")
        self.status = tk.StringVar()
        self.status.set(self.status_options[0]) # set default value to "All"

        self.user = tk.StringVar()
        self.user.set("ambr") # set default user to "ambr"

        self.place_widgets()

        self.get_q()

    def place_widgets(self):
        # top frame widgets

        b_refresh = tk.Button(self.topframe, text="Refresh", width=10, command=self.get_q, font=self.buttonfont)
        b_refresh.grid(row=0, column=3, sticky="ew", pady=5, padx=5)


        self.status_menu = tk.OptionMenu(self.topframe, self.status, *self.status_options)
        self.status_menu.grid(row=0, column=2, sticky="ew", pady=5, padx=5)

        b_userfilter = tk.Button(self.topframe, text="Filter by user", width=10, font=self.buttonfont)
        b_userfilter.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        b_cpu = tk.Button(self.topframe, text="Check CPU usage", command=self.test, font=self.buttonfont)
        b_cpu.grid(row=1, column=3, sticky="ew", pady=5, padx=5)
        
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
        if self.user.get() == "":
            cmd = ["squeue", "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]
        else:
            cmd = ["squeue", "-u", "{}".format(self.user.get()), "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        q_all = process.stdout.read().splitlines()

        header = q_all[0]
        q_run = filter(lambda x: x.split()[4] == "RUNNING", q_all)
        q_pen = filter(lambda x: x.split()[4] == "PENDING", q_all)

        self.status.set(self.status_menu.get())

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        
        if self.status == "All":
            for line in q_all:
                self.txt.insert(tk.END, line + "\n")
        elif self.status == "Running":
            self.txt.insert(tk.END, header + "\n")
            for line in q_run:
                self.txt.insert(tk.END, line + "\n")
        elif self.status == "Pending":
            self.txt.insert(tk.END, header + "\n")
            for line in q_pen:
                self.txt.insert(tk.END, line + "\n")


        self.txt.config(state=tk.DISABLED)

    def cpu_usage(self):
        self.txt.delete(1.0, tk.END)
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, "CPU usage on stallo\n")
        self.txt.config(state=tk.DISABLED)
        self.txt.config(font=qfont)

    def quepasa(self):
        pass

    def test(self):
        print(self.user.get())


##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    master.geometry("1000x500")
    master.title("QueueGui")
    app = QueueGui(master)
    master.mainloop()
