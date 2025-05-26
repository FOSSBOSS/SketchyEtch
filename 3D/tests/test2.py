#!/usr/bin/env python3

import math
import pyautogui
pyautogui.FAILSAFE = False # stop 0,0 safety feature
import re
import serial
from solid import *
from solid.utils import *
import subprocess
from time import sleep

# CONFIG
OUTPUT_FILE = "turtle3d.scad"
PORT = "/dev/ttyACM0"   
BAUD = 115200

'''
VPD is a read only constant, distance from a point of interest, 0,0,0 by defualt, while VPR changes. 
VPR .. turns out I like 45,0.,
'''
# List of predefined $vpr values
view_angles = [
    [0, 0, 0],
    [45, 0, 0],
    [0, 45, 0],
    [0, 0, 45],
    [45, 45, 0],
    [0, 45, 45],
    [45, 0, 45],
    [45, 45, 45],
    [-45, 0, 0],
    [0, -45, 0],
    [0, 0, -45],
    [-45, 45, 0],
    [0, 45, -45],
    [45, 0, -45],
    [-45, -45, 45],
    [90, 0, 0]
]; #33

class Turtle3D:
    def __init__(self):
        self.view_angle = 0  # New attribute
        self.current_vpr = [0,0,0]
        self.position = [0.0, 0.0, 0.0]
        self.heading = [1.0, 0.0, 0.0]  # Initial heading in +X direction
        self.lines = []

    def set_view_angle(self, index):
        if 0 <= index < len(view_angles):
            self.current_vpr = view_angles[index]
            self._save_and_refresh()
        else:
            self.current_vpr = [0, 0, 0]  # fallback

	
    def _unit_vector(self, vec):
        length = math.sqrt(sum([v ** 2 for v in vec]))
        return [v / length for v in vec]

    def forward(self, distance):
        dir = self._unit_vector(self.heading)
        new_pos = [
            self.position[0] + dir[0] * distance,
            self.position[1] + dir[1] * distance,
            self.position[2] + dir[2] * distance,
        ]
        self.add_line(self.position, new_pos)
        self.position = new_pos

    def turn(self, axis, degrees):
        # Rotate heading vector around axis
        rad = math.radians(degrees)
        x, y, z = self.heading
        if axis == 'z':
            self.view_angle += degrees
            x2 = x * math.cos(rad) - y * math.sin(rad)
            y2 = x * math.sin(rad) + y * math.cos(rad)
            self.heading = [x2, y2, z]
        elif axis == 'y':
            x2 = x * math.cos(rad) + z * math.sin(rad)
            z2 = -x * math.sin(rad) + z * math.cos(rad)
            self.heading = [x2, y, z2]
        elif axis == 'x':
            y2 = y * math.cos(rad) - z * math.sin(rad)
            z2 = y * math.sin(rad) + z * math.cos(rad)
            self.heading = [x, y2, z2]

    def add_line(self, p1, p2):
        line = self._cylinder_between(p1, p2)
        self.lines.append(line)
        self._save_and_refresh()

    def _cylinder_between(self, p1, p2, r=0.5):
        # Create cylinder from p1 to p2
        dx, dy, dz = [b - a for a, b in zip(p1, p2)]
        length = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        if length == 0:
            return []

        # Rotation
        axis = [dx, dy, dz]
        axis = self._unit_vector(axis)
        a, b, c = axis

        return translate(p1)(
            rotate(a=[math.degrees(math.atan2(dy, dx)), 0, 0])(
                rotate(a=90, v=[0, 1, 0])(
                    cylinder(h=length, r=r)
                )
            )
        )

    def _save_and_refresh(self):
        scad_code = scad_render(union()(self.lines))
        vpr_line = f"$vpr = [{self.current_vpr[0]}, {self.current_vpr[1]}, {self.current_vpr[2]}];\n"
	#vpr_line = f"$vpr = [0, 0, {self.view_angle:.2f}];\n"
        with open(OUTPUT_FILE, "w") as f:
            f.write(vpr_line + scad_code)
        pyautogui.press("f5")
        sleep(1)




def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE])
    sleep(3)  # Wait for OpenSCAD to load

if __name__ == "__main__":
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("Listening to Teensy on", PORT)

    last_positions = [None, None, None, None]
    pending_update_angle = None    
    t = Turtle3D()
    #self.current_vpr = [0, 0, 0]
    launch_openscad()

    t.forward(10)
    t.turn('z', 144)
    t.forward(10)
    t.turn('z', 144)
    sleep(1)
    t.forward(10)
    t.turn('x', 144)
    t.forward(10)
    t.turn('y', 144)
    t.forward(10)
    '''
    for i in range(1,33):
        t.set_view_angle(i)
        sleep(1)
    '''
    while True:
        line = ser.readline().decode(errors="ignore").strip()

        if line.startswith("X:"):
            match = re.match(
                r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), E4:\s*(-?\d+)", line)
            if match:
                positions = list(map(int, match.groups()))
                if positions != last_positions:
                    print(f"Encoders: {positions}")
                    last_positions = positions
                    pending_update_angle = positions[3]

        elif line.strip() == "E#3 pressed":
            if pending_update_angle is not None:
                print(f"Applying view angle Z = {pending_update_angle}")
                #update_openscad_vpr(pending_update_angle)
                t.set_view_angle(pending_update_angle)
