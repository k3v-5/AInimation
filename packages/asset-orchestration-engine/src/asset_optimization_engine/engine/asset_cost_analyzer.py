from typing import Any, Dict
from ..core.optimization_schema import AssetCost

class AssetCostAnalyzer:
    @classmethod
    def analyze_cost(
        cls,
        generated_geometry: Any, # F58
        surface_result: Any,     # F59
        context: Dict[str, Any]
    ) -> AssetCost:
        triangles = getattr(generated_geometry, "triangle_count", 80)
        vertices = getattr(generated_geometry, "vertex_count", 48)
        meshes = getattr(generated_geometry, "mesh_count", 1)
        
        materials = len(getattr(surface_result, "materials", {})) or 1
        textures = getattr(surface_result, "texture_count", 2) or 2
        tex_mem = getattr(surface_result, "estimated_vram_mb", 16.0) or 16.0
        draw_calls = max(1, materials * meshes)

        # Cost index 0-100 baseline
        cost_index = round((triangles * 0.4 + tex_mem * 2.0 + materials * 10.0), 2)

        return AssetCost(
            triangle_count=triangles,
            vertex_count=vertices,
            mesh_count=meshes,
            material_count=materials,
            texture_count=textures,
            texture_memory_mb=tex_mem,
            estimated_draw_calls=draw_calls,
            total_cost_index=cost_index
        )
