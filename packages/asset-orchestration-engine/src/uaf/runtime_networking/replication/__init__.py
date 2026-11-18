"""
UAF-81.83: Replication layer exports.
"""

from .bandwidth import BandwidthArbiter
from .baseline import ClientBaselineTracker
from .delta import DeltaCompressor, DeltaSnapshot, EntityDelta
from .dormancy import DormancyManager
from .property import PropertyContainer, quantize_value
from .relevancy import SpatialRelevancyManager

__all__ = [
    "BandwidthArbiter",
    "ClientBaselineTracker",
    "DeltaCompressor",
    "DeltaSnapshot",
    "DormancyManager",
    "EntityDelta",
    "PropertyContainer",
    "SpatialRelevancyManager",
    "quantize_value",
]
