import Tkinter as tk
import tkFont, tkFileDialog
import subprocess as sub
from glob import glob
from datetime import datetime, timedelta
import os
from collections import OrderedDict
from convertme import ConvertMe
from toolbox import ToolBox

class MainWindow(tk.Frame):
    
    def __init__(self, application): # 'application' here is a reference to 'self' in the main QueueGui application.
        tk.Frame.__init__(self, application)
        self.application = application

        self.application.columnconfigure(0, weight=1)
        self.application.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.maincolor = "dark slate gray"
        self["bg"] = self.maincolor

        self.buttonfont = tkFont.Font(family="Arial", size=10)

        # define default options
        self.status_options = OrderedDict()
        self.status_options["All Jobs"] = "all"
        self.status_options["Running Jobs"] = "r"
        self.status_options["Pending Jobs"] = "pd"
        self.status_options["Completed Jobs"] = "cd"
        self.status_options["Cancelled Jobs"] = "ca"
        self.status_options["Timeouted Jobs"] = "to"
        
        self.status = tk.StringVar()
        self.status.set(self.status_options.keys()[0]) # set default value to "All"

        self.user = tk.StringVar()
        self.user.set("ambr") # set default user to "ambr"

        self.job_starttime_options = [datetime.now().date() - timedelta(days=i) for i in range(31)]
        self.job_starttime = tk.StringVar()
        self.job_starttime.set(datetime.now().date()) # default option will be the current date

        # place widgets in grids
        self.place_widgets()
        self.log_update("Welcome to Queue-Gui!")
        # generate queue at start up
        self.get_q()


    def place_widgets(self):

        # generate frames in grid
        self.topleft = tk.Frame(self, bg=self.maincolor)
        self.topright = tk.Frame(self, bg=self.maincolor)
        self.mid = tk.Frame(self, bg=self.maincolor)
        self.bot = tk.Frame(self, bg=self.maincolor)

        self.topleft.grid(row=0, column=0, sticky="w")
        self.topright.grid(row=0, column=1, sticky="nsew")
        self.mid.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.bot.grid(row=2, column=0, columnspan=2, sticky="sw")

        self.topright.columnconfigure(0, weight=1)
        self.mid.columnconfigure(0, weight=1)
        self.mid.rowconfigure(0, weight=1)

        # top frame widgets
        b_refresh = tk.Button(self.topleft, text="Update Queue", command=self.get_q, font=self.buttonfont)
        b_refresh.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        b_openoutput = tk.Button(self.topleft, text="Output file", command=self.open_output, font=self.buttonfont)
        b_openoutput.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        b_openinput = tk.Button(self.topleft, text="Input File", command=self.open_input, font=self.buttonfont)
        b_openinput.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

        b_showsubmitscript = tk.Button(self.topleft, text="Submit Script", command=self.open_submitscript, font=self.buttonfont)
        b_showsubmitscript.grid(row=2, column=0)

        optionmenu_jobhis_starttime = tk.OptionMenu(self.topleft, self.job_starttime, *self.job_starttime_options)
        optionmenu_jobhis_starttime.grid(row=2, column=3, sticky="ew")

        b_showjobinfo = tk.Button(self.topleft, text="Job Info", command=self.open_jobinfo, font=self.buttonfont)
        b_showjobinfo.grid(row=2, column=1)

        b_jobhis = tk.Button(self.topleft, text="Job History", command=self.open_jobhis, font=self.buttonfont)
        b_jobhis.grid(row=2, column=2)

        status_menu = tk.OptionMenu(self.topleft, self.status, *self.status_options.keys())
        status_menu.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        b_cpu = tk.Button(self.topleft, text="Check CPU Usage", command=self.cpu_usage, font=self.buttonfont)
        b_cpu.grid(row=0, column=2, sticky="ew", pady=5, padx=5)
        
        b_quepasa = tk.Button(self.topleft, text="Que Pasa?", command=self.quepasa, font=self.buttonfont)
        b_quepasa.grid(row=1, column=3, sticky="ew", pady=5, padx=5)
        
        b_moldenout = tk.Button(self.topleft, text="Molden Output", command=self.molden_output, font=self.buttonfont)
        b_moldenout.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        self.entry_user = tk.Entry(self.topleft, width=10)
        self.entry_user.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        self.entry_user.bind("<Return>", self.get_q)
 

        yscroll_log = tk.Scrollbar(self.topright, relief=tk.SUNKEN)
        yscroll_log.grid(row=0, rowspan=3, column=1, pady=2, padx=2, sticky="ns")
        self.log = tk.Text(self.topright, yscrollcommand=yscroll_log.set, bg="black", fg="white", height=7, width=90)
        self.log.grid(row=0, rowspan=3, column=0, pady=5, padx=5, sticky="nsew")
        yscroll_log.config(command=self.log.yview)

        # mid frame widgets
        yscrollbar = tk.Scrollbar(self.mid)
        yscrollbar.grid(row=0, column=1, sticky="ns", pady=2, padx=2)

        xscrollbar = tk.Scrollbar(self.mid, orient="horizontal")
        xscrollbar.grid(row=1, column=0, sticky="ew", pady=2, padx=2)
        
        self.txt = tk.Text(self.mid, wrap=tk.NONE, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        self.txt.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        self.txt.config(state=tk.DISABLED)
        
        yscrollbar.config(command=self.txt.yview)
        xscrollbar.config(command=self.txt.xview)
        
        self.txt.tag_configure("even_line", background="#13001a")
        self.txt.tag_configure("odd_line", background="#001a00")
        self.txt.tag_configure("inchoco", foreground="#FF0000")
        self.txt.tag_configure("ambr", foreground="#00FF00")
        self.txt.tag_configure("job_completed", foreground="#59aeff")
        self.txt.tag_configure("job_pending", foreground="#fdbf2c")
        self.txt.tag_configure("job_running", foreground="#34ffcc")
        self.txt.tag_configure("job_timeout", foreground="#FF0000")
        self.txt.tag_configure("job_cancelled", foreground="#e52de5")
        self.txt.tag_raise(tk.SEL)

        # bottom frame widgets
        b_exit = tk.Button(self.bot, text="Quit", bg="black", fg="red", command=self.application.destroy, font=self.buttonfont)
        b_exit.grid(row=0, column=0, pady=5, padx=5)

        b_killjob = tk.Button(self.bot, text="Kill Selected Job", bg="black", fg="red", command=self.kill_job, font=self.buttonfont)
        b_killjob.grid(row=0, column=1, pady=5, padx=5)

        b_convertme = tk.Button(self.bot, text="Launch ConvertMe", bg="blue", fg="white", command=self.launch_convertme, font=self.buttonfont)
        b_convertme.grid(row=0, column=2, pady=5, padx=5)



    def get_q(self, *args):
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])

        # obtain the length of the job with the longest name
        cmd = ["squeue", "-u", self.user.get(), "-o", "%.300j"]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        q = process.stdout.readlines()
        
        namelengths = []
        for job in q:
            namelengths.append(len(job.strip()))
        maxname = max(namelengths)

        if self.user.get().strip() == "" or self.user.get() == "all":
            cmd = ["squeue", "-S", "i", "-o", "%.40j %.7i %.9P %.8T %.8u %.10M %.9l %.6D %R"]
        else:
            cmd = ["squeue", "-u", self.user.get(), "-t", self.status.get() , "-S", "i", "-o", "%.{}j %.7i %.9P %.8T %.8u %.10M %.9l %.6D %R".format(maxname+1)]

        process = sub.Popen(cmd, stdout=sub.PIPE)

        q = process.stdout.readlines()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for i, job in enumerate(q):
            if i % 2 == 0:
                self.txt.insert(tk.END, job)
            else:
                self.txt.insert(tk.END, job)

            if "RUNN" in job.split()[3]:
                self.txt.tag_add("job_running", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "PEND" in job.split()[3]:
                self.txt.tag_add("job_pending", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "TIME" in job.split()[3]:
                self.txt.tag_add("job_timeout", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "COMPL" in job.split()[3]:
                self.txt.tag_add("job_completed", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "CANCEL" in job.split()[3]:
                self.txt.tag_add("job_cancelled", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))

        self.txt.config(state=tk.DISABLED)

        # now make sure the current status shown in the drop down menu corresponds to the same status used for the last job history command
        for stat, opt in self.status_options.items():
            if self.status.get() == opt:
                self.status.set(stat)
                break

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
        
        # defining the computational choco members
        user = [u for u in user]
        choco = ["ambr", "mobst", "ljilja", "diego", "kathrin"]
        
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.insert(tk.END, "User    Run     %     Pending\n")
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        

        maxlen = (max(len(x) for x in user) , max(len(str(x)) for x in cpu_running), max(len(str(x)) for x in oftotal), max(len(str(x)) for x in cpu_pending))
        for i,u in enumerate(user):
            self.txt.insert(tk.END, "{} {} {} {} {} {} {}\n".format(u, 
                                                                   (maxlen[0] - len(user[i])) * " ",
                                                                   cpu_running[i],
                                                                   (maxlen[1] - len(str(cpu_running[i]))) * " ",
                                                                   oftotal[i],
                                                                   (maxlen[2] - len(oftotal[i])) * " ",
                                                                   cpu_pending[i]))
            if u in choco: # make choco members red
                self.txt.tag_add("inchoco", "{}.0".format(i+4), "{}.{}".format(i+4, tk.END))
                if u == "ambr": # make my name green
                    self.txt.tag_add("ambr", "{}.0".format(i+4), "{}.{}".format(i+4, tk.END))
                
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
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        f = open(outputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_input(self):
        inputfile = self.eval_workfile("input")
        if "ErrorCode_" in inputfile:
            self.log_update(inputfile)
            return inputfile

        f = open(inputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def quepasa(self):
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        self.log_update("Que Pasa? {}".format(outputfile))
        sub.call(["bash", "/home/ambr/bin/gaussian_howsitgoing.sh", "{}".format(outputfile)])

    def molden_output(self):
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        self.log_update("molden {}".format(outputfile))
        sub.call(["molden", "{}".format(outputfile)])

    def select_text(self):
        if self.txt.tag_ranges(tk.SEL):
            return self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            self.log_update("No PID selected. ErrorCode_las02")
            return "ErrorCode_las02"

    def eval_workfile(self, filetype):
        pid = self.select_text()
        try: # check that the selected text is a valid pid
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_xal49")
            return "ErrorCode_xal49"

        # define the workdir. using user variable to access other users files
        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)
        # getting jobname from the scontrol command
        jobname = self.get_jobname(pid)

        # determine which extension to use
        if filetype == "output":
            ext = [".out"]
        elif filetype == "input":
            ext = [".com", ".inp"]
        else:
            self.log_update("Filetype '{}' not supported. ErrorCode_tot91".format(filetype))
            return "ErrorCode_tot91"

        usefile = None
        for x in ext:
            f = workdir + jobname + x
            if os.path.isfile(f):
                usefile = f
                break # a useable file was found, so we break out of the loop. no need to evaluate other extensions

        # make sure some file actually was found by checking that the initial value of 'usefile' did not change from None
        if usefile == None:
            self.log_update("No file found. ErrorCode_tyr86")
            return "ErrorCode_tyr86"

        # now we attempt to open the found file
        try:
            s = open(usefile, "r")
            s.close()
            self.log_update("Using this file: {}".format(usefile))
            return usefile # return the fill path to the file, to be used by subsequent methods
        except IOError:
            self.log_update("File not found: {}. ErrorCode_poz32".format(usefile))
            return "ErrorCode_poz32"


    def get_jobname(self, pid):
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_mel73")
            return "ErrorCode_mel73"

        cmd = ["scontrol", "show", "jobid", pid]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        return process.stdout.read().splitlines()[0].split()[1].split("=")[1]

    def kill_job(self):
        pid = self.select_text()
        cmd = ["scancel", pid]
        self.log_update(" ".join(cmd))
        sub.call(cmd)
        self.get_q()

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

    def open_submitscript(self):
        pid = self.select_text()
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_toj60")
            return ErrorCode_toj60

        cmd = ["scontrol", "show", "jobid", "-dd", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        subscript = process.stdout.read().split("BatchScript=\n")[1]
       
        self.log_update(" ".join(cmd))
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in subscript:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_jobinfo(self):
        pid = self.select_text()
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_toj66")
            return ErrorCode_toj66

        cmd = ["scontrol", "show", "jobid", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        jobinfo = process.stdout.read().split()

        self.log_update(" ".join(cmd))
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in jobinfo:
            self.txt.insert(tk.END, line + "\n")
        self.txt.config(state=tk.DISABLED)

    def open_jobhis(self):
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])

        # obtain the length of the job with the longest name
        cmd = ["squeue", "-u", self.user.get(), "-o", "%.300j"]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        q = process.stdout.readlines()
        
        namelengths = []
        for job in q:
            namelengths.append(len(job.strip()))
        maxname = max(namelengths)

        if self.user.get().strip() == "":
            self.log_update("No user selected. ErrorCode_hus28")
            return "ErrorCode_hus28"

        if self.status.get() == self.status_options["All Jobs"]:
            cmd = ["sacct", "-u", self.user.get(), "--starttime", self.job_starttime.get(), "--format=Jobname%{},JobID%7,User,state%10,time,nnodes%3,CPUTime,elapsed,Start,End".format(maxname+1)]
        else:
            cmd = ["sacct", "-u", self.user.get(), "-s", self.status.get(), "--starttime", self.job_starttime.get(), "--format=Jobname%{},JobID%7,User,state%10,time,nnodes%3,CPUTime,elapsed,Start,End".format(maxname+1)]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        jh = process.stdout.readlines()

        # now get rid of useless lines in the history
        history = [jh[0]] # start with the header present in the list
        for line in jh:
            try:
                int(line.split()[1])
            except ValueError:
                continue
            history.append(line)
       
        self.log_update("Showing job history for {} starting from {}".format(self.user.get(), self.job_starttime.get()))
      
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)

        for i, line in enumerate(history):
            if i % 2 == 0:
                self.txt.insert(tk.END, line)
            else:
                self.txt.insert(tk.END, line)

            if "RUNN" in line.split()[3]:
                self.txt.tag_add("job_running", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "PENDI" in line.split()[3]:
                self.txt.tag_add("job_pending", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "TIMEO" in line.split()[3]:
                self.txt.tag_add("job_timeout", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "COMPLE" in line.split()[3]:
                self.txt.tag_add("job_completed", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            elif "CANCEL" in line.split()[3]:
                self.txt.tag_add("job_cancelled", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
        
        self.txt.config(state=tk.DISABLED)

        # now make sure the current status shown in the drop down menu corresponds to the same status used for the last job history command
        for stat, opt in self.status_options.items():
            if self.status.get() == opt:
                self.status.set(stat)
                break

    def launch_convertme(self):
        convertme = ConvertMe()




