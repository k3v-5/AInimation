from typing import Dict, Any, List, Tuple
import math

class DimensionComparator:
    @staticmethod
    def compare_component_dimensions(
        actual_dims: Dict[str, Dict[str, float]],
        expected_dims: Dict[str, Dict[str, float]],
        tolerance: float = 0.005
    ) -> List[Dict[str, Any]]:
        """
        Compara dimensiones reales vs esperadas por componente y eje.
        """
        deltas = []
        for cid, exp_d in expected_dims.items():
            # Buscar en actual_dims por ID exacto o sufijo
            act_d = None
            for a_cid, a_d in actual_dims.items():
                if a_cid == cid or a_cid.endswith(f".{cid}"):
                    act_d = a_d
                    break

            if act_d:
                for axis in ["width", "depth", "height"]:
                    if axis in exp_d and axis in act_d:
                        exp_v = float(exp_d[axis])
                        act_v = float(act_d[axis])
                        diff = round(act_v - exp_v, 4)
                        if not math.isclose(act_v, exp_v, abs_tol=tolerance):
                            deltas.append({
                                "component_id": cid,
                                "axis": axis,
                                "current": act_v,
                                "expected": exp_v,
                                "delta": diff,
                                "relative_error": round(abs(diff) / max(exp_v, 0.001), 4)
                            })
        return deltas
