#!/usr/bin/env python3
from smbus2 import SMBus, i2c_msg
import time
# FFFFFFFFFFFFFFFFFFFFFFFFFFffff encode bus timing. 
'''
ok the adruin libs use gpio, which is a hack for the complex issue of bus monitoring the registers.
becuase the 16 bit field goes low, but then the low value shifts through the registers.
you can watch it happen with 
sudo i2cdump -y 1 0x36

'''
I2C_BUS_NUM = 1
I2C_ADDR = 0x36

SEESAW_ENCODER_BASE = 0x11
SEESAW_ENCODER_STATUS = 0x00

def read_encoder_status(bus, addr):
    try:
        write = i2c_msg.write(addr, [SEESAW_ENCODER_BASE, SEESAW_ENCODER_STATUS])
        read = i2c_msg.read(addr, 1)
        bus.i2c_rdwr(write, read)
        data = list(read)[0]
        return data
    except Exception as e:
        print(f"I2C communication error: {e}")
        return 0

def main():
    print("Monitoring encoder button for changes...")
    last_pressed = False  # Last known button state

    with SMBus(I2C_BUS_NUM) as bus:
        try:
            while True:
                status = read_encoder_status(bus, I2C_ADDR)

                pressed_now = bool(status & (1 << 2))  # Bit 2 = pressed
                released_now = bool(status & (1 << 3))  # Bit 3 = released

                if pressed_now and not last_pressed:
                    print("Button pressed!")
                    last_pressed = True

                if released_now and last_pressed:
                    print("Button released!")
                    last_pressed = False

                time.sleep(0.01)  # 10ms cycle is smooth
        except KeyboardInterrupt:
            print("\nExiting button monitor.")

if __name__ == "__main__":
    main()
