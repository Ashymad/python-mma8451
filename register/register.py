from enum import IntEnum
import register.addr as REG

class STATUS(IntEnum):
    addr            = REG.STATUS
    ZYXOW           = 0x80
    ZOW             = 0x40
    YOW             = 0x20
    XOW             = 0x10
    ZYXDR           = 0x08
    ZDR             = 0x04
    YDR             = 0x02
    XDR             = 0x01
class F_STATUS(IntEnum):
    addr            = REG.F_STATUS
    F_OVF           = 0x80
    F_WMRK_FLAG     = 0x40
    F_CNT           = 0x3F
class OUT_X_MSB(IntEnum):
    addr            = REG.OUT_X_MSB
class OUT_X_LSB(IntEnum):
    addr            = REG.OUT_X_LSB
class OUT_Y_MSB(IntEnum):
    addr            = REG.OUT_Y_MSB
class OUT_Y_LSB(IntEnum):
    addr            = REG.OUT_Y_LSB
class OUT_Z_MSB(IntEnum):
    addr            = REG.OUT_Z_MSB
class OUT_Z_LSB(IntEnum):
    addr            = REG.OUT_Z_LSB
class F_SETUP(IntEnum):
    addr            = REG.F_SETUP
    F_MODE1         = 0x80
    F_MODE0         = 0x40
    F_WMRK          = 0x3F
    F_MODE_Disabled = 0x00
    F_MODE_Fill     = 0x40
    F_MODE_Circular = 0x80
    F_MODE_Trigger  = 0xC0
class TRIG_CFG(IntEnum):
    addr            = REG.TRIG_CFG
    Trig_TRANS      = 0x20
    Trig_LNDPRT     = 0x10
    Trig_PULSE      = 0x08
    Trig_FF_MT      = 0x04
class SYSMOD(IntEnum):
    addr            = REG.SYSMOD
    FGERR           = 0x80
    FGT             = 0x3C
    SYSMOD          = 0x03
    SYSMOD_STANDBY  = 0x00
    SYSMOD_WAKE     = 0x01
    SYSMOD_SLEEP    = 0x02
class INT_SOURCE(IntEnum):
    addr            = REG.INT_SOURCE
    SRC_ASLP        = 0x80
    SRC_FIFO        = 0x40
    SRC_TRANS       = 0x20
    SRC_LNDPRT      = 0x10
    SRC_PULSE       = 0x08
    SRC_FF_MT       = 0x04
    SRC_DRDY        = 0x01
class WHO_AM_I(IntEnum):
    addr            = REG.WHO_AM_I
class XYZ_DATA_CFG(IntEnum):
    addr            = REG.XYZ_DATA_CFG
    HPF_OUT         = 0x10
    FS              = 0x03
    FS_2g           = 0x00
    FS_4g           = 0x01
    FS_8g           = 0x02
class HP_FILTER_CUTOFF(IntEnum):
    addr            = REG.HP_FILTER_CUTOFF
    Pulse_HPF_BYP   = 0x20
    Pulse_LPF_EN    = 0x10
    SEL_Highest     = 0x00
    SEL_Higher      = 0x01
    SEL_Lower       = 0x02
    SEL_Lowest      = 0x03
class PL_STATUS(IntEnum):
    addr            = REG.PL_STATUS
    NEWLP           = 0x80
    LO              = 0x40
    LAPO            = 0x06
    LAPO_PO_UP      = 0x00
    LAPO_PO_DOWN    = 0x02
    LAPO_LA_RIGHT   = 0x04
    LAPO_LA_LEFT    = LAPO
class PL_CFG(IntEnum):
    addr            = REG.PL_CFG
    DBCNTM          = 0x80
    PL_EN           = 0x40
class PL_COUNT(IntEnum):
    addr            = REG.PL_COUNT
class PL_BF_ZCOMP(IntEnum):
    addr            = REG.PL_BF_ZCOMP
    BKFR            = 0xC0
    ZLOCK           = 0x07
