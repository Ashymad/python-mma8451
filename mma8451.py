#!/usr/bin/env python3
# See 'LICENSE'  for copying

# Parts of this library
from mma8451.iic import IIC
from mma8451.register.configuration import Configuration
from mma8451.register import register as REG

# Python modules
from threading import Thread, Semaphore
from multiprocessing import Queue, Process
from queue import Empty
import time

# External libraries
import pigpio
import numpy as np


class DataProcessor(Process):
    DataQueue = Queue()

    def __init__(self, bit_depth, n, vrange, callback,
                 convert_to_float=True, **kwargs):
        self.bit_depth = bit_depth
        self.callback = callback
        self.convert_to_float = convert_to_float
        self.n = n
        self.vrange = vrange
        self.maxn = 2**(bit_depth-1)-1
        self.signed_maxn = 2**bit_depth
        super().__init__(**kwargs)

    def reg2num(self, msb, lsb=None):
        num = ((int(msb) << 8) | int(lsb)) >> 2
        num -= self.signed_maxn if num > self.maxn else 0
        if self.convert_to_float:
            num = num/(self.maxn+1)*self.vrange
        return num

    def prepare_data(self, bitvec):
        data = np.zeros(
            [len(bitvec)//6, 3],
            dtype=np.float64 if self.convert_to_float else np.int16)
        for i in range(0, len(bitvec), 6):
            data[i//6, 0] = self.reg2num(bitvec[i], bitvec[i+1])
            data[i//6, 1] = self.reg2num(bitvec[i+2], bitvec[i+3])
            data[i//6, 2] = self.reg2num(bitvec[i+4], bitvec[i+5])
        return data

    def run(self):
        data = None
        while True:
            try:
                raw_data = DataProcessor.DataQueue.get(timeout=1)
            except Empty:
                break
            if data is None:
                data = self.prepare_data(raw_data)
            else:
                data = np.append(data, self.prepare_data(raw_data), axis=0)
                if len(data) > self.n-1:
                    self.callback(data)
                    del data
                    data = None
        print("DataProcessor exiting...")


class ThreadedDataReader(Thread):
    InterruptSF = Semaphore(0)

    def __init__(self, iic, bit_depth, **kwargs):
        self.f_run = True
        self.bit_depth = bit_depth
        self.iic = iic
        super().__init__(**kwargs)

    @staticmethod
    def callback(GPIO, level, tick):
        ThreadedDataReader.InterruptSF.release()

    def stop(self):
        self.f_run = False

    def run(self):
        while ThreadedDataReader.InterruptSF.acquire(timeout=1) and self.f_run:
            status = self.iic.read_register(REG.F_STATUS)
            f_cnt = status & REG.F_STATUS.F_CNT
            if f_cnt == 32:
                print("Warning: FIFO buffer overflow!")
            DataProcessor.DataQueue.put(
                self.iic.block_read(REG.OUT_X_MSB,
                                    f_cnt*3*round(self.bit_depth/8)))
            self.iic.read_register(REG.F_STATUS)
        print("ThreadedDataReader exiting...")


class Device():
    def __init__(self, iic_addr=0x1D, device_name=0x1A):
        self.iic_addr = iic_addr
        self.device_name = device_name
        self.conf = Configuration()

    def __enter__(self):
        self.open()

    def open(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise OSError("Error connecting to pigpio daemon")
        iic_dev = 1 if self.pi.get_hardware_revision() > 1 else 0
        self.iic = IIC(self.pi, iic_dev, self.iic_addr)
        whoami = self.iic.read_register(REG.WHO_AM_I)
        if whoami != self.device_name:
            raise NameError(
                "Error! Device not recognized! (" + str(whoami) + ")")

    def restart(self):
        """Restart device. Sets all registers to default values."""
        self.iic.set_flag(REG.CTRL_REG2.RST)
        time.sleep(0.01)
        self.conf = Configuration()

    def configure(self, **settings):
        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)

        for option in settings.keys():
            setting = settings[option]
            if option == "bit_depth":
                self.iic.unset_flag(
                    *Configuration.get_unset_params(option))
            else:
                self.iic.set_flag(
                    *Configuration.get_set_params(option, setting))
        self.conf.update(**settings)

        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)

    def setup_threaded_fifo_callback(self, gpio_pin, callback,
                                     interrupt_pin=2,
                                     time_interval=60,
                                     convert_to_float=True):

        self.iic.unset_flag(REG.CTRL_REG1.ACTIVE)

        self.iic.set_flag(REG.CTRL_REG4.INT_EN_FIFO)

        if interrupt_pin == 1:
            self.iic.set_flag(REG.CTRL_REG5.INT_CFG_FIFO)

        self.pi.set_mode(gpio_pin, pigpio.INPUT)

        self.pi.set_pull_up_down(gpio_pin, pigpio.PUD_UP)

        self.pi.callback(gpio_pin, pigpio.FALLING_EDGE,
                         ThreadedDataReader.callback)

        self.thr_dr = ThreadedDataReader(iic=self.iic,
                                         bit_depth=self.conf.get("bit_depth"))

        self.dta_proc = DataProcessor(
            bit_depth=self.conf.get("bit_depth"),
            n=self.conf.get("data_rate")*time_interval,
            vrange=self.conf.get("full_scale_range"),
            convert_to_float=convert_to_float,
            callback=callback)

        self.iic.set_flag(REG.CTRL_REG1.ACTIVE)

        self.thr_dr.start()
        self.dta_proc.start()

    def __exit__(self):
        self.close()

    def close(self):
        if self.thr_dr is not None and self.thr_dr.is_alive():
            self.thr_dr.stop()
            self.thr_dr.join()
        if self.pi.connected:
            self.iic.close()
            self.pi.stop()
        if self.dta_proc is not None and self.dta_proc.is_alive():
            self.dta_proc.join()
