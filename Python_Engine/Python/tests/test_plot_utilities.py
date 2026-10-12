from pathlib import Path
from tempfile import gettempdir

import matplotlib.pyplot as plt
from python_toolkit.plot.utilities import (
    base64_to_image,
    figure_to_base64,
    image_to_base64,
)


def test_figure_round_trip():
    """very simple test to check that base64 serialisation is working"""
    fig, _ = plt.subplots(1, 1)
    base64 = figure_to_base64(fig)
    assert isinstance(base64, str)

    path = base64_to_image(
        base64, image_path=Path(gettempdir()) / "test_figure_round_trip.png"
    )
    assert path.exists()

    base64_2 = image_to_base64(path)
    path.unlink()  # make sure to clean up after ourselves
    assert base64 == base64_2
