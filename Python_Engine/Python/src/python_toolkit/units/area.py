from enum import Enum

class AreaUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to metres squared, lambda from metres squared)
    """
    ft2 = ("Feet Squared", lambda ft2: ft2 * (3.048e-1**2), lambda m2: m2 / (3.048e-1**2))
    km2 = ("Kilometres Squared", lambda km2: km2 * (1e3**2), lambda m2: m2 / (1e3**2))
    m2 = ("Metres Squared", lambda m2: m2, lambda m2: m2)
    mi2 = ("Miles Squared", lambda mi2: mi2 * (1.609344e3**2), lambda m2: m2 / (1.609344e3**2))

    def convert(self, value: float, to_unit: "AreaUnit"):
        return to_unit.value[2](self.value[1](value))
