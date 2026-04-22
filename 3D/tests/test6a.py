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
placed_bricks = set()


X_STEP = 16   # half of 32 mm
Y_STEP = 8     # half of 16 mm
Z_STEP = 9.6  # full height

# Global position tracker [x, y, z]
current_position = None
current_rotation = 0 # R value modulo 4 (i.e. 0, 1, 2, 3)

# Rather than including brick.scad, lets just write it.
def brick_scad():
    with open('b.scad', 'w') as f:
        f.write('// brick.scad\nw = 8; \n h = 9.6; \n module lego_brick(studs=4){ \n $fn = 80; \n width = 8 * studs; \n cube([width,16,9.6]); \n for (xpos=[4 : 8 : width-4]){ \n translate([xpos,4,1.7]) cylinder(h=9.6,d=4.8); \n translate([xpos,12,1.7]) cylinder(h=9.6,d=4.8); \n } \n } \n') 


# this addresses an issue in open scad around load large files, by ensuring the output file is always blank
# OMG here is my errase function
def lego_scad():
    with open(OUTPUT_FILE, "w") as f:
        f.write("use <brick.scad>;\n")
        f.write("$vpd = 600;\n")
        f.write("$vpr = [60,0,0];\n")
brick_scad()
lego_scad()

def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE])
    #subprocess.Popen(["openscad", OUTPUT_FILE])
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

def update_view(rotation):
    try:
        with open(OUTPUT_FILE, "r") as f:
            lines = f.readlines()

        found_vpr = False

        with open(OUTPUT_FILE, "w") as f:
            for line in lines:
                if line.strip().startswith("$vpr"):
                    f.write(f"$vpr = [60,0,{rotation}];\n")
                    found_vpr = True
                else:
                    f.write(line)

            if not found_vpr:
                f.write(f"$vpr = [60,0,{rotation}];\n")

    except Exception as e:
        print("Error updating view:", e)
        return

    print(f"[VIEW] Set to [60,0,{rotation}]")


def main():
    global current_position, current_rotation

    try:
        # Ensure SCAD file exists and initialized
        if not os.path.exists(OUTPUT_FILE):
            lego_scad()

        launch_openscad()
        sleep(2)

        ser = serial.Serial(PORT, BAUD, timeout=1)
        sleep(2)
        ser.reset_input_buffer()

        print("Listening to Teensy on", PORT)

        last_positions = [0, 0, 0, 0, 0]  # X, Y, Z, R, V

        while True:
            try:
                line = ser.readline().decode(errors="ignore").strip()
            except serial.serialutil.SerialException as e:
                print(f"[SERIAL ERROR] {e}")
                sleep(1)
                ser = serial.Serial(PORT, BAUD, timeout=1)
                sleep(2)
                ser.reset_input_buffer()
                print("[SERIAL] Reconnected")
                continue

            if line:
                print("RAW:", line)

            if not line.startswith("X:"):
                continue

            match = re.match(
                r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), R:\s*(-?\d+), V:\s*(-?\d+)",
                line
            )

            if not match:
                print("[WARN] Failed to parse encoder line:", line)
                continue

            new_positions = list(map(int, match.groups()))

            if new_positions == last_positions:
                continue  # no change, skip everything

            x, y, z, r, v = new_positions

            print(f"[ENCODER UPDATE] X={x} Y={y} Z={z} R={r} V={v}")

            # ---- Position → real world ----
            x_real = x * X_STEP
            y_real = y * Y_STEP
            z_real = round(z * Z_STEP, 2)  # prevent float drift

            brick_key = (x_real, y_real, z_real)

            # ---- Brick placement ----
            if brick_key not in placed_bricks:
                print(f"[AUTO-DRAW] Placing brick at {brick_key}")
                update_scad_with_brick(x_real, y_real, z_real)
            else:
                print(f"[SKIP] Brick already placed at {brick_key}")

            # ---- View rotation (1 tick = 1 degree) ----
            if r != last_positions[3]:
                angle = r
                update_view(angle)

            # ---- Update state ----
            last_positions = new_positions
            current_position = (x, y, z)
            current_rotation = r

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        try:
            if ser and ser.is_open:
                ser.close()
                print("[INFO] Serial port closed.")
        except Exception as e:
            print(f"[WARN] Error closing serial port: {e}")
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
'''
Ok this is a fully functional 3D drawing program, but its still buggy, 
the IO is a teensy 4.0, with 4 rotary encoders, the IO can easily overload 
both the i2C bus it is on, and the program Openscad, which it uses to draw the 3D 
models. 
 
Need to make improvements, but it do work. ... provided I don't alter the functions of
the serial commands the MCU provides. a fresh build of open scad can help
performance, by adjusting the rendering properties to manifold, and by increasing the 
number of objects / RAM openscad uses to process objects.
 
There is also a bug in openscad, where manifold only re-renders objects, 
this means, dont load large files initially, but reloading them is fine. 
Still waiting for gooners at openscad to fix the issue.
'''
