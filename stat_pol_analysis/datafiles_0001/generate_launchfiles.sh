source /home/ambr/scripts_compchem/bash_stallo_functions.sh

orbdir=/global/work/ambr/benchmark_orbitals

no_jobs=$(ls *_?????_*.inp | wc -l)
counter=0
for i in *_?????_*.inp; do
    (( counter++ ))
    echo $counter/$no_jobs

    jobname=$(echo $i | strip_ext $i)
    molecule=$(echo $jobname | cut -d"_" -f1)
    functional=$(echo $jobname | cut -d"_" -f2)
    strength=$(echo $jobname | cut -d"_" -f3)
    direction=$(echo $jobname | cut -d"_" -f4)


#    echo Inputfile:::$i
#    echo Launch file:${molecule}_${functional}_${strength}_${direction}.launch
#    echo Orbitals::::${orbdir}/${molecule}_${functional}_000_orbitals
#    echo ""

    launchfile=${molecule}_${functional}_${strength}_${direction}.launch
    # Remove old launch file and touch a new one
    if [ -f $launchfile ]; then
        rm $launchfile
    fi
    touch ${molecule}_${functional}_${strength}_${direction}.launch

    echo "#!/bin/bash" >> $launchfile
    echo "" >> $launchfile
    echo "#SBATCH --account=nn9330k" >> $launchfile
    echo "#SBATCH --job-name=$jobname" >> $launchfile
    echo "#SBATCH --nodes=1" >> $launchfile
    echo "#SBATCH --ntasks-per-node=2" >> $launchfile
    echo "#SBATCH --cpus-per-task=10" >> $launchfile
    echo "#SBATCH --time=24:00:00" >> $launchfile
    echo "#SBATCH --mem=30GB" >> $launchfile
    echo "#SBATCH --partition=normal" >> $launchfile
    echo "#SBATCH --output=${jobname}.log" >> $launchfile
    echo "#SBATCH --error=${jobname}.err" >> $launchfile
    echo "" >> $launchfile
    echo "module purge" >> $launchfile
    echo "module restore mrchem" >> $launchfile
    echo "" >> $launchfile
    echo "export OMP_NUM_THREADS=\${SLURM_CPUS_PER_TASK}" >> $launchfile
    echo "" >> $launchfile
    echo "SCRATCH_DIR=/global/work/\$USER/MRCHEM-\$SLURM_JOBID" >> $launchfile
    echo "mkdir -p \$SCRATCH_DIR" >> $launchfile
    echo "cd \$SCRATCH_DIR" >> $launchfile
    echo "" >> $launchfile
    echo "cp \${SLURM_SUBMIT_DIR}/$i mrchem.inp" >> $launchfile
    echo "cp -r ${orbdir}/${molecule}_${functional}_000_orbitals orbitals" >> $launchfile
    echo "" >> $launchfile
    echo "/home/ambr/mrchem/install-mrchem/bin/mrchem -D mrchem.inp" >> $launchfile
    echo "mpirun /home/ambr/mrchem/install-mrchem/bin/mrchem.x @mrchem.inp > ${jobname}.out" >> $launchfile
    echo "" >> $launchfile
    echo "cp ${jobname}.out \${SLURM_SUBMIT_DIR}/" >> $launchfile
    echo "" >> $launchfile
    echo "exit 0" >> $launchfile

    # Add MPI section to input file

    echo "MPI {" >> $i
    echo "numerically_exact = false" >> $i
    echo "share_coulomb_density = false" >> $i
    echo "share_coulomb_potential = true" >> $i
    echo "share_nuclear_potential = true" >> $i
    echo "share_xc_density = false" >> $i
    echo "share_xc_potential = false" >> $i
    echo "}" >> $i

done
