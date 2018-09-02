#!/usr/bin/env python
import struct
import os
import glob
import argparse
import fcntl

pstates = range(0xC0010064, 0xC001006C)

def writemsr(msr, val, cpu = -1):
    try:
        if cpu == -1:
            for c in glob.glob('/dev/cpuctl[0-9]*'):
                f = os.open(c, os.O_WRONLY)
                fcntl.ioctl(f, 0xc0106302, struct.pack('@IQ', msr, val))
                os.close(f)
        else:
            f = os.open('/dev/cpuctl%d' % (cpu), os.O_WRONLY)
            fcntl.ioctl(f, 0xc0106302, struct.pack('@IQ', msr, val))
            os.close(f)
    except:
        raise OSError("cpuctl module not loaded (run kldload cpuctl)")

def readmsr(msr, cpu = 0):
    try:
        f = os.open('/dev/cpuctl%d' % cpu, os.O_RDONLY)
        val = struct.unpack('QQ', fcntl.ioctl(f, 0xc0106301, struct.pack('@IQ', msr, 0)))[1]
        os.close(f)
        return val
    except:
        raise OSError("cpuctl module not loaded (run kldload cpuctl)")

def pstate2str(val):
    if val & (1 << 63):
        fid = val & 0xff
        did = (val & 0x3f00) >> 8
        vid = (val & 0x3fc000) >> 14
        iddv = (val & 0x3fc00000) >> 22
        iddd = (val & 0xc0000000) >> 30
        ratio = 0.25 * fid / (did * 0.125)
        vcore = 1.55 - 0.00625 * vid
        return "Enabled - FID = %X - DID = %X - VID = %X - IDD = %X( / %X )\n             - Ratio = %.2f - vCore = %.5f" % (fid, did, vid, iddv, iddd, ratio, vcore)
    else:
        return "Disabled"

def setbits(val, base, length, new):
    return (val ^ (val & ((2 ** length - 1) << base))) + (new << base)

def setfid(val, new):
    return setbits(val, 0, 8, new)

def setdid(val, new):
    return setbits(val, 8, 6, new)

def setvid(val, new):
    return setbits(val, 14, 8, new)

def setidd(val, new):
    return setbits(val, 22, 8, new)

def hex(x):
    return int(x, 16)

parser = argparse.ArgumentParser(description='Sets P-States for Ryzen processors')
parser.add_argument('-l', '--list', action='store_true', help='List all P-States')
parser.add_argument('-p', '--pstate', default=-1, type=int, choices=range(8), help='P-State to set')
parser.add_argument('--enable', action='store_true', help='Enable P-State')
parser.add_argument('--disable', action='store_true', help='Disable P-State')
parser.add_argument('-f', '--fid', default=-1, type=hex, help='FID to set (in hex)')
parser.add_argument('-d', '--did', default=-1, type=hex, help='DID to set (in hex)')
parser.add_argument('-v', '--vid', default=-1, type=hex, help='VID to set (in hex)')
parser.add_argument('-i', '--idd', default=-1, type=hex, help='IDD to set (in hex)')
parser.add_argument('--cc6-enable', action='store_true', help='Enable Core C-State C6')
parser.add_argument('--cc6-disable', action='store_true', help='Disable Core C-State C6')
parser.add_argument('--pc6-enable', action='store_true', help='Enable Package C-State C6')
parser.add_argument('--pc6-disable', action='store_true', help='Disable Package C-State C6')
parser.add_argument('--cpb-enable', action='store_true', help='Enable Core Performance Boost')
parser.add_argument('--cpb-disable', action='store_true', help='Disable Core Performance Boost')

args = parser.parse_args()

if args.list:
    for p in range(len(pstates)):
        print('P' + str(p) + " - " + pstate2str(readmsr(pstates[p])))
    print('Core Performance Boost - ' + ('Disabled' if readmsr(0xC0010015) & (1 << 25) else 'Enabled'))
    print('C6 State - Package - ' + ('Enabled' if readmsr(0xC0010292) & (1 << 32) else 'Disabled'))
    print('C6 State - Core - ' + ('Enabled' if readmsr(0xC0010296) & ((1 << 22) | (1 << 14) | (1 << 6)) == ((1 << 22) | (1 << 14) | (1 << 6)) else 'Disabled'))

if args.pstate >= 0:
    new = old = readmsr(pstates[args.pstate])
    print('Current P' + str(args.pstate) + ': ' + pstate2str(old))
    if args.enable:
        new = setbits(new, 63, 1, 1)
        print('Enabling state')
    if args.disable:
        new = setbits(new, 63, 1, 0)
        print('Disabling state')
    if args.fid >= 0:
        new = setfid(new, args.fid)
        print('Setting FID to %X' % args.fid)
    if args.did >= 0:
        new = setdid(new, args.did)
        print('Setting DID to %X' % args.did)
    if args.vid >= 0:
        new = setvid(new, args.vid)
        print('Setting VID to %X' % args.vid)
    if args.idd >= 0:
        new = setidd(new, args.idd)
        print('Setting IDD to %X' % args.idd)
    if new != old:
        if not (readmsr(0xC0010015) & (1 << 21)):
            print('Locking TSC frequency')
            for c in range(len(glob.glob('/dev/cpuctl[0-9]*'))):
                writemsr(0xC0010015, readmsr(0xC0010015, c) | (1 << 21), c)
        print('New P' + str(args.pstate) + ': ' + pstate2str(new))
        writemsr(pstates[args.pstate], new)

if args.cc6_enable:
    writemsr(0xC0010292, readmsr(0xC0010292) | (1 << 32))
    print('Enabling Core C6 state')

if args.cc6_disable:
    writemsr(0xC0010292, readmsr(0xC0010292) & ~(1 << 32))
    print('Disabling Core C6 state')

if args.pc6_enable:
    writemsr(0xC0010292, readmsr(0xC0010292) | (1 << 32))
    print('Enabling Package C6 state')

if args.pc6_disable:
    writemsr(0xC0010292, readmsr(0xC0010292) & ~(1 << 32))
    print('Disabling Package C6 state')

if args.cpb_enable:
    writemsr(0xC0010015, readmsr(0xC0010015) & ~(1 << 25))
    print('Enabling Core Performance Boost')

if args.cpb_disable:
    writemsr(0xC0010015, readmsr(0xC0010015) | (1 << 25))
    print('Disabling Core Performance Boost')

if not args.list and args.pstate == -1 and not args.cc6_enable and not args.cc6_disable and not args.pc6_enable and not args.pc6_disable and not args.cpb_enable and not args.cpb_disable:
    parser.print_help()
