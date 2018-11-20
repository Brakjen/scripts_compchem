#! /usr/bin/env python
import time

# Define the class GaussianOut, which will be Gaussian output files.
class GaussianOut(object):
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
        return "<GaussianOut(filename={})>".format(self.filename)

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
        if list(self.content())[-1].strip().startswith("Normal termination"):
            return True
        return False
    
    @timeit
    def scf_energy(self):
        """Return a list of floats containing the optimized SCF energies"""
        energies = filter(lambda x: x.strip().startswith("SCF Done:"), self.content())
        return map(lambda x: float(x.split()[4]), energies)

    @timeit
    def no_scfcycles(self):
        """Return a list of floats containing the number of SCF iterations needed for converging each geom step"""
        cycles = filter(lambda x: x.strip().startswith("SCF Done:"), self.content())
        return map(int, map(lambda x: x.strip().split()[7], cycles))

    @timeit
    def walltime(self):
        """Return the total walltime for the job (float) in seconds"""
        w = filter(lambda x: x.strip().startswith("Elapsed time:"), self.content())[0].strip().split()
        return float(w[2])*24*60*60 + float(w[4])*60*60 + float(w[6])*60 + float(w[8])

    @timeit
    def no_atoms(self):
        """Return the number of atoms of the system (integer)"""
        for line in self.content():
            if line.strip().startswith("NAtoms="):
                return int(line.strip().split()[1])

    @timeit
    def geometry_trajectory(self):
        """Return list of all geometry steps from a geometry optimization. The last step is the optimized geometry"""
        natoms = self.no_atoms()

        # list of elements used to replace atomic number with atomic symbol. Dummy to shift up by 1
        elements = ['Dummy','H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P', 'S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga', 'Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag', 'Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu', 'Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au', 'Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am', 'Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg', 'Cn','Nh','Fl','Mc','Lv','Ts','Og']


        # Now extract the number of atoms and all the geometries in the output file
        # taken from each "Input orientation" statement in the output file. We use 
        # the number of atoms to decide how many lines to append to the variable containing
        # all the geometries.
        traj = []

        # Convert the generator to a list to be used in the inner loop. We can still use the generator for the outer loop
        content = list(self.content())
        for i,line in enumerate(self.content()):
            if line.strip().startswith("Input orientation"):
                for j in range(natoms):
                    traj.append(content[i+j+5].strip())

        # for convenience we define a variable that contains the number of geometries in the trajectory
        ngeoms = len(traj)/natoms
        
        # Now we make the long list into a list of list, where each sublist contains one geometry
        traj = [traj[natoms*i:natoms*(i+1)] for i in range(ngeoms)]
        # Now we make each "line" into its own sublist
        traj = [[traj[i][j].split() for j in range(len(traj[i]))] for i in range(len(traj))]
        
        # Now we need to delete the unnecessary numbers in each sublist ()
        for geom in traj:
            for atom in geom:
                del(atom[0])
                del(atom[1]) # remember that due to the first deletion the index shifts by one
                
                # Now we replace the atomic number with the corresponding atomic symbol
                atom[0]  = elements[int(atom[0])]
        
        # We discard the last geometry because it will be a duplicate
        return traj[:-1]
    
    @timeit
    def no_geomcycles(self):
        """Return the number of geometry cycles needed for convergence. Return an integer."""
        return len(list(self.geometry_trajectory()))
    
    @timeit
    def no_basisfunctions(self):
        """Return the number of basis functions (integer)."""
        nbasis = None
        for line in self.content():
            if line.strip().startswith("NBasis="):
                nbasis = int(line.strip().split()[1])
                break
        return nbasis

    @timeit
    def maxforce(self):
        """Return a list of floats containing all Max Forces for each geometry iteration"""
        l = filter(lambda x: ' '.join(x.split()).startswith("Maximum Force"), self.content())
        l = map(lambda x: x.split()[2], l)
        return map(float, l)

    @timeit
    def rmsforce(self):
        """Return a list of floats containing all RMS Forces for each geometry iteration"""
        l = filter(lambda x: ' '.join(x.split()).startswith("RMS Force"), self.content())
        l = map(lambda x: x.split()[2], l)
        return map(float, l)

    @timeit
    def maxstep(self):
        """Return a list of floats containing all Max Steps for each geometry iteration"""
        l = filter(lambda x: ' '.join(x.split()).startswith("Maximum Displacement"), self.content())
        l = map(lambda x: x.split()[2], l)
        return map(float, l)

    @timeit
    def rmsstep(self):
        """Return a list of floats containing all RMS Steps for each geometry iteration"""
        l = filter(lambda x: ' '.join(x.split()).startswith("RMS Displacement"), self.content())
        l = map(lambda x: x.split()[2], l)
        return map(float, l)
    
    @timeit
    def tol_maxforce(self):
        """Return the Max Force convergence tolerance as float"""
        t = None
        for line in self.content():
            if line.strip().startswith("Maximum Force"):
                t = float(line.strip().split()[3])
                break
        return t

    @timeit
    def tol_rmsforce(self):
        """Return the RMSD Force convergence tolerance as float"""
        t = None
        for line in self.content():
            if ' '.join(line.strip().split()).startswith("RMS Force"):
                t = float(line.strip().split()[3])
                break
        return t

    @timeit
    def tol_maxstep(self):
        """Return the Max Step convergence tolerance as float"""
        t = None
        for line in self.content():
            if line.strip().startswith("Maximum Displacement"):
                t = float(line.strip().split()[3])
                break
        return t

    @timeit
    def tol_rmsstep(self):
        """Return the RMSD Step convergence tolerance as float"""
        t = None
        for line in self.content():
            if ' '.join(line.strip().split()).startswith("RMS Displacement"):
                t = float(line.strip().split()[3])
                break
        return t


# This class may not be useful for anything.....
class GaussianIn(object):
    def __init__(self, filename):
        self.filename = filename

    def keywords(self):
        pass

    def linkzero(self):
        pass

