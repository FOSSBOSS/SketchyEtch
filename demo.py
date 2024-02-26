 #!/usr/bin/python3
import turtle 
import time
import math
# There is a chance all of this has to be in raw mode on the pi
#Demo functions for sketch-y-etch

t = turtle.Turtle()
t.hideturtle()
t.speed(0.5)
t.width(4)
t.color("blue")

# Set up the turtle screen
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # Set the window to full-screen mode

####General Use Function#####
def blank():
    t.goto(0,0)
    t.clear()
    t.hideturtle()


#######Function drawings#####
def draw_Flower():
	#inverted Arguelle's mandala
    RAD = 200
    radii = [RAD, RAD/1.25, RAD/1.5, RAD/1.75, RAD/2, RAD/2.25, RAD/3, RAD/4]

    def derp():
        t.pendown()
        for r in radii:
            t.circle(r, 360)
        t.penup()

    derp()
    t.left(-90) 
    derp()
    t.goto(0,0)
    t.left(-180) 
    derp()
    t.goto(0,0)
    t.left(-270) 
    derp()
    
def mandala():
## http://programming1work.oyosite.com/ch_turtle-mandala.html
    t.pendown()
    for times in range(36):
        t.color("blue")
        t.speed(11)
        t.circle(100)
        t.color("red")
        t.forward(200)
        t.left(120)
        t.color("orange")
        t.forward(100)
        t.right(120)
        t.left(170)
        t.left(20)
        t.forward(15)
        
            
def arguelles():
    RAD = 200
    radii = [RAD, RAD/1.25, RAD/1.5, RAD/1.75, RAD/2, RAD/2.25, RAD/3, RAD/4]

    def derp():
        t.pendown()
        for r in radii:
            t.circle(r, 360)
        t.penup()

    derp()
    t.goto(RAD,RAD)
    t.left(90) 
    derp()
    t.goto(0,0)
    t.goto(-RAD,RAD)
    t.left(180) 
    derp()
    t.goto(0,0)
    t.goto(0,RAD*2)
    t.left(270) 
    derp()
    
#Demo mode function for dumping source code clone to the turtle window
def dumpSRC():
    def draw_text_line(t, text, y):
        t.penup()
        t.goto(-500, y)  # Start position for the text
        t.pendown()
        t.write(text, font=("Arial", 24, "normal"))  # Write the text
    
    with open("source.txt", "r") as file:
        y = 350  # Starting y-coordinate for the first line of text
        for line in file:
            draw_text_line(t, line.strip(), y)
            y -= 34  # Move down for the next line

        # Check if the next line will exceed the window height
            if y < -350:
                time.sleep(2)
            # Clear the screen & resume writing
                t.clear()
            # Reset the start position
                y = 350
    draw_text_line(t, "Source Code Dump Successful", y)

# Draw a yin yang symbol
def taiju():
    t.penup()
    RAD = 200
    RAD2 = RAD / 2
    RAD6 = RAD / 6
    t.hideturtle()
    t.degrees() # Switch to degrees
    t.goto(0,-RAD)
    t.pendown()
# Draw the circle, radius 100, half black
    t.fillcolor('black')
    t.begin_fill()
    t.circle(RAD, 180)
    t.end_fill()
    t.circle(RAD, 180)

# Draw black head
    t.left(180)
    t.penup()
    t.goto(0, RAD)
    t.pendown()
    t.begin_fill()
    t.circle(RAD2, 180)
    t.end_fill()

# Draw white head
    t.penup()
    t.goto(0, -RAD)
    t.pendown()
    t.fillcolor('white')
    t.begin_fill()
    t.circle(RAD2, 180)
    t.end_fill()

# Draw eyes
    t.penup()
    t.goto(0, RAD2 + RAD6)
    t.begin_fill()
    t.circle(RAD6)
    t.end_fill()

    t.fillcolor('black')
    #t.goto(0, 2 * (RAD - RAD6))
    t.goto(0, 2 * (-RAD6))
    t.begin_fill()
    t.circle(RAD6)
    t.end_fill()    
            
def gear1(teeth, tdepth, twidth, RAD):
    # Setup Turtle
    t.home()
    t.speed(0)
    t.hideturtle()
    #print(t.pos())

    # Calculate the angle for each tooth
    angle = 360 / teeth

    # Draw one gear fragment for the number of teeth
    for _ in range(teeth):

        t.forward(twidth)        
        t.left(90)                        
        t.forward(tdepth)       
        t.right(90)                      
        t.circle(RAD,angle)     
        t.right(90)                      
        t.forward(tdepth)       
        t.left(90)                        

    # Inner circle 
    t.penup()
    t.goto(0,0)
    #t.goto(twidth/2, (tdepth + RAD) /math.pi) 
    t.goto(twidth/2, tdepth*2) 
    t.pendown()
    t.circle(RAD, 360)

# Draw a pine tree

####END FUNCTIONS######


"""
Functions:
draw_Flower()
mandala()
arguelles()
dumpSRC()
taiju()
gear1
"""  
    
   
