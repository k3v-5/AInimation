"""
WeightGenerator computes initial bone influences based on bone proximity and semantic roles.
UAF-81.5 Sections 27, 28.
"""

import math
from typing import Dict, Any, List, Optional
from .skinning_definition import SkinningDefinition, VertexWeights, WeightMethod
from .weight_normalizer import WeightNormalizer
from ..skeleton.skeleton_definition import CharacterSkeletonDefinition
from ...geometry.models.mesh_data import MeshData


class WeightGenerator:
    """
    Computes smooth proximity and inverse-distance skinning weights for character meshes.
    """
    @classmethod
    def generate_weights(
        cls,
        mesh_id: str,
        mesh: MeshData,
        skeleton: CharacterSkeletonDefinition,
        method: WeightMethod = WeightMethod.DISTANCE,
        max_influences: int = 4,
    ) -> SkinningDefinition:
        # Collect deformable bones
        deform_bones = [b for b in skeleton.bones.values() if b.deformation_enabled and b.role.value != "ROOT"]
        if not deform_bones:
            deform_bones = list(skeleton.bones.values())

        weights_dict: Dict[int, VertexWeights] = {}

        for v_idx, v_pos in enumerate(mesh.vertices):
            # Calculate distance to each deformable bone
            bone_dists = []
            for b in deform_bones:
                dx = v_pos[0] - b.position[0]
                dy = v_pos[1] - b.position[1]
                dz = v_pos[2] - b.position[2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                bone_dists.append((b.bone_id, dist))

            # Sort by proximity
            bone_dists.sort(key=lambda x: x[1])

            # Inverse-distance weighting with falloff
            influences: Dict[str, float] = {}
            # Take closest candidates
            candidates = bone_dists[:max_influences]
            for bone_id, d in candidates:
                # 1 / (d^2 + epsilon)
                w = 1.0 / (max(1e-4, d) ** 2)
                influences[bone_id] = w

            weights_dict[v_idx] = VertexWeights(vertex_index=v_idx, influences=influences)

        skinning = SkinningDefinition(
            mesh_id=mesh_id,
            skeleton_id=skeleton.skeleton_id,
            weight_method=method,
            max_influences_per_vertex=max_influences,
            weights=weights_dict,
        )

        # Normalize and return
        return WeightNormalizer.normalize_skinning(skinning)
