# Battery information and watchdog script

Tested on Debian squeeze and OpenBSD 4.9 systems.

# Usage

Run

    python bat.py [ stdout | notify | watchd ]

Or add following line into root's(or user's) crontab:

    */10 * * * * /usr/bin/env python /root/bat.py notify watchd

to check battery status every 10 minutes.

Also it is required to add the following line

    %sudo ALL=NOPASSWD: /usr/sbin/pm-suspend

into sudoers in case you placed this script into user's crontab.

# Requirements

You should have following packges installed:

    pyosd
    pm-utils    (Linux)

# License

Licensed under the terms of GPLv3 license
