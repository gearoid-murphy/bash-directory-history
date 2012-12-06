#!/usr/bin/python
#
# searchDirHistory.py - Search amongst directory navigation history
#
# This file is part of the bash-directory-history project
#
# Copyright (c) 2011-2012 by Gearoid Murphy
#
# The bash-directory-history project is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# The bash-directory-history project is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bash-directory-history project; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#

import os, sys, termios, tty, select, fcntl, struct, collections

# Some obscure ioctl tickling to get the size of the terminal window
height, width, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
blankString = ''.join(int(width)*[' '])

def searchPaths(paths, searchTerms):

    tailFilter = None
    if len(searchTerms) > 0 and searchTerms [-1] [-1] == '<':
        tailFilter = searchTerms [-1] [0:-1]
        searchTerms = searchTerms [0:-1]
    #
    
    #
    altTerms = []
    for term in searchTerms:
        altTerms.append(term.lower())
    numTerms = len(searchTerms)
    
    rankedPaths = []
    for pi in range(0, len(paths)):
        
        path = paths [pi]
        if len(path) == 0: continue 
        score = 0
        altPath = path.lower()
        for i in range(0, numTerms):
            if searchTerms [i] in path:
                score += 2
            elif altTerms [i] in altPath:
                score += 1
            #
        #
        if tailFilter != None and path.endswith(tailFilter):
            score += 100
        
        rankedPaths.append((score, pi, path))
    #
    
    # python sort is stable, so it preserves the list order
    rankedPaths.sort(key=lambda ranked: ranked[0], reverse=True)
    return rankedPaths
#

def blankWorkArea(numRows):
    sys.stderr.write('\r')
    for i in range(0, numRows):sys.stderr.write(blankString + "\n")
    # Return to original position
    for i in range(0, numRows):sys.stderr.write('\x1b' + '[' + 'A')
#

def handleUserIO(paths, searchChars):
    #

    
    old_settings = termios.tcgetattr(sys.stdin)
    numResults = 10
    if len(paths) < numResults: numResults = len(paths) - 1
    if numResults < 1: 
        sys.stderr.write("Not enough directory entries\n")
        sys.exit(1)
    numRows = numResults + 1
    resOffset = -1
    c = None
    try:
        fd = sys.stdin.fileno()
        # Even more obscure I/O blocking manipulation a la fcntl
        stdFlags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, stdFlags | os.O_NONBLOCK)
        fcntl.fcntl(fd, fcntl.F_SETFL, stdFlags)
        tty.setcbreak(sys.stdin.fileno())
        
        # Terminal input usually comes 1 char at a time
        # But terminal extensions allow extended sequences (ie, for the arrow keys)
        def getChars():
            chars = []
            chars.append(sys.stdin.read(1))
            
            # Set non-blocking IO, read until exception, set back to blocking...
            try:
                fcntl.fcntl(fd, fcntl.F_SETFL, stdFlags | os.O_NONBLOCK)
                while True: chars.append(sys.stdin.read(1))
            except:
                fcntl.fcntl(fd, fcntl.F_SETFL, stdFlags)
            return chars
            #
        #
        while True:
            searchTerms = [t for t in (''.join(searchChars)).split(' ') if len(t) > 0] # filter spaces
            searchString = ''.join(searchChars)
            rankedPaths = searchPaths(paths, searchTerms)
            # Blank the output area
            blankWorkArea(numRows)
            # Print out the orginal search string
            sys.stderr.write(searchString + '\n')
            # Print out the ranked paths
            for i in range(0, numResults):
                marker = "[%i]" % (i)
                if i == resOffset:
                    marker = ">>>"
                sys.stderr.write("%s %s\n" % (marker, rankedPaths [i] [2] [-(width-4):]))
            # Return to the original position
            for i in range(0, numRows):sys.stderr.write('\x1b' + '[' + 'A')
            # Offset for the size of the search string
            for i in range(0, len(searchString)):sys.stderr.write('\x1b' + '[' + 'C')
            
            chars = getChars()
            if len(chars) == 1:
                c = chars [0]
                if c == '\x1b': raise NameError('User pressed escape')
                if ord(c) == 10: # 'enter' was pressed...
                    blankWorkArea(numRows)
                    if resOffset == -1:
                        print rankedPaths [0] [2]
                    else:
                        print rankedPaths [resOffset] [2]
                    break
                elif c == '\x7f' and len(searchChars) > 0:
                    searchChars.pop()
                else:
                    searchChars.append(c)
                #
                resOffset = -1 ;
            else:
                assert len(chars) == 3
                if chars [1] == '[' and chars [2] == 'B'and resOffset < numResults-1:
                    resOffset += 1
                elif chars [1] == '[' and chars [2] == 'A' and resOffset > 0:
                    resOffset -= 1
                #
            #
        #
    except:
        #raise # for debugging...
        blankWorkArea(numRows)
        sys.exit(1)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    #
    dirHistFile = os.path.join(os.environ["HOME"], ".dir_history.txt")
    if not os.path.isfile(dirHistFile):
        print "Directory history file not found:", dirHistFile
        sys.exit(1)
    
    # Raw paths contains the history of 'cd'
    # It may contain duplicate references to the same directory
    rawPaths = open(dirHistFile).read().split('\n')
    
    # We iterate in reverse order over list from new to old
    # removing duplicates as we go
    uniquePaths = collections.OrderedDict()
    for rawPath in reversed(rawPaths):
        rawPath = rawPath.strip()
        if len(rawPath) > 0:
            uniquePaths [rawPath] = None
    paths = list(uniquePaths)
    #
    open(dirHistFile, 'w').write('\n'.join(reversed(paths)))
    # Setup terminal interface and wait for user input
    handleUserIO(paths, list(' '.join(sys.argv[1:])))
#

