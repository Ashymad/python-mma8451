import smbus
from mma8451.register.classes import Register, Flag

class IIC():
    def __init__(self, busNumber : int, address : int):
        self.bus = smbus.SMBus(busNumber)
        self.addr = address

    def _write_register(self, register : int, data : int):
        self.bus.write_byte_data(self.addr, register, data)

    def _read_register(self, register : int) -> int:
        return self.bus.read_byte_data(self.addr, register)

    def _block_read(self, offset : int, length : int) -> int:
        return self.bus.read_i2c_block_data(self.addr, offset, length)

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
        self.bus.close()
