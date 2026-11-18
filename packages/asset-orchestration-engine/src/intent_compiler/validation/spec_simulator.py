from typing import Tuple, List, Dict, Any
from ..core.intent_schema import BuildSpecification

class SpecificationSimulator:
    @staticmethod
    def simulate_feasibility(spec: BuildSpecification, area_bounds: Tuple[float, float] = None) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Comprobar Densidad / Footprint si aplica
        count_req = spec.requirements.get("count")
        if count_req and area_bounds:
            total_count = count_req.value
            max_area = area_bounds[0] * area_bounds[1]
            min_house_footprint = 16.0 # 4m x 4m
            required_area = total_count * min_house_footprint
            if required_area > max_area:
                errors.append(f"FOOTPRINT_EXCEEDED: Requested {total_count} assets require {required_area}m² which exceeds available area {max_area}m².")

        return len(errors) == 0, errors
