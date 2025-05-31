#!/usr/bin/env python3
import os
import re
import serial
import subprocess
from time import sleep
import pyautogui
# you dont need theta if youre drawing a cube
#
# Todo: Coalencense? make xyz blocks append when 2 of the 3 arent changing.
#
# CONFIG
PORT = "/dev/ttyACM0"
BAUD = 115200
OUTPUT_FILE = "lego.scad"
BRICK_MODULE_FILE = "brick.scad" # the model brick
placed_bricks = set()


X_STEP = 16   # half of 32 mm
Y_STEP = 8     # half of 16 mm
Z_STEP = 9.6  # full height

# Global position tracker [x, y, z]
current_position = None
#current_rotation = 0 # R value modulo 4 (i.e. 0, 1, 2, 3)
def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE])
    sleep(2)

#def update_scad_with_brick(x, y, z, rotation_deg):
def update_scad_with_brick(x, y, z):
    #brick_key = (x, y, z, rotation_deg)
    brick_key = (x, y, z)
    if brick_key in placed_bricks:
        print(f"[SKIP] Brick already placed at {brick_key}")
        return

    placed_bricks.add(brick_key)
    #brick_line = f"rotate([0,0,{rotation_deg}]) translate([{x}, {y}, {z}]) lego_brick(4);\n"
    brick_line = f"translate([{x}, {y}, {z}]) lego_brick(2);\n"
    try:
        with open(OUTPUT_FILE, "a") as f:
            f.write(brick_line)
    except Exception as e:
        print("Error writing brick to SCAD file:", e)
        return

    print(f"[SCAD] Added brick at {brick_key}")
    pyautogui.press("f5")
    sleep(0.2)


def main():
    global current_position, current_rotation

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
                #r"X:\s*(-?\d+),\s*Y:\s*(-?\d+),\s*Z:\s*(-?\d+),\s*R:\s*(-?\d+),\s*V:\s*(-?\d+)" 


                if match:
                    new_positions = list(map(int, match.groups()))
                    if new_positions != last_positions:
                        print(f"[ENCODER UPDATE] X={new_positions[0]} Y={new_positions[1]} Z={new_positions[2]} R={new_positions[3]} V={new_positions[4]}")
                        # Compute real-world position
                        x_real = new_positions[0] * X_STEP
                        y_real = new_positions[1] * Y_STEP
                        z_real = new_positions[2] * Z_STEP
                        brick_key = (x_real, y_real, z_real)

                        if brick_key not in placed_bricks:
                            print(f"[AUTO-DRAW] Placing brick at {brick_key}")
                            update_scad_with_brick(x_real, y_real, z_real)
                        else:
                            print(f"[SKIP] Brick already placed at {brick_key}")

                        last_positions = new_positions
                        current_position = new_positions[0:3]
                
                else:
                    print("[WARN] Failed to parse encoder line:", line)


    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        try:
            if ser and ser.is_open:
                ser.close()
                print("[INFO] Serial port closed.")
        except Exception as e:
            print(f"[WARN] Error closing serial port: {e}")
if __name__ == "__main__":
    main()
