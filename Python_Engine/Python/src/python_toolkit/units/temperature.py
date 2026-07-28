from enum import Enum

class TemperatureUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to kelvin, lambda from kelvin)
    """
    C = ("Celcius", lambda c: c + 273.15, lambda k: k - 273.15)
    K = ("Kelvin", lambda k: k, lambda k: k)
    F = ("Fahrenheit", lambda f: (f + 459.67) * (5/9), lambda k: (k / (5/9)) - 459.67)
    R = ("Rankine", lambda r: r * (5/9), lambda k: k / (5/9))

    def convert(self, value: float, to_unit: "TemperatureUnit"):
        return to_unit.value[2]((self.value[1](value)))
