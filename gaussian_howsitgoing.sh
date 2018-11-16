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
    if [ -f $file.$i ]; then
        rm $file.$i
    fi
done


################ E X T R A C T I N G   D A T A #################
grep "SCF Done" $file.out | awk '{print $5}' > $file.energies
NSTEPS=$(cat $file.energies | wc -l)

grep "SCF Done" $file.out | awk '{print $8}' > $file.cycles
grep "Predicted change in Energy" $file.out | awk '{print $4}' | cut -d"=" -f2 > $file.pred; sed -i s/D/e/g $file.pred
grep "Maximum Force" $file.out | awk '{print $3}' >> $file.maxgrad
grep "RMS     Force" $file.out | awk '{print $3}' >> $file.rmsgrad
grep "Maximum Displacement" $file.out | awk '{print $3}' >> $file.maxstep
grep "RMS     Displacement" $file.out | awk '{print $3}' >> $file.rmsstep

# Computing changes by subtracting previous value from current value
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $file.maxgrad > $file.deltamaxgrad
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $file.rmsgrad > $file.deltarmsgrad
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $file.maxstep > $file.deltamaxstep
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $file.maxstep > $file.deltarmsstep
awk 'NR > 1 { print $0 - prev } { prev = $0 }' < $file.energies > $file.deltaenergies
awk 'NR == 1 {START = $0} {$0 = ($0 - START) * 627.509; print}' $file.energies > $file.relenergies

# Define the convergence tolerances by extracting from output file
tolmaxgrad=$(grep "Maximum Force" $file.out | head -1 |  awk '{print $4}')
tolrmsgrad=$(grep "RMS     Force" $file.out | head -1 |  awk '{print $4}')
tolmaxstep=$(grep "Maximum Displacement" $file.out | head -1 |  awk '{print $4}')
tolrmsstep=$(grep "RMS     Displacement" $file.out  | head -1 |  awk '{print $4}')


################ P L O T T I N G ###############
# Checking if old gnuplot file exists.
if [ -f $file.gnuplot ]; then
    rm $file.gnuplot
fi

# setting some variables
echo "set term x11 enhanced dashed size 2000,1000 font ',15'" >> $file.gnuplot
echo "#!/usr/bin/gnuplot -persist" >> $file.gnuplot
echo "set font ',20'" >> $file.gnuplot
echo "set multiplot layout 3, 3" >> $file.gnuplot
echo "set xlabel 'Optimization Step'" >> $file.gnuplot
echo "unset key" >> $file.gnuplot
echo "set xtics out" >> $file.gnuplot
echo "set ytics out" >> $file.gnuplot
echo "set xrange [0:$NSTEPS]" >> $file.gnuplot

# Plotting the number of SCF cycles needed for convergence
echo "set title '# of SCF Cycles'" >> $file.gnuplot
echo "set ylabel '# of SCF cycles' tc rgb 'blue'" >> $file.gnuplot
echo "plot '$file.cycles' w boxes lc rgb 'blue'" >> $file.gnuplot


# Plotting the energy convergence (relative energy)
echo "set title 'Energy'" >> $file.gnuplot
echo "set y2range [-1e-7:1e-7]" >> $file.gnuplot
echo "set y2tics format '%.1e'" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "set ylabel 'Relative energy [kcal/mol]'" >> $file.gnuplot
echo "set y2label 'Energy change [Hartree]' tc rgb 'red'" >> $file.gnuplot
echo "plot '$file.relenergies' w l lw 3 lc rgb 'blue', '$file.deltaenergies' w l lw 2 lt 1 lc rgb 'red' axis x1y2" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot

# Plotting the predicted energy change
echo "set title 'Predicted Energy Change'" >> $file.gnuplot
echo "set ylabel 'Energy [Hartree]'" >> $file.gnuplot
echo "set y2label 'Energy [Hartree]' tc rgb 'red'" >> $file.gnuplot
echo "set yrange [*:1e-3]" >> $file.gnuplot
echo "set y2range [-1e-7:1e-10]" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "plot '$file.pred' w l lw 2 lc rgb 'blue' axis x1y1, '$file.pred' w l lw 2 lt 1 lc rgb 'red' axis x1y2" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot

