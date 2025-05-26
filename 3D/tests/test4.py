#!/usr/bin/env python3

import re
import serial
from time import sleep
from solid import *
from solid.utils import *
import os

# CONFIGURE THESE
PORT = "/dev/ttyACM0"
BAUD = 115200
OUTPUT_FILE = "pen.scad"
PEN_SIZE = 3

class Turtle3D:
    def __init__(self):
        self.position = [0, 0, 0]

    def update_position(self, x, y, z):
        self.position = [x, y, z]

    def scad_model(self):
        return translate(self.position)(
            cube([PEN_SIZE] * 3, center=True)
        )

    def write_to_file(self, filename=OUTPUT_FILE):
        scad_render_to_file(self.scad_model(), filename, file_header='$fn=50;')
        print(f"SCAD updated: {filename}")

def launch_openscad(filepath):
    # Launch OpenSCAD preview (optional)
    if not os.fork():
        os.execvp("openscad", ["openscad", filepath])
        exit(0)

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("Listening to Teensy on", PORT)

        view = Turtle3D()
        last_position = None

        launch_openscad(OUTPUT_FILE)
        sleep(1)  # Give OpenSCAD time to start

        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if line.startswith("X:"):
                match = re.match(r"X:(-?\d+),\s*Y:(-?\d+),\s*Z:(-?\d+),\s*E4:(-?\d+)", line)
                if match:
                    last_positions = list(map(int, match.groups()))
                    print(f"Encoders: {last_positions}")
                    x, y, z, _ = map(int, match.groups())
                    new_pos = [x, y, z]

                    if new_pos != last_position:
                        last_position = new_pos
                        view.update_position(*new_pos)
                        view.write_to_file()

            elif line == "E#3 pressed":
                print("view btn pressed")
            elif line == "E#2 pressed":
                print("Z btn pressed")	
            elif line == "E#1 pressed":
                print("X btn pressed")
            elif line == "E#0 pressed":
                print("Y btn pressed") 
		 


    except KeyboardInterrupt:
        try:
            ser.close()
            print("\nInterrupted by user. Exiting cleanly.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")

if __name__ == "__main__":
    main()
