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
OUTPUT_FILE = "lego.scad"
PEN_SIZE = 3

class ViewController:
    def __init__(self):
        self.last_z_angle = None

    def write_vpr_to_file(self, z_angle):
        vpr_line = f"$vpr = [45, 0, {z_angle}];\n"

        try:
            with open(OUTPUT_FILE, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: {OUTPUT_FILE} not found.")
            return

        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith("$vpr"):
                lines[i] = vpr_line
                updated = True
                break

        if not updated:
            lines.insert(0, vpr_line)

        with open(OUTPUT_FILE, "w") as f:
            f.writelines(lines)

        print(f"Updated $vpr = [45, 0, {z_angle}] in {OUTPUT_FILE}")
        pyautogui.press("f5")
        sleep(0.2)
	
def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE])
    sleep(3)


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("Listening to Teensy on", PORT)

        view = ViewController()
        last_positions = [None, None, None, None, None]

        launch_openscad()

        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if line.startswith("X:"):
                match = re.match(
                    #r"E1:\s*(-?\d+), E2:\s*(-?\d+), E3:\s*(-?\d+), E4:\s*(-?\d+)", line)
                    #r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), E4:\s*(-?\d+)", line)
                    r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), R:\s*(-?\d+), V:\s*(-?\d+)", line)
                if match:
                    last_positions = list(map(int, match.groups()))
                    print(f"Encoders: {last_positions}")

            elif line.strip() == "E#3 pressed":
                if last_positions is not None:
                    z_angle = last_positions[4] % 360
                    view.write_vpr_to_file(z_angle)
            elif line == "E#0 pressed":
                print("view btn pressed")
            elif line == "E#1 pressed":
                print("Z btn pressed")	
            elif line == "E#2 pressed":
                print("X btn pressed")
            elif line == "E#3 pressed":
                print("Y btn pressed") 		    
            elif line == "E#4 pressed":
                print("Rotate btn pressed") 		    

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting cleanly.")
        try:
            ser.close()
        except:
            pass
