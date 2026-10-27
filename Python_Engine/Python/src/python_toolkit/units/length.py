from enum import Enum

class LengthUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to metres, lambda from metres)
    """
    cm = ("Centimetre", lambda cm: cm * 1e-2, lambda m: m / 1e-2)
    ft = ("Foot", lambda ft: ft * 3.048e-1, lambda m: m / 3.048e-1)
    In = ("Inch", lambda In: In * 2.54e-2, lambda m: m / 2.54e-2)
    km = ("Kilometre", lambda km: km * 1e3, lambda m: m / 1e3)
    m = ("Metre", lambda m: m, lambda m: m)
    mi = ("Mile", lambda mi: mi * 1.609344e3, lambda m: m / 1.609344e3)
    mm = ("Millimetre", lambda mm: mm * 1e-3, lambda m: m / 1e-3)
    yd = ("Yard", lambda yd: yd * 9.144e-1, lambda m: m / 9.144e-1)

    def convert(self, value: float, to_unit: "LengthUnit"):
        return to_unit.value[2](self.value[1](value))
