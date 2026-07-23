from enum import Enum

class SpeedUnit(Enum):
    """Each unit value is a tuple in the format:
        (display name, lambda to metres per secomd, lambda from metres per second)
    """
    m_s = ("Metres Per Second", lambda m_s: m_s, lambda m_s: m_s)
    km_h = ("Kilometres Per Hour", lambda km_h: km_h * 3.6e6, lambda m_s: m_s / 3.6e6)
    mi_h = ("Miles Per Hour", lambda mi_h: mi_h * 5.7936384e6, lambda m_s: m_s / 5.7936384e6)
    ft_s = ("Feet Per Second", lambda ft_s: ft_s * 3.048e-1, lambda m_s: m_s / 3.048e-1)

    def convert(self, value: float, to_unit: "SpeedUnit"):
        return to_unit.value[2](self.value[1](value))
