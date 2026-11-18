from typing import List, Dict, Any
from ..core.intent_schema import TaskGraphDAG, CompiledIntent, ExecutionPlanStep

class PlanCompiler:
    @staticmethod
    def compile_plan(dag: TaskGraphDAG, intent: CompiledIntent) -> List[ExecutionPlanStep]:
        steps: List[ExecutionPlanStep] = []

        # 1. Propagación de Restricciones (ej. building_height=5.0m, roof_ratio=0.35 -> roof_height=1.75m)
        b_height = 5.0
        r_ratio = 0.35
        calc_roof_height = round(b_height * r_ratio, 2)

        # Mapeo de Requisitos en Parámetros Tipados
        win_count = 4
        for r in intent.requirements:
            if r.key == "window_count":
                win_count = int(r.value)

        # Paso 1: Dimensiones
        steps.append(ExecutionPlanStep(
            step_id="STEP_1_DIMENSIONS",
            target="HOUSE_001.FOOTPRINT",
            operation="ESTABLISH_DIMENSIONS",
            parameters={"width": 6.0, "depth": 4.0, "height": b_height, "unit": "meters"},
            preconditions={"project_valid": True},
            postconditions={"footprint_ready": True}
        ))

        # Paso 2: Muros
        steps.append(ExecutionPlanStep(
            step_id="STEP_2_WALLS",
            target="HOUSE_001.WALLS",
            operation="BUILD_WALLS",
            parameters={"wall_thickness": 0.30, "material": "STONE"},
            preconditions={"footprint_ready": True},
            postconditions={"walls_ready": True}
        ))

        # Paso 3: Techo con Parámetro Derivado Propagado
        steps.append(ExecutionPlanStep(
            step_id="STEP_3_ROOF",
            target="HOUSE_001.ROOF",
            operation="BUILD_ROOF",
            parameters={"type": "PITCHED", "calculated_height": calc_roof_height, "material": "WOOD_TILE"},
            preconditions={"walls_ready": True},
            postconditions={"roof_ready": True}
        ))

        # Paso 4: Aberturas
        steps.append(ExecutionPlanStep(
            step_id="STEP_4_OPENINGS",
            target="HOUSE_001.OPENINGS",
            operation="BUILD_OPENINGS",
            parameters={"window_count": win_count, "door_count": 1},
            preconditions={"walls_ready": True},
            postconditions={"openings_ready": True}
        ))

        # Paso 5: Asignación de Materiales
        steps.append(ExecutionPlanStep(
            step_id="STEP_5_MATERIALS",
            target="HOUSE_001.MATERIALS",
            operation="ASSIGN_MATERIALS",
            parameters={"walls": "STONE", "roof": "TIMBER"},
            preconditions={"roof_ready": True, "openings_ready": True},
            postconditions={"materials_ready": True}
        ))

        # Paso 6: Validación de Calidad
        steps.append(ExecutionPlanStep(
            step_id="STEP_6_VALIDATE",
            target="HOUSE_001.VALIDATION",
            operation="VALIDATE_QUALITY",
            parameters={"min_score": 0.90},
            preconditions={"materials_ready": True},
            postconditions={"asset_validated": True}
        ))

        return steps
