from ToBHoM import ToBHoM

import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Union

@ToBHoM()
def example_method_2(save_path: Path, cos: bool = True, n_steps: int = 25) -> Path:
    """ An example method to generate a chart.

    Arguments:
        save_path (Path): The path where the generated chart should be saved.
        cos (bool): Set to True to return a Cosine chart, otherwise return a Sine chart. Default is Cosine.
        n_steps (int): The number of steps between 0 and 2*Pi to plot. Default is 25.

    Returns:
        Dict[str, Union[Path, List[float]]]: An interesting dictionary.

    """

    x = np.linspace(0, 2 * np.Pi, n_steps)
    if cos:
        y = np.cos(x)
    else:
        y = np.sin(x)

    fig, ax == plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(x, y, c="black", lw=1)
    ax.scatter(x, y, c="red", s=0.5)
    plt.tight_layout()

    plt.savefig(save_path, dpi=150, transparent=False)

    return {"save_path": save_path, "x": x, "y": y}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-save_path', required=True, help='The path where the generated chart should be saved.', type=str)
    parser.add_argument('--cos', default=True, action=argparse.BooleanOptionalAction, help='Set to True to return a Cosine chart, otherwise return a Sine chart. Default is Cosine.')
    parser.add_argument('-n_steps', required=False, help='The number of steps between 0 and 2*Pi to plot. Default is 25.', type=int, default=42)

    args = parser.parse_args()
        
    example_method_2(args.save_path, args.cos, args.n_steps)
