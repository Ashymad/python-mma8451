#!/usr/bin/env python3
# See 'LICENSE'  for copying

import RPi.GPIO as GPIO
from mma8451.register import register as REG
from mma8451.iic import IIC
from threading import Thread, Semaphore
from queue import Queue
import time

device_name = 0x1A
iic_addr    = 0x1D

InterruptSF = Semaphore(0)
DataQueue = Queue()

def int1_callback(channel):
    InterruptSF.release()

class ThreadedDataReader(Thread):
    def __init__(self, iic = None, **kwargs):
        self.iic = IIC(1, iic_addr) 
        self.f_stop = False
        super().__init__(**kwargs)

    def run(self):
        while True:
            InterruptSF.acquire(timeout=1)
            if self.f_stop: break
            status = self.iic.read_register(REG.F_STATUS)
            if self.iic.check_flag(status, REG.F_STATUS.F_OVF):
                print("Warning: FIFO buffer overflow!")
            #f_cnt = status & REG.F_STATUS.F_CNT
            #if f_cnt > 5: f_cnt = 5
            data = self.iic.block_read(REG.OUT_X_MSB, 30)
            DataQueue.put(data)

    def stop(self):
        self.f_stop = True

class Accel():
    def __init__(self):
        if GPIO.RPI_INFO['P1_REVISION'] == 1:
            myBus = 0
        else:
            myBus = 1

        self.iic = IIC(myBus, iic_addr)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self.thr_dr = ThreadedDataReader(iic=self.iic)
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
        self.iic.set_flag(REG.F_SETUP, 5)
        # Enable FIFO interrupt signal
        self.iic.set_flag(REG.CTRL_REG4.INT_EN_FIFO)
        # Route interrupt to pin 1
        self.iic.set_flag(REG.CTRL_REG5.INT_CFG_FIFO)
        # Setup GPIO callback
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(11, GPIO.FALLING, callback=int1_callback)
        self.thr_dr.start()
        # Activate the device
        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)

    def getQueue(self):
        return DataQueue

    def cleanup(self):
        self.thr_dr.stop()
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)
        GPIO.cleanup()
        self.iic.close()
