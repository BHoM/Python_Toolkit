import numpy as np

from ..bhom.analytics import bhom_analytics

@bhom_analytics()
def cardinality(direction_angle: float, directions: int = 16):
    """Returns the cardinal orientation of a given angle, where that angle is related to north at
        0 degrees.
    Args:
        direction_angle (float):
            The angle to north in degrees (+Ve is interpreted as clockwise from north at 0.0
            degrees).
        directions (int):
            The number of cardinal directions into which angles shall be binned (This value should
            be one of 4, 8, 16 or 32, and is centred about "north").
    Returns:
        int:
            The cardinal direction the angle represents.
    """

    if direction_angle > 360 or direction_angle < 0:
        raise ValueError(
            "The angle entered is beyond the normally expected range for an orientation in degrees."
        )

    cardinal_directions = {
        4: ["N", "E", "S", "W"],
        8: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        16: [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ],
        32: [
            "N",
            "NbE",
            "NNE",
            "NEbN",
            "NE",
            "NEbE",
            "ENE",
            "EbN",
            "E",
            "EbS",
            "ESE",
            "SEbE",
            "SE",
            "SEbS",
            "SSE",
            "SbE",
            "S",
            "SbW",
            "SSW",
            "SWbS",
            "SW",
            "SWbW",
            "WSW",
            "WbS",
            "W",
            "WbN",
            "WNW",
            "NWbW",
            "NW",
            "NWbN",
            "NNW",
            "NbW",
        ],
    }

    if directions not in cardinal_directions:
        raise ValueError(
            f'The input "directions" must be one of {list(cardinal_directions.keys())}.'
        )

    val = int((direction_angle / (360 / directions)) + 0.5)

    arr = cardinal_directions[directions]

    return arr[(val % directions)]

@bhom_analytics()
def angle_from_cardinal(cardinal_direction: str) -> float:
    """
    For a given cardinal direction, return the corresponding angle in degrees.

    Args:
        cardinal_direction (str):
            The cardinal direction.
    Returns:
        float:
            The angle associated with the cardinal direction.
    """
    cardinal_directions = [
        "N",
        "NbE",
        "NNE",
        "NEbN",
        "NE",
        "NEbE",
        "ENE",
        "EbN",
        "E",
        "EbS",
        "ESE",
        "SEbE",
        "SE",
        "SEbS",
        "SSE",
        "SbE",
        "S",
        "SbW",
        "SSW",
        "SWbS",
        "SW",
        "SWbW",
        "WSW",
        "WbS",
        "W",
        "WbN",
        "WNW",
        "NWbW",
        "NW",
        "NWbN",
        "NNW",
        "NbW",
    ]
    if cardinal_direction not in cardinal_directions:
        raise ValueError(f"{cardinal_direction} is not a known cardinal_direction.")
    angles = np.arange(0, 360, 11.25)

    lookup = dict(zip(cardinal_directions, angles))

    return lookup[cardinal_direction]

def angle_from_north(vector: list[float]) -> float:
    """For an X, Y vector, determine the clockwise angle to north at [0, 1].

    Args:
        vector (list[float]):
            A vector of length 2.

    Returns:
        float:
            The angle between vector and north in degrees clockwise from [0, 1].
    """
    north = [0, 1]
    angle1 = np.arctan2(*north[::-1])
    angle2 = np.arctan2(*vector[::-1])
    return np.rad2deg((angle1 - angle2) % (2 * np.pi))

def angle_to_vector(clockwise_angle_from_north: float) -> list[float]:
    """Return the X, Y vector from of an angle from north at 0-degrees.

    Args:
        clockwise_angle_from_north (float):
            The angle from north in degrees clockwise from [0, 360], though
            any number can be input here for angles greater than a full circle.

    Returns:
        list[float]:
            A vector of length 2.
    """

    clockwise_angle_from_north = np.radians(clockwise_angle_from_north)

    return np.sin(clockwise_angle_from_north), np.cos(clockwise_angle_from_north)
