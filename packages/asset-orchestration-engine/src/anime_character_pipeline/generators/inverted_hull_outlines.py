"""
NPR Inverted Hull Outlines Generator (Guilty Gear / Genshin Standard)
=====================================================================
Applies the industry-standard Inverted Hull Solidify technique to render
clean, dynamic, camera-invariant anime ink outlines directly on 3D meshes.
"""

from typing import Dict, Any, Tuple
from ..core.anime_schema import NPROutlineSpec


class InvertedHullOutlines:
    """Manages Inverted Hull outline setup for NPR anime characters."""

    def __init__(self, spec: NPROutlineSpec):
        self.spec = spec

    def compute_modifier_parameters(self) -> Dict[str, Any]:
        """Calculates exact Solidify parameters for anime ink line width."""
        return {
            "name": "NPR_InvertedHull_Outline",
            "type": "SOLIDIFY",
            "thickness": self.spec.thickness,
            "offset": self.spec.offset,
            "use_flip_normals": True,
            "use_rim": True,
            "material_offset": 1,  # Points to the second material slot (Outline Mat)
            "material_offset_rim": 1,
            "use_quality_normals": True
        }

    def get_blender_outline_code(self) -> str:
        """Returns Python code for Blender to configure Inverted Hull outlines."""
        code = '''
def setup_inverted_hull_outline(obj, outline_mat, thickness=0.0035):
    """
    Applies the Arc System Works Inverted Hull technique:
    1. Adds outline material in second slot
    2. Adds Solidify modifier with flipped normals and backface culling
    """
    if obj.type != 'MESH':
        return None
    
    # Ensure outline material exists in slots
    if outline_mat.name not in [m.name for m in obj.data.materials if m]:
        obj.data.materials.append(outline_mat)
    
    mat_idx = [i for i, m in enumerate(obj.data.materials) if m and m.name == outline_mat.name][0]

    mod = obj.modifiers.get("NPR_InvertedHull_Outline")
    if not mod:
        mod = obj.modifiers.new(name="NPR_InvertedHull_Outline", type='SOLIDIFY')
    
    mod.thickness = thickness
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = True
    mod.material_offset = mat_idx
    mod.material_offset_rim = mat_idx
    mod.use_quality_normals = True
    return mod
'''
        return code
