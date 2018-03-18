import smbus
from register.classes import Register, Flag

class IIC():
    def __init__(self, busNumber : int, address : int):
        self.bus = smbus.SMBus(busNumber)
        self.addr = address

    def write_register(self, register : Register, data : int):
        self.bus.write_byte_data(self.addr, register._addr, data)

    def read_register(self, register : Register):
        return self.bus.read_byte_data(self.addr, register._addr)

    def block_read(self, offset : Register, length : int):
        return self.bus.read_i2c_block_data(self.addr, offset._addr, length)

    def set_flag(self, register : Register, flag : int):
        self.writeRegister(register._addr, self.readRegister(register._addr) | flag)

    def unset_flag(self, register : Register, flag : int):
        self.writeRegister(register._addr, self.readRegister(register._addr) & ~flag)

    def set_flag(self, flag : Flag):
        self.writeRegister(flag._addr, self.readRegister(flag._addr) | flag)

    def unset_flag(self, flag : Flag):
        self.writeRegister(flag._addr, self.readRegister(flag._addr) & ~flag)

    def read_flag(self, flag : Flag):
        return (self.readRegister(flag._addr) & flag) != 0
    
    def close(self):
        self.bus.close()
