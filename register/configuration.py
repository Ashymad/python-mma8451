from mma8451.register import register as REG

_NONE = 0x00

_conf = {
    "fifo_mode": {
        "default": "disabled",
        "register": REG.F_SETUP,
        "flags": {
            "disabled": REG.F_SETUP.F_MODE_Disabled,
            "circular": REG.F_SETUP.F_MODE_Circular,
            "fill": REG.F_SETUP.F_MODE_Fill,
            "trigger": REG.F_SETUP.F_MODE_Trigger,
        }
    },
    "bit_depth": {
        "default": 8,
        "register": REG.CTRL_REG1,
        "flags": {
            8: REG.CTRL_REG1.F_READ,
            14: _NONE,
        }
    },
    "fifo_watermark": {
        "default": 0,
        "register": REG.F_SETUP,
        "flags": range(0, 33),
    }
}
