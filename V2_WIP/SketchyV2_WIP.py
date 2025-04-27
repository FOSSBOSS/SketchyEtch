#!/usr/bin/env python3
# Run in your venv. If you can't find it, use vnv
'''
using standard i2c libraries, so it should run on anything, 
without hardware specific GPIO libraries. 
The seesaw encoders have memory, which is REALLY HELPFUL. 
This means you can read the encoders whenever and not have to constantly listen with IRQs.
it also saves me a step in having to listen for events and count steps, which should prevent
memory related issues present in version 1.

Current hardware expenses: 
HDMI Tap: 6$
4 seesaw rotoray encoders 8$*4 =32$
filament, wire and misc ~4$?
cost 42$
could be less if someone made an actual kit, and knew what they were doing when designing this thing.

Enjoy!
'''

import turtle
import os
from smbus2 import SMBus, i2c_msg
import struct
from time import sleep
import sys

# Setup Turtle
t = turtle.Turtle()
t.home()
t.shape('circle')
t.shapesize(0.5)  # Cursor size: 0.5 is half of normal
t.width(10)
t.speed(0)  # Fastest drawing speed

# Constants
i = 0   # Color index
BYTES = 4
I2C_BUS_NUM = 1         # I2C bus number
I2C_ADDR_X = 0x36       # Encoder for X
I2C_ADDR_Y = 0x37       # Encoder for Y
I2C_ADDR_COLOR = 0x38   # Encoder for color toggle
I2C_ADDR_PEN = 0x39     # Encoder for pen size
SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x30
SEESAW_ENCODER_DELTA = 0x40

# Pen size control
PEN_MIN = 1.0
PEN_MAX = 1000.0
pen_size = 100.0  # Starting pen size

# Color list
#colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 0)]
colors = [
    (1, 0, 0),    # Red
    (0, 1, 0),    # Green
    (0, 0, 1),    # Blue
    (0, 1, 1),    # Cyan
    (1, 0, 1),    # Magenta
    (1, 1, 0),    # Yellow
    (1, 1, 1),    # White
    (0, 0, 0),    # Black
    (0.5, 0, 0),  # Dark Red
    (0, 0.5, 0),  # Dark Green
    (0, 0, 0.5),  # Dark Blue
    (0.5, 0.5, 0),# Olive
    (0.5, 0, 0.5),# Purple
    (0, 0.5, 0.5),# Teal
    (0.5, 0.5, 0.5), # Gray
    (0.25, 0.25, 0.25) # Dark Gray
]


def read_register(bus, addr, base, reg, length):
    try:
        write = i2c_msg.write(addr, [base, reg])
        read = i2c_msg.read(addr, length)
        bus.i2c_rdwr(write, read)
        return list(read)
    except OSError as e:
        print(f"I2C Bus {bus} or Address 0x{addr:02X} not responding.")
        sys.exit(1)

def read_encoder_position(bus, addr):
    data = read_register(bus, addr, SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION, 4)
    pos = struct.unpack(">i", bytes(data))[0]
    return pos

def read_encoder_delta(bus, addr):
    data = read_register(bus, addr, SEESAW_ENCODER_BASE, SEESAW_ENCODER_DELTA, 4)
    delta = struct.unpack(">i", bytes(data))[0]
    return delta

def write_encoder_position(bus, addr, value):
    try:
        data = struct.pack(">i", value)
        write = i2c_msg.write(addr, [SEESAW_ENCODER_BASE, SEESAW_ENCODER_POSITION] + list(data))
        bus.i2c_rdwr(write)
    except OSError as e:
        print(f"Failed to write to encoder at address 0x{addr:02X}. Error: {e}")

def erase(bus):
    write_encoder_position(bus, I2C_ADDR_X, 0)
    write_encoder_position(bus, I2C_ADDR_Y, 0)
    # a small line appears on init, so now we
    # Actively wait until encoders say 0
    
    while True:
        x = read_encoder_position(bus, I2C_ADDR_X)
        y = read_encoder_position(bus, I2C_ADDR_Y)
        if x == 0 and y == 0:
            break
        sleep(0.01)  # Small wait so you don't hammer the bus

    t.clear()
    t.penup()        # lift pen when moving to center. 
    t.goto(0, 0)
    t.pendown()      


def adjust_pen_size(bus):
    global pen_size
    delta = read_encoder_delta(bus, I2C_ADDR_PEN)
    if delta != 0:
        pen_size += delta #* 0.1  # Scale down change
        pen_size = max(PEN_MIN, min(PEN_MAX, pen_size))  # Clamp
        t.width(pen_size)
        print(f"Pen size adjusted to: {pen_size:.1f}")

def toggle_color(bus):
    global i
    delta = read_encoder_delta(bus, I2C_ADDR_COLOR)
    if delta != 0:
        i += delta
        t.pencolor(colors[i % len(colors)])
        print(f"Color changed to: {colors[i % len(colors)]}")

def move_turtle(bus):
    x = read_encoder_position(bus, I2C_ADDR_X)
    y = read_encoder_position(bus, I2C_ADDR_Y)
    # Scale encoder values down because they are too large for the screen or use a giant TV lol
    t.goto(x / 0.1, y / 0.1) # maybe make a dynamic speed function, or add another encoder?

# Turtle screen setup
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # 1,1 = Full screen 
canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.overrideredirect(1)  # Hide window borders

# Main loop
with SMBus(I2C_BUS_NUM) as bus:
    try:
        erase(bus)  # Start fresh
        while True:
            move_turtle(bus)
            adjust_pen_size(bus)
            toggle_color(bus)
            sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting program.")
        sys.exit(0)

screen.mainloop()
'''
dev notes:
Raspberry pi does something weird on the i2c bus / HDMI. You can however run this on a pi, 
as is, though you will have to find the right bus, probably, i2c-1
broken out from the GPIO header. but you wont have to import any GPIO hardware specific libraries.
you just wont be able to use the HDMI in line breakout addapter. Im still figuring out why that is. 
allegdedly, it is possbile, from online reading / official docs, but from bus analyis I see no evidence.
it appears that the video i2c bus is broken out to the GPIO header. Once you do that, it seems to work.

Todo:
write a hardware check for the HMDI hotplug to automagicaly detect bus number.
right now it is manualy assigned. 

write an OS detection function 

add buttons for clear, might just use encoder buttons. was thinking about adding an ADC to handle buttons. but tryna keep hardware costs low.

** Write other programs for this hardware platform. Many possibilities. 

############ Some other feature ideas: #########
background color change.
vectors
a config file
size and shape variants of the pen
more colours
acceleration to speed up drawing large images. 
N size screen detect N size / step ratio to give a relative drawing expirience independent of screen size.

'''
