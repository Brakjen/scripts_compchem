function q() {
NOJOBS=$(bc <<< "$(squeue -u ambr | wc -l) - 1")
NORUNNING=$(squeue -u ambr | awk '$5 == "R" {print $5}' | wc -l)
NOPENDING=$(squeue -u ambr | awk '$5 == "PD" {print $5}' | wc -l)

echo "------------------------ # -------------------------------------------------------------------------------"
echo "                         #                         mmmm"
echo "            mmm   mmmmm  #mmm    m mm         \$$   #   \"m"
echo "           '   #  # # #  #' '#   #'  '             #    #         Number of jobs:         $NOJOBS"
echo "           m'''#  # # #  #   #   #            \$$   #    #         Number of jobs running: $NORUNNING"
echo "           'mm'#  # # #  ##m#'   #                 #mmm\"          Number of jobs pending: $NOPENDING"
echo "----------------------------------------------------------------------------------------------------------"

squeue -u ambr -S i -o "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"
}
function qcl() {
	clear
	q
}
function jh() {
TODAY=$1
if [ "$1" == "" ];then
	TODAY=$(date +%Y-%m-%d)
fi

echo "-------------------------------------------------------"
echo "Showing job history starting from $TODAY"
echo "-------------------------------------------------------"
sacct --starttime $TODAY --format=User%4,JobID,Jobname%50,state,time,nnodes%2,ncpus%3,CPUTime,elapsed,Start | grep "ambr"
}

function bashsource() {
source ~/.bashrc
}
function jhc() {
TODAY=$1
if [ "$1" == "" ];then
        TODAY=$(date +%Y-%m-%d)
fi

clear
echo "-------------------------------------------------------"
echo "Showing job history starting from $TODAY"
echo "-------------------------------------------------------"
sacct --starttime $TODAY --format=User%4,JobID,Jobname%50,state,time,nnodes%2,ncpus%3,CPUTime,elapsed,Start | grep "ambr"
}

function rmm() {
mv "$@" ~/Trash/
}

function emptytrash() {
trashdir=~/Trash
if [ -d $trashdir ]; then
	if [ "$(ls -A $trashdir)" ]; then
		rm -r $trashdir/*
		echo "Success!"
	else
		echo "$trashdir is already empty!"
	fi
else
	echo "$trashdir does not exist!"
fi
}

function wd() {
JOBID=$1
find /global/work/ambr/*${JOBID}* -iname "*.out"
find /global/work/ambr/*${JOBID}* -iname "*.trj"
find /global/work/ambr/*${JOBID}* -iname "*.chk"

}

function sf() {
NAME=$1
find /home/ambr/* -iname "$1*"
}

function gt() {
cd "$(dirname "$1")"
}

function rmallbutinput() {
jobname=$1
for extension in log out job gbw hess; do
    if [ -f ${jobname}.${extension} ]; then
        rm ${jobname}.${extension}
    fi
done
if [ -f ${jobname}_opt.xyz ]; then
    rm ${jobname}_opt.xyz
fi
}

function ediff_opt() {
START=$(grep "FINAL SINGLE POINT ENERGY" $1 | head -1 | cut -d"Y" -f2)
STOP=$(grep "FINAL SINGLE POINT ENERGY" $1 | tail -1 | cut -d"Y" -f2)
EDIFF=$(bc <<< "($STOP - $START)*627.509")
echo "The energy difference is $EDIFF kcal/mol."
}

function viout() {
OUTFILE=$(wd $1 | head -1)
vi $OUTFILE
}

function gsum() {
clear
JOBNAME=$(echo $1 | cut -d"." -f1)
INFILE=$(find /home/ambr/projects/ -name $JOBNAME.com)
OUTFILE=$(find /home/ambr/projects/ -name $JOBNAME.out)
CHECKFILE=$(find /home/ambr/projects/ -name $JOBNAME.chk)

ROUTE=$(grep "#" $JOBNAME.com)
LINK=$(grep "%" $JOBNAME.com)

printf "Jobname:     \t\t%s\n\n" "$JOBNAME"
printf "Input file:     \t%s\n" "$INFILE"

if [ ! -z $OUTFILE ]; then
    printf "Output file:     \t%s\n" "$OUTFILE"
else
    printf "Output file: \t\t%s\n" "File missing. Perhaps the job is queued?"
fi

if [ ! -z $CHECKFILE ]; then
    printf "Checkpoint file:     \t%s\n\n" "$CHECKFILE"
else
    printf "Checkpoint file: \t%s\n\n" "File missing. Perhaps the job is queued?"
fi

printf "The Link0 section: \n%s\n\n" "$LINK"
printf "The Route section: \n%s\n" "$ROUTE"
}

function check() {
CHECKFILE=$(find /global/work/ambr/$1/* -iname "*.chk")
chkchk $CHECKFILE
}

function g16() {
pid=$(~/bin/g16.sh $1 $2 $3 | cut -d" " -f4)
echo "Submitted batch job $pid"

# Removing old pid files
for file in $1.[0-9][0-9][0-9][0-9][0-9][0-9][0-9]; do
    rmm $file
done
touch $1.$pid
echo "Process ID for $1: $pid" > $1.$pid

HOURS=$(bc <<< "$2 * $3 * 16")
echo "Requested number of CPU hours: $HOURS"
}

function g16_devel() {
pid=$(~/bin/g16_devel.sh $1 | cut -d" " -f4)
echo "Submitted batch job $pid"
touch $1.$pid
echo $pid > $1.$pid
}

function g16_bigmem() {
pid=$(~/bin/g16_bigmem.sh $1 $2 $3 | cut -d" " -f4)
echo "Submitted batch job $pid"
touch $1.$pid
echo $pid > $1.$pid
}

function qfil() {
qcl
IFS='
'
for i in $(squeue -hu ambr -S i); do
    echo $i | awk '{print $1 "     " $6}'
    wd $(echo $i | awk '{print $1}')
    echo ""
done
}

function lspid() {
job=$(echo $1 | cut -d"." -f1)
ls $job* | egrep '.*\.[0-9]{2,}'
}

function updatescripts() {
DIR=/home/ambr/scripts_compchem
CURR_DIR=$PWD
cd $DIR
git pull origin master
cd $CURR_DIR
git checkout .
for file in $DIR/*.py $DIR/*.sh; do
    if [ -L $HOME/bin/$(basename $file) ]; then
        unlink $HOME/bin/$(basename $file)
    fi
    ln -s $file $HOME/bin/$(basename $file)
    chmod +x $HOME/bin/$(basename $file)
done
}
