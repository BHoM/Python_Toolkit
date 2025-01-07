import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from pathlib import Path

from python_toolkit.plot.utilities import figure_to_base64, image_to_base64, base64_to_image, figure_to_image

def test_figure_round_trip():
    """very simple test to check that base64 serialisation is working"""
    fig, ax = plt.subplots(1, 1)
    base64 = figure_to_base64(fig)
    assert isinstance(base64, str)

    path = base64_to_image(base64, image_path = Path("tests/assets/temp.png").resolve())
    assert path.exists()
    
    base64_2 = image_to_base64(path)
    path.unlink() #make sure to clean up after ourselves
    assert base64 == base64_2