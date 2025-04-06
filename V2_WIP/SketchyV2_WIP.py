#!/usr/bin/env python3
# Run in your venv. if you cant find it use vnv
import turtle
import os
from smbus2 import SMBus, i2c_msg
import struct
from time import sleep
import sys


t = turtle.Turtle()
t.home()
t.shape('circle')
t.shapesize(0.5)  # Cursor size: 0.5 is half of normal
t.width(10)

i = 0   #index: current colour count
BYTES = 4
I2C_BUS = 4        # Change if needed
I2C_ADDR1 = 0x36    # X
I2C_ADDR2 = 0x37   # Y
I2C_ADDR3 = 0x38   # color 
I2C_ADDR4 = 0x39   # pen size
SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x30
SEESAW_ENCODER_DELTA = 0x40
# pen stuff
PEN_MIN = 0.1
PEN_MAX = 255
pen_size = 10.0  # starting pen size


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

def write_encoder_position(bus, addr, value):
    try:
        data = struct.pack(">i", value)
        write = i2c_msg.write(addr, [SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION] + list(data))
        bus.i2c_rdwr(write)
    except OSError as e:
        print(f"Failed to write to encoder at address 0x{addr:02X}. Error: {e}")

def erase():   # chan2
    write_encoder_position(bus, I2C_ADDR1, 0)
    write_encoder_position(bus, I2C_ADDR2, 0)
    t.goto(0,0)
    t.clear()
    
def adjust_pen_size(bus):
    global pen_size
    try:
        data = read_register(bus, SEESAW_ENCODER_BASE, SEESAW_ENCODER_DELTA, 4)
        delta = struct.unpack(">i", bytes(data))[0]
        if delta != 0:
            pen_size += delta
            pen_size = max(PEN_MIN, min(PEN_MAX, pen_size))  # Clamp
            t.width(pen_size)
            print(f"Pen size adjusted to: {pen_size:.1f}")
    except Exception as e:
        print(f"Failed to adjust pen size: {e}")    

def move(X,Y):
    X = t.xcor()
    Y = t.ycor()
    
#toggle though colors 
def Colour(channel):     # chan 3, or use another encoder... hm.
    global i
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 0)]  # List of RGB colors
    t.pencolor(colors[i % len(colors)])  # Set pen color based on the current index of the length of the color list
    i += 1

def lift_pen(channel):   # scan ADS1115 for sig chan4
    if t.isdown():
        t.penup()
    else:
        t.pendown()

screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode

canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.overrideredirect(1)
# make a run loop and put it here.
#screen.listen()  # Listen for key presses
with SMBus(I2C_BUS) as bus:
    while True:
        adjust_pen_size(bus)
        sleep(0.1)
screen.mainloop()
