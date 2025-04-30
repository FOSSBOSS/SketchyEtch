#!/usr/bin/env python3
# Run in your venv. If you can't find it, use vnv
'''
https://docs.python.org/3/library/turtle.html
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
t.shapesize(1)  # Cursor size: 0.5 is half of normal
#t.width(10)
t.speed(0)  # Fastest drawing speed

# look for the bus with your known addresses
I2C_BUS_NUM = 0
def findbus():
    known_addrs = {0x36, 0x37, 0x38, 0x39}    # put your known encoder addresses here.
    
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
I2C_BUS_NUM = findbus()
if I2C_BUS_NUM is not None:
    print(f"All devices found on I2C bus {I2C_BUS_NUM}")
else:
    I2C_BUS_NUM = 1  
    print("Update known address list. defaulting to addr 1")
    
    
#print(I2C_BUS_NUM)

i = 0   # Color index
BYTES = 4
I2C_BUS_NUM = 1         # I2C bus number
# Set or check the function of your encoders here
I2C_ADDR_X = 0x36       # Encoder for X
I2C_ADDR_Y = 0x37       # Encoder for Y
I2C_ADDR_COLOR = 0x38   # Encoder for color toggle
I2C_ADDR_PEN = 0x39     # Encoder for pen size

SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x30
SEESAW_ENCODER_DELTA = 0x40

### ADC setup (BUTTONS)
I2C_ADDR = 0x48
CONFIG_REG = 0x01
CONVERSION_REG = 0x00

# MUX values for AIN0–AIN3
MUX = [0x4000, 0x5000, 0x6000, 0x7000]

# Base config:
# - OS=1 (start single conversion)
# - PGA=±4.096V
# - MODE=single-shot
# - DR=128SPS
# - Comparator disabled
BASE_CONFIG = 0x8000 | 0x0200 | 0x0100 | 0x0080 | 0x0003



# Pen size control
PEN_MIN = 1.0
PEN_MAX = 1000.0
pen_size = 100.0  # Starting pen size

# Color list
colors = [
    (1, 0, 0),         # Red
    (0, 1, 0),         # Green
    (0, 0, 1),         # Blue
    (0, 1, 1),         # Cyan
    (1, 0, 1),         # Magenta
    (1, 1, 0),         # Yellow
    #(1, 1, 1),         # White button for that now
    (0, 0, 0),         # Black
    (0.5, 0, 0),       # Dark Red
    (0, 0.5, 0),       # Dark Green
    (0, 0, 0.5),       # Dark Blue
    (0.5, 0.5, 0),     # Olive
    (0.5, 0, 0.5),     # Purple
    (0, 0.5, 0.5),     # Teal
    (0.5, 0.5, 0.5),   # Gray
    (0.25, 0.25, 0.25) # Dark Gray
]
# Turning the knob quickly can flood the bus.


def read_adc(bus, channel):
    config = BASE_CONFIG | MUX[channel]
    config_bytes = [(config >> 8) & 0xFF, config & 0xFF]
    bus.write_i2c_block_data(I2C_ADDR, CONFIG_REG, config_bytes)
    sleep(0.1)
    raw = bus.read_i2c_block_data(I2C_ADDR, CONVERSION_REG, 2)
    value = (raw[0] << 8) | raw[1]
    if value > 0x7FFF:
        value -= 0x10000
    return value


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

    while True:
        x = read_encoder_position(bus, I2C_ADDR_X)
        y = read_encoder_position(bus, I2C_ADDR_Y)
        if x == 0 and y == 0:
            break
        sleep(0.01)  # Small wait so you don't flood the bus

    t.clear()
    t.penup()        # lift pen when moving to center. 
    t.goto(0, 0)
    t.pendown()      

def lift_pen(bus):
    if t.isdown():
        t.penup()
    else:
        t.pendown()

def adjust_pen_size(bus):
    global pen_size
    delta = read_encoder_delta(bus, I2C_ADDR_PEN)
    if delta != 0:
        pen_size += delta + 10 #* 0.1  # Scale down change
        pen_size = max(PEN_MIN, min(PEN_MAX, pen_size))  # Clamp
        t.width(pen_size)       
        #print(f"Pen size adjusted to: {pen_size:.1f}")

def toggle_color(bus):
    global i
    delta = read_encoder_delta(bus, I2C_ADDR_COLOR)
    if delta != 0:
        i += delta
        t.pencolor(colors[i % len(colors)])
        #print(f"Color changed to: {colors[i % len(colors)]}")
	# yeah we call it toggle, but it is an encoder now

def move_turtle(bus):
    x = read_encoder_position(bus, I2C_ADDR_X)
    y = read_encoder_position(bus, I2C_ADDR_Y)
    #print(f"x:{x} y:{y}")
    t.goto(x * xscale, y * yscale) # maybe make a dynamic speed function, or add another encoder?

def delete(bus):
    # write in white until knob change color
    t.pencolor('white') 
    

def proc_btns(channel):
    # sure its hacky but its simple.
    if channel == 0:
        erase(bus)
        #print("btn1 presed")
    if channel == 1:
        lift_pen(bus)
        #print("btn2 presed")
    
    if channel == 2:
        delete(bus)
        #print("btn3 presed")
    '''
    if channel == 3:
        # make a save function
	save()
	sleep(3) # no spam
        print("btn4 presed")
    '''	


# Turtle screen setup
screen = turtle.Screen()
width = screen.window_width()
height = screen.window_height() 
screen.setup(width=0.5, height=0.5)  # 1,1 = Full screen 
canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.overrideredirect(1)  # Hide window borders

## performance tuning
xscale = 10
yscale = 10


# Main loop
with SMBus(I2C_BUS_NUM) as bus:
    try:
        erase(bus)  # Start fresh
        while True:
            for ch in range(3):
                val = read_adc(bus, ch)
                if val <= 10:
                    proc_btns(ch)
            move_turtle(bus)
            adjust_pen_size(bus)
            toggle_color(bus)
            sleep(0.05) # 50 ms run loop. how much bandwdith is that.?
    except KeyboardInterrupt:
        print("Exiting program.")
        sys.exit(0)

screen.mainloop()

'''
Todo: make a save()
do that performance tuning thing.
'''
