unalias cd
cd "$@" && echo $PWD >> $HOME/.dir_history.txt
alias cd='source $HOME/bin/cdHistory.sh'
