import Tkinter as tk
import tkFont, tkFileDialog, tkMessageBox
import subprocess as sub
from glob import glob
from datetime import datetime, timedelta
import os
from collections import OrderedDict
from convertme import ConvertMe
from toolbox import ToolBox
from notepad import NotePad
from logbook import LogBook
from MRChem import MrchemOut

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

        self.killjobanswer = False # default option False. Safety from killing jobs by accident

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

        self.jobhisfilter = tk.StringVar()
        self.jobhisfilter.set("") # setting default value to empty string

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

        b_mrc_convergence = tk.Button(self.topleft, text="MRChem conv.", command=self.mrchem_plot_convergence, font=self.buttonfont)
        b_mrc_convergence.grid(row=3, column=3, pady=5, padx=5, sticky="ew")
        
        self.entry_user = tk.Entry(self.topleft, width=10)
        self.entry_user.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        self.entry_user.bind("<Return>", self.get_q)

        self.entry_filter = tk.Entry(self.topleft, width=10)
        self.entry_filter.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        self.entry_filter.insert(0, self.jobhisfilter.get())
        self.entry_filter.bind("<Return>", self.update_textbox)

        l_jobhisfilter = tk.Label(self.topleft, text="Multi-purpose filter:", bg=self.maincolor)
        l_jobhisfilter.grid(row=3, column=0, sticky="ew", pady=5, padx=5)

        

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

        b_killalljobs = tk.Button(self.bot, text="Kill All Jobs", bg="black", fg="red", command=self.kill_all_jobs, font=self.buttonfont)
        b_killalljobs.grid(row=0, column=2, pady=5, padx=5)

        b_convertme = tk.Button(self.bot, text="Convert-Me!", bg="blue", fg="white", command=self.launch_convertme, font=self.buttonfont)
        b_convertme.grid(row=0, column=3, pady=5, padx=5)

        b_toolbox = tk.Button(self.bot, text="The ToolBox", bg="blue", fg="white", command=self.launch_toolbox, font=self.buttonfont)
        b_toolbox.grid(row=0, column=4, pady=5, padx=5)

        b_notepad = tk.Button(self.bot, text="NotePad", bg="blue", fg="white", command=self.launch_notepad, font=self.buttonfont)
        b_notepad.grid(row=0, column=5, pady=5, padx=5)

        b_logbook = tk.Button(self.bot, text="LogBook", bg="blue", fg="white", command=self.launch_logbook, font=self.buttonfont)
        b_logbook.grid(row=0, column=6, pady=5, padx=5)

    def get_q(self, *args):
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])

        # obtain the length of the job with the longest name
        cmd = ["squeue", "-u", self.user.get(), "-o", "%.300j, %20i"]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        q = process.stdout.readlines()
        
        namelengths = []
        pidlengths = []
        for job in q:
            namelengths.append(len(job.split()[0].strip()))
            pidlengths.append(len(job.split()[1].strip()))
        maxname = max(namelengths)
        maxpid = max(pidlengths)

        if self.user.get().strip() == "" or self.user.get() == "all":
            cmd = ["squeue", "-S", "i", "-o", "%.40j %.{}i %.9P %.8T %.8u %.10M %.9l %.6D %R".format(maxpid+1)]
        else:
            cmd = ["squeue", "-u", self.user.get(), "-t", self.status.get() , "-S", "i", "-o", "%.{}j %.{}i %.9P %.8T %.8u %.10M %.9l %.6D %R".format(maxname+1, maxpid+1)]

        process = sub.Popen(cmd, stdout=sub.PIPE)

        q = process.stdout.readlines()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for i, job in enumerate(q):
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
        pid = self.select_text()
        outputfile = self.locate_output_file(pid)
        if "ErrorCode_" in outputfile:
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
        inputfile = self.locate_input_file()
        if "ErrorCode_" in inputfile:
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
        outputfile = self.locate_output_file(self.select_text())
        if "ErrorCode_"in outputfile:
            return outputfile

        self.log_update("Que Pasa? {}".format(outputfile))
        sub.call(["bash", "/home/ambr/bin/gaussian_howsitgoing.sh", "{}".format(outputfile)])

    def molden_output(self):
        outputfile = self.locate_output_file(self.select_text())
        if "ErrorCode_" in outputfile:
            return outputfile

        self.log_update("molden {}".format(outputfile))
        sub.call(["molden", "{}".format(outputfile)])

    def select_text(self):
        try:
            return self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            return "ErrorCode_pol98"

    def get_jobname(self, pid):
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_mel73")
            return "ErrorCode_mel73"

        cmd = ["scontrol", "show", "jobid", pid]

        info = sub.Popen(cmd, stdout=sub.PIPE).stdout.read().splitlines()
        jobname = None
        for line in info:
            if line.strip().startswith("Command"):
                return os.path.basename(line.split("=")[1]).split(".")[0]
    
    def get_jobstatus(self, pid):
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_mel74")
            return "ErrorCode_mel74"

        cmd = ["scontrol", "show", "jobid", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        output = process.stdout.read().splitlines()
       
        status = None
        for line in output:
            for el in line.split():
                if "JobState" in el:
                    status = el.split("=")[1]
        if status == None:
            self.log_update("Job Status not found. ErrorCode_mel34")
            return "ErrorCode_mel34"
        else:
            return status


    def kill_job(self):
        pid = self.select_text()
        cmd = ["scancel", pid]

        result = tkMessageBox.askyesno("Queue-Gui", "Are you sure you want to kill JobID {}?".format(pid))
        
        if result is True:
            self.log_update(" ".join(cmd))
            sub.call(cmd)
            self.get_q()
        else:
            return

    def kill_all_jobs(self):
        self.user.set(self.entry_user.get())
        cmd = ["scancel", "-u", self.user.get()]

        result = tkMessageBox.askyesno("Queue-Gui", "Are you sure you want to kill all jobs for user {}".format(self.user.get()))
        if result:
            result2 = tkMessageBox.askyesno("Queue-Gui", "Are you mad?")

        if result and result2:
            self.log_update(" ".join(cmd))
            sub.call(cmd)
            self.get_q()
        else:
            return


    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to Queue-Gui!")
        return None

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see("end")
        return None

    def open_submitscript(self):
        self.user.set(self.entry_user.get())
        pid = self.select_text()

        jobname = self.get_jobname(pid)
        workdir = self.get_workdir(pid)

        # Locate the submit script file. Common extensions are "job" and "launch"
        slurmscript_extensions = [".job", ".launch"]
        for ext in slurmscript_extensions:
            try:
                f = open(os.path.join(workdir, jobname+ext), "r")
                content = f.read()
                f.close()

                self.txt.configure(state=tk.NORMAL)
                self.txt.delete(1.0, tk.END)
                self.txt.insert(1.0, content)
                self.txt.configure(state=tk.DISABLED)
            except IOError:
                if ext == slurmscript_extensions[-1]:
                    self.log_update("Submit script file not found. ErrorCode_juq91")
                    return "ErrorCode_juq91"
                else:
                    pass

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

    def open_jobhis(self, *args):
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])
        self.jobhisfilter.set(self.entry_filter.get())
        
        self.log_update("Showing job history for {} starting from {}".format(self.user.get(), self.job_starttime.get()))

        # obtain the length of the job with the longest name
        cmd = ["sacct", "-u", self.user.get(), "--format=JobName%300, JobID%40", "--starttime", self.job_starttime.get()]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        jobhis = process.stdout.readlines()
        
        namelengths = []
        pidlengths = []
        for job in jobhis[2:]:
            namelengths.append(len(job.split()[0].strip()))
            if "proxy" not in job.split()[0] and ".batch" not in job.split()[1]:
                pidlengths.append(len(job.split()[1].strip()))
        
        if len(namelengths) == 0:
            self.log_update("Job history is empty. Try selecting an earlier start time in the drop down menu. ErrorCode_hyx916")
            return "ErrorCode_hyx916"
        maxname = max(namelengths)
        maxpid = max(pidlengths)

        if self.user.get().strip() == "":
            self.log_update("No user selected. ErrorCode_hus28")
            return "ErrorCode_hus28"

        if self.status.get() == self.status_options["All Jobs"]:
            cmd = ["sacct", "-u", self.user.get(), "--starttime", self.job_starttime.get(), "--format=Jobname%{},JobID%{},User,state%10,time,nnodes%3,CPUTime,elapsed,Start,End".format(maxname+1, maxpid+1)]
        else:
            cmd = ["sacct", "-u", self.user.get(), "-s", self.status.get(), "--starttime", self.job_starttime.get(), "--format=Jobname%{},JobID%{},User,state%10,time,nnodes%3,CPUTime,elapsed,Start,End".format(maxname+1, maxpid+1)]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        jh = process.stdout.readlines()

        # now get rid of useless lines in the history
        history = [jh[0]] # start with the header present in the list
        for line in jh:
            try:
                int(line.split()[1])
                history.append(line)
            except ValueError:
                if "." in line.split()[1]:
                    continue
                elif "proxy" in line.split()[0]:
                    continue
                elif "batch" in line.split()[0]:
                    continue
                else:
                    history.append(line)
                
      
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)

        # make sure the header will be printed regardless  of filter options
        self.txt.insert(tk.END, history[0])

        for i, line in enumerate(history[2:]):
            # if entry filter is empty 
            if self.jobhisfilter.get().strip() == "":
                self.txt.insert(tk.END, line)
            # if filter is to be applied
            else:
                for f in self.jobhisfilter.get().strip().split():
                    if f in line:
                        self.txt.insert(tk.END, line)

        for i,line in enumerate(self.txt.get(1.0, tk.END).splitlines()):
            try:
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
            except IndexError:
                continue
        
        self.txt.config(state=tk.DISABLED)

        # now make sure the current status shown in the drop down menu corresponds to the same status used for the last job history command
        for stat, opt in self.status_options.items():
            if self.status.get() == opt:
                self.status.set(stat)
                break

    def get_submitdir(self):
        pid = self.select_text()
        cmd = ["scontrol", "show", "jobid", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        s = process.stdout.readlines()
        
        for line in s:
            if "Invalid job id specified" in s:
                self.log_update("Specified JobID not valid. ErrorCode_hyr85")
                return "ErrorCode_hyr85"
            elif "WorkDir=/" in line:
                return line.split("=")[1].strip()
        self.log_update("Work directory not found. ErrorCode_kod47")
        return "ErrorCode_kod47"
                

    def launch_convertme(self):
        pid = self.select_text()
        workdir = self.get_submitdir()

        if "ErrorCode_" in pid:
            workdir = "/home/ambr/projects/5hz2/phb-synth/pbe/model-10/redo-with-Gaussian"
        elif workdir.strip() == "":
            workdir = "/home/ambr/projects/5hz2/phb-synth/pbe/model-10/redo-with-Gaussian"
        elif "ErrorCode_" in workdir:
            workdir = "/home/ambr/projects/5hz2/phb-synth/pbe/model-10/redo-with-Gaussian"
        elif self.user.get() not in workdir:
            self.log_update("Suspicious-looking directory...")
            workdir = "/home/ambr/projects/5hz2/phb-synth/pbe/model-10/redo-with-Gaussian"

        convertme = ConvertMe(self, workdir)

    def launch_toolbox(self):
        pid = self.select_text()
        workdir = self.get_submitdir()

        if "ErrorCode_" in pid:
            workdir = "/home/ambr/projects"
        elif workdir.strip() == "":
            workdir = "/home/ambr/projects"
        elif "ErrorCode_" in workdir:
            workdir = "/home/ambr/projects"
        elif self.user.get() not in workdir:
            self.log_update("Suspicious-looking directory...")
            workdir = "/home/ambr/projects"

        toolbox = ToolBox(self, workdir)

    def launch_notepad(self):
        notepad = NotePad(self)

    def launch_logbook(self):
        logbook = LogBook(self)

    def get_slurmarray_child_pid(self):
        pid_parent = self.select_text()
        cmd = ["scontrol", "show", "jobid", pid_parent]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        s = process.stdout.readlines()
        pid_child = int(s[0].split()[0].split("=")[1])

        filename = None
        for line in s:
            if line.strip().startswith("StdOut=/"):
                filename = os.path.basename(line.split("=")[1].strip()).split(".")[0]
        return pid_child, filename

    def mrchem_plot_convergence(self):
        pid = self.select_text()
        self.jobhisfilter.set(self.entry_filter.get())
        self.user.set(self.entry_user.get())

        if "array" in self.jobhisfilter.get():
            array = True
        else:
            array = False

        if array:
            pid, filename = self.get_slurmarray_child_pid()

            workdir = "/global/work/{}/MRCHEM-{}".format(self.user.get(), pid)
            outputfile = MrchemOut(os.path.join(workdir, filename+".out"))
            outputfile.plot_scf_energy()
            return None
            
            
        else:
            workdir = "/global/work/{}/MRCHEM-{}".format(self.user.get(), pid)
            outputfile = MrchemOut(self.locate_output_file(pid))
            outputfile.plot_scf_energy()
            return None

    def locate_output_file(self, pid):
        """Return the absolute path to the output file for the specified job id, as string."""
        self.user.set(self.entry_user.get())

        scratch_location = "/global/work/{}".format(self.user.get())

        # first determine whether the job is "normal" or "array". we do this by inspecting the 'scontrol show jobid <pid>' stdout
        cmd = ["scontrol", "show", "jobid", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        try:
            scontrolout = process.stdout.readlines()[0].split() # the jobid info is always contained in the first element of the output
        except:
            self.log_update("PID not valid. ErrorCode_bud821")
            return "ErrorCode_bud821"

        scontrolout = [i.split("=") for i in scontrolout] # getting a format similar to a zipped list of tuples

        entryfields = []
        for el in scontrolout:
            entryfields.append(el[0])
        if "Array" in ''.join(entryfields):
            array = True
            self.log_update("Array job detected")
        else:
            array = False
            self.log_update("Non-array job detected")
        #########################################

        # now locate the output file. We get botht the child pid and the child jobname from the scontrol output above
        if array:
            pid_child = scontrolout[0][1]
    
            all_scratch_dirs = os.listdir(scratch_location)
            scratchdir_child = None
            for scratch in all_scratch_dirs:
                if scratch.endswith(pid_child):
                    scratchdir_child = os.path.join(scratch_location, scratch)
                    break
            if scratchdir_child == None:
                self.log_update("Scratch directory for job id {} not found. ErrorCode_hoq999".format(pid_child))
                return "ErrorCode_hoq999"

            outputfile = glob("{}/*.out".format(scratchdir_child))
            if len(outputfile) > 1:
                self.log_update("Warning: Multiple files with extension '.out' found, attempting to use the first one: {}".format(outputfile[0]))
            
            # make sure the file exists by trying to open it
            try:
                f = open(outputfile[0])
                f.close()
            except IOError:
                self.log_update("The file {} does not exist. ErrorCode_mud813".format(outputfile[0]))
                return "ErrorCode_mud813"
            return outputfile[0]

        else:
            all_scratch_dirs = os.listdir(scratch_location)
            scratchdir_job = None
            for scratch in all_scratch_dirs:
                if scratch.endswith(pid):
                    scratchdir_job = os.path.join(scratch_location, scratch)
                    break
            if scratchdir_job == None:
                self.log_update("Scratch directory for job id {} not found. ErrorCode_hoq998".format(pid))
                return "ErrorCode_hoq998"

            outputfile = glob("{}/*.out".format(scratchdir_job))
            if len(outputfile) > 1:
                self.log_update("Warning: Multiple files with extension '.out' found, attempting to use the first one: {}".format(outputfile[0]))
            
            # make sure the file exists by trying to open it
            try:
                f = open(outputfile[0])
                f.close()
            except IOError:
                self.log_update("The file {} does not exist. ErrorCode_mud812".format(outputfile[0]))
                return "ErrorCode_mud812"
            return outputfile[0]

    def get_workdir(self, pid):
        process = sub.Popen(["scontrol", "show", "jobid", pid], stdout=sub.PIPE)
        output = process.stdout.read().splitlines()

        workdir = None
        for line in output:
            if line.strip().startswith("WorkDir"):
                workdir = line.split("=")[1]
        if workdir == None:
                self.log_update("WorkDir not found. ErrorCode_nut62")
                return "ErrorCode_nut62"
        else:
            return workdir


    def locate_input_file(self):
        """"""
        self.user.set(self.entry_user.get())
        pid = self.select_text()

        if self.get_jobstatus(pid) == "PENDING":
            jobname = self.get_jobname(pid)
            workdir = self.get_workdir(pid)

            # Determine the origin of input file
            inp, com = False, False
            try:
                f = open(os.path.join(workdir, jobname+".inp"), "r")
                content = f.read()
                inp = True
                f.close()
            except IOError:
                try:
                    f = open(os.path.join(workdir, jobname+".com"), "r")
                    content = f.read()
                    com = True
                    f.close()
                except IOError:
                    self.log_update("Input file not found. ErrorCode_juq81")
                    return "ErrorCode_juq81"
            if inp:
                return os.path.join(workdir, jobname+".inp")
            elif com:
                return os.path.join(workdir, jobname+".com")

        
        elif self.get_jobstatus(pid) == "RUNNING":
            outputfile = self.locate_output_file(pid)

            scratch_directory = os.path.dirname(outputfile)

            # determine whether the job is of Gaussian type, ORCA type, or MRChem type
            with open(outputfile, "r") as f:
                content = f.read()

            gaussian, orca, mrchem = False, False, False
            if "Entering Gaussian System" in content:
                gaussian = True
            elif "An Ab Initio, DFT and Semiempirical electronic structure package" in content:
                orca = True
            elif "Stig Rune Jensen" in content:
                mrchem = True

            if not gaussian and not orca and not mrchem:
                self.log_update("File type not recognized. ErrorCode_jur213")
                return "ErrorCode_jur213"
            ################################################################

            # Now we know the job type, so we can deduce the naming of the input file
            if mrchem:
                inputfile = os.path.join(scratch_directory, "mrchem.inp")
            elif gaussian:
                inputfile = os.path.join(scratch_directory, os.path.basename(outputfile).replace(".out", ".com"))
                # since some users used the .inp extension, we perform a quick test to make sure we got it right. If not, then we
                # change the extension to .inp
                try:
                    o = open(inputfile, "r")
                    o.close()
                except IOError:
                    inputfile = inputfile.replace(".com", ".inp")
            elif orca:
                inputfile = os.path.join(scratch_directory, os.path.basename(outputfile).replace(".out", ".inp"))
                self.log_update(inputfile)

            return inputfile

    def update_textbox(self, *args):
        # get the filter variables
        self.jobhisfilter.set(self.entry_filter.get())
        if self.jobhisfilter.get().strip() == "":
            self.log_update("The filter is empty")
            return

        # Collect whatever is currently in the textbox, and loop over it to filter
        current = self.txt.get(1.0, tk.END).splitlines()
        new = current[:2]
        for line in current:
            for f in self.jobhisfilter.get().strip().split():
                if f in line:
                    new.append(line)
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)

        for i, line in enumerate(new):
            self.txt.insert(tk.END, line+"\n")
            try:
                if "RUNN" in line.split()[3]:
                    self.txt.tag_add("job_running", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
                elif "PEND" in line.split()[3]:
                    self.txt.tag_add("job_pending", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
                elif "TIME" in line.split()[3]:
                    self.txt.tag_add("job_timeout", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
                elif "COMPL" in line.split()[3]:
                    self.txt.tag_add("job_completed", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
                elif "CANCEL" in line.split()[3]:
                    self.txt.tag_add("job_cancelled", "{}.0".format(i+1), "{}.{}".format(i+1, tk.END))
            except IndexError:
                continue
        self.txt.config(state=tk.DISABLED)
