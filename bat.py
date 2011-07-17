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

import string, time, os, sys

BATPATH="/sys/class/power_supply/BAT0/"
argv=sys.argv
argc=len(argv)

username="ilya" # change this username according to your username
osdfont="DejaVuSans 36"

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

def notify(t):
    cmd="export DISPLAY=:0.0; killall -q aosd_cat; su %s -c \"echo \\\"battery level: %s\\\" | aosd_cat -n \\\"%s\\\" & \"" % (username,t,osdfont)
    os.system(cmd)

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

# determine mode
MOD_STDOUT=False
MOD_NOTIFY=False
MOD_WATCHD=False

if ( argc>0 ):
    for i in argv:
        if ( i=='stdout' ):
            MOD_STDOUT=True
            continue

        if ( i=='notify' ):
            MOD_NOTIFY=True
            continue

        if ( i=='watchd' ):
            MOD_STDOUT=True
            continue

# if AC plugged in -- just print info and delete tmp file
# else -- calc remTime
if ( not s.startswith("Discharging") ):
    if ( MOD_STDOUT ):
        print ret

    if ( MOD_NOTIFY ):
        notify(ret)

    if ( os.path.exists(batPath_prev) ):
        os.remove(batPath_prev)
    sys.exit(0)

# body

remTimes=""
remTime=0

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

if ( MOD_STDOUT ):
    print ret

if ( MOD_NOTIFY ):
    notify(ret)

if ( MOD_WATCHD ):
    pass
