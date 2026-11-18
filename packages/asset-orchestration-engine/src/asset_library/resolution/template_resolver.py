import uuid
from typing import Dict, Any, Tuple, Optional
from ..core.library_schema import BuildIntent, ResolvedBuildSpec, ComponentDefinition
from ..core.dependency_lock import ManifestHasher
from ..components.component_registry import ComponentRegistry
from ..templates.variant_registry import VariantRegistry
from ..templates.preset_registry import PresetRegistry
from .parameter_solver import ParameterHierarchySolver
from .constraint_engine import LibraryConstraintEngine

class TemplateResolver:
    def __init__(
        self,
        comp_registry: ComponentRegistry,
        variant_registry: VariantRegistry,
        preset_registry: PresetRegistry
    ):
        self.comp_registry = comp_registry
        self.variant_registry = variant_registry
        self.preset_registry = preset_registry

    def resolve_intent(self, intent: BuildIntent) -> Tuple[bool, Optional[ResolvedBuildSpec], str]:
        # 1. Comprobar parámetros desconocidos
        KNOWN_PARAMS = {"blade_length", "blade_width", "blade_thickness", "guard_width", "guard_thickness", "handle_length", "handle_radius", "pommel_size", "total_length"}
        all_incoming = list(intent.parameters.keys()) + list(intent.user_overrides.keys())
        for p in all_incoming:
            if p not in KNOWN_PARAMS:
                return False, None, f"UNKNOWN_PARAMETER: Parameter '{p}' is not defined in template schema."

        # 2. Cargar Variante y Preset
        var_def = self.variant_registry.get_variant(intent.variant_id) if intent.variant_id else None
        pre_def = self.preset_registry.get_preset(intent.preset_id) if intent.preset_id else None

        # 3. Selección de Componentes
        comp_selection = dict(var_def.component_selection if var_def else {
            "blade": "blade_standard",
            "guard": "guard_cross",
            "handle": "handle_leather",
            "pommel": "pommel_round"
        })
        comp_selection.update(intent.component_overrides)

        resolved_components: Dict[str, ComponentDefinition] = {}
        for role, comp_id in comp_selection.items():
            comp_obj = self.comp_registry.get_component(comp_id)
            if not comp_obj:
                return False, None, f"UNKNOWN_COMPONENT: Component '{comp_id}' for role '{role}' does not exist in library."
            resolved_components[role] = comp_obj

        # 4. Resolver Parámetros por Jerarquía
        template_defaults = {
            "total_length": 1.20,
            "blade_length": 0.90,
            "blade_width": 0.05,
            "blade_thickness": 0.02,
            "guard_width": 0.18,
            "handle_length": 0.22
        }
        ok_p, resolved_params, msg_p = ParameterHierarchySolver.solve_parameters(
            template_defaults=template_defaults,
            preset_overrides=pre_def.parameter_overrides if pre_def else {},
            variant_overrides=var_def.parameter_overrides if var_def else {},
            ai_parameters=intent.parameters,
            user_overrides=intent.user_overrides
        )

        # 5. Validación de Restricciones
        ok_c, msg_c = LibraryConstraintEngine.validate_constraints(resolved_params)
        if not ok_c:
            return False, None, msg_c

        # 6. Generar Dependency Lock & Manifest Hash
        dep_lock = {role: comp.version for role, comp in resolved_components.items()}
        manifest_hash = ManifestHasher.calculate_manifest_hash(
            template_id=intent.template_id,
            template_version="1.0.0",
            component_versions=dep_lock,
            resolved_parameters=resolved_params,
            seed=intent.seed
        )

        spec = ResolvedBuildSpec(
            spec_id=f"bspec_{uuid.uuid4().hex[:6]}",
            template_id=intent.template_id,
            template_version="1.0.0",
            variant_id=intent.variant_id or "Default",
            preset_id=intent.preset_id,
            components=resolved_components,
            resolved_parameters=resolved_params,
            dependency_lock=dep_lock,
            manifest_hash=manifest_hash
        )

        return True, spec, "Build intent successfully resolved."
