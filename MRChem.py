#! /usr/bin/env python
import sys
import matplotlib.pyplot as plt
import time
import numpy as np
import os

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

    #@timeit
    def source(self, cutoff):
        """Return entire file contents as a string."""
        with open(self.filename, "r") as f:
                return f.read()

    def normaltermination(self):
        """This method evaluates whether the job
        terminated normally, and returns a Boolean:
        True if termination was notmal, False if not."""
        try:
            if "Exiting MRChem" in list(self.content())[-7]:
                return True
        except IndexError:
            return False
        return False


    #@timeit
    def dipole_norm_debye(self):
        """Return the norm of the calculated
        dipole moment vector in Debye (float)"""
        output = list(self.content())
        dipmom = None

        for i,line in enumerate(self.content()):
            if line.strip().startswith("Length of vector"):
                dipmom = output[i+1]

        return float(dipmom.split()[-1])
    
    #@timeit
    def dipole_norm_au(self):
        """Return the norm of the calculated
        dipole moment vector in atomic units (float)"""
        output = list(self.content())
        dipmom = None

        for i,line in enumerate(self.content()):
            if line.strip().startswith("Length of vector"):
                dipmom = float(output[i].split()[-1])

        return dipmom

    def dipole_vector(self):
        """Return a list of the three components of the dipole moment, in au"""
        content = list(self.content())
        vec = None
        for i, line in enumerate(content):
            if line.strip().startswith("Length of vector"):
                # different version of MRChem show different dipole moment data.
                # so first determine the correct way to extract the vector info
                if "--- Total ---" in content[i+3]:
                    vec = content[i+5]
                    # we need to get rid of brackets and commas
                    while "," in vec or "[" in vec or "]" in vec:
                        spec_char = ",[]"
                        for c in spec_char:
                            vec = ''.join(vec.split(c))
                    vec = vec.split()
                    break
                else:
                    vec = content[i+5].split()
                    break

        return map(float, vec)

    def polarizability_tensor(self):
        """Return a list of the polarizability tensor, in a.u."""
        content = list(self.content())
        tensor = None
        for i, line in enumerate(content):
            if "--- Tensor ---" in line:
                tensor = content[i+2:i+5]
                # Now get rid of brackets and commas in the tensor
                for j, el in enumerate(tensor):
                    while "," in tensor[j] or "[" in tensor[j] or "]" in tensor[j]:
                        chars = ",[]"
                        for c in chars:
                            tensor[j] = ''.join(tensor[j].split(c))
                break
        tensor = map(lambda x: x.strip(), tensor)
        tensor = [el.split() for el in tensor]
        tensor = [map(float, el) for el in tensor]
        return tensor

    def polarizability_diagonal(self, unit="au"):
        """Return the diagonal elements of the polarizability tensor as a list of floats"""

        tensor = self.polarizability_tensor()
        diag = []
        for i, line in enumerate(tensor):
            for j, el in enumerate(line):
                if i==j:
                    diag.append(el)
        if unit == "au" or unit == "bohr":
            return diag
        elif unit == "angstrom":
            return map(lambda x: x / 1.8897162**3, diag)

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
            if line.strip().startswith("Precision"):
                return float(line.strip().split()[2])

    #@timeit
    def no_scfcycles(self):
        """This method returns the number of SCF cycles performed before convergence (float)"""
        return len(filter(lambda x: "SCF cycle" in x, self.content()))

    #@timeit
    def scf_energy(self):
        """Return a list of floats containing the SCF energies"""
        # New version
        e = []
        content = list(self.content())
        for i, line in enumerate(content):
            if line.strip().startswith("Iter"):
                for cycle in content[i+2:]:
                    if "---" in cycle or cycle == content[-1]:
                        return e
                    else:
                        e.append((float(cycle.split()[1]), float(cycle.split()[2]), float(cycle.split()[3])))
        # Old version
        #else:
        #    e = filter(lambda x: x.strip().startswith("Total energy"), self.content())
        #    return map(float, map(lambda x: x.strip().split()[-1], e))

    #@timeit
    def plot_scf_energy(self, title=None):
        """Return a graph plotting the potential energies"""

        prop_thrs = self.property_threshold()
        orb_thrs = self.orbital_threshold()

        mo_residual, energies, updates = zip(*self.scf_energy())
        xs = range(len(energies))

        property_thresholds = [prop_thrs for _x in xs]
        orbital_thresholds = [orb_thrs for _x in xs]

        fig = plt.Figure(figsize=(15, 5), dpi=100)
        plt.title("Job {}: {}".format(title, os.path.basename(self.filename)))
        ax = plt.gca()
        ax.plot(xs, map(abs, updates), color="red", marker="o", markersize=2, mfc="black", mec="black", label="Energy Update")
        ax.plot(xs, mo_residual, color="blue", marker="o", markersize=2, mfc="black", mec="black", label="MO Residual")
        ax.plot(xs, orbital_thresholds, color="blue", linestyle="--", linewidth=1, label="Orbital Threshold")
        ax.plot(xs, property_thresholds, color="red", linestyle="--", linewidth=1, label="Energy Threshold")

        ax.set_ylabel("Energy [a.u]")
        ax.set_xlabel("SCF iteration")
        ax.set_yscale("log")

        ax.legend()
        plt.grid(axis="both")
        plt.tight_layout()
        return plt.show()

    #@timeit
    def walltime(self):
        """Return the total walltime for the job (float) in seconds"""
        for line in self.content():
            if ' '.join(line.strip().split()).startswith("*** Wall time"):
                return float(line.strip().split()[3])
        return

    #@timeit
    def orbital_threshold(self):
        """Return the orbital convergence threshold as a float"""
        t = filter(lambda x: x.strip().startswith("Orbital threshold"), self.content())[0].split()[3]
        return float(t)

    #@timeit
    def property_threshold(self):
        """Return the property convergence threshold as a float. This is the energy convergence threshold."""
        t = filter(lambda x: x.strip().startswith("Energy threshold"), self.content())[0].split()[3]
        return float(t)
        
    def no_orbitals(self):
        """Return an integer value of the number of orbitals used in the calculation"""
        for line in self.content():
            if line.strip().startswith("OrbitalVector"):
                return int(line.split()[1])
        return

    def version(self):
        """Return the line of output describing the MRChem version"""
        for line in self.content():
            if line.split()[1] == "VERSION":
                return " ".join(line)
