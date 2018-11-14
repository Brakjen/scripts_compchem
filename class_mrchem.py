#! /usr/bin/env python
import sys


# Define the class MrchemOut, which will be MRChem output files.
class MrchemOut(object):
    def __init__(self, filename):
        """self.content returns a list of strings where each string
        is a line in the original file."""
        self.filename = filename
        with open(self.filename, "r") as f:
            self.content = f.readlines()

    def normaltermination(self):
        """This method evaluates whether the job
        terminated normally, and returns a Boolean:
        True if termination was notmal, False if not."""
        if "Exiting MRChem" in self.content[-7]:
            return True
        return False


    def dipole_debye(self):
        """This method returns the calculated
        dipole moment in Debye (float)"""
        output = self.content
        dipmom = None

        for i,line in enumerate(output):
            if line.strip().startswith("Length of vector"):
                dipmom = output[i+1]

        return float(dipmom.split()[-1])
    
    def dipole_au(self):
        """This method returns the calculated
        dipole moment in atomic units (float)"""
        output = self.content
        dipmom = None

        for i,line in enumerate(output):
            if line.strip().startswith("Length of vector"):
                dipmom = output[i]

        return float(dipmom.split()[-1])

    def energy_pot(self):
        """This method returns the optimized potential energy (float)"""
        output = self.content
        e = None
        for line in output:
            if ' '.join(line.split()).startswith("Total energy (au)"):
                e = float(line.split()[-1].strip())
        return e

    def precision(self):
        """This method returns the multiwavelet precision used in the calculation (float)"""
        output = self.content
        prec = None
        for line in output:
            if line.strip().startswith("Current precision"):
                prec = float(line.strip().split()[2])
                break
        return prec

    def no_scfcycles(self):
        """This method returns the number of SCF cycles performed before convergence (float)"""
        pass

    def walltime(self):
        """This function returns the total walltime for the job (float) in seconds"""
        output = self.content
        w = None
        for line in output:
            if ' '.join(line.strip().split()).startswith("*** Wall time"):
                w_tot = float(line.strip().split()[3])
        return w



