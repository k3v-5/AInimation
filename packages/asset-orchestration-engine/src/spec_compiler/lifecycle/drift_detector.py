from typing import Dict, Any, Tuple
from ..core.asset_spec import AssetSpec

class SpecificationDriftDetector:
    @staticmethod
    def check_drift(actual_measurements: Dict[str, float], spec: AssetSpec) -> Tuple[str, float, str]:
        """
        Devuelve (drift_severity, drift_percentage, message).
        drift_severity: NONE, LOW, MEDIUM, HIGH, CRITICAL
        """
        # Comparar blade length si existe
        if "blade_length" in actual_measurements and "blade" in spec.components:
            spec_blade_dim = spec.components["blade"].dimensions.get("length")
            if spec_blade_dim:
                target_l = spec_blade_dim.target
                actual_l = actual_measurements["blade_length"]
                drift_pct = abs(actual_l - target_l) / target_l

                if drift_pct > 0.20:
                    return "HIGH", round(drift_pct, 4), f"SPEC_DRIFT: Blade length deviated by {drift_pct*100:.1f}% ({actual_l:.2f}m vs spec {target_l:.2f}m)."
                elif drift_pct > 0.08:
                    return "MEDIUM", round(drift_pct, 4), f"SPEC_DRIFT: Moderate drift of {drift_pct*100:.1f}%."

        return "NONE", 0.0, "No significant drift detected."
