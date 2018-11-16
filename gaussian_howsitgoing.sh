#!/bin/bash -i

# This script will collect geometry convergence data from a Gaussian output file,
# and plot them for visual inspection.



# Check if a file was given as argument
if [ -z $1 ]; then
    echo "No output file given!"
    exit 0
fi

# now change directory to where the the output file is located
job=$(echo $1 | cut -d"." -f1)
cd "$(dirname "$job.out")"



################ R E M O V I N G   O L D   D A T A   F I L E S #################
for i in cycles maxgrad rmsgrad maxstep rmsstep energies relenergies pred; do
    if [ -f $job.$i ]; then
        rm $job.$i
    fi
done


################ E X T R A C T I N G   D A T A #################
grep "SCF Done" $job.out | awk '{print $5}' > $job.energies
NSTEPS=$(cat $job.energies | wc -l)

grep "SCF Done" $job.out | awk '{print $8}' > $job.cycles
grep "Predicted change in Energy" $job.out | awk '{print $4}' | cut -d"=" -f2 > $job.pred; sed -i s/D/e/g $job.pred
grep "Maximum Force" $job.out | awk '{print $3}' >> $job.maxgrad
grep "RMS     Force" $job.out | awk '{print $3}' >> $job.rmsgrad
grep "Maximum Displacement" $job.out | awk '{print $3}' >> $job.maxstep
grep "RMS     Displacement" $job.out | awk '{print $3}' >> $job.rmsstep

# Computing changes by subtracting previous value from current value
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $job.maxgrad > $job.deltamaxgrad
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $job.rmsgrad > $job.deltarmsgrad
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $job.maxstep > $job.deltamaxstep
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $job.maxstep > $job.deltarmsstep
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $job.energies > $job.deltaenergies
awk 'NR == 1 {START = $0} {$0 = ($0 - START) * 627.509; print}' $job.energies > $job.relenergies

# Define the convergence tolerances by extracting from output file
tolmaxgrad=$(grep "Maximum Force" $job.out | head -1 |  awk '{print $4}')
tolrmsgrad=$(grep "RMS     Force" $job.out | head -1 |  awk '{print $4}')
tolmaxstep=$(grep "Maximum Displacement" $job.out | head -1 |  awk '{print $4}')
tolrmsstep=$(grep "RMS     Displacement" $job.out  | head -1 |  awk '{print $4}')


################ P L O T T I N G ###############
# Checking if old gnuplot file exists.
if [ -f $job.gnuplot ]; then
    rm $job.gnuplot
fi

# setting some variables
echo "set term x11 enhanced dashed size 2000,1000 font ',15'" >> $job.gnuplot
echo "#!/usr/bin/gnuplot -persist" >> $job.gnuplot
echo "set font ',20'" >> $job.gnuplot
echo "set multiplot layout 3, 3" >> $job.gnuplot
echo "set xlabel 'Optimization Step'" >> $job.gnuplot
echo "unset key" >> $job.gnuplot
echo "set xtics out" >> $job.gnuplot
echo "set ytics out" >> $job.gnuplot
echo "set xrange [0:$NSTEPS]" >> $job.gnuplot

# Plotting the number of SCF cycles needed for convergence
echo "set title '# of SCF Cycles'" >> $job.gnuplot
echo "set ylabel '# of SCF cycles' tc rgb 'blue'" >> $job.gnuplot
echo "plot '$job.cycles' w boxes lc rgb 'blue'" >> $job.gnuplot


# Plotting the energy convergence (relative energy)
echo "set title 'Energy'" >> $job.gnuplot
echo "set y2range [-1e-7:1e-7]" >> $job.gnuplot
echo "set y2tics format '%.1e'" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "set ylabel 'Relative energy [kcal/mol]'" >> $job.gnuplot
echo "set y2label 'Energy change [Hartree]' tc rgb 'red'" >> $job.gnuplot
echo "plot '$job.relenergies' w l lw 3 lc rgb 'blue', '$job.deltaenergies' w l lw 2 lt 1 lc rgb 'red' axis x1y2" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot

# Plotting the predicted energy change
echo "set title 'Predicted Energy Change'" >> $job.gnuplot
echo "set ylabel 'Energy [Hartree]'" >> $job.gnuplot
echo "set y2label 'Energy [Hartree]' tc rgb 'red'" >> $job.gnuplot
echo "set yrange [*:1e-3]" >> $job.gnuplot
echo "set y2range [-1e-7:1e-10]" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "plot '$job.pred' w l lw 2 lc rgb 'blue' axis x1y1, '$job.pred' w l lw 2 lt 1 lc rgb 'red' axis x1y2" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot

