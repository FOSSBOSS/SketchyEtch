#!/usr/bin/env python3
import os
import re
import serial
import subprocess
from time import sleep
import pyautogui

# CONFIG
PORT = "/dev/ttyACM0"
BAUD = 115200
OUTPUT_FILE = "lego.scad"
BRICK_MODULE_FILE = "brick.scad" # the model brick
X_STEP = 16   # half of 32 mm
Y_STEP = 8     # half of 16 mm
Z_STEP = 9.6  # full height

print("You open")
# Global position tracker [x, y, z]
current_position = None
current_rotation = 0 # R value modulo 4 (i.e. 0, 1, 2, 3)
print("2")
def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE])
    sleep(2)

def update_scad_with_brick(x, y, z, rotation_deg):
    brick_line = f"rotate([0,0,{rotation_deg}]) translate([{x}, {y}, {z}]) lego_brick(4);\n"

    try:
        with open(OUTPUT_FILE, "a") as f:
            f.write(brick_line)
    except Exception as e:
        print("Error writing brick to SCAD file:", e)
        return

    print(f"Added brick at x={x} y={y} z={z} rotation={rotation_deg}")
    pyautogui.press("f5")
    sleep(0.2)

def main():
    global current_position, current_rotation
    print("You open 3")
    try:
        # Ensure SCAD file starts with module include
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                f.write(f'use <{BRICK_MODULE_FILE}>;\n')

        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("Listening to Teensy on", PORT)

        launch_openscad()
        last_positions = [0, 0, 0, 0, 0]  # X, Y, Z, R, V

        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if line:
                print("RAW:", line)  # Log all input for debugging

            if line.startswith("X:"):
                match = re.match(r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), R:\s*(-?\d+), V:\s*(-?\d+)", line)
                '''
                if match:
                    new_positions = list(map(int, match.groups()))
                    if new_positions != last_positions:
                        print(f"[ENCODER UPDATE] X={new_positions[0]} Y={new_positions[1]} Z={new_positions[2]} R={new_positions[3]} V={new_positions[4]}")
                        last_positions = new_positions
                        current_position = new_positions[0:3]
                        current_rotation = new_positions[3] % 4
                '''
                if match:
                    new_positions = list(map(int, match.groups()))
                    if new_positions != last_positions:
                        print(f"[ENCODER UPDATE] X={new_positions[0]} Y={new_positions[1]} Z={new_positions[2]} R={new_positions[3]} V={new_positions[4]}")
                        last_positions = new_positions
                        current_position = new_positions[0:3]
                        current_rotation = new_positions[3] % 4
                
                else:
                    print("[WARN] Failed to parse encoder line:", line)

            elif line == "E#0 pressed":
                print("[BUTTON] E#0 (View) pressed")
            elif line == "E#1 pressed":
                print("[BUTTON] E#1 (Z) pressed")
            elif line == "E#2 pressed":
                print("[BUTTON] E#2 (X) pressed")
            elif line == "E#3 pressed":
                if current_position is None:
                    print("[SKIP] No position data yet — ignoring button press")
                    continue
                print("[BUTTON] E#3 (Y / PLACE) pressed → Drawing brick")
                #x, y, z = current_position
                #angle = current_rotation * 90
                #update_scad_with_brick(x, y, z, angle)
               # Half-brick step increments
                X_STEP_MM = 16   # Half of 4-stud width (32 mm)
                Y_STEP_MM = 8    # Half of brick depth (16 mm)
                Z_STEP_MM = 9.6  # Full height

                x_real = current_position[0] * X_STEP
                y_real = current_position[1] * Y_STEP
                z_real = current_position[2] * Z_STEP
                angle = current_rotation * 90

                print(f"[DRAW] Brick @ X:{x_real} Y:{y_real} Z:{z_real} Angle:{angle}")
                update_scad_with_brick(x_real, y_real, z_real, angle)

            elif line == "E#4 pressed":
                print("[BUTTON] E#4 (Rotate) pressed")


    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        try:
            ser.close()
        except:
            ser.close()
            pass
if __name__ == "__main__":
    main()
