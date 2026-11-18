from typing import Dict, Any, Optional, Tuple
from ..core.template_registry import TemplateRegistry
from ..templates.base_template import IAssetTemplate
from ..solver.parameter_resolver import ParameterResolver
from ..solver.constraint_solver import ParameterConstraintSolver
from ..execution.procedural_builder import ProceduralBuilder
from ..execution.partial_rebuilder import PartialRebuilder
from ...spec_compiler.core.asset_spec import AssetSpec
from ...correction_execution.providers.blender_provider import IBlenderProvider

class ProceduralTemplatesAPI:
    """
    Procedural Asset Templates & Deterministic Construction API (AOE v15)
    
    Regla Fundamental:
    LA IA NO DEBE MODELAR LO QUE EL MOTOR PUEDE CALCULAR.
    AssetSpec -> Template Selection -> Parameter Mapping -> Deterministic Construction.
    """
    def __init__(self, provider: IBlenderProvider, max_operations_budget: int = 50):
        self.provider = provider
        self.registry = TemplateRegistry()
        self.builder = ProceduralBuilder(provider, max_operations_budget=max_operations_budget)

    def build_from_spec(
        self,
        asset_id: str,
        spec: AssetSpec,
        seed: int = 42,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        # 1. Matching de Plantilla
        template, score = self.registry.match_template(spec)
        if not template:
            return {
                "success": False,
                "construction_mode": "AI_FALLBACK",
                "message": f"TEMPLATE_NOT_FOUND for asset type '{spec.asset_type}'."
            }

        # 2. Resolución de Parámetros
        params = ParameterResolver.resolve_parameters(spec, template)

        # 3. Solver de Restricciones
        ok_const, msg_const = ParameterConstraintSolver.validate_and_solve(params)
        if not ok_const:
            return {"success": False, "construction_mode": "TEMPLATE", "message": msg_const}

        # 4. Construcción del Plan
        plan = template.build_plan(params, seed=seed)

        # 5. Ejecución en Blender Provider
        ok_build, msg_build = self.builder.build_asset(asset_id, plan, dry_run=dry_run)
        return {
            "success": ok_build,
            "construction_mode": "TEMPLATE",
            "template_id": template.template_id,
            "template_version": template.template_version,
            "score": score,
            "parameters": params,
            "plan": plan,
            "message": msg_build
        }

    def apply_parameter_patch(
        self,
        asset_id: str,
        target_component: str,
        parameter_name: str,
        new_value: Any
    ) -> Tuple[bool, str]:
        return PartialRebuilder.apply_parameter_patch_and_rebuild(
            asset_id=asset_id,
            target_component=target_component,
            parameter_name=parameter_name,
            new_value=new_value,
            provider=self.provider
        )
