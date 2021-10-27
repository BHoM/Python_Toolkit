from typing import List
import numpy as np
import matplotlib.pyplot as plt

def main(x: List[float], y: List[float], save_path: str) -> None:
    """
    Plot a graph of the given x and y values.
    """

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.scatter(x, y, marker="o", c="blue", zorder=4)
    ax.plot(x, y, c='red', zorder=3)
    ax.grid()
    [ax.spines[i].set_visible(False) for i in ["top", "right"]]

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)

if __name__ == "__main__":
    x = np.linspace(0, np.pi * 2, 40)
    y = np.sin(x)
    fp = r"C:\ProgramData\BHoM\Extensions\Python\ScriptTest.png"
    main(x, y, fp)
    print(fp)
