from enum import Enum

class EnergyUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to joules, lambda from joules)
    """
    BTU = ("British Thermal Unit", lambda btu: btu * 1.05505585262e3, lambda j: j / 1.05505585262e3)
    J = ("Joule", lambda j: j, lambda j: j)
    kBTU = ("Kilo British Thermal Unit", lambda kbtu: kbtu * 1.05505585262e6, lambda j: j / 1.05505585262e6)
    kJ = ("Kilojoule", lambda kj: kj * 1e3, lambda j: j / 1e3)
    kWh = ("kilowatt Hour", lambda kwh: kwh * 3.6e6, lambda j: j / 3.6e6)
    MBTU = ("Mega British Thermal Unit", lambda mbtu: mbtu * 1.05505585262e9, lambda j: j / 1.05505585262e9)
    MJ = ("Megajoule", lambda mj: mj * 1e6, lambda j: j / 1e6)
    MWh = ("Megawatt Hour", lambda mwh: mwh * 3.6e9, lambda j: j / 3.6e9)
    Wh = ("Watt Hour", lambda wh: wh * 3.6e3, lambda j: j / 3.6e3)

    def convert(self, value: float, to_unit: "EnergyUnit"):
        return to_unit.value[2](self.value[1](value))
