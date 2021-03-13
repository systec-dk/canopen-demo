#!/usr/bin/env python3

import canopen
import sys
import os
import traceback
import logging
import time
import link
from can import CanError

class Node:

    def __init__(self, ifname):
        self.ifname = ifname

    def print_pdo(self, message):
        str = '{} received:'.format(message.name) \
            + ''.join([(' {} = {:>04b}' if 'DI' in var.name else ' {} ={:> 6}').format(var.od.name, var.raw) for var in message])
        print(str)

    def run(self):

        ifname = self.ifname
        try:

            logging.basicConfig(level=logging.INFO)

            # Start with creating a network representing one CAN bus
            network = canopen.Network()

            link.wait_until_up(ifname)

            # Connect to the CAN bus
            network.connect(channel=ifname, bustype='socketcan')

            network.check()

            # send heartbeat as master, so all the slaves can monitor the master
            network.send_periodic(0x701, b'\x05', 1)

            node = network.add_node(0x40, 'eds/4003002_0.eds')

            node.tpdo.read()
            node.rpdo.read()

            node.nmt.state = 'PRE-OPERATIONAL'

            node.tpdo[1].clear()
            node.tpdo[1].add_variable(0x6000, 1)
            node.tpdo[1].add_variable(0x6401, 1)
            node.tpdo[1].add_variable(0x6401, 2)
            node.tpdo[1].inhibit_time = 2000
            node.tpdo[1].enabled = True
            node.tpdo[1].add_callback(self.print_pdo)

            node.tpdo[2].enabled = False

            node.tpdo.save()

            node.rpdo[1][0x6200].raw = 5

            node.rpdo[1].start(2)

            # have the slave disable the outputs, when this master stops
            node.sdo['Consumer Heartbeat Time'][1].raw = (1 << 16) | 1500

            node.nmt.state = 'OPERATIONAL'

            input('Press enter to exit...\n')

        except KeyboardInterrupt:
            pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            traceback.print_exc()
        finally:
            # Disconnect from CAN bus
            print('going to exit... stopping...')
            if network:
                network.disconnect()


if __name__ == '__main__':
    ifname='vcan0'

    if len(sys.argv) >= 2:
        ifname = sys.argv[1]

    node = Node(ifname)
    node.run()