# Plotting the maximum gradients
echo "set title 'Maximum Gradient'" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set y2label 'd Max gradient [Hartree/Bohr]' tc rgb 'red'" >> $job.gnuplot
echo "set ylabel 'Max gradient [Hartree/Bohr]'" >> $job.gnuplot
echo "set yrange [-0.001:*]" >> $job.gnuplot
echo "set y2range [-10*$tolmaxgrad:10*$tolmaxgrad]" >> $job.gnuplot
echo "set arrow from second 0,$tolmaxgrad to second $NSTEPS,$tolmaxgrad nohead lt 2 lw 2 lc rgb 'black'" >> $job.gnuplot
echo "set arrow from second 0,-$tolmaxgrad to second $NSTEPS,-$tolmaxgrad nohead lt 2 lw 2 lc rgb 'black'" >> $job.gnuplot
echo "plot '$job.maxgrad' w l lw 2 lc rgb 'blue' axis x1y1, '$job.deltamaxgrad' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $job.gnuplot
echo "unset arrow" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot

# Plotting the RMS gradients
echo "set title 'RMS Gradient'" >> $job.gnuplot
echo "set y2label 'd RMS gradient [Hartree/Bohr]' tc rgb 'red'" >> $job.gnuplot
echo "set ylabel 'RMS gradient [Ha/Bohr]'" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set y2tics format '%.1e'" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "set y2range [-10*$tolrmsgrad:10*$tolrmsgrad]" >> $job.gnuplot
echo "set arrow from second 0,$tolrmsgrad to second $NSTEPS,$tolrmsgrad nohead lt 2 lw 2 lc rgb 'black'" >> $job.gnuplot
echo "set arrow from second 0,-$tolrmsgrad to second $NSTEPS,-$tolrmsgrad nohead lt 2 lw 2 lc rgb 'black'" >> $job.gnuplot
echo "plot '$job.rmsgrad' w l lw 2 lc rgb 'blue', '$job.deltarmsgrad' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $job.gnuplot
echo "unset arrow" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot

# Plotting the maximum Displacements
echo "set title 'Maximum displacement'" >> $job.gnuplot
echo "set y2label 'd Max displacement [Hartree/Bohr]' tc rgb 'red'" >> $job.gnuplot
echo "set ylabel 'Max displacement [Bohr]'" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "set y2tics format '%.1e'" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set y2range [-10*$tolmaxstep:10*$tolmaxstep]" >> $job.gnuplot
echo "set arrow from second 0,$tolmaxstep to second $NSTEPS,$tolmaxstep nohead lt 2 lc rgb 'black'" >> $job.gnuplot
echo "set arrow from second 0,-$tolmaxstep to second $NSTEPS,-$tolmaxstep nohead lt 2 lc rgb 'black'" >> $job.gnuplot
echo "plot '$job.maxstep' w l lw 2 lc rgb 'blue', '$job.deltamaxstep' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $job.gnuplot
echo "unset arrow" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot

# Plotting the RMS displacements
echo "set title 'RMS Displacement'" >> $job.gnuplot
echo "set ytics nomirror out" >> $job.gnuplot
echo "set y2label 'd RMS displacement [Hartree/Bohr]' tc rgb 'red'" >> $job.gnuplot
echo "set ylabel 'RMS displacement [Bohr]'" >> $job.gnuplot
echo "set y2tics nomirror" >> $job.gnuplot
echo "set y2range [-10*$tolrmsstep:10*$tolrmsstep]" >> $job.gnuplot
echo "set y2tics format '%.1e'" >> $job.gnuplot
echo "set arrow from second 0,$tolrmsstep to second $NSTEPS,$tolrmsstep nohead lt 2 lc rgb 'black'" >> $job.gnuplot
echo "set arrow from second 0,-$tolrmsstep to second $NSTEPS,-$tolrmsstep nohead lt 2 lc rgb 'black'" >> $job.gnuplot
echo "plot '$job.rmsstep' w l lc rgb 'blue' lw 2, '$job.deltarmsstep' w l lc rgb 'red' lt 1 lw 2 axis x1y2" >> $job.gnuplot
echo "unset arrow" >> $job.gnuplot
echo "set autoscale y" >> $job.gnuplot
echo "set autoscale y2" >> $job.gnuplot
echo "unset y2label" >> $job.gnuplot
echo "unset y2tics" >> $job.gnuplot


gnuplot -persist $job.gnuplot

# Cleaning up
for i in gnuplot deltaenergies deltamaxgrad deltarmsgrad deltamaxstep deltarmsstep cycles maxgrad rmsgrad maxstep rmsstep energies relenergies pred; do
    if [ -f $job.$i ]; then
        rm $job.$i
    fi
done
