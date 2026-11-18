"""
Physical terrain erosion simulators (hydraulic and thermal).
"""

from uaf.landscape.erosion.hydraulic import HydraulicErosionSimulator
from uaf.landscape.erosion.thermal import ThermalErosionSimulator

__all__ = [
    "HydraulicErosionSimulator",
    "ThermalErosionSimulator",
]
