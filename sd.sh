#!/bin/sh

JUMP_DIR=`python $HOME/bin/searchDirHistory.py $@`
if [ $? -eq 0 ];
then
	echo "Jumping to $JUMP_DIR"
	cd "$JUMP_DIR"
fi

