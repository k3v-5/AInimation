"""
GeometryGenerator base protocol for all geometry synthesis engines.
UAF-81.3 Section 80.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.geometry_component import GeometryComponent
from ...core.specification.asset_specification import AssetSpecification


class GeometryGenerator(ABC):
    """
    Contract for geometry engines producing GeometryComponent assemblies.
    """
    @abstractmethod
    def generate(self, spec: AssetSpecification, parameters: Optional[Dict[str, Any]] = None) -> GeometryComponent:
        pass
