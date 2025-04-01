#!/usr/bin/env python3
# Run in your venv. if you cant find it use vnv
import turtle
import os
from smbus2 import SMBus, i2c_msg
import struct
from time import sleep
import sys
#import demo
# Discount Sketch-Y-Etch version for standard keyboard hardware
# using a teensy for IO, and processing the keypresses.

t = turtle.Turtle()
t.home()
t.shape('circle')
t.shapesize(0.5)  # Cursor size: 0.5 is half of normal
t.width(10)

i = 0   #index: current colour count
BYTES = 4
I2C_BUS = 4        # Change if needed
I2C_ADDR = 0x36
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
'''
def move(key):
    x = t.xcor()
    y = t.ycor()
    screen.title(f"X: {t.xcor()}, Y: {t.ycor()}")
    if key == "Up":
        y += 10
        t.goto(x, y )

    elif key == "Down":
        y -= 10
        t.goto(x, y )

    elif key == "Left":
        x -= 10
        t.goto(x, y)

    elif key == "Right":
        x += 10
        t.goto(x, y)

    elif key == "Clear":    # c key
        t.reset()
        t.shape('circle')
        t.shapesize(0.5)  # Cursor size: 0.5 is half of normal
        t.width(10)
        
    elif key == "Quit":      # q key
        exit()
'''
#toggle though colors 
def Colour(channel):     # g key
    global i
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 0)]  # List of RGB colors
    t.pencolor(colors[i % len(colors)])  # Set pen color based on the current index of the length of the color list
    i += 1

def lift_pen(channel):   # l key
    if t.isdown():
        t.penup()
    else:
        t.pendown()
'''
def saveSVG(channel):    # s key
    # utilizing geg
    # Get the current Unix time
    current_time = int(time.time())
    t.hideturtle()
    canvas_data = turtle.getcanvas().postscript()
    # Construct the file name with the current time and the .ps extension
    ps_file_name = f"{current_time}.ps"
    svg_file_name = f"{current_time}.svg"
    File_path = '/home/m/Desktop/git/SketchyEtch'
    output_path = os.path.join(File_path, svg_file_name)
    with open(ps_file_name, 'w') as f:
        f.write(canvas_data)
    # Show the turtle again
    t.showturtle()
    os.system('eps2svg ' + ps_file_name + ' ' + output_path)
    os.system('rm ' + ps_file_name)
'''
'''
# Demo mode switch
def demoMode(channel):
    t.hideturtle()
    demo.dumpSRC()
    time.sleep(2)
    demo.blank()
    demo.draw_Flower()
    time.sleep(3)
    demo.blank()
    demo.arguelles()
    time.sleep(3)
    demo.blank()
    demo.mandala()
    time.sleep(3)
    demo.blank()
    demo.taiju() 
    time.sleep(3)
    demo.blank()
    t.showturtle()   
'''        
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode

canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.overrideredirect(1)
'''
# Bind arrow key presses to the move function
screen.onkeypress(lambda: move("Up"), "Up")
screen.onkeypress(lambda: move("Down"), "Down")
screen.onkeypress(lambda: move("Left"), "Left")
screen.onkeypress(lambda: move("Right"), "Right")
screen.onkeypress(lambda: move("Clear"), "c")
screen.onkeypress(lambda: move("Quit"), "q")
screen.onkeypress(lambda: Colour("Color"), "g")
screen.onkeypress(lambda: lift_pen("lift"), "l")
screen.onkeypress(lambda: saveSVG("save"), "s")
screen.onkeypress(lambda: demoMode("demo"), "d")
'''
screen.listen()  # Listen for key presses

screen.mainloop()
