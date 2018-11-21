#! /usr/bin/env python
import time

# Define the class GaussianOut, which will be Gaussian output files.
class OrcaOut(object):
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

    @timeit
    def __repr__(self):
        return "<OrcaOut(filename={})>".format(self.filename)

    @timeit
    def content(self):
        """Return a generator that iterates over lines in the file, one by one."""
        with open(self.filename, "r") as f:
            while True:
                yield f.next()
    
    @timeit
    def source(self):
        """Return the file content as a string."""
        with open(self.filename, "r") as f:
            return f.read()
    
    @timeit
    def normaltermination(self):
        """Evaluate whether the job
        terminated normally, and return a Boolean:
        True if termination was normal, False if not."""
        if list(self.content())[-1].strip().startswith("TOTAL RUN TIME:"):
            return True
        return False
    
    @timeit
    def scf_energy(self):
        """Return a list of floats containing the optimized SCF energies"""
        e = filter(lambda x: x.strip().startswith("FINAL SINGLE POINT ENERGY"), self.content())
        return map(float, map(lambda x: x.split()[4], e))

    @timeit
    def no_scfcycles(self):
        """Return a list of floats containing the number of SCF iterations needed for converging each geom step"""
        c = filter(lambda x: ' '.join(x.split()).startswith("* SCF CONVERGED AFTER"), self.content())
        return map(int, map(lambda x: x.split()[4], c))

    @timeit
    def walltime(self):
        """Return the total walltime for the job (float) in seconds"""
        pass

    @timeit
    def no_atoms(self):
        """Return the number of atoms of the system (integer)"""
        pass

    @timeit
    def geometry_trajectory(self):
        """Return list of all geometry steps from a geometry optimization. The last step is the optimized geometry"""
        pass
    @timeit
    def no_geomcycles(self):
        """Return the number of geometry cycles needed for convergence. Return an integer."""
        pass
    
    @timeit
    def no_basisfunctions(self):
        """Return the number of basis functions (integer)."""
        pass

    @timeit
    def maxforce(self):
        """Return a list of floats containing all Max Forces for each geometry iteration"""
        pass

    @timeit
    def rmsforce(self):
        """Return a list of floats containing all RMS Forces for each geometry iteration"""
        pass

    @timeit
    def maxstep(self):
        """Return a list of floats containing all Max Steps for each geometry iteration"""
        pass

    @timeit
    def rmsstep(self):
        """Return a list of floats containing all RMS Steps for each geometry iteration"""
        pass
    
    @timeit
    def tol_maxforce(self):
        """Return the Max Force convergence tolerance as float"""
        pass

    @timeit
    def tol_rmsforce(self):
        """Return the RMSD Force convergence tolerance as float"""
        pass

    @timeit
    def tol_maxstep(self):
        """Return the Max Step convergence tolerance as float"""
        pass

    @timeit
    def tol_rmsstep(self):
        """Return the RMSD Step convergence tolerance as float"""
        pass

    @timeit
    def orcaversion(self):
        pass


# This class may not be useful for anything.....
class OrcaIn(object):
    def __init__(self, filename):
        self.filename = filename

    def keywords(self):
        pass


