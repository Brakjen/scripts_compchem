alias ltr="ls -ltr"
alias cls="clear;ls -1v"
alias cla="clear;ls -a1v"
alias monitor="while true;do sleep 2;qcl;done"
alias bashed="vim ~/.bashrc"
alias killall="scancel -t PENDING -u ambr; scancel -t RUNNING -u ambr"
alias vi="vim"
alias bashsource="source $HOME/.bashrc"
alias strip_ext="echo $1 | cut -d"," -1"

if [ $(echo $PWD | cut -d"/" -f2) == "cluster" ]; then
    alias queuegui="python $HOME/scripts_compchem/QueueGui-fram/queuegui.py"
else
    alias queuegui="python $HOME/scripts_compchem/QueueGui/queuegui.py"
fi
