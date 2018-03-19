from enum import IntEnum

class Register(type(IntEnum)):
    def __int__(self):
        return int(self._addr)
    def __repr__(cls):
        return "<" + cls.__name__ + ": " + str(hex(cls._addr)) + ">"

class Flag(IntEnum, metaclass=Register):
    def __repr__(cls):
        return "<" + cls.__class__.__name__ + "." + \
            cls.name + ": " + hex(cls.value) + ">"

