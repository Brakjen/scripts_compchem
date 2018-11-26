#!/usr/bin/env python

import subprocess as sub
import sys


 

cmd = ["squeue", "-o", "%u %C %t"]
process = sub.Popen(cmd, stdout=sub.PIPE)
q = process.stdout.read().splitlines()

# Total number of CPU on Stallo, taken from
# https://www.sigma2.no/content/stallo
cpu_pendingal = float(14116)

q = map(lambda x: x.split(), q)
r = filter(lambda x: x[-1] == "R", q)
p = filter(lambda x: x[-1] == "PD", q)

for i,job in enumerate(r):
    for j,c in enumerate(job):
       if j == 1:
           r[i][j] = int(r[i][j])
for i,job in enumerate(p):
    for j,c in enumerate(job):
       if j == 1:
           p[i][j] = int(p[i][j])

# Initialize list to contain the users from all running jobs
users = []
for job in r:
    for j,el in enumerate(job):
        if j == 0:
            users.append(el)

# Initialize a idct in which the sum of all CPUs will be accumulated
cpu = {usr: 0 for usr in set(users)}
cpu_pending = {usr: 0 for usr in set(users)}

#perform the sum
for job in r:
    for u in cpu.keys():
        if u in job:
            cpu[u] += job[1]
for job in p:
    for u in cpu.keys():
        if u in job:
            cpu_pending[u] += job[1]


# zipping and sorting
zipped = sorted(zip(cpu.keys(), [c for user, c in cpu.items()], [c for user, c in cpu_pending.items()]), key=lambda x: x[1], reverse=True)

# unzipping 
user, cpu, cpu_pending = zip(*zipped)
# get ratio of running cpus to stallo's total
oftotal = map(lambda x: float(x) / cpu_pendingal * 100, cpu)

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
        print("{} \t {} \t\t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5], cpu_pending[i]))
    elif len(user[i]) < 7:
        print("{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5], cpu_pending[i]))
    elif len(user[i]) > 16:
        print("{} \t\t {} \t\t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5], cpu_pending[i]))
print("-----------------------------------------------------------------")
print("SUM: \t\t {} \t\t {} \t\t {}".format(sum(cpu[:num]), str(sum(oftotal[:num]))[0:5], sum(cpu_pending[:num])))
print("-----------------------------------------------------------------")
