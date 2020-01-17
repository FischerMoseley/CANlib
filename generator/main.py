import sys
sys.path.append('ParseCAN')
import ParseCAN

import constants
import pack_unpack_c
import pack_unpack_h
import enum_atom
import structs
import sys
import computers_h
import computers_c
import test_h
import test_c
import send_receive
import bus
import drivers_inc

if __name__ == '__main__':
    specpath = sys.argv[1]
    specfile = open(specpath, 'r')
    system = ParseCAN.spec.System.from_yaml(specfile)
    can = system.protocol['name']['can']

    constants.write(can)
    pack_unpack_c.write(can)
    pack_unpack_h.write(can)
    enum_atom.write(can)
    send_receive.write(can)
    structs.write(can)
    bus.write(can, system.computer)
    computers_h.write(system, can, system.computer)
    computers_c.write(can, system.computer)
    test_h.write(can)
    test_c.write(can)

    drivers_inc.write(system)
