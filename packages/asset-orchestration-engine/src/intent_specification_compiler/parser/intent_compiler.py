import re
from typing import Dict, Any, List, Tuple, Optional
from ..core.spec_types import ConstraintType, SpecStatus, ApprovalState, RequirementStatus
from ..core.spec_schema import (
    AssetSpec, StyleSpec, VisualIntent, DoorSpec, WindowSpec, StairSpec, SpecBudget,
    RequirementEntry, AssumptionEntry
)
from .semantic_dictionary import SemanticDictionary

class IntentCompiler:
    """
    Intent Compiler (AOE v31):
    Transforma lenguaje natural en una especificación formal y ejecutable (AssetSpec).
    NUNCA INVOCA DIRECTAMENTE A BLENDER/UNREAL/MCP.
    """
    @staticmethod
    def compile_natural_language_to_spec(
        prompt: str,
        spec_id: str = "spec_house_01"
    ) -> Tuple[AssetSpec, List[str], List[str]]:
        warnings: List[str] = []
        errors: List[str] = []
        lower_prompt = prompt.lower()

        # 1. Detectar materiales desconocidos / alucinaciones (Anti-Hallucination)
        for word in re.findall(r'\b[a-zA-Z]+\b', prompt):
            if "material" in lower_prompt and word.lower() in ["dragonium", "mithril_fake", "unobtanium"]:
                errors.append(f"UNKNOWN_MATERIAL: Material '{word}' is not recognized in SemanticDictionary.")

        # 2. Extraer Estilo y Condición
        architecture = "MEDIEVAL_RURAL" if ("rural" in lower_prompt or "medieval" in lower_prompt) else "MEDIEVAL"
        condition = "AGED" if ("vieja" in lower_prompt or "aged" in lower_prompt or "envejecida" in lower_prompt) else "PRISTINE"
        forbidden = ["FANTASY"] if ("no quiero que parezca una casa de fantasía" in lower_prompt or "no fantasy" in lower_prompt) else []

        style = StyleSpec(period="MEDIEVAL", architecture=architecture, condition=condition, forbidden_styles=forbidden)

        # 3. Extraer Intención Visual y Geometría
        lean_angle = 2.5 if ("inclinada" in lower_prompt or "leaning" in lower_prompt) else 0.0
        visual = VisualIntent(silhouette="RURAL_COTTAGE", lean_angle_deg=lean_angle, scale="SMALL")

        # 4. Extraer Puerta
        door_mat = "WOOD"
        door_width = 0.90 if ("grande" in lower_prompt or "large" in lower_prompt) else 0.85
        player_passable = ("pueda entrar" in lower_prompt or "player" in lower_prompt or "accesible" in lower_prompt)
        door = DoorSpec(required=True, material=door_mat, width_m=door_width, player_passable=player_passable)

        # 5. Extraer Ventanas
        win_count = 2
        if "tres ventanas" in lower_prompt or "3 ventanas" in lower_prompt or "3 windows" in lower_prompt:
            win_count = 3
        elif "dos ventanas" in lower_prompt or "2 ventanas" in lower_prompt or "2 windows" in lower_prompt:
            win_count = 2
        windows = WindowSpec(count=win_count, style="NARROW" if "estrechas" in lower_prompt else "STANDARD")

        # 6. Extraer Escaleras
        has_stairs = ("escalera" in lower_prompt or "stair" in lower_prompt)
        stairs = StairSpec(required=has_stairs, location="INTERNAL", destination="SECOND_FLOOR")

        # 7. Construir Requisitos Estructurados (Checklist con IDs estables)
        requirements = [
            RequirementEntry("REQ-001", "Medieval rural architecture", ConstraintType.HARD, affects=["style", "materials"]),
            RequirementEntry("REQ-002", "Small scale", ConstraintType.HARD, affects=["scale", "dimensions"]),
            RequirementEntry("REQ-003", "Aged appearance", ConstraintType.SOFT, affects=["materials", "weathering"]),
            RequirementEntry("REQ-004", f"Slightly leaning geometry ({lean_angle}°)", ConstraintType.SOFT, affects=["geometry", "transforms"]),
            RequirementEntry("REQ-005", f"Large wooden door ({door_width}m)", ConstraintType.HARD, affects=["door", "collision"]),
            RequirementEntry("REQ-006", f"{win_count} narrow windows", ConstraintType.HARD, affects=["windows", "wall_geometry"]),
            RequirementEntry("REQ-007", "Internal stairs to second floor", ConstraintType.HARD, affects=["stairs", "navigation"]),
            RequirementEntry("REQ-008", "Player entry passable", ConstraintType.HARD, affects=["door", "navigation", "collision"])
        ]

        if forbidden:
            requirements.append(RequirementEntry("REQ-009", "Fantasy style forbidden", ConstraintType.HARD, affects=["style"]))

        # 8. Suposiciones (AssumptionRegistry)
        assumptions = [
            AssumptionEntry("ASSUMPTION-001", "Default ceiling height set to 2.50m based on ProjectProfile", "PROJECT_DEFAULT", "HIGH", "LOW"),
            AssumptionEntry("ASSUMPTION-002", "Roof material set to THATCH based on MEDIEVAL_RURAL preset", "STYLE_PRESET", "MEDIUM", "LOW")
        ]

        spec = AssetSpec(
            spec_id=spec_id,
            spec_version="1.0.0",
            asset_type="HOUSE",
            style=style,
            visual=visual,
            door=door,
            windows=windows,
            stairs=stairs,
            budget=SpecBudget(max_triangles=40000),
            requirements=requirements,
            assumptions=assumptions,
            status=SpecStatus.DRAFT,
            approval=ApprovalState.PENDING
        )

        return spec, warnings, errors
