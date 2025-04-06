#!/usr/bin/env python3
from smbus2 import SMBus, i2c_msg
import struct
from time import sleep
import sys
"""
The seesaw ecoders have some differences from the encoders used in V1 SketchyEtch:
first, i2c addresssing
second, memory, they can save the value of where they last were. ... for the entire time they are powered.
    removing the device from power, theyll forget thier position.
    but you can turn the knobs with this program off, and thyell keep storing positional data.
    which is really interesting.
    
might implement the buttons though I dont anticapte using them. 
There is also an RGB neopixel on each encoder.
"""
BYTES = 4
I2C_BUS = 4        # Change if needed
I2C_ADDR1 = 0x36
I2C_ADDR2 = 0x37
SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x30
SEESAW_ENCODER_DELTA = 0x40

def read_register(bus, addr, base, reg, length):
    try:
        # Write base + reg
        write = i2c_msg.write(addr, [base, reg])
        read = i2c_msg.read(addr, length)
        bus.i2c_rdwr(write, read)
        return list(read)
    except OSError as e:
        # ok still a logical error here, you can have the right bus on the wrong addr, or the wrong bus on the right addr or...
        # want to fail gracefully, but with good descriptions.
        print(f"I2C Bus 0x{I2C_BUS:02X} not responding.")
        print(f"I2C Address 0x{addr:02X} not responding.")
        print("Check your Bus and addresses.")
        sys.exit(1)      

def read_encoder_position(bus):
    data = read_register(bus, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, I2C_BUS)
    pos = struct.unpack(">i", bytes(data))[0]
    return pos

def read_encoder_delta(bus):
    data = read_register(bus, SEESAW_ENCODER_BASE, SEESAW_ENCODER_DELTA, I2C_BUS)
    delta = struct.unpack(">i", bytes(data))[0]
    return delta

if __name__ == "__main__":
    with SMBus(I2C_BUS) as bus:
        try:
            while True:
                addr_x = read_register(bus, I2C_ADDR1, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)
                addr_y = read_register(bus, I2C_ADDR2, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)
                X = struct.unpack(">i", bytes(addr_x))[0]
                Y = struct.unpack(">i", bytes(addr_y))[0]

                
                print(f"X {X}, Y {Y}")
                
                '''
                for addr in [I2C_ADDR, I2C_ADDR2]:
                    data = read_register(bus, addr, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)
                    pos = struct.unpack(">i", bytes(data))[0]
                    print(f"Encoder {addr:02X} Position: {pos}")

                #pos = read_encoder_position(bus)
                #delta = read_encoder_delta(bus)
                #print(f"Position: {pos}, Delta: {delta}")
                '''
                sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
