"""
ProceduralPrimitiveGenerator generates procedural geometry using primitives and optional remesh.
UAF-81.3 Sections 86, 102.
"""

from typing import Dict, Any, Optional
from ..models.geometry_component import GeometryComponent
from ..models.mesh_data import MeshData
from ..models.transform import Transform3D
from .generator_interface import GeometryGenerator
from ...core.specification.asset_specification import AssetSpecification


class ProceduralPrimitiveGenerator(GeometryGenerator):
    """
    Fast CSG / primitive procedural geometry synthesis suitable for simple robots,
    blockouts, and rapid prototyping with optional volume fusion/remesh.
    """
    def __init__(self, name: str = "ProceduralPrimitiveGenerator"):
        self.name = name

    def generate(self, spec: AssetSpecification, parameters: Optional[Dict[str, Any]] = None) -> GeometryComponent:
        params = parameters or spec.parameters
        size = float(params.get("size", 1.0))
        enable_remesh = bool(params.get("enable_remesh", True))

        # Base primitive form (centered cube or cylinder)
        base_mesh = MeshData.create_cube(size=size)
        base_mesh.calculate_facet_normals()

        root = GeometryComponent(
            component_id=f"root_{spec.identity.asset_id}",
            semantic_role="STRUCTURAL",
            transform=Transform3D(position=[0.0, 0.0, 0.0]),
            mesh_data=base_mesh,
            quality_level="prototype",
        )

        # Attach secondary primitive (head/sensor)
        sensor_mesh = MeshData.create_cube(size=size * 0.4)
        sensor_mesh.calculate_facet_normals()
        sensor_comp = GeometryComponent(
            component_id=f"sensor_{spec.identity.asset_id}",
            semantic_role="FUNCTIONAL",
            transform=Transform3D(position=[0.0, 0.0, size * 0.7]),
            mesh_data=sensor_mesh,
        )
        root.add_child(sensor_comp)

        return root
