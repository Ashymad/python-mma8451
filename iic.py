from mma8451.register.classes import Register, Flag

class IIC():
    def __init__(self, pigpio_pi, iic_dev : int, iic_addr : int):
        self.pi = pigpio_pi
        self.iic = self.pi.i2c_open(iic_dev, iic_addr)

    def _write_register(self, register : int, data : int):
        self.pi.i2c_write_byte_data(self.iic, register, data)

    def _read_register(self, register : int) -> int:
        return self.pi.i2c_read_byte_data(self.iic, register)

    def _block_read(self, register : int, length : int) -> int:
        data_size, data = self.pi.i2c_read_i2c_block_data(self.iic, register, length)
        if data_size < 0:
            raise OSError('Error ' + str(data_size) + ': unable to read i2c block data')
        return data

    def write_register(self, register : Register, data : int):
        self._write_register(register._addr, data)

    def read_register(self, register : Register) -> int:
        return self._read_register(register._addr)

    def block_read(self, offset : Register, length : int) -> int:
        return self._block_read(offset._addr, length)

    def _set_flag(self, register : int, flag : int):
        self._write_register(register, self._read_register(register) | flag)

    def _unset_flag(self, register : int, flag : int):
        self._write_register(register, self._read_register(register) & ~flag)

    def set_flag(self, regorflag, flag : int = None):
        if flag is None: flag = regorflag
        self._set_flag(regorflag._addr, flag)

    def unset_flag(self, regorflag, flag : int = None):
        if flag is None: flag = regorflag
        self._unset_flag(regorflag._addr, flag)

    @staticmethod
    def check_flag(bitfield : int, flag : int) -> bool:
        if flag == 0:
            raise ValueError("Flag does not have any bits set!")
        return (bitfield & flag) != 0

    def read_flag(self, flag : Flag) -> bool:
        return self.check_flag(self.read_register(flag._addr), flag)
    
    def close(self):
        self.pi.i2c_close(self.iic)
