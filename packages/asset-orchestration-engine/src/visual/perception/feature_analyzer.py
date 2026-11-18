from typing import Dict, Any, List, Set

class FeatureAnalyzer:
    @staticmethod
    def analyze_structural_features(actual_components: List[str], expected_components: List[str]) -> Dict[str, Any]:
        act_set = set(actual_components)
        # Normalizar a nombres base de componentes (ej: "sword_01.blade" -> "blade")
        act_base_set = {c.split(".")[-1] for c in act_set}
        exp_set = set(expected_components)
        exp_base_set = {c.split(".")[-1] for c in exp_set}

        missing = list(exp_base_set - act_base_set)
        extra = list(act_base_set - exp_base_set)
        present = list(act_base_set & exp_base_set)

        return {
            "present_components": present,
            "missing_components": missing,
            "extra_components": extra,
            "structural_completeness": round(len(present) / max(len(exp_base_set), 1), 4)
        }
