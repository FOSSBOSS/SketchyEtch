Sketch-Y-Etch is a retrospective etch-a-sketch-esque drawing expirience with a modern twist.
The project is housed in a 43 inch TV, with the addition of 2 rotary encoders, 4 buttons and 1 switch.
Use the switch to enter demo mode, where your propaganda can be displayed. 
Button features include: Save, penup / pendown, colour change, and erase.
Rotary encoders are used to perform XY cordinate based drawing. 

Built on a Raspberry Pi 3B+ using a Teensy 4.1 to gernated keyboard IO. 

Here are some documentation resources I found helpful:
Turtle Graphics API: <br>
https://docs.python.org/3/library/turtle.html

How to Autostart Programs in Raspberry Pi OS:

https://www.instructables.com/Autostart-a-Program-When-Raspberry-Pi-Boots-Newbie/

To simply have the program run on boot (on a Pi):

sudo apt install lxsession-default-apps

Unclutter was used to hide the mouse. 

This project should work on any OS, using a keyboard, or sensor IO.
Only tested on linux though. Good Luck!
