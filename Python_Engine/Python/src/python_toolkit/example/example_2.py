import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from python_toolkit.bhom.bhom_analytics import bhom_analytics


@bhom_analytics
def example_2(save_path: Path, n_steps: int = 25) -> Path:
    """An example method to generate a chart and returns a dictionary.

    Arguments:
        save_path (Path): The path where the generated chart should be saved.
        n_steps (int): The number of steps between 0 and 2*Pi to plot. Default is 25.

    Returns:
        Dict[str, Union[Path, List[float]]]: An interesting dictionary.

    """

    x = np.linspace(0, 2 * np.pi, n_steps)
    sin_x = np.sin(x)
    cos_x = np.cos(x)

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))

    for y in [sin_x, cos_x]:
        ax.plot(x, y, lw=1, zorder=2)
        ax.scatter(x, y, c="k", s=2, zorder=3)
    ax.grid(ls="--")
    plt.tight_layout()
    ax.set_title("Woohoo, a chart!")
    plt.savefig(save_path.absolute(), dpi=150, transparent=False)

    return {"save_path": save_path.absolute(), "x": x, "sin_x": sin_x, "cos_x": cos_x}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-save_path",
        required=True,
        help="The path where the generated chart should be saved.",
        type=lambda p: Path(p).absolute(),
    )
    parser.add_argument(
        "-n_steps",
        required=False,
        help="The number of steps between 0 and 2*Pi to plot. Default is 25.",
        type=int,
        default=25,
    )

    args = parser.parse_args()

    example_2(args.save_path, args.n_steps)
