import copy
from typing import Dict, Any, Optional, Tuple, List
from ..core.amsl_types import ConstraintType
from ..core.amsl_schema import (
    AssetSpecification, BuildRequirements, ConstraintSpec
)
from .spec_validator import AMSLValidator

class SpecificationCompiler:
    """
    AMSL Specification Compiler (AOE v35):
    Valida la especificación, resuelve restricciones, detecta conflictos de bloqueo,
    calcula la especificación efectiva y deriva los Requisitos de Construcción para el BuildPlanner.
    """
    @staticmethod
    def compile(
        spec: AssetSpecification,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Tuple[AssetSpecification, BuildRequirements]:
        effective = copy.deepcopy(spec)
        overrides = overrides or {}

        # 1. Validar integridad de esquema y unidades
        AMSLValidator.validate_spec(effective)

        # 2. Comprobar conflictos con restricciones bloqueadas (Locked Constraint Conflicts)
        locked_rules = []
        for c in effective.constraints:
            if c.type == ConstraintType.HARD and "preserve" in c.rule:
                locked_rules.append(c.rule["preserve"])

        for target_prop, new_val in overrides.items():
            for locked in locked_rules:
                if locked in target_prop:
                    raise ValueError(f"SPECIFICATION_CONFLICT: Cannot modify locked property '{target_prop}' (Locked rule: preserve {locked}).")

        # 3. Aplicar Overrides sobre la especificación efectiva
        for prop, val in overrides.items():
            if prop == "dimensions.width" and effective.dimensions.width:
                effective.dimensions.width.target = float(val)
            elif prop == "structure.roof.pitch":
                effective.structure.roof["pitch"] = float(val)
            elif prop.startswith("material.") and effective.materials:
                mat_id = prop.split(".")[1]
                for m in effective.materials:
                    if m.material_id == mat_id:
                        m.base_color = str(val)

        # 4. Determinar Requisitos de Construcción (Build Requirements)
        req_builders: List[str] = []
        deps: List[str] = []
        requires_rebuild = False
        mod_cost = "LOW"

        # Si sólo se modificó material
        if overrides and all(k.startswith("material.") for k in overrides.keys()):
            req_builders = ["MaterialBuilder"]
            mod_cost = "LOW"
            requires_rebuild = False
        # Si se modificó techo
        elif overrides and any("roof" in k for k in overrides.keys()):
            req_builders = ["RoofBuilder", "WallBuilder"]
            deps = ["WALL_OPENINGS", "ROOF_SUPPORT", "COLLISION"]
            mod_cost = "HIGH"
            requires_rebuild = True
        # Construcción inicial
        else:
            req_builders = ["FoundationBuilder", "WallBuilder", "OpeningBuilder", "RoofBuilder", "MaterialBuilder"]
            deps = ["FOUNDATION", "WALLS", "DOOR", "WINDOWS", "ROOF"]
            mod_cost = "HIGH"
            requires_rebuild = True

        build_reqs = BuildRequirements(
            required_builders=req_builders,
            modification_cost=mod_cost,
            requires_rebuild=requires_rebuild,
            dependencies=deps
        )

        return effective, build_reqs
