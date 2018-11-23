#!/usr/bin/env python

import subprocess as sub

cmd = ["squeue", "-o", "%u %C %m %t"]
process = sub.Popen(cmd, stdout=sub.PIPE)
q = process.stdout.read().splitlines()

# Total number of CPU on Stallo, taken from
# https://www.sigma2.no/content/stallo
cpu_total = float(14116)

q = map(lambda x: x.split(), q)
r = filter(lambda x: x[-1] == "R", q)

for i,job in enumerate(r):
    for j,c in enumerate(job):
       if j == 1:
           r[i][j] = int(r[i][j])
       if j == 2:
           r[i][j] = int(r[i][j][0:-1])

# Initialize list to contain the users from all running jobs
users = []
for job in r:
    for j,el in enumerate(job):
        if j == 0:
            users.append(el)

# Initialize a idct in which the sum of all CPUs will be accumulated
cpu = {usr: 0 for usr in set(users)}

# perform the sum
for job in r:
    for u in cpu.keys():
        if u in job:
            cpu[u] += job[1]

# zipping and sorting
zipped = sorted(zip(cpu.keys(),    [c for user, c in cpu.items()]), key=lambda x: x[1], reverse=True)

# unzipping 
user, cpu = zip(*zipped)
oftotal = map(lambda x: float(x) / cpu_total * 100, cpu)

# adding arrow to username.. First convert from tuple to list
user = [u for u in user]
for i,u in enumerate([u for u in user]):
    if u == "ambr":
        user[i] += " <--------"

print("--------------------------------------------------------")
print("User \t\t No. of CPUs \t % of total")
print("--------------------------------------------------------")
for i in range(len(user)):
    if len(user[i]) > 6:
        print("{} \t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5]))
    elif len(user[i]) < 7:
        print("{} \t\t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5]))
    elif len(user[i]) > 12:
        print("{} \t\t {} \t\t {}".format(user[i], cpu[i], str(oftotal[i])[0:5]))
print("--------------------------------------------------------")
        




