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

# last full capacity
fh=open(BATPATH+"charge_full", "r")
s=fh.read()
fh.close()
fullCap=string.atof(s)

# remaining capacity
fh=open(BATPATH+"charge_now", "r")
s=fh.read()
fh.close()
remCap=string.atof(s)

# create info skeleton
ret="%i"%(remCap/fullCap*100.0)+chr(37)

# time remaining
batPath_prev="/tmp/bat.tmp"
period=30

fh=open(BATPATH+"status", "r")
s=fh.read()
fh.close()

# if AC plugged in -- just print info and delete tmp file
# else -- calc remTime
if ( not s.startswith("Discharging") ):
    print ret
    if ( os.path.exists(batPath_prev) ):
        os.remove(batPath_prev)
    sys.exit(0)

# functions

def dump(remTime):
    fh=open(batPath_prev, "w")
    fh.write( str( int(time.time()) )+"\n" )
    fh.write( str( int(remCap) )+"\n" )
    fh.write( str( remTime )+"\n" )
    fh.close()

def toTime(t):
    remTimes="calculating"
    if ( not t==0 ):
        remH=int(t/60/60)
        remM=(t-remH*60*60)/60
        remTimes="%02d:%02d"%(remH, remM)

    return remTimes

# body

remTimes=""

# if !first run -- read prev results
if ( os.path.exists(batPath_prev) ):
    curTime=int(time.time())
    fh=open(batPath_prev, "r")
    
    oldTime=string.atoi( fh.readline() )
    oldCap=string.atof( fh.readline() )
    oldRemTime=string.atof( fh.readline() )
    
    fh.close()

    if( curTime-oldTime >= period ):
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
