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

    #@timeit
    def __repr__(self):
        return "<OrcaOut(filename={})>".format(self.filename)

    #@timeit
    def content(self):
        """Return a generator that iterates over lines in the file, one by one."""
        with open(self.filename, "r") as f:
            while True:
                yield f.next()
    
    #@timeit
    def geometry_trajectory(self):
        """Return list of all geometry steps from a geometry optimization. The last step is the optimized geometry"""
        output = list(self.content())
        traj = []
        for i, line in enumerate(output):
            if line.strip().startswith("CARTESIAN COORDINATES (ANGSTROEM)"):
                traj.append(output[i+2:i+self.no_atoms()+2])
        # Strip all white space and newilne characters in traj
        traj = [map(lambda x: ' '.join(x.strip().split()), geom) for geom in traj]
        return traj

    #@timeit
    def source(self):
        """Return the file content as a string."""
        with open(self.filename, "r") as f:
            return f.read()
   
    def inputfile(self):
        """Return the input file as a string"""
        pass

    #@timeit
    def normaltermination(self):
        """Evaluate whether the job
        terminated normally, and return a Boolean:
        True if termination was normal, False if not."""
        if list(self.content())[-1].strip().startswith("TOTAL RUN TIME:"):
            return True
        return False
    
    #@timeit
    def scf_energy(self):
        """Return a list of floats containing the optimized SCF energies"""
        e = filter(lambda x: x.strip().startswith("FINAL SINGLE POINT ENERGY"), self.content())
        return map(float, map(lambda x: x.split()[4], e))

    #@timeit
    def no_scfcycles(self):
        """Return a list of floats containing the number of SCF iterations needed for converging each geom step"""
        c = filter(lambda x: ' '.join(x.split()).startswith("* SCF CONVERGED AFTER"), self.content())
        return map(int, map(lambda x: x.split()[4], c))[0]

    #@timeit
    def walltime(self):
        """Return the total walltime for the job (float) in seconds"""
        w = filter(lambda x: x.strip().startswith("TOTAL RUN TIME:"), self.content())[0].split()
        return float(w[3])*86400 + float(w[5])*3600 + float(w[7])*60 + float(w[9]) + float(w[11])/1000

    #@timeit
    def no_atoms(self):
        """Return the number of atoms of the system (integer)"""
        natoms = None
        for line in self.content():
            if line.strip().startswith("Number of atoms"):
                natoms = line.strip().split()[-1]
                break
        return int(natoms)
             
    #@timeit
    def no_geomcycles(self):
        """Return the number of geometry cycles needed for convergence. Return an integer."""
        return len(self.geometry_trjectory())
    
    #@timeit
    def no_basisfunctions(self):
        """Return the number of basis functions (integer)."""
        nbasis = None
        for line in self.content():
            if line.strip().startswith("Basis Dimension"):
                nbasis = int(line.strip().split()[-1])
                break
        return nbasis

    #@timeit
    def maxforce(self):
        """Return a list of floats containing all Max Forces for each geometry iteration"""
        l = filter(lambda x: x.strip().startswith("MAX gradient"), self.content())
        l = filter(lambda x: len(x.split()) > 4, l)
        return map(float, map(lambda x: x.strip().split()[2], l))

    #@timeit
    def rmsforce(self):
        """Return a list of floats containing all RMS Forces for each geometry iteration"""
        l = filter(lambda x: x.strip().startswith("RMS gradient"), self.content())
        l = filter(lambda x: len(x.split()) > 4, l)
        return map(float, map(lambda x: x.strip().split()[2], l))
    
    #@timeit
    def maxstep(self):
        """Return a list of floats containing all Max Steps for each geometry iteration"""
        l = filter(lambda x: x.strip().startswith("MAX step"), self.content())
        return map(float, map(lambda x: x.strip().split()[2], l))
    
    #@timeit
    def rmsstep(self):
        """Return a list of floats containing all RMS Steps for each geometry iteration"""
        l = filter(lambda x: x.strip().startswith("RMS step"), self.content())
        return map(float, map(lambda x: x.strip().split()[2], l))

    #@timeit
    def tol_maxforce(self):
        """Return the Max Force convergence tolerance as float"""
        tol = None
        for line in self.content():
            if line.strip().startswith("MAX gradient") and len(line.split()) > 4:
                tol = float(line.strip().split()[3])
                break
        return tol

    #@timeit
    def tol_rmsforce(self):
        """Return the RMSD Force convergence tolerance as float"""
        tol = None
        for line in self.content():
            if line.strip().startswith("RMS gradient") and len(line.split()) > 4:
                tol = float(line.strip().split()[3])
                break
        return tol
        pass

    #@timeit
    def tol_maxstep(self):
        """Return the Max Step convergence tolerance as float"""
        tol = None
        for line in self.content():
            if line.strip().startswith("MAX step"):
                tol = float(line.strip().split()[3])
                break
        return tol
        pass

    #@timeit
    def tol_rmsstep(self):
        """Return the RMSD Step convergence tolerance as float"""
        tol = None
        for line in self.content():
            if line.strip().startswith("RMS step"):
                tol = float(line.strip().split()[3])
                break
        return tol
        pass

    #@timeit
    def orcaversion(self):
        v = None
        for line in self.content():
            if line.strip().startswith("Program Version"):
                v = line.strip()
                break
        return v

    def dipole_vector(self):
        """Return a list of floats containing the dipole vector components"""
        for line in self.content():
            if line.strip().startswith("Total Dipole Moment"):
                u = line.split()[4:]
        return u

    def polarizability_diagonal(self):
        content = list(self.content())
        for i, line in enumerate(content):
            if line.strip().startswith("diagonalized tensor:"):
                return map(float, content[i+1].split())


# This class may not be useful for anything.....
class OrcaIn(object):
    def __init__(self, filename):
        self.filename = filename

    def keywords(self):
        pass


