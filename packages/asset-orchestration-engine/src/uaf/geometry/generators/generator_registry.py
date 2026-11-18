"""
GeometryGeneratorRegistry indexes all physical geometry generation backends.
UAF-81.3 Section 82, 83.
"""

from typing import List, Optional
from ...contracts.registry import BaseRegistry
from .generator_interface import GeometryGenerator


class GeometryGeneratorRegistry(BaseRegistry[GeometryGenerator]):
    def __init__(self):
        super().__init__(name="GeometryGeneratorRegistry")
