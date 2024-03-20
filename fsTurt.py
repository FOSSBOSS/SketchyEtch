#!/usr/bin/python3
import turtle
import os
import time
# Discount Sketch-Y-Etch version for standard keyboard hardware
# OK turns out Im super frustrated with raw_turtle  and GPIO latency.
# using a teensy for IO, and processing the keypresses.

t = turtle.Turtle()
t.home()
t.shape('circle')
t.shapesize(0.5)  # Cursor size: 0.5 is half of normal
t.width(10)

i = 0   #index: current colour count

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

def saveSVG(channel):    # s key
    # utilizing geg
    # Get the current Unix time
    current_time = int(time.time())
    t.hideturtle()
    canvas_data = turtle.getcanvas().postscript()
    # Construct the file name with the current time and the .ps extension
    ps_file_name = f"{current_time}.ps"
    svg_file_name = f"{current_time}.svg"
    File_path = '/home/e/img'
    output_path = os.path.join(File_path, svg_file_name)
    with open(ps_file_name, 'w') as f:
        f.write(canvas_data)
    # Show the turtle again
    t.showturtle()
    os.system('eps2svg ' + ps_file_name + ' ' + output_path)
    os.system('rm ' + ps_file_name)

#def demo(channel):

screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode

canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.overrideredirect(1)

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
#screen.onkeypress(lambda: demo("demo"), "d")

screen.listen()  # Listen for key presses

screen.mainloop()
