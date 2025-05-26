#!/usr/bin/env python3

import pyautogui
import re
import serial
import subprocess
from time import sleep

# CONFIGURATION
PORT = "/dev/ttyACM0"  # Adjust this to match your Teensy serial port
BAUD = 115200
OUTPUT_FILE = "box.scad"  # SCAD file you want to modify

# Disable mouse failsafe
pyautogui.FAILSAFE = False

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
        last_positions = [None, None, None, None]

        launch_openscad()

        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if line.startswith("X:"):
                match = re.match(
                    #r"E1:\s*(-?\d+), E2:\s*(-?\d+), E3:\s*(-?\d+), E4:\s*(-?\d+)", line)
                    r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), E4:\s*(-?\d+)", line)
                if match:
                    last_positions = list(map(int, match.groups()))
                    print(f"Encoders: {last_positions}")

            elif line.strip() == "E#3 pressed":
                if last_positions is not None:
                    z_angle = last_positions[3] % 360
                    view.write_vpr_to_file(z_angle)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting cleanly.")
        try:
            ser.close()
        except:
            pass


if __name__ == "__main__":
    main()
