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
                vec = content[i+5].split()
                break

        return map(float, vec)


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
        
        # define the energies, energy_change x values, and orbital convergence threshold
        e = self.scf_energy()
        x_e = range(1, len(e)+1)
        x_delta_e = x_e[0:-1]
        t = [self.orbital_threshold() for i in range(len(e) - 1)]
        t_plus  = self.orbital_threshold() + 10*self.orbital_threshold()
        t_minus = -1*self.orbital_threshold() - 10*self.orbital_threshold()

        delta_e = []
        for i, energy in enumerate(e):
            if i == 0:
                continue
            delta_e.append(e[i] - e[i-1])

        fig = plt.figure(figsize=(12,5), dpi=50)
        plt.subplots_adjust(wspace=0.27)

        plt.subplot(1, 2, 1)
        plt.plot(x_e, e, "black", linewidth=2)
        plt.ylabel("Total Energy [a.u]")
        plt.xlabel("SCF iteration")

        plt.subplot(1, 2, 2)
        plt.plot(x_delta_e, delta_e, "black", x_delta_e, map(lambda x: -1*x, t), "r--", x_delta_e, t, "r--", linewidth=2.0)
        plt.ylabel("Energy Change [a.u]")
        plt.xlabel("SCF iteration")
        plt.ylim(t_minus, t_plus)

        return plt.show()

    #@timeit
    def walltime(self):
        """This function returns the total walltime for the job (float) in seconds"""
        w = None
        for line in self.content():
            if ' '.join(line.strip().split()).startswith("*** Wall time"):
                w_tot = float(line.strip().split()[3])
        return w


    #@timeit
    def orbital_threshold(self):
        """Return the orbital convergence threshold as a float"""
        t = filter(lambda x: x.strip().startswith("Orbital threshold"), self.content())[0].split()[2]
        return float(t)

    #@timeit
    def property_threshold(self):
        """Return the property convergence threshold as a float"""
        t = filter(lambda x: x.strip().startswith("Property threshold"), self.content())[0].split()[2]
        return float(t)
        
