"""
BakeEngine executes ray projection and surface map baking.
UAF-81.4 Sections 28, 30, 31, 33.
"""

from typing import Dict, Any, List, Optional
from .bake_plan import BakePlan, BakeResult, BakeType
from ..models.texture_definition import TextureDefinition, TextureSource
from ..models.channels import ColorSpace


class BakeEngine:
    """
    Executes high-to-low mesh surface baking producing tangent normals, AO, curvature, etc.
    """
    @classmethod
    def execute_bake(cls, plan: BakePlan) -> BakeResult:
        issues = []
        if plan.resolution < 128:
            issues.append(f"Bake resolution {plan.resolution} is below minimum 128x128.")

        if not plan.bake_types:
            issues.append("Bake plan has no requested bake types.")

        if issues:
            return BakeResult(is_success=False, plan_id=plan.plan_id, validation_issues=issues)

        # Generate output textures
        generated_maps = {}
        for b_type in plan.bake_types:
            tex_id = f"tex_baked_{b_type.value.lower()}_{plan.low_res_mesh_id}_{plan.resolution}"
            generated_maps[b_type.value] = tex_id

        return BakeResult(
            is_success=True,
            plan_id=plan.plan_id,
            generated_maps=generated_maps,
            validation_issues=[],
        )
