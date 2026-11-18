import uuid
from typing import Dict, Any, List
from .base_template import IAssetTemplate
from ..core.template_schema import ParameterDefinition, ParameterType, ComponentDefinition
from ..core.construction_plan import ConstructionPlan, ConstructionOperation

class SwordTemplate(IAssetTemplate):
    @property
    def template_id(self) -> str:
        return "weapon.sword.standard"

    @property
    def template_version(self) -> str:
        return "1.0.0"

    @property
    def supported_asset_types(self) -> List[str]:
        return ["SWORD", "LONGSWORD", "BROADSWORD"]

    def get_parameter_definitions(self) -> Dict[str, ParameterDefinition]:
        return {
            "total_length": ParameterDefinition("total_length", ParameterType.FLOAT, default_value=1.20, min_value=0.50, max_value=2.50),
            "blade_length": ParameterDefinition("blade_length", ParameterType.FLOAT, default_value=0.90, min_value=0.30, max_value=1.80),
            "blade_width": ParameterDefinition("blade_width", ParameterType.FLOAT, default_value=0.05, min_value=0.01, max_value=0.20),
            "blade_thickness": ParameterDefinition("blade_thickness", ParameterType.FLOAT, default_value=0.02, min_value=0.005, max_value=0.05),
            "guard_width": ParameterDefinition("guard_width", ParameterType.FLOAT, default_value=0.18, min_value=0.05, max_value=0.50),
            "guard_thickness": ParameterDefinition("guard_thickness", ParameterType.FLOAT, default_value=0.04, min_value=0.01, max_value=0.10),
            "handle_length": ParameterDefinition("handle_length", ParameterType.FLOAT, default_value=0.22, min_value=0.10, max_value=0.60),
            "handle_radius": ParameterDefinition("handle_radius", ParameterType.FLOAT, default_value=0.03, min_value=0.01, max_value=0.08),
            "pommel_size": ParameterDefinition("pommel_size", ParameterType.FLOAT, default_value=0.04, min_value=0.02, max_value=0.12)
        }

    def build_plan(self, params: Dict[str, Any], seed: int = 42) -> ConstructionPlan:
        # Calcular dimensiones componentes
        b_len = params.get("blade_length", 0.90)
        b_w = params.get("blade_width", 0.05)
        b_th = params.get("blade_thickness", 0.02)

        g_w = params.get("guard_width", 0.18)
        g_th = params.get("guard_thickness", 0.04)

        h_len = params.get("handle_length", 0.22)
        h_rad = params.get("handle_radius", 0.03)

        p_size = params.get("pommel_size", 0.04)

        ops = [
            # 1. Crear componentes geométricos
            ConstructionOperation(
                operation_id="op_blade",
                type="CREATE_COMPONENT",
                target_component="blade",
                parameters={"dimensions": (b_w, b_th, b_len), "material": {"metallic": 0.90, "roughness": 0.25}},
                dependencies=[]
            ),
            ConstructionOperation(
                operation_id="op_guard",
                type="CREATE_COMPONENT",
                target_component="guard",
                parameters={"dimensions": (g_w, g_th, g_th), "material": {"metallic": 0.90, "roughness": 0.30}},
                dependencies=[]
            ),
            ConstructionOperation(
                operation_id="op_grip",
                type="CREATE_COMPONENT",
                target_component="grip",
                parameters={"dimensions": (h_rad, h_rad, h_len), "material": {"material_type": "LEATHER", "roughness": 0.80}},
                dependencies=[]
            ),
            ConstructionOperation(
                operation_id="op_pommel",
                type="CREATE_COMPONENT",
                target_component="pommel",
                parameters={"dimensions": (p_size, p_size, p_size), "material": {"metallic": 0.90, "roughness": 0.30}},
                dependencies=[]
            ),
            # 2. Ensamblaje Jerárquico
            ConstructionOperation(
                operation_id="op_assemble",
                type="ASSEMBLE",
                target_component="root",
                parameters={"hierarchy": {"guard": "blade", "grip": "guard", "pommel": "grip"}},
                dependencies=["op_blade", "op_guard", "op_grip", "op_pommel"]
            )
        ]

        return ConstructionPlan(
            plan_id=f"cplan_{uuid.uuid4().hex[:6]}",
            template_id=self.template_id,
            template_version=self.template_version,
            parameters=params,
            components=["blade", "guard", "grip", "pommel"],
            operations=ops,
            seed=seed,
            estimated_objects=4,
            estimated_polycount=650
        )
