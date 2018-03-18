import smbus
from register.classes import Register, Flag

class IIC():
    def __init__(self, busNumber : int, address : int):
        self.bus = smbus.SMBus(busNumber)
        self.addr = address

    def write_register(self, register : Register, data : int):
        self.bus.write_byte_data(self.addr, register._addr, data)

    def read_register(self, register : Register) -> int:
        return self.bus.read_byte_data(self.addr, register._addr)

    def block_read(self, offset : Register, length : int) -> int:
        return self.bus.read_i2c_block_data(self.addr, offset._addr, length)

    def _set_flag(self, register : int, flag : int):
        self.writeregister(register, self.readregister(register) | flag)

    def _unset_flag(self, register : int, flag : int):
        self.writeregister(register, self.readregister(register) & ~flag)

    def set_flag(self, register : Register, flag : int):
        self._set_flag(register._addr, flag)

    def unset_flag(self, register : Register, flag : int):
        self._unset_flag(register._addr, flag)

    def set_flag(self, flag : Flag):
        self._set_flag(flag._addr, flag)

    def unset_flag(self, flag : Flag):
        self._unset_flag(flag._addr, flag)

    @staticmethod
    def check_flag(bitfield : int, flag : int) -> bool:
        if flag == 0:
            raise ValueError("Flag does not have any bits set!")
        return (bitfield & flag) != 0

    def read_flag(self, flag : Flag) -> bool:
        return self.check_flag(self.readRegister(flag._addr), flag)
    
    def close(self):
        self.bus.close()