class P_L_THIS_REG(IntEnum):
    addr            = REG.P_L_THIS_REG
    P_L_THIS        = 0xF8
    HYS             = 0x07
class FF_MT_CFG(IntEnum):
    pass
class FF_MT_SRC(IntEnum):
    pass
class FF_MT_THS(IntEnum):
    pass
class FF_MT_COUNT(IntEnum):
    pass
class TRANSIENT_CFG(IntEnum):
    pass
class TRANSIENT_SCR(IntEnum):
    pass
class TRANSIENT_THS(IntEnum):
    pass
class TRANSIENT_COUNT(IntEnum):
    pass
class PULSE_CFG(IntEnum):
    pass
class PULSE_SRC(IntEnum):
    pass
class PULSE_THSX(IntEnum):
    pass
class PULSE_THSY(IntEnum):
    pass
class PULSE_THSZ(IntEnum):
    pass
class PULSE_TMLT(IntEnum):
    pass
class PULSE_LTCY(IntEnum):
    pass
class PULSE_WIND(IntEnum):
    pass
class ASLP_COUNT(IntEnum):
    addr            = REG.ASLP_COUNT
class CTRL_REG1(IntEnum):
    addr            = REG.CTRL_REG1
    ASLP_RATE       = 0xC0
    ASLP_RATE_50Hz  = 0x00
    ASLP_RATE_12_5Hz= 0x40
    ASLP_RATE_6_25Hz= 0x80
    ASLP_RATE_1_56Hz= ASLP_RATE
    DR              = 0x38
    DR_800Hz        = 0x00
    DR_400Hz        = 0x08
    DR_200Hz        = 0x10
    DR_100Hz        = 0x18
    DR_50Hz         = 0x20
    DR_12_5Hz       = 0x28
    DR_6_25Hz       = 0x30
    DR_1_56Hz       = 0x38
    LNOISE          = 0x04
    F_READ          = 0x02
    ACTIVE          = 0x01
class CTRL_REG2(IntEnum):
    addr            = REG.CTRL_REG2
    ST              = 0x80
    RST             = 0x40
    SMODS           = 0x18
    SMODS_Normal    = 0x00
    SMODS_LN_LP     = 0x08
    SMODS_HR        = 0x10
    SMODS_LP        = 0x18
    SLPE            = 0x04
    MODS            = 0x03
    MODS_Normal     = 0x00
    MODS_LN_LP      = 0x01
    MODS_HR         = 0x02
    MODS_LP         = 0x03
class CTRL_REG3(IntEnum):
    addr            = REG.CTRL_REG3
    FIFO_GATE       = 0x80
    WAKE_TRANS      = 0x40
    WAKE_LNDPRT     = 0x20
    WAKE_PULSE      = 0x10
    WAKE_FF_MT      = 0x08
    IPOL            = 0x02
    PP_OD           = 0x01
class CTRL_REG4(IntEnum):
    addr            = REG.CTRL_REG4
    INT_EN_ASLP     = 0x80
    INT_EN_FIFO     = 0x40
    INT_EN_TRANS    = 0x20
    INT_EN_LNDPRT   = 0x10
    INT_EN_PULSE    = 0x08
    INT_EN_FF_MT    = 0x04
    INT_EN_DRDY     = 0x01
class CTRL_REG5(IntEnum):
    addr            = REG.CTRL_REG5
    INT_CFG_ASLP    = 0x80
    INT_CFG_FIFO    = 0x40
    INT_CFG_TRANS   = 0x20
    INT_CFG_LNDPRT  = 0x10
    INT_CFG_PULSE   = 0x08
    INT_CFG_FF_MT   = 0x04
    INT_CFG_DRDY    = 0x01
class OFF_X(IntEnum):
    addr            = REG.OFF_X
class OFF_Y(IntEnum):
    addr            = REG.OFF_Y
class OFF_Z(IntEnum):
    addr            = REG.OFF_Z
