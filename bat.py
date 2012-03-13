#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

# Battery information and watchdog script
# Copyright (C) 2011, 2012 Ilya Arefiev <arefiev.id@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import string, time, os, sys, stat, pyosd

MSG_UNSUPPORTED_SYSTEM="don't know what can i do on this OS"
MSG_NOT_IMPLEMENTED="not implemented yet"

BATPATH="/sys/class/power_supply/BAT0/"
argv=sys.argv
argc=len(argv)

# tts=1800 # time to suspend (seconds)
pts = 7 # percents to suspend
percents=100

isLinux=( sys.platform.find("linux")>=0 )
isObsd=( sys.platform.find("openbsd")>=0 )

# workaround 4 pyosd
if (not os.environ.has_key("DISPLAY")):
	os.putenv("DISPLAY", ":0.0")

notifyer=pyosd.osd(colour="#00FF00", shadow=3, timeout=3, pos=pyosd.POS_BOT, font='-*-terminus-*-*-*-*-32-*-*-*-*-*-koi8-r')
notifyer.set_shadow_offset(2)
notifyer.set_shadow_colour("#000000")

# functions
def dump(remTime):
    fh=open(batPath_prev, "w")
    fh.write( str( int(time.time()) )+"\n" )
    fh.write( str( remCap )+"\n" )
    fh.write( str( remTime )+"\n" )
    fh.close()

    os.chmod( batPath_prev, stat.S_IRUSR | stat.S_IWUSR |
                            stat.S_IRGRP | stat.S_IWGRP |
                            stat.S_IROTH | stat.S_IWOTH )

def toTime(t):
    remTimes="....." # 5 dots for fixed-width output (HH:MM)
    if ( not t==0 ):
        remH=int(t/60/60)
        remM=(t-remH*60*60)/60
        remTimes="%02d:%02d"%(remH, remM)

    return remTimes

def notify(t):
	notifyer.display(t)
	notifyer.wait_until_no_display()

def watchd(p):
	if ( p < pts ): 
		notify( "going to suspend: %d percents on battery left"%(p) )
		if ( isLinux ):
			cmd="sudo /usr/sbin/pm-suspend"
			os.system(cmd)
		elif( isObsd ):
			cmd="/usr/sbin/apm -z"
			os.system(cmd)
		else:
			notify(MSG_UNSUPPORTED_SYSTEM)

#
# last full capacity
#
#print "getting # last full capacity"
fullCap=0
if ( isLinux ):
	fh=open(BATPATH+"charge_full", "r")
	s=fh.read()
	fh.close()
	fullCap=string.atof(s)
elif ( isObsd ):
	cmd="sysctl -n hw.sensors.acpibat0.amphour0 | sed 's/\ Ah.*//'"
	pipe=os.popen(cmd)
	s=pipe.readline()
	pipe.close()
	fullCap=string.atof(s)
	#print fullCap
else:
	print MSG_UNSUPPORTED_SYSTEM
	sys.exit(1)

#
# remaining capacity
#
#print "getting # remaining capacity"
remCap=0
if ( isLinux ):
	fh=open(BATPATH+"charge_now", "r")
	s=fh.read()
	fh.close()
	remCap=string.atof(s)
elif ( isObsd ):
	cmd="sysctl -n hw.sensors.acpibat0.amphour3 | sed 's/\ Ah.*//'"
	pipe=os.popen(cmd)
	s=pipe.readline()
	pipe.close()
	remCap=string.atof(s)
	#print fullCap
else:
	print MSG_UNSUPPORTED_SYSTEM
	sys.exit(1)

#
# create info skeleton
#
percents=remCap/fullCap*100.0
ret="%3i"%(percents)+chr(37) # %3i -- fixed-width output

#
# time remaining
#
batPath_prev="/tmp/bat.tmp"
period=30

#
# status
#
#print "getting # status"
s=""
if ( isLinux ):
	fh=open(BATPATH+"status", "r")
	s=fh.read()
	fh.close()
elif ( isObsd ):
	cmd="sysctl -n hw.sensors.acpibat0.raw0 | sed -e 's/.*(//' -e 's/).*//'"
	pipe=os.popen(cmd)
	s=pipe.readline()
	pipe.close()
	#print s
else:
	print MSG_UNSUPPORTED_SYSTEM
	sys.exit(1)

#
# determine mode
#
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
            MOD_WATCHD=True
            continue

# if AC plugged in -- just print info and delete tmp file
# else -- calc remTime
if ( not (s.find("ischarging")>=0) ):
    if ( MOD_STDOUT ):
        print ret

    if ( MOD_NOTIFY and percents < 99):
        notify(ret)

    if ( os.path.exists(batPath_prev) ):
        os.remove(batPath_prev)
    sys.exit(0)

# body

remTimes=""
remTime=0
suspendAllowed=True

# if !first run -- read prev results
if ( os.path.exists(batPath_prev) ):
    curTime=int(time.time())
    fh=open(batPath_prev, "r")

    oldTime=string.atoi( fh.readline() )
    oldCap=string.atof( fh.readline() )
    oldRemTime=string.atof( fh.readline() )

    ## debug
    #print "rc %f"%( remCap )
    #print "ot %f; oc %f; ort %f"%( oldTime, oldCap, oldRemTime )

    fh.close()

    if( curTime-oldTime >= period ):
        deltaCap=abs(oldCap-remCap)
        deltaTime=curTime-oldTime
        vel=deltaCap/deltaTime

        ## debug
        #print "dc %f; dt %f; v %f"%( deltaCap, deltaTime, vel )

        try:
          remTime=remCap/vel
        except ZeroDivisionError:
          remTime=oldRemTime # keep old value
        remTimes=toTime(remTime)

        dump( remTime )
    else:
        remTime=oldRemTime # keep old value
        remTimes=toTime( oldRemTime )
else:
    # first write
    dump( 0 )
    suspendAllowed=False

ret+=" %s"%remTimes

if ( MOD_STDOUT ):
    print ret

if ( MOD_NOTIFY ):
    notify("battery level: "+ret)

if ( MOD_WATCHD and suspendAllowed ):
    # watchd(remTime)
	watchd( percents )
