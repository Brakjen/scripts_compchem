#! /usr/bin/env python
import sys
import matplotlib.pyplot as plt
import time

# Define the class MrchemOut, which will be MRChem output files.
class MrchemOut(object):
    def __init__(self, filename):
        self.filename = filename
    
    # Timing decorator function
    def timeit(method):
        """This function will act as a decorator so we can time all functions"""
        def timed(*args, **kwargs):
            before = time.time()
            result = method(*args, **kwargs)
            after = time.time()
    
            print("Elapsed time: {} seconds".format(after - before))
    
            return result
        return timed
    #@timeit
    def content(self):
        """Return a generator that yields the lines of the output file"""
        with open(self.filename, "r") as f:
            while True:
                yield f.next()

    def normaltermination(self):
        """This method evaluates whether the job
        terminated normally, and returns a Boolean:
        True if termination was notmal, False if not."""
        if "Exiting MRChem" in list(self.content())[-7]:
            return True
        return False


    #@timeit
    def dipole_debye(self):
        """This method returns the calculated
        dipole moment in Debye (float)"""
        output = list(self.content())
        dipmom = None

        for i,line in enumerate(self.content()):
            if line.strip().startswith("Length of vector"):
                dipmom = output[i+1]

        return float(dipmom.split()[-1])
    
    #@timeit
    def dipole_au(self):
        """This method returns the calculated
        dipole moment in atomic units (float)"""
        output = list(self.content())
        dipmom = None

        for i,line in enumerate(self.content()):
            if line.strip().startswith("Length of vector"):
                dipmom = float(output[i].split()[-1])

        return dipmom

    #@timeit
    def final_energy_pot(self):
        """This method returns the optimized potential energy (float)"""
        e = None
        for line in self.content():
            if ' '.join(line.split()).startswith("Total energy (au)"):
                e = float(line.split()[-1].strip())
        return e
    
    #@timeit
    def precision(self):
        """This method returns the multiwavelet precision used in the calculation (float)"""
        output = self.content()
        prec = None
        for line in output:
            if line.strip().startswith("Current precision"):
                prec = float(line.strip().split()[2])
                break
        return prec

    #@timeit
    def no_scfcycles(self):
        """This method returns the number of SCF cycles performed before convergence (float)"""
        return len(filter(lambda x: "SCF cycle" in x, self.content()))

    #@timeit
    def scf_energy(self):
        """Return a list of floats containing the SCF energies"""
        e = filter(lambda x: x.strip().startswith("Total energy"), self.content())
        return map(float, map(lambda x: x.strip().split()[-1], e))

    #@timeit
    def plot_scf_energy(self):
        """Return a graph plotting the potential energies"""
        return plt.show(plt.plot(self.scf_energy()))

    #@timeit
    def walltime(self):
        """This function returns the total walltime for the job (float) in seconds"""
        w = None
        for line in self.content():
            if ' '.join(line.strip().split()).startswith("*** Wall time"):
                w_tot = float(line.strip().split()[3])
        return w



