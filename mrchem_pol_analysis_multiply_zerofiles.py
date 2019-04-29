import os
import shutil
from glob import glob
import sys

root = "/Users/abr121/iCloudDrive/Education/PhD/prosjekt/mrchem/benchmark/field0001/dataanalysis"

outputdir = os.path.join(root,"datafiles_highprec")

outputfiles = glob("{}/*.out".format(outputdir))

for f in outputfiles:
    if "_000." in f:
        shutil.copyfile(f, f.replace(".out", "_x.out"))
        shutil.copyfile(f, f.replace(".out", "_y.out"))
        shutil.copyfile(f, f.replace(".out", "_z.out"))
        shutil.copyfile(f.replace(".out", ".inp"), f.replace(".out", "_x.inp"))
        shutil.copyfile(f.replace(".out", ".inp"), f.replace(".out", "_y.inp"))
        shutil.copyfile(f.replace(".out", ".inp"), f.replace(".out", "_z.inp"))

