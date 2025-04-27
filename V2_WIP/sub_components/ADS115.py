#!/usr/bin/env python3
from smbus2 import SMBus
import time

# Setup
I2C_BUS = 4
I2C_ADDR = 0x48
CONFIG_REG = 0x01
CONVERSION_REG = 0x00

# MUX values for AIN0–AIN3
MUX = [0x4000, 0x5000, 0x6000, 0x7000]

# Base config:
# - OS=1 (start single conversion)
# - PGA=±4.096V
# - MODE=single-shot
# - DR=128SPS
# - Comparator disabled
BASE_CONFIG = 0x8000 | 0x0200 | 0x0100 | 0x0080 | 0x0003

def read_adc(bus, channel):
    config = BASE_CONFIG | MUX[channel]
    config_bytes = [(config >> 8) & 0xFF, config & 0xFF]
    bus.write_i2c_block_data(I2C_ADDR, CONFIG_REG, config_bytes)
    time.sleep(0.1)
    raw = bus.read_i2c_block_data(I2C_ADDR, CONVERSION_REG, 2)
    value = (raw[0] << 8) | raw[1]
    if value > 0x7FFF:
        value -= 0x10000
    return value

# Main loop
with SMBus(I2C_BUS) as bus:
    while True:
        for ch in range(4):
            val = read_adc(bus, ch)
            print(f"AIN{ch}: {val}")
        print("-" * 20)
        time.sleep(0.5)