# Plotting the maximum gradients
echo "set title 'Maximum Gradient'" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set y2label 'd Max gradient [Hartree/Bohr]' tc rgb 'red'" >> $file.gnuplot
echo "set ylabel 'Max gradient [Hartree/Bohr]'" >> $file.gnuplot
echo "set yrange [-0.001:*]" >> $file.gnuplot
echo "set y2range [-10*$tolmaxgrad:10*$tolmaxgrad]" >> $file.gnuplot
echo "set arrow from second 0,$tolmaxgrad to second $NSTEPS,$tolmaxgrad nohead lt 2 lw 2 lc rgb 'black'" >> $file.gnuplot
echo "set arrow from second 0,-$tolmaxgrad to second $NSTEPS,-$tolmaxgrad nohead lt 2 lw 2 lc rgb 'black'" >> $file.gnuplot
echo "plot '$file.maxgrad' w l lw 2 lc rgb 'blue' axis x1y1, '$file.deltamaxgrad' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $file.gnuplot
echo "unset arrow" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot

# Plotting the RMS gradients
echo "set title 'RMS Gradient'" >> $file.gnuplot
echo "set y2label 'd RMS gradient [Hartree/Bohr]' tc rgb 'red'" >> $file.gnuplot
echo "set ylabel 'RMS gradient [Ha/Bohr]'" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set y2tics format '%.1e'" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "set y2range [-10*$tolrmsgrad:10*$tolrmsgrad]" >> $file.gnuplot
echo "set arrow from second 0,$tolrmsgrad to second $NSTEPS,$tolrmsgrad nohead lt 2 lw 2 lc rgb 'black'" >> $file.gnuplot
echo "set arrow from second 0,-$tolrmsgrad to second $NSTEPS,-$tolrmsgrad nohead lt 2 lw 2 lc rgb 'black'" >> $file.gnuplot
echo "plot '$file.rmsgrad' w l lw 2 lc rgb 'blue', '$file.deltarmsgrad' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $file.gnuplot
echo "unset arrow" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot

# Plotting the maximum Displacements
echo "set title 'Maximum displacement'" >> $file.gnuplot
echo "set y2label 'd Max displacement [Hartree/Bohr]' tc rgb 'red'" >> $file.gnuplot
echo "set ylabel 'Max displacement [Bohr]'" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "set y2tics format '%.1e'" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set y2range [-10*$tolmaxstep:10*$tolmaxstep]" >> $file.gnuplot
echo "set arrow from second 0,$tolmaxstep to second $NSTEPS,$tolmaxstep nohead lt 2 lc rgb 'black'" >> $file.gnuplot
echo "set arrow from second 0,-$tolmaxstep to second $NSTEPS,-$tolmaxstep nohead lt 2 lc rgb 'black'" >> $file.gnuplot
echo "plot '$file.maxstep' w l lw 2 lc rgb 'blue', '$file.deltamaxstep' w l lw 2 lc rgb 'red' lt 1 axis x1y2" >> $file.gnuplot
echo "unset arrow" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot

# Plotting the RMS displacements
echo "set title 'RMS Displacement'" >> $file.gnuplot
echo "set ytics nomirror out" >> $file.gnuplot
echo "set y2label 'd RMS displacement [Hartree/Bohr]' tc rgb 'red'" >> $file.gnuplot
echo "set ylabel 'RMS displacement [Bohr]'" >> $file.gnuplot
echo "set y2tics nomirror" >> $file.gnuplot
echo "set y2range [-10*$tolrmsstep:10*$tolrmsstep]" >> $file.gnuplot
echo "set y2tics format '%.1e'" >> $file.gnuplot
echo "set arrow from second 0,$tolrmsstep to second $NSTEPS,$tolrmsstep nohead lt 2 lc rgb 'black'" >> $file.gnuplot
echo "set arrow from second 0,-$tolrmsstep to second $NSTEPS,-$tolrmsstep nohead lt 2 lc rgb 'black'" >> $file.gnuplot
echo "plot '$file.rmsstep' w l lc rgb 'blue' lw 2, '$file.deltarmsstep' w l lc rgb 'red' lt 1 lw 2 axis x1y2" >> $file.gnuplot
echo "unset arrow" >> $file.gnuplot
echo "set autoscale y" >> $file.gnuplot
echo "set autoscale y2" >> $file.gnuplot
echo "unset y2label" >> $file.gnuplot
echo "unset y2tics" >> $file.gnuplot


gnuplot -persist $file.gnuplot

# Cleaning up
for i in gnuplot deltaenergies deltamaxgrad deltarmsgrad deltamaxstep deltarmsstep cycles maxgrad rmsgrad maxstep rmsstep energies relenergies pred; do
    if [ -f $file.$i ]; then
        rm $file.$i
    fi
done
