# ZenStates-FreeBSD
Collection of utilities for Ryzen processors and motherboards

## zenstates.py
Dynamically edit AMD Ryzen processor P-States

Requires root access and the cpuctl kernel module loaded (just run "kldload cpuctl" as root).

    usage: zenstates.py [-h] [-l] [-p {0,1,2,3,4,5,6,7}] [--enable] [--disable] [-f FID] [-d DID] [-v VID]

    Sets P-States for Ryzen processors

    optional arguments:
      -h, --help            show this help message and exit
      -l, --list            List all P-States
      -p {0,1,2,3,4,5,6,7}, --pstate {0,1,2,3,4,5,6,7}
                            P-State to set
      --enable              Enable P-State
      --disable             Disable P-State
      -f FID, --fid FID     FID to set (in hex)
      -d DID, --did DID     DID to set (in hex)
      -v VID, --vid VID     VID to set (in hex)
      -i IDD, --idd IDD     IDD to set (in hex)
      --cc6-enable          Enable Core C-State C6
      --cc6-disable         Disable Core C-State C6
      --pc6-enable          Enable Package C-State C6
      --pc6-disable         Disable Package C-State C6
      --cpb-enable          Enable Core Performance Boost
      --cpb-disable         Disable Core Performance Boost


## togglecode.py
Turns on/off the Q-Code display on ASUS Crosshair VI Hero motherboards (and other boards with a compatible Super I/O chip)

Requires root access and the portio python module (to install run "pip install portio")
