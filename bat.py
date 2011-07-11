#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Battery information and watchdog script
# Copyright (C) 2011  Ilya Arefiev <arefiev.id@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re, string, time, os, sys

BATPATH="/sys/class/power_supply/BAT0/"

fh=open(BATPATH+"charge_full", "r")
s=fh.read()
fh.close()

# design capacity

#pat=re.compile(r"last\ full\ capacity:\ +[0-9]+")
#fullCap=pat.findall(s)[0]
fullCap=string.atoi(s)

#pat=re.compile(r"[0-9]+")
#fullCap=string.atof( pat.findall(fullCap)[0] )

# remaining capacity
fh=open(BATPATH+"charge_now", "r")
s=fh.read()
fh.close()

#pat=re.compile(r"remaining\ capacity:\ +[0-9]+")
#remCap=pat.findall(s)[0]
remCap=string.atoi(s)

#pat=re.compile(r"[0-9]+")
#remCap=string.atof( pat.findall(remCap)[0] )

ret="%i"%(remCap/fullCap*100)+chr(37)

# time remaining
batPath_prev="/tmp/bat.tmp"
period=30

print "1st if"

if ( s.find("discharging")==-1 ):
    print ret
    if ( os.path.exists(batPath_prev) ):
        os.remove(batPath_prev)
    sys.exit(0)

def dump(remTime):
    print "dump"
    fh=open(batPath_prev, "w")
    fh.write( str( int(time.time()) )+"\n" )
    fh.write( str( int(remCap) )+"\n" )
    fh.write( str( remTime )+"\n" )
    fh.close()

def toTime(t):
    if (t==0):
        remTimes="calculating"
    else:
        remH=int(t/60/60)
        remM=(t-remH*60*60)/60
        remTimes="%02d:%02d"%(remH, remM)

    return remTimes

print "body"

if ( os.path.exists(batPath_prev) ):
    curTime=int(time.time())
    fh=open(batPath_prev, "r")
    
    oldTime=string.atoi( fh.readline() )
    oldCap=string.atoi( fh.readline() )
    oldRemTime=string.atof( fh.readline() )
    
    fh.close()

    if( curTime-oldTime>=period ):
        deltaCap=oldCap-remCap
        deltaTime=curTime-oldTime
        vel=deltaCap/deltaTime

        try:
          remTime=remCap/vel
        except ZeroDivisionError:
          remTime=0
        remTimes=toTime(remTime)
        
        dump( remTime )
    else:
        remTimes=toTime( oldRemTime )
else:
    # first write
    dump( 0 )

ret+=" %s"%remTimes
    
print ret
