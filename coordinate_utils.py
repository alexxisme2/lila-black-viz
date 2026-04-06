"""
Coordinate conversion: game world (x, z) → minimap pixel (px, py)

Formula from README:
  u = (x - origin_x) / scale
  v = (z - origin_z) / scale
  pixel_x = u * 1024
  pixel_y = (1 - v) * 1024   ← flipped because image origin is top-left

For Plotly (y=0 at bottom, y=1024 at top), we convert:
  plot_y = 1024 - pixel_y
"""

import numpy as np

MINIMAP_SIZE = 1024

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}


def world_to_pixel_vectorized(x_series, z_series, map_id: str):
    """
    Vectorized conversion — pass pandas Series, get numpy arrays back.
    Use this for batch processing the entire dataframe (fast).
    """
    cfg = MAP_CONFIG[map_id]
    u = (x_series - cfg["origin_x"]) / cfg["scale"]
    v = (z_series - cfg["origin_z"]) / cfg["scale"]
    pixel_x = u * MINIMAP_SIZE
    pixel_y = (1 - v) * MINIMAP_SIZE  # image coords (0 = top)
    plot_y   = MINIMAP_SIZE - pixel_y  # plotly coords (0 = bottom)
    return pixel_x.values, plot_y.values
