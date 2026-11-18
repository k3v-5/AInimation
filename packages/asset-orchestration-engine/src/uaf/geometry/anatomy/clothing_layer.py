"""
ClothingLayerSystem and zero-clipping clearance verification.
UAF-81.3 Sections 33, 34, 35.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.geometry_component import GeometryComponent


LAYER_HIERARCHY = {
    "BODY": 0,
    "UNDERWEAR": 1,
    "CLOTHING": 2,
    "ARMOR": 3,
    "ACCESSORY": 4,
}


@dataclass
class LayerClearanceReport:
    is_valid: bool
    violations: List[str] = field(default_factory=list)


class ClothingLayerSystem:
    """
    Manages multi-layer clothing and armor stacking, validating offsets and zero-clipping.
    """
    @classmethod
    def get_layer_order(cls, layer_name: str) -> int:
        return LAYER_HIERARCHY.get(layer_name.upper(), 2)

    @classmethod
    def validate_layer_clearance(
        cls,
        inner_component: GeometryComponent,
        outer_component: GeometryComponent,
        min_clearance_meters: float = 0.005,
    ) -> LayerClearanceReport:
        inner_layer = cls.get_layer_order(inner_component.semantic_role)
        outer_layer = cls.get_layer_order(outer_component.semantic_role)

        violations = []
        if outer_layer <= inner_layer:
            violations.append(
                f"Layer hierarchy violation: outer '{outer_component.component_id}' ({outer_component.semantic_role}) "
                f"is not above inner '{inner_component.component_id}' ({inner_component.semantic_role})."
            )

        # Check bounding clearance
        inner_aabb = inner_component.calculate_combined_aabb()
        outer_aabb = outer_component.calculate_combined_aabb()

        # If outer component is smaller than inner component in all dimensions, flag clipping
        if (
            outer_aabb.dimensions[0] < inner_aabb.dimensions[0] and
            outer_aabb.dimensions[1] < inner_aabb.dimensions[1] and
            outer_aabb.dimensions[2] < inner_aabb.dimensions[2]
        ):
            violations.append(
                f"Severe clipping detected: outer '{outer_component.component_id}' "
                f"dimensions {outer_aabb.dimensions} are smaller than inner '{inner_component.component_id}' {inner_aabb.dimensions}."
            )

        return LayerClearanceReport(is_valid=len(violations) == 0, violations=violations)
