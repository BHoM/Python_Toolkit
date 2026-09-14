from python_toolkit.plot.heatmap import heatmap
from ..decorators import bhom_wrapper
import pandas as pd

@bhom_wrapper.bhom_callable("test")
def heatmap_2(geometry, **kwargs):
    print(geometry)
    print(kwargs["arg2"])
    geometry.x = 20
    return geometry
