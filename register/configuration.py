from mma8451.register import register as REG
from functools import reduce

class Configuration():
    _NONE = 0x00

    _default = {
        "fifo_mode": "disabled",
        "bit_depth": 8,
        "fifo_watermark": 0,
        "power_mode": "normal",
        "sleep_power_mode": "normal",
        "full_scale_range": 2,
        "data_rate": 800,
        "auto_sleep": True,
        "low_noise": False,
    }

    _conf = {
        "fifo_mode": {
            "register": REG.F_SETUP,
            "flags": {
                "disabled": REG.F_SETUP.F_MODE_Disabled,
                "circular": REG.F_SETUP.F_MODE_Circular,
                "fill": REG.F_SETUP.F_MODE_Fill,
                "trigger": REG.F_SETUP.F_MODE_Trigger,
            }
        },
        "bit_depth": {
            "register": REG.CTRL_REG1,
            "flags": {
                8: REG.CTRL_REG1.F_READ,
                14: _NONE, 
            }
        },
        "fifo_watermark": {
            "register": REG.F_SETUP,
            "flags": range(0, 33),
        },
        "power_mode": {
            "register": REG.CTRL_REG2,
            "flags": {
                "normal": REG.CTRL_REG2.MODS_Normal,
                "low_power": REG.CTRL_REG2.MODS_LP,
                "low_noise": REG.CTRL_REG2.MODS_LN_LP,
                "high_resolution": REG.CTRL_REG2.MODS_HR
            }
        },
        "sleep_power_mode": {
            "register": REG.CTRL_REG2,
            "flags": {
                "normal": REG.CTRL_REG2.SMODS_Normal,
                "low_power": REG.CTRL_REG2.SMODS_LP,
                "low_noise": REG.CTRL_REG2.SMODS_LN_LP,
                "high_resolution": REG.CTRL_REG2.SMODS_HR
            }
        },
        "full_scale_range": {
            "register": REG.XYZ_DATA_CFG,
            "flags": {
                2: REG.XYZ_DATA_CFG.FS_2g,
                4: REG.XYZ_DATA_CFG.FS_4g,
                8: REG.XYZ_DATA_CFG.FS_8g,
            }
        },
        "data_rate": {
            "register": REG.CTRL_REG1,
            "flags": {
                800: REG.CTRL_REG1.DR_800Hz,
                400: REG.CTRL_REG1.DR_400Hz,
                200: REG.CTRL_REG1.DR_200Hz,
                100: REG.CTRL_REG1.DR_100Hz,
                50: REG.CTRL_REG1.DR_50Hz,
                12.5: REG.CTRL_REG1.DR_12_5Hz,
                6.25: REG.CTRL_REG1.DR_6_25Hz,
                1.5: REG.CTRL_REG1.DR_1_56Hz,
            }
        },
        "auto_sleep": {
            "register": REG.CTRL_REG2,
            "flags": {
                True: REG.CTRL_REG2.SLPE,
                False: _NONE, 
            }
        },
        "low_noise": {
            "register": REG.CTRL_REG1,
            "flags": {
                True: REG.CTRL_REG1.LNOISE,
                False: _NONE, 
            }
        },
    }

    def __init__(self):
        self.conf = Configuration._default.copy()

    @staticmethod
    def get_default(option):
        return Configuration._default[option]

    def get(self, option):
        return self.conf[option]

    def update(self, **options):
        for option in options.keys():
            self.conf[option] = options[option]

    @staticmethod
    def get_unset_params(option):
        op = Configuration._conf[option]
        val = op["flags"].values() if isinstance(op["flags"], dict) else op["flags"]
        return op["register"], reduce(lambda a, b: a | b, val)

    @staticmethod
    def get_set_params(option, setting):
        op = Configuration._conf[option]
        return op["register"], op["flags"][setting]
