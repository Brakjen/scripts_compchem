#!/usr/bin/env python

import subprocess as sub
import sys

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

# How many rows to print?
if len(sys.argv[1:]) < 1:
    num = len(set(user))
elif len(sys.argv[1:]) > 1:
    sys.exit("Error! Only give one argument")
elif sys.argv[1:] == ["0"]:
    sys.exit("Error! Number must be greater than zero")
else:
    try:
        num = int(sys.argv[1])
        if num > len(set(user)):
            sys.exit("Error! Number must be smaller or equal to {}".format(len(set(user))))
    except ValueError:
        sys.exit("Error! Number must be an integer!")


print("-----------------------------------------------------------------")
print("User \t\t No. of CPUs \t % of total \t Pending CPUs")
print("-----------------------------------------------------------------")

for i in range(num):
    if len(user[i]) > 6:
        print("{} \t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
    elif len(user[i]) < 7:
        print("{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
    elif len(user[i]) > 16:
        print("{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu_running[i], str(oftotal[i])[0:5], cpu_pending[i]))
print("-----------------------------------------------------------------")
print("SUM: \t\t {} \t\t {} \t\t {}".format(sum(cpu_running[:num]), str(sum(oftotal[:num]))[0:5], sum(cpu_pending[:num])))
print("-----------------------------------------------------------------")
