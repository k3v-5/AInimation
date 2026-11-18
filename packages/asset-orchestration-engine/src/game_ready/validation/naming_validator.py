from typing import Tuple, Optional, List, Set

class NamingValidator:
    VALID_PREFIXES = ["SM_", "SK_", "M_", "MI_", "T_", "NS_", "UCX_"]

    @classmethod
    def validate_name(cls, name: str, expected_prefix: str = "SM_") -> Tuple[bool, Optional[str]]:
        if not name.startswith(expected_prefix):
            return False, f"NAMING_INVALID: Asset name '{name}' must start with standard Unreal prefix '{expected_prefix}'."
        
        # Evitar nombres por defecto de Blender
        bad_patterns = ["Cube", "Cube.001", "Object", "Object001", "Mesh", "Mesh.001"]
        if name in bad_patterns:
            return False, f"NAMING_INVALID: Asset name '{name}' uses generic default pattern."

        return True, None

    @classmethod
    def check_collisions(cls, names: List[str]) -> Tuple[bool, Optional[str]]:
        seen: Set[str] = set()
        for n in names:
            if n in seen:
                return False, f"NAMING_COLLISION: Duplicate asset/object name detected '{n}'."
            seen.add(n)
        return True, None
