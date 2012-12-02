#!/bin/bash

#http://superuser.com/questions/299694/is-there-a-directory-history-for-bash

#XXX: all special characters must be escaped!
overrideFunctions=$(echo "
#bdh-install-start-DO-NOT-REMOVE-MANUALLY-USE-UNINSTALLER
cd()
{
    builtin cd \"\$@\" && echo \$PWD >> \$HOME/.dir_history.txt
}
sd()
{
    JUMP_DIR=\`python \$HOME/.searchDirHistory.py \$@\`
    if [ \$? -eq 0 ];
    then
       echo \"Jumping to \$JUMP_DIR\"
       cd \"\$JUMP_DIR\"
    fi
}
#bdh-install-end-DO-NOT-REMOVE-MANUALLY-USE-UNINSTALLER
")

usage()
{
cat << EOF
usage: $0 options

This script can install or remove the bash directory history functions

OPTIONS:
   -h      Show this message
   -i      Install
   -u      Uninstall
EOF
}

uninstall()
{
    #http://stackoverflow.com/questions/6287755/using-sed-to-delete-all-lines-between-two-matching-patterns
    sed -i '/^#bdh-install-start/,/^#bdh-install-end/{d}' ~/.bashrc
    rm -f ~/.searchDirHistory.py
}

install()
{
    # If it's already installed, remove it
    if [[ ! -z $(grep "bdh-install-start" ~/.bashrc) ]]
    then
        uninstall
    fi
    
    # Install our functions
    echo "$overrideFunctions" >> ~/.bashrc
    
    # Install the python search script
    cp searchDirHistory.py ~/.searchDirHistory.py
    
    # Bootstrap the history with some locations if history does not exist
    if [[ ! -e ~/.dir_history.txt ]]
    then
        echo $HOME >> ~/.dir_history.txt
        echo "/proc" >> ~/.dir_history.txt
        echo "/proc/sys" >> ~/.dir_history.txt
        echo "/etc" >> ~/.dir_history.txt
        echo "/usr" >> ~/.dir_history.txt
        echo "/bin" >> ~/.dir_history.txt
    fi
    
    echo
    echo "** bash directory history installed **"
    echo
    echo "Use the 'sd' command to quickly search amongst previous directories accessed by 'cd'"
    echo " - Type distinctive substrings of your target directory to focus the search"
    echo " - Use the up/down arrow keys to navigate amongst the results"
    echo " - Directories are ordered by Most-Recently-Used"
    echo " - Use escape or Ctrl-C to quit"
    echo " - Enjoy :)"
    echo
}

while getopts “hiu” OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         i)
             install
             exit 0
             ;;
         u)
             uninstall
             exit 0
             ;;
     esac
done

usage

