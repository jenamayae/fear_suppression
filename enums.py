from enum import Enum

class ModulationMode(Enum):
    phase_reversal = "phase_reversal"
    on_off_flicker = "on_off_flicker"

class UpperLowerPhaseMode(Enum):
    synchronized = "synchronized"
    offset = "offset"

class SurroundCondition(Enum):
    absent = "absent"
    static = "static"
    dynamic = "dynamic"
