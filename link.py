#!/usr/bin/env python3

import sys
import time
from pyroute2 import IPRoute

def wait_until_up(ifname):

    ipr = IPRoute()

    while True:
        devs = ipr.get_links(ifname=ifname)
        if len(devs) == 0:
            print(ifname, 'not existing yet')
            time.sleep(2)
            continue
        state = devs[0]['state']
        print(ifname, state)
        if state != 'up':
            time.sleep(2)
            continue
        break

if __name__ == '__main__':
    ifname='vcan0'

    if len(sys.argv) >= 2:
        ifname = sys.argv[1]
    
    wait_until_up(ifname)
