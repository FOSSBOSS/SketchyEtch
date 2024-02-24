#!/usr/bin/python3
import turtle
# Discount Sketchy Etch version for Lame standard keyboard hardware
# 
t = turtle.Turtle()
t.home()

i = 0   #index: current colour count

def move(key):
    x = t.xcor()
    y = t.ycor()
    screen.title(f"X: {t.xcor()}, Y: {t.ycor()}")
    if key == "Up":
        y += 1
        t.goto(x, y )

    elif key == "Down":
        y -= 1
        t.goto(x, y )

    elif key == "Left":
        x -= 1
        t.goto(x, y)

    elif key == "Right":
        x += 1
        t.goto(x, y)

    elif key == "Clear":    # c key
        t.reset()
        
    elif key == "Quit":      # q key
        exit()

#toggle though colors 
def Colour(channel):     # g key
    global i
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 0)]  # List of RGB colors
    t.pencolor(colors[i % len(colors)])  # Set pen color based on the current index of the length of the color list
    i += 1


screen = turtle.Screen()
#screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode

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

screen.listen()  # Listen for key presses

screen.mainloop()
