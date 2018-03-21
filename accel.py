#!/usr/bin/env python3
# See 'LICENSE'  for copying

import pigpio
from mma8451.register import register as REG
from mma8451.iic import IIC
from threading import Thread, Semaphore
from queue import Queue
import time

device_name = 0x1A
iic_addr    = 0x1D


class ThreadedDataReader(Thread):
    InterruptSF = Semaphore(0)

    def __init__(self, iic, **kwargs):
        self.iic = iic 
        self.f_stop = False
        super().__init__(**kwargs)

    def run(self):
        global InterruptSF
        while not self.f_stop:
            if ThreadedDataReader.InterruptSF.acquire(timeout=1):
                status = self.iic.read_register(REG.F_STATUS)
                if self.iic.check_flag(status, REG.F_STATUS.F_OVF):
                    print("Warning: FIFO buffer overflow!")
                    f_cnt = 32
                else:
                    f_cnt = status & REG.F_STATUS.F_CNT
                for i in range(0,f_cnt,5):
                    Accel.DataQueue.put(self.iic.block_read(REG.OUT_X_MSB, 30))
                self.iic.read_register(REG.F_STATUS)

    def stop(self):
        self.f_stop = True

class Accel():
    DataQueue = Queue()

    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise OSError("Error connecting to pigpio daemon")

        iic_dev = 1 if self.pi.get_hardware_revision() > 1 else 0
        self.iic = IIC(self.pi, iic_dev, iic_addr)
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
        # Data Rate (800 Hz is the default)
        self.iic.set_flag(REG.CTRL_REG1.DR_800Hz)
        # Full Scale Range (2g is the default)
        self.iic.set_flag(REG.XYZ_DATA_CFG.FS_2g)
        # Low Noise mode
        self.iic.set_flag(REG.CTRL_REG1.LNOISE)
        # No Auto-Sleep
        self.iic.unset_flag(REG.CTRL_REG2.SLPE)
        # High Resolution
        self.iic.set_flag(REG.CTRL_REG2.SMODS_HR)
        # Enable FIFO fill mode
        self.iic.set_flag(REG.F_SETUP.F_MODE_Fill)
        # Set watermark to 15 samples
        self.iic.set_flag(REG.F_SETUP, 15)
        # Enable FIFO interrupt signal
        self.iic.set_flag(REG.CTRL_REG4.INT_EN_FIFO)
        # Route interrupt to pin 1 (2 is the dafault)
        self.iic.set_flag(REG.CTRL_REG5.INT_CFG_FIFO)
        # Setup GPIO callback at GPIO 17
        gpio_num = 17 # SoC numeration!
        self.pi.set_mode(gpio_num, pigpio.INPUT)
        self.pi.set_pull_up_down(gpio_num, pigpio.PUD_UP)
        self.pi.callback(gpio_num, pigpio.FALLING_EDGE, Accel.int1_callback)
        self.thr_dr.start()
        # Activate the device
        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)

    @staticmethod
    def int1_callback(GPIO, level, tick):
        ThreadedDataReader.InterruptSF.release()

    @staticmethod
    def getQueue():
        return Accel.DataQueue

    def cleanup(self):
        self.thr_dr.stop()
        self.thr_dr.join()
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)
        self.iic.close()
        self.pi.stop()
