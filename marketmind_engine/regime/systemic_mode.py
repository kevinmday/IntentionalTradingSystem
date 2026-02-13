from enum import Enum

class SystemicMode(str, Enum):
    NORMAL = "normal"
    STRESSED = "stressed"
    PRE_SYSTEMIC = "pre_systemic"
    SYSTEMIC = "systemic"
    STANDBY = "standby"
