from typing import Dict, Any, List, Set, Optional
from ..core.knowledge_types import (
    ComponentNecessity, StyleEra, DefectPatternType
)
from ..core.knowledge_schema import (
    ArchetypeDefinition, RuleValidationResult, CorrectionPattern
)

class DesignRuleEngine:
    @staticmethod
    def validate_asset_design(
        archetype: ArchetypeDefinition,
        parameters: Dict[str, Any],
        active_components: Set[str]
    ) -> RuleValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Comprobar Componentes Obligatorios (MANDATORY)
        for sname, slot in archetype.component_slots.items():
            if slot.necessity == ComponentNecessity.MANDATORY and sname not in active_components:
                errors.append(f"MISSING_MANDATORY_COMPONENT: Component '{sname}' is required for archetype '{archetype.archetype_id}'.")

        # 2. Reglas de Incompatibilidad Geométrica
        roof_type = parameters.get("roof_type", "GABLE")
        base_shape = parameters.get("base_shape", "RECTANGULAR")
        if base_shape == "ROUND" and roof_type == "GABLE":
            errors.append("INCOMPATIBLE_COMBINATION: Round tower base is incompatible with GABLE roof geometry (use CONICAL).")

        # 3. Reglas de Pendiente de Tejado
        pitch = parameters.get("roof_pitch", 35.0)
        if pitch < 25.0:
            errors.append(f"DESIGN_RULE_VIOLATION: Roof pitch ({pitch} deg) is below minimum (25 deg) required for tile/thatch drainage.")

        # 4. Reglas de Acoplamiento y Dependencia (Chimenea requiere Techo)
        if "chimney" in active_components and "roof" not in active_components:
            errors.append("UNSATISFIED_ATTACHMENT: Component 'chimney' requires 'roof' attachment target.")

        # 5. Límites de Capacidad de Ranura (Slot Capacity)
        win_count = parameters.get("window_count", 4)
        if "windows" in archetype.component_slots:
            max_win = archetype.component_slots["windows"].max_count
            if win_count > max_win:
                errors.append(f"SLOT_CAPACITY_EXCEEDED: Window count ({win_count}) exceeds slot capacity ({max_win}).")

        # 6. Reglas de Coherencia de Estilo
        wall_mat = str(parameters.get("wall_material", "STONE")).upper()
        if "NEON" in wall_mat or "FUTURISTIC" in wall_mat:
            errors.append(f"STYLE_INCOMPATIBILITY: Material '{wall_mat}' is incompatible with {archetype.style_era.value} architectural style.")

        # 7. Reglas de Altura de Aberturas
        w_height = parameters.get("wall_height", 3.0)
        win_sill = parameters.get("window_sill_height", 1.0)
        win_h = parameters.get("window_height", 1.2)
        if (win_sill + win_h) > w_height:
            errors.append(f"SPATIAL_RULE_VIOLATION: Window top ({win_sill + win_h}m) exceeds wall height ({w_height}m).")

        return RuleValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

class CorrectionPatternEngine:
    KNOWN_PATTERNS: Dict[DefectPatternType, CorrectionPattern] = {
        DefectPatternType.ROOF_TOO_HIGH: CorrectionPattern(
            DefectPatternType.ROOF_TOO_HIGH, "roof_height", 0.80, 0.95, "Reduce roof height by 20% to align with archetype proportions."
        ),
        DefectPatternType.FACADE_TOO_WIDE: CorrectionPattern(
            DefectPatternType.FACADE_TOO_WIDE, "width", 0.85, 0.92, "Reduce facade width by 15% to restore vertical proportion."
        ),
        DefectPatternType.ROOF_TOO_FLAT: CorrectionPattern(
            DefectPatternType.ROOF_TOO_FLAT, "roof_pitch", 1.25, 0.90, "Increase roof pitch by 25% for historic authenticity."
        ),
        DefectPatternType.INSUFFICIENT_OVERHANG: CorrectionPattern(
            DefectPatternType.INSUFFICIENT_OVERHANG, "roof_overhang", 1.20, 0.88, "Increase roof overhang by 20% to avoid wall clipping."
        )
    }

    @classmethod
    def lookup_pattern(cls, defect_type: DefectPatternType) -> Optional[CorrectionPattern]:
        return cls.KNOWN_PATTERNS.get(defect_type)
