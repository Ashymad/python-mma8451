#!/usr/bin/env python3
# See 'LICENSE'  for copying

# Parts of this library
from mma8451.register import register as REG
from mma8451.iic import IIC

# Python modules
from threading import Thread, Semaphore
from multiprocessing import Queue, Process
from queue import Empty
import time
from datetime import datetime

# External libraries
import h5py as h5
import pigpio
import numpy as np

device_name = 0x1A
iic_addr    = 0x1D

class DataProcessor(Process):
    DataQueue = Queue()
    prec = 14
    Fs = 800
    maxn = 2**(prec-1)-1
    signed_maxn = 2**prec

    def reg2int(self, msb, lsb):
        num = ((int(msb) << 8) | int(lsb)) >> 2
        num -= self.signed_maxn if num > self.maxn else 0
        return num

    def prepare_data(self, bitvec):
        data = np.zeros([len(bitvec)//6,3], dtype=np.int16)
        for i in range(0, len(bitvec), 6):
            data[i//6,0] = self.reg2int(bitvec[i],bitvec[i+1])
            data[i//6,1] = self.reg2int(bitvec[i+2],bitvec[i+3])
            data[i//6,2] = self.reg2int(bitvec[i+4],bitvec[i+5])
        return data

    def run(self):
        data = None
        dt = 60
        n = self.Fs*dt
        dtime = datetime.now()
        while True:
            try:
                raw_data = DataProcessor.DataQueue.get(timeout=1)
            except Empty:
                break
            if data is None:
                data = self.prepare_data(raw_data)
            else:
                data = np.append(data, self.prepare_data(raw_data), axis=0)
                if len(data) > n-1:
                    dataset = dtime.strftime("%Y/%m/%d/%H/%M")
                    with h5.File("data.h5", "a") as f:
                        f.create_dataset(dataset, data=data)
                    del data
                    data = None
                    dtime = datetime.now()

class ThreadedDataReader(Thread):
    InterruptSF = Semaphore(0)

    def __init__(self, iic, **kwargs):
        self.iic = iic 
        super().__init__(**kwargs)

    @staticmethod
    def callback(GPIO, level, tick):
        ThreadedDataReader.InterruptSF.release()

    def run(self):
        while ThreadedDataReader.InterruptSF.acquire(timeout=1):
            status = self.iic.read_register(REG.F_STATUS)
            f_cnt = status & REG.F_STATUS.F_CNT
            if f_cnt == 32:
                print("Warning: FIFO buffer overflow!")
            DataProcessor.DataQueue.put(self.iic.block_read(REG.OUT_X_MSB, f_cnt*6))
            self.iic.read_register(REG.F_STATUS)

class Accel():
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise OSError("Error connecting to pigpio daemon")
        iic_dev = 1 if self.pi.get_hardware_revision() > 1 else 0
        self.iic = IIC(self.pi, iic_dev, iic_addr)
        self.thr_dr = ThreadedDataReader(iic=self.iic)
        self.dta_proc = DataProcessor()
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
        # self.iic.set_flag(REG.CTRL_REG1.DR_800Hz)
        # Full Scale Range (2g is the default)
        # self.iic.set_flag(REG.XYZ_DATA_CFG.FS_2g)
        # Low Noise mode
        self.iic.set_flag(REG.CTRL_REG1.LNOISE)
        # No Auto-Sleep
        self.iic.unset_flag(REG.CTRL_REG2.SLPE)
        # High Resolution
        self.iic.set_flag(REG.CTRL_REG2.SMODS_HR)
        # Enable FIFO fill mode
        self.iic.set_flag(REG.F_SETUP.F_MODE_Fill)
        # Set watermark to 15 samples
        self.iic.set_flag(REG.F_SETUP, 20)
        # Enable FIFO interrupt signal
        self.iic.set_flag(REG.CTRL_REG4.INT_EN_FIFO)
        # Route interrupt to pin 1 (2 is the dafault)
        self.iic.set_flag(REG.CTRL_REG5.INT_CFG_FIFO)
        # Setup GPIO callback at GPIO 17
        gpio_num = 17 # SoC numeration!
        self.pi.set_mode(gpio_num, pigpio.INPUT)
        self.pi.set_pull_up_down(gpio_num, pigpio.PUD_UP)
        self.pi.callback(gpio_num, pigpio.FALLING_EDGE, ThreadedDataReader.callback)
        self.thr_dr.start()
        self.dta_proc.start()
        # Activate the device
        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)
        # Start data saver

    def cleanup(self):
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)
        self.thr_dr.join()
        self.iic.close()
        self.pi.stop()
        self.dta_proc.join()
