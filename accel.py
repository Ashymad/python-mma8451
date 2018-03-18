#!/usr/bin/env python3
# See 'LICENSE'  for copying

import smbus
import time
from scipy.constants import g
import RPi.GPIO as GPIO
from register import register as REG

device_name = 0x1A
iic_addr    = 0x1D

def int1_callback(channel):
    print("Interrupt detected")
    bus = smbus.SMBus(1)
    status = bus.read_byte_data(i2caddr, REG)
    print("F_OVF: " + str((status & FLAG_F_OVF) != 0))
    print("F_WMRK_FLAG: " + str((status & FLAG_F_WMRK_FLAG) != 0))
    print("F_CNT: " + str(status & ~0xc0))

class Accel():

    def __init__(self):

        if GPIO.RPI_INFO['P1_REVISION'] == 1:
            myBus = 0
        else:
            myBus = 1

        self.bus = smbus.SMBus(myBus)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self.addr = i2caddr


    def writeRegister(self, regNumber, regData):
        self.bus.write_byte_data(self.addr, regNumber, regData)

    def readRegister(self, regNumber):
        return self.bus.read_byte_data(self.addr, regNumber)

    def block_read(self, offset, length):
        return self.bus.read_i2c_block_data(self.addr, offset, length)

    def set_flag(self, flag):
        self.writeRegister(flag.addr, self.readRegister(flag.addr) | flag)

    def unset_flag(self, flag):
        self.writeRegister(flag.addr, self.readRegister(flag.addr) & ~flag)

    def read_flag(self, flag):
        return (self.readRegister(flag.addr) & flag) != 0

    def init_callback(self):
        # Reset
        self.set_flag(REG.CTRL_REG2.RST)
        # Put the device in Standby
        self.unset_flag(REG.CTRL_REG1.ACTIVE)
        # No Fast-Read (14-bits), Fast-Read (8-Bits)
        self.unset_flag(REG.CTRL_REG1.F_READ)
        # Data Rate
        self.set_flag(REG.CTRL_REG1.DR_800Hz)
        # Full Scale Range 2g, 4g or 8g
        self.set_flag(REG.XYZ_DATA_CFG.FS_2g)
        # Low Noise
        self.set_flag(REG.CTRL_REG1.LNOISE)
        # No Auto-Sleep
        self.unset_flag(REG_CTRL_REG2, FLAG_SLPE)
        # High Resolution
        self.set_flag(REG_CTRL_REG2, FLAG_SMODS_HR)
        # P/L Detection Disabled
        self.unset_flag(REG_PL_CFG, FLAG_PL_CFG_PL_EN)
        # Enable FIFO stop mode
        self.set_flag(REG_F_SETUP, FLAG_F_MODE_FIFO_STOP)
        # Set watermark to 16 samples
        self.set_flag(REG_F_SETUP, 0x10)
        # Enable FIFO interrupt signal
        self.set_flag(REG_CTRL_REG4, FLAG_INT_EN_FIFO)
        # Route interrupt to pin 1
        self.set_flag(REG_CTRL_REG5, FLAG_INT_CFG_FIFO)
        # Setup GPIO callback
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN)
        GPIO.add_event_detect(11, GPIO.FALLING, callback=int1_callback)
        # Activate the device
        self.set_flag(REG_CTRL_REG1, FLAG_ACTIVE)

    def cleanup(self):
        bus.close()
        GPIO.cleanup()
        self.unset_flag(REG.CTRL_REG1.addr, REG.CTRL_REG1.ACTIVE)
