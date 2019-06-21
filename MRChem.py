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
    def plot_scf_energy(self, title=None):
        """Return a graph plotting the potential energies"""

        # Determine which of the convergence thresholds that were used for the optimizastion:
        # orbital_thrs, property_thrs, or both.
        orb = True if self.orbital_threshold() != -1 else False
        prop = True if self.property_threshold() != -1 else False
        prop_thrs = self.property_threshold()
        orb_thrs = self.orbital_threshold()

        energies = self.scf_energy()
        delta_e = [energies[i] - energies[i - 1] for i in range(1, len(energies))]
        x_delta_e = range(1, len(delta_e) + 1)

        orb_err = self.orbital_total_error()
        x_orb_err = range(1, len(orb_err) + 1)

        property_thresholds = np.asarray([prop_thrs for i in range(len(delta_e))])
        orbital_thrsholds = np.asarray([orb_thrs for i in range(len(orb_err))])

        fig = plt.Figure(figsize=(15, 5), dpi=100)
        plt.title("Job {}: {}".format(title, os.path.basename(self.filename)))
        ax = plt.gca()
        ax.plot(x_delta_e, map(lambda x: abs(x), delta_e), color="red", marker="o", markersize=2, mfc="black", mec="black", label="Energy change")
        ax.plot(x_orb_err, orb_err, color="blue", marker="o", markersize=2, mfc="black", mec="black", label="Orbital energy error")
        ax.set_ylabel("Total Energy [a.u]")
        ax.set_xlabel("SCF iteration")
        ax.set_yscale("log")
        if orb:
            ax.plot(x_orb_err, orbital_thrsholds, color="blue", linestyle="--", linewidth=1, label="orbital_thrs")
        if prop:
            ax.plot(x_delta_e, property_thresholds, color="red", linestyle="--", linewidth=1, label="property_thrs")

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

    def orbital_total_error(self):
        """Return a list of floats containing the total error for the orbitals for each SCF iteration."""
        err = []
        for i, line in enumerate(self.content()):
            if line.strip().startswith("Orbitals"):
                err.append(float(list(self.content())[i + 3 + self.no_orbitals() + 2].split()[2]))
        return err

    #@timeit
    def orbital_threshold(self):
        """Return the orbital convergence threshold as a float"""
        t = filter(lambda x: x.strip().startswith("Orbital threshold"), self.content())[0].split()[2]
        return float(t)

    #@timeit
    def property_threshold(self):
        """Return the property convergence threshold as a float. This is the energy convergence threshold."""
        t = filter(lambda x: x.strip().startswith("Property threshold"), self.content())[0].split()[2]
        return float(t)
        
    def no_orbitals(self):
        """Return an integer value of the number of orbitals used in the calculation"""
        for line in self.content():
            if line.strip().startswith("OrbitalVector"):
                return int(line.split()[1])
        return
