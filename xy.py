#!/usr/bin/python3
import RPi.GPIO as GPIO
import turtle
from svg_turtle import SvgTurtle
import time
import os

"""
 Possible improvements: 
 figure out wtf is wrong with svg_turtle lib to eliminate extra file writes
 Write classes to elimate global vars
 Consider using a dictionary instead of a list for color tuples
  
 Fixed svg_turtle issue by:
 $sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
 

"""
# Encoder positions
oldX = 0
oldY = 0
x_coord = 0
y_coord = 0
penState = False  # False for pen down, True for pen up
i = 0             # index of current color

# GPIO pins for the encoders
encoder2_pins = (23, 24)  # A and B pins for encoder 2 (y-axis)
encoder1_pins = (15, 14)  # A and B pins for encoder 1 (x-axis)

# Setup GPIO
clearBtn = 12
liftBtn = 16
saveSvgBtn = 21
ColorBtn = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(clearBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(liftBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(saveSvgBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ColorBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder1_pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder1_pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder2_pins[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder2_pins[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables to store encoder state
encoder1_last_state = (GPIO.input(encoder1_pins[0]) << 1) | GPIO.input(encoder1_pins[1])
encoder2_last_state = (GPIO.input(encoder2_pins[0]) << 1) | GPIO.input(encoder2_pins[1])

# Create a turtle object 
#t = turtle.Turtle()

# Set up the turtle screen
screen = turtle.Screen()
#screen.title(f"X: {x_coord}, Y: {y_coord}") #this is in the update function now

screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode
canvas = screen.getcanvas()

# Create a RawTurtle object with the canvas
raw_turtle = turtle.RawTurtle(canvas)
raw_turtle.shape('circle')
raw_turtle.shapesize(0.5)  # Cursor size: 0.5 is half of normal
raw_turtle.width(6)
raw_turtle.speed(0)

root = canvas.winfo_toplevel()
root.overrideredirect(1)
##BUTTONS
    

#toggle though colors 
def Change_Color(channel):
    global i
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 0)]  # List of RGB colors
    raw_turtle.pencolor(colors[i % len(colors)])  # Set pen color based on the current index of the length of the color list
    i += 1

# Define a callback function to run when the button is pressed
def ClearScrnBtn(channel):
    global x_coord, y_coord
    #print("Clear Screen")
    raw_turtle.reset()  # Reset the turtle, resets everything including point size
    raw_turtle.shapesize(0.5)  # Cursor size: 0.5 is half of normal
    raw_turtle.width(6)
    x_coord = 0  # Reset the x coordinate to 0
    y_coord = 0  # Reset the y coordinate to 0

# Callback function to lift or lower the pen
def lift_pen(channel):
    global penState
    penState = not penState
    if penState:
        raw_turtle.penup()
    else:
        raw_turtle.pendown()

def saveSVG(channel):
    # Get the current Unix time
    current_time = int(time.time())
    #print(current_time)
    raw_turtle.hideturtle()
    canvas_data = turtle.getcanvas().postscript()
    # Construct the file name with the current time and the .ps extension
    ps_file_name = f"{current_time}.ps"
    svg_file_name = f"{current_time}.svg"
    #print(ps_file_name)
    #print(svg_file_name)
    with open(ps_file_name, 'w') as f:
        f.write(canvas_data)
    # Show the turtle again
    raw_turtle.showturtle()
    os.system('eps2svg ' + ps_file_name + ' ' + svg_file_name)
    os.system('rm ' + ps_file_name)

# Callback function for encoder 1 (x-axis)
def encoder1_callback(channel):
    global encoder1_last_state, x_coord
    a = GPIO.input(encoder1_pins[0])
    b = GPIO.input(encoder1_pins[1])
    new_state = (a << 1) | b
    if (encoder1_last_state == 0b00 and new_state == 0b10) or (encoder1_last_state == 0b11 and new_state == 0b01):
        x_coord += 1
    elif (encoder1_last_state == 0b10 and new_state == 0b00) or (encoder1_last_state == 0b01 and new_state == 0b11):
        x_coord -= 1
    encoder1_last_state = new_state

# Callback function for encoder 2 (y-axis)
def encoder2_callback(channel):
    global encoder2_last_state, y_coord
    a = GPIO.input(encoder2_pins[0])
    b = GPIO.input(encoder2_pins[1])
    new_state = (a << 1) | b
    if (encoder2_last_state == 0b00 and new_state == 0b10) or (encoder2_last_state == 0b11 and new_state == 0b01):
        y_coord -= 1
    elif (encoder2_last_state == 0b10 and new_state == 0b00) or (encoder2_last_state == 0b01 and new_state == 0b11):
        y_coord += 1
    encoder2_last_state = new_state

# Add event detection for encoder 1 (x-axis)
GPIO.add_event_detect(encoder1_pins[0], GPIO.BOTH, callback=encoder1_callback)
GPIO.add_event_detect(encoder1_pins[1], GPIO.BOTH, callback=encoder1_callback)

# Add event detection for encoder 2 (y-axis)
GPIO.add_event_detect(encoder2_pins[0], GPIO.BOTH, callback=encoder2_callback)
GPIO.add_event_detect(encoder2_pins[1], GPIO.BOTH, callback=encoder2_callback)

# Add event listener to the button pins
GPIO.add_event_detect(clearBtn, GPIO.FALLING, callback=ClearScrnBtn, bouncetime=300)
GPIO.add_event_detect(liftBtn, GPIO.FALLING, callback=lift_pen, bouncetime=300)
GPIO.add_event_detect(saveSvgBtn, GPIO.FALLING, callback=saveSVG, bouncetime=300)
GPIO.add_event_detect(ColorBtn, GPIO.FALLING, callback=Change_Color, bouncetime=300)


# Function to update the turtle's position based on encoder callbacks
def update_position():
    global x_coord, y_coord, oldX, oldY
    if (x_coord != oldX or y_coord != oldY):
        #print(f"X: {x_coord}, Y: {y_coord}")
        screen.title(f"X: {x_coord}, Y: {y_coord}")
        raw_turtle.goto(x_coord, y_coord)
    oldX = x_coord
    oldY = y_coord
    screen.ontimer(update_position, 10)  # Schedule the next update

# Start updating the position
update_position()
# Start the turtle main loop
turtle.mainloop()

# Clean up GPIO on keyboard interrupt
GPIO.cleanup()
turtle.done()   #not mentioned in turtle documentation for raw


