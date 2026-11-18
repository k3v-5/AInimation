"""
WeightNormalizer enforces sum(weights)=1.0, influence caps, and weight pruning.
UAF-81.5 Sections 29, 30, 31.
"""

from typing import Dict, List, Tuple
from .skinning_definition import SkinningDefinition, VertexWeights


class WeightNormalizer:
    """
    Mathematical normalizer ensuring physical deformation invariants for all vertices.
    """
    @classmethod
    def normalize_skinning(
        cls,
        skinning: SkinningDefinition,
        threshold: float = 0.001,
    ) -> SkinningDefinition:
        max_inf = skinning.max_influences_per_vertex

        for v_idx, vw in skinning.weights.items():
            # 1. Prune tiny influences below threshold
            filtered = {b: w for b, w in vw.influences.items() if w >= threshold}

            # If all pruned, pick the largest original
            if not filtered and vw.influences:
                best_bone = max(vw.influences, key=vw.influences.get)
                filtered = {best_bone: 1.0}

            # 2. Keep only top max_influences
            if len(filtered) > max_inf:
                sorted_bones = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:max_inf]
                filtered = dict(sorted_bones)

            # 3. Normalize remaining to sum to 1.0
            total = sum(filtered.values())
            if total > 1e-8:
                normalized = {b: w / total for b, w in filtered.items()}
            else:
                normalized = {b: 1.0 / len(filtered) for b in filtered} if filtered else {}

            vw.influences = normalized

        return skinning

    @classmethod
    def validate_skinning(
        cls,
        skinning: SkinningDefinition,
        tolerance: float = 1e-4,
    ) -> Tuple[bool, List[str]]:
        issues = []
        max_inf = skinning.max_influences_per_vertex

        for v_idx, vw in skinning.weights.items():
            if not vw.influences:
                issues.append(f"Vertex {v_idx} has zero bone influences.")
                continue

            if len(vw.influences) > max_inf:
                issues.append(f"Vertex {v_idx} has {len(vw.influences)} influences, exceeding max of {max_inf}.")

            total = sum(vw.influences.values())
            if abs(total - 1.0) > tolerance:
                issues.append(f"Vertex {v_idx} weights do not sum to 1.0 (sum = {total:.6f}).")

        return (len(issues) == 0, issues)
