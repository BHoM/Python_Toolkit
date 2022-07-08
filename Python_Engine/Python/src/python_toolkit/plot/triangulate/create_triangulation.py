import copy
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri.triangulation import Triangulation


def create_triangulation(
    x: List[float],
    y: List[float],
    alpha: float = 1.1,
    max_iterations: int = 250,
    increment: float = 0.01,
) -> Triangulation:
    """Create a matplotlib Triangulation from a list of x and y coordinates, including a mask to remove elements with edges larger than alpha.

    Args:
        x (List[float]): A list of x coordinates.
        y (List[float]): A list of y coordinates.
        alpha (float, optional): A value to start alpha at. Defaults to 1.1.
        max_iterations (int, optional): The number of iterations to run to check against triangulation validity. Defaults to 250.
        increment (int, optional): The value by which to increment alpha by when searching for a valid triangulation. Defaults to 0.01.

    Returns:
        Triangulation: A matplotlib Triangulation object.
    """

    if len(x) != len(y):
        raise ValueError("x and y must be the same length")

    # Traingulate X, Y locations
    triang = Triangulation(x, y)

    xtri = x[triang.triangles] - np.roll(x[triang.triangles], 1, axis=1)
    ytri = y[triang.triangles] - np.roll(y[triang.triangles], 1, axis=1)
    maxi = np.max(np.sqrt(xtri**2 + ytri**2), axis=1)

    # Iterate triangulation masking until a possible mask is found
    count = 0
    fig, ax = plt.subplots(1, 1)
    synthetic_values = range(len(x))
    success = False
    while not success:
        count += 1
        try:
            tr = copy.deepcopy(triang)
            tr.set_mask(maxi > alpha)
            ax.tricontour(tr, synthetic_values)
            success = True
        except ValueError:
            alpha += increment
        else:
            break
        if count > max_iterations:
            raise ValueError(
                f"Could not create a valid triangulation mask within {max_iterations}"
            )
    plt.close(fig)
    triang.set_mask(maxi > alpha)
    return triang
