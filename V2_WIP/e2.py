#!/usr/bin/env python3
from smbus2 import SMBus, i2c_msg
import struct
from time import sleep
import sys
import turtle

t = turtle.Turtle()
t.home()
t.shape('circle')
t.shapesize(1)  # Cursor size: 0.5 is half of normal
t.width(10)

# I2C Encoder Stuff
BYTES = 4
I2C_BUS = 4        # Change if needed
I2C_ADDR1 = 0x36   # X
I2C_ADDR2 = 0x37   # Y
I2C_ADDR3 = 0x38   # size
I2C_ADDR4 = 0x39   # Colour
SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x30
SEESAW_ENCODER_DELTA = 0x40

 
# HARDWARE FUNCTIONS

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

def write_encoder_position(bus, addr, value):
    try:
        data = struct.pack(">i", value)
        write = i2c_msg.write(addr, [SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION] + list(data))
        bus.i2c_rdwr(write)
    except OSError as e:
        print(f"Failed to write to encoder at address 0x{addr:02X}. Error: {e}")
        

def read_encoder_position(bus):
    data = read_register(bus, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, I2C_BUS)
    pos = struct.unpack(">i", bytes(data))[0]
    return pos

def read_encoder_delta(bus):
    data = read_register(bus, SEESAW_ENCODER_BASE, SEESAW_ENCODER_DELTA, I2C_BUS)
    delta = struct.unpack(">i", bytes(data))[0]
    return delta
# SOFTWARE FUNCTIONS
# Screen stuff:
def get_screen_size_turtle():
    screen = turtle.Screen()
    width = screen.window_width()
    height = screen.window_height()
    return width/2, height/2
    
     
w, h = get_screen_size_turtle()
print(f"Turtle screen size: {w}x{h}") # w,h, are half of total size as turtle puts 0,0 at center of screen.


def erase(bus):   # chan2 
    write_encoder_position(bus, I2C_ADDR1, 0)
    write_encoder_position(bus, I2C_ADDR2, 0)
    t.goto(0,0)
    t.clear() 

def lift_pen(bus):   # scan ADS1115 for sig chan4
    if t.isdown():
        t.penup()
    else:
        t.pendown()

if __name__ == "__main__":
    with SMBus(I2C_BUS) as bus:
        try:
            while True:
                addr_x = read_register(bus, I2C_ADDR1, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)
                addr_y = read_register(bus, I2C_ADDR2, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)
                addr_S = read_register(bus, I2C_ADDR3, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)   # pen size
                addr_C = read_register(bus, I2C_ADDR4, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, BYTES)   # color
		
                X = struct.unpack(">i", bytes(addr_x))[0]
                Y = struct.unpack(">i", bytes(addr_y))[0]
                S = struct.unpack(">i", bytes(addr_S))[0]
                C = struct.unpack(">i", bytes(addr_C))[0]
		              
                print(f"X {X}, Y {Y}, Size:{S}, Colour index{C}")
                t.shapesize(S)
                t.color(C)
                t.goto(X,Y)
		# fix this bro
                if X > 40 or Y > 40:   # move more than 40 out to clear 
                    erase()
                sleep(1)
		# add a read for the pen state here.
        except KeyboardInterrupt:
            print("\nExiting...")
            
"""
The seesaw ecoders have some differences from the encoders used in V1 SketchyEtch:
first, i2c addresssing
second, memory, they can save the value of where they last were. ... for the entire time they are powered.
    removing the device from power, theyll forget thier position.
    but you can turn the knobs with this program off, and thyell keep storing positional data.
    which is really interesting.
    
might implement the encoder buttons though I dont anticapte using them. 
There is also an RGB neopixel on each encoder.
"""
