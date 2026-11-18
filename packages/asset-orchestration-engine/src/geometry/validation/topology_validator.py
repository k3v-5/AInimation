from typing import Tuple, List
from ..generators.base_generator import GeneratedGeometry

class TopologyValidator:
    @staticmethod
    def validate_topology(geo: GeneratedGeometry) -> Tuple[bool, List[str]]:
        errors = []
        # Verificar índices de caras válidos
        v_count = len(geo.vertices)
        for f_idx, face in enumerate(geo.faces):
            if len(face) < 3:
                errors.append(f"Face {f_idx} has fewer than 3 vertices ({len(face)})")
            for v in face:
                if v < 0 or v >= v_count:
                    errors.append(f"Face {f_idx} references invalid vertex index {v} (total={v_count})")

        return len(errors) == 0, errors
