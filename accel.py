#!/usr/bin/env python3
# See 'LICENSE'  for copying

from scipy.constants import g
import RPi.GPIO as GPIO
from mma8451.register import register as REG
from mma8451.iic import IIC
import time

device_name = 0x1A
iic_addr    = 0x1D

def int1_callback(channel):
    print("Interrupt detected")

class Accel():
    def __init__(self):
        if GPIO.RPI_INFO['P1_REVISION'] == 1:
            myBus = 0
        else:
            myBus = 1

        self.iic = IIC(myBus, iic_addr)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

        whoami = self.iic.read_register(REG.WHO_AM_I)
        if whoami != device_name:
            raise NameError("Error! Device not recognized! (" + str(whoami) + ")")


    def init_callback(self):
        # Reset
        self.iic.set_flag(REG.CTRL_REG2.RST)
        time.sleep(0.01)
        # Put the device in Standby
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)
        # No Fast-Read (14-bits), Fast-Read (8-Bits)
        self.iic.unset_flag(REG.CTRL_REG1.F_READ)
        # Data Rate
        self.iic.set_flag(REG.CTRL_REG1.DR_800Hz)
        # Full Scale Range 2g, 4g or 8g
        self.iic.set_flag(REG.XYZ_DATA_CFG.FS_2g)
        # Low Noise
        self.iic.set_flag(REG.CTRL_REG1.LNOISE)
        # No Auto-Sleep
        self.iic.unset_flag(REG.CTRL_REG2.SLPE)
        # High Resolution
        self.iic.set_flag(REG.CTRL_REG2.SMODS_HR)
        # P/L Detection Disabled
        self.iic.unset_flag(REG.PL_CFG.PL_EN)
        # Enable FIFO fill mode
        self.iic.set_flag(REG.F_SETUP.F_MODE_Fill)
        # Set watermark to 16 samples
        self.iic.set_flag(REG.F_SETUP, 0x10)
        # Enable FIFO interrupt signal
        self.iic.set_flag(REG.CTRL_REG4.INT_EN_FIFO)
        # Route interrupt to pin 1
        self.iic.set_flag(REG.CTRL_REG5.INT_CFG_FIFO)
        # Setup GPIO callback
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN)
        GPIO.add_event_detect(11, GPIO.FALLING, callback=int1_callback)
        # Activate the device
        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)

    def cleanup(self):
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)
        GPIO.cleanup()
        self.iic.close()
