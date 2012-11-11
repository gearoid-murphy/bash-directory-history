bash-directory-history
======================

These scripts give you the ability to quickly navigate directories.

To install, create a 'bin' directory in your $HOME.

Copy "cdHistory.sh", "sd.sh" and "searchDirHistory.py" into $HOME/bin.

Add the following aliases to your  $HOME/.bashrc:

alias cd='source $HOME/bin/cdHistory.sh'
alias sd='source $HOME/bin/sd.sh'

Restart bash. Now, each time you cd, a hidden file in your home directory called
'$HOME/.dir_history.txt' will log the name of the directory.

Using the 'sd' command, you can search for directories, similar to the bash
reverse search tool. The up and down arrow keys will cycle between the
available paths. Hitting return will jump you to the selected directory.
