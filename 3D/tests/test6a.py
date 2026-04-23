#!/usr/bin/env python3
import os
import re
import serial
import subprocess
import time
import pyautogui
from time import sleep
'''
Include Cursor # to highlight current possition.
'''

# CONFIG
PORT = "/dev/ttyACM0"
BAUD = 115200
OUTPUT_FILE = "lego.scad"
placed_bricks = set()

X_STEP = 16
Y_STEP = 8
Z_STEP = 9.6

current_position = None
current_rotation = 0

# ---- refresh control ----
last_refresh_time = 0.0
REFRESH_INTERVAL = 0.08   # ~12 FPS
needs_refresh = False


# ---- SCAD init ----
def brick_scad():
    with open('brick.scad', 'w') as f:
        f.write('''
w = 8;
h = 9.6;

module lego_brick(studs=4){
    $fn = 40;
    width = 8 * studs;
    cube([width,16,9.6]);

    for (xpos=[4 : 8 : width-4]){
        translate([xpos,4,1.7]) cylinder(h=9.6,d=4.8);
        translate([xpos,12,1.7]) cylinder(h=9.6,d=4.8);
    }
}
''')

def lego_scad():
    with open(OUTPUT_FILE, "w") as f:
        f.write("use <brick.scad>;\n")
        f.write("$vpd = 600;\n")
        f.write("$vpr = [60,0,0];\n")


brick_scad()
lego_scad()
def update_cursor(x, y, z):
    global needs_refresh

    try:
        with open(OUTPUT_FILE, "r") as f:
            lines = f.readlines()

        new_lines = []

        # remove any existing highlighted cursor
        for line in lines:
            if line.strip().startswith("#translate"):
                continue
            new_lines.append(line)

        # add new cursor at end
        cursor_line = f"#translate([{x}, {y}, {z}]) lego_brick(2);\n"
        new_lines.append(cursor_line)

        with open(OUTPUT_FILE, "w") as f:
            f.writelines(new_lines)

    except Exception as e:
        print("Error updating cursor:", e)
        return

    print(f"[CURSOR] at ({x}, {y}, {z})")
    needs_refresh = True

def launch_openscad():
    subprocess.Popen(["openscad", OUTPUT_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sleep(2)


# ---- SCAD updates ----
def update_scad_with_brick(x, y, z):
    global needs_refresh

    brick_key = (x, y, z)
    if brick_key in placed_bricks:
        print(f"[SKIP] Brick already placed at {brick_key}")
        return

    placed_bricks.add(brick_key)

    brick_line = f"translate([{x}, {y}, {z}]) lego_brick(2);\n"

    try:
        with open(OUTPUT_FILE, "a") as f:
            f.write(brick_line)
    except Exception as e:
        print("Error writing brick:", e)
        return

    print(f"[SCAD] Added brick at {brick_key}")
    needs_refresh = True


def update_view(rotation):
    global needs_refresh

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

    print(f"[VIEW] {rotation}°")
    needs_refresh = True


def refresh_openscad():
    global last_refresh_time, needs_refresh

    now = time.time()

    if not needs_refresh:
        return

    if now - last_refresh_time < REFRESH_INTERVAL:
        return

    pyautogui.press("f5")
    last_refresh_time = now
    needs_refresh = False


# ---- MAIN LOOP ----
def main():
    global current_position, current_rotation

    try:
        launch_openscad()

        ser = serial.Serial(PORT, BAUD, timeout=1)
        sleep(2)
        ser.reset_input_buffer()

        print("Listening to Teensy on", PORT)

        last_positions = [0, 0, 0, 0, 0]

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

            if line.startswith("X:"):
                match = re.match(
                    r"X:\s*(-?\d+), Y:\s*(-?\d+), Z:\s*(-?\d+), R:\s*(-?\d+), V:\s*(-?\d+)",
                    line
                )

                if not match:
                    print("[WARN] Parse fail:", line)
                else:
                    new_positions = list(map(int, match.groups()))

                    if new_positions != last_positions:
                        x, y, z, r, v = new_positions

                        print(f"[ENCODER] X={x} Y={y} Z={z} R={r}")

                        x_real = x * X_STEP
                        y_real = y * Y_STEP
                        z_real = round(z * Z_STEP, 2)
                        update_cursor(x_real, y_real, z_real)
                        brick_key = (x_real, y_real, z_real)

                        if brick_key not in placed_bricks:
                            update_scad_with_brick(x_real, y_real, z_real)

                        if r != last_positions[3]:
                            update_view(r)

                        last_positions = new_positions
                        current_position = (x, y, z)
                        current_rotation = r

            refresh_openscad()

    except KeyboardInterrupt:
        print("\nExiting...")
        try:
            if ser and ser.is_open:
                ser.close()
        except:
            pass


if __name__ == "__main__":
    main()
