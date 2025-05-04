#!/usr/bin/env python3
import os
from smbus2 import SMBus

def findbus():
    known_addrs = {0x36, 0x37, 0x38, 0x39}
    
    for entry in sorted(os.listdir('/dev')):
        if entry.startswith('i2c-'):
            bus_num = int(entry.split('-')[1])
            try:
                with SMBus(bus_num) as bus:
                    if all(_device_present(bus, addr) for addr in known_addrs):
                        return bus_num
            except Exception:
                continue
    return None

def _device_present(bus, addr):
    try:
        bus.read_byte(addr)
        return True
    except OSError:
        return False

# Example usage
I2C_BUS_NUM = findbus()
if I2C_BUS_NUM is not None:
    print(f"All devices found on I2C bus {I2C_BUS_NUM}")
else:
    I2C_BUS_NUM = 1  
    print("Update known address list. defaulting to addr 1")
    
