from enum import Enum

class PowerUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to watts, lambda from watts)
    """
    BTU_h = ("British Thermal Unit Per Hour", lambda btu_h: btu_h * (1.05505585262e3 / 3600), lambda w: w / (1.05505585262e3 / 3600))
    W = ("Watt", lambda w: w, lambda w: w)
    kBTU_h = ("Kilo British Thermal Unit Per Hour", lambda kbtu_h: kbtu_h * 1.05505585262e6, lambda w: w / 1.05505585262e6)
    kW = ("Kilowatt", lambda kw: kw * 1e3, lambda w: w / 1e3)
    MBTU_h = ("Mega British Thermal Unit Per Hour", lambda mbtu_h: mbtu_h * (1.05505585262e9 / 3600), lambda w: w / (1.05505585262e9 / 3600))
    MW = ("Megawatt", lambda mj: mj * 1e6, lambda j: j / 1e6)

    def convert(self, value: float, to_unit: "PowerUnit"):
        return to_unit.value[2](self.value[1](value))
