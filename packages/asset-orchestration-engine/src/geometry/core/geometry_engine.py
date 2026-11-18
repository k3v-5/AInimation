import time
import copy
from typing import Dict, Any, Optional, List, Tuple
from ..generators.generator_registry import GeometryGeneratorRegistry
from ..generators.base_generator import GeneratedGeometry
from ..components.component_registry import ComponentRegistry, GeometricComponent
from ..components.component_dependencies import ComponentDependencies
from ..parameters.parameter_resolver import ParameterResolver
from ..rebuild.dirty_tracker import DirtyTracker
from ..rebuild.dependency_analyzer import DependencyAnalyzer
from ..rebuild.rebuild_planner import RebuildPlanner
from ..validation.geometry_validator import GeometryValidator
from ..validation.dimension_validator import DimensionValidator
from ..validation.topology_validator import TopologyValidator
from .geometry_context import GeometryContext

class GeometryEngine:
    """
    Geometry Construction Engine (AOE v3)
    
    Responsabilidad: Convertir planes y parámetros en geometría 3D determinista.
    Principio: La geometría es una consecuencia de los parámetros.
    """
    def __init__(self, generator_registry: Optional[GeometryGeneratorRegistry] = None):
        self.generators = generator_registry or GeometryGeneratorRegistry()
        self.registry = ComponentRegistry()
        self.dependencies = ComponentDependencies()
        self.dirty_tracker = DirtyTracker()
        self.dependency_analyzer = DependencyAnalyzer(self.dependencies, self.dirty_tracker)
        self.rebuild_planner = RebuildPlanner(self.dirty_tracker, self.registry)
        self.context = GeometryContext()
        self.derived_rules: Dict[str, Dict[str, str]] = {} # comp_id -> {param: formula}

    def create_component(
        self,
        asset_id: str,
        component_id: str,
        generator_type: str,
        parameters: Dict[str, Any],
        parent_id: Optional[str] = None,
        scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # 1. Validar Scope
        if scope and component_id not in scope and component_id.split(".")[-1] not in scope:
            return {"success": False, "error_code": "SCOPE_VIOLATION", "message": f"Component '{component_id}' is not in allowed scope {scope}."}

        # 2. Obtener generador
        gen = self.generators.get(generator_type)
        if not gen:
            return {"success": False, "error_code": "GENERATOR_NOT_FOUND", "message": f"Generator '{generator_type}' not registered."}

        # 3. Validar Parámetros
        val_ok, val_err = gen.validate_parameters(parameters)
        if not val_ok:
            return {"success": False, "error_code": "INVALID_PARAMETER", "message": val_err}

        # 4. Construir Geometría
        t0 = time.time()
        geo = gen.build(component_id, parameters, self.context)
        t_build = time.time() - t0

        # 5. Validar Geometría
        g_ok, g_errs = GeometryValidator.validate_geometry(geo)
        if not g_ok:
            return {"success": False, "error_code": "GEOMETRY_BUILD_FAILED", "message": "; ".join(g_errs)}

        # 6. Registrar Componente
        full_cid = f"{asset_id}.{component_id}" if "." not in component_id else component_id
        comp = GeometricComponent(
            component_id=full_cid,
            asset_id=asset_id,
            component_type=component_id.split(".")[-1],
            generator_type=generator_type,
            parameters=dict(parameters),
            parent_id=parent_id,
            geometry=geo,
            version=1,
            status="BUILT"
        )
        self.registry.register(comp)
        if parent_id:
            self.dependencies.set_parent(full_cid, parent_id)
        self.dirty_tracker.mark_built(full_cid)
        self.context.record_metrics(t_build, len(geo.vertices), geo.triangle_count)

        return {
            "success": True,
            "component_id": full_cid,
            "geometry_id": geo.geometry_id,
            "version": 1,
            "vertices_count": len(geo.vertices),
            "triangle_count": geo.triangle_count,
            "dimensions": geo.dimensions,
            "status": "BUILT"
        }

    def set_derived_rule(self, target_comp_id: str, param_name: str, formula: str):
        """Define una relación geométrica derivada (ej. guard.width = blade.width * 3)."""
        if target_comp_id not in self.derived_rules:
            self.derived_rules[target_comp_id] = {}
        self.derived_rules[target_comp_id][param_name] = formula
        # Registrar dependencia paramétrica inversa
        import re
        matches = re.findall(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', formula)
        for src_comp, _ in matches:
            self.dependencies.add_parametric_dependency(src_comp, target_comp_id)

    def modify_component(
        self,
        component_id: str,
        parameter_or_changes: Any,
        operation: str = "SET",
        value: Any = None,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Modifica quirúrgicamente un componente y reconstruye ÚNICAMENTE los componentes afectados.
        """
        comp = self.registry.get(component_id)
        if not comp:
            return {"success": False, "error_code": "COMPONENT_NOT_FOUND", "message": f"Component '{component_id}' does not exist."}

        # 1. Scope Check
        if scope and comp.component_id not in scope and comp.component_type not in scope:
            return {"success": False, "error_code": "SCOPE_VIOLATION", "message": f"Component '{comp.component_id}' outside allowed scope {scope}."}

        # Snapshot previo para rollback en caso de fallo
        snapshot_params = copy.deepcopy(comp.parameters)
        snapshot_geo = comp.geometry

        # 2. Calcular nuevos parámetros
        new_params = dict(comp.parameters)
        if isinstance(parameter_or_changes, dict):
            for k, v in parameter_or_changes.items():
                new_params[k] = v
        elif isinstance(parameter_or_changes, str):
            p_name = parameter_or_changes
            cur_v = float(new_params.get(p_name, 1.0))
            if operation == "SET": new_params[p_name] = float(value)
            elif operation == "INCREMENT": new_params[p_name] = cur_v + float(value)
            elif operation == "MULTIPLY": new_params[p_name] = cur_v * float(value)
            elif operation == "DECREMENT": new_params[p_name] = cur_v - float(value)

        # 3. Detección NO_OP
        if new_params == comp.parameters:
            return {"success": True, "status": "NO_OP", "component_id": comp.component_id, "modified_components": []}

        # 4. Validar parámetros
        gen = self.generators.get(comp.generator_type)
        if not gen:
            return {"success": False, "error_code": "GENERATOR_NOT_FOUND", "message": f"Generator '{comp.generator_type}' not found."}

        val_ok, val_err = gen.validate_parameters(new_params)
        if not val_ok:
            return {"success": False, "error_code": "INVALID_PARAMETER", "message": val_err}

        # 5. Análisis de Dependencias y Dirty Tracking
        dirty_list = self.dependency_analyzer.propagate_dirty(comp.component_id)

        if dry_run:
            return {
                "success": True,
                "status": "dry_run",
                "component_id": comp.component_id,
                "dirty_components": dirty_list,
                "new_parameters": new_params
            }

        try:
            # 6. Aplicar nuevos parámetros al componente modificado
            comp.parameters = new_params
            rebuilt_components = []

            # 7. Reconstruir ÚNICAMENTE los componentes en dirty_list
            all_context_params = {c.component_id: c.parameters for c in self.registry.list_components(comp.asset_id)}

            for d_cid in dirty_list:
                d_comp = self.registry.get(d_cid)
                if not d_comp: continue

                # Recalcular derivadas si existen
                if d_cid in self.derived_rules:
                    d_comp.parameters = ParameterResolver.resolve_derived_parameters(
                        d_cid, d_comp.parameters, all_context_params, self.derived_rules[d_cid]
                    )

                d_gen = self.generators.get(d_comp.generator_type)
                new_geo = d_gen.build(d_comp.component_id, d_comp.parameters, self.context)
                
                # Validar geometría reconstruida
                g_ok, g_errs = GeometryValidator.validate_geometry(new_geo)
                if not g_ok:
                    raise RuntimeError(f"GEOMETRY_VALIDATION_FAILED: {'; '.join(g_errs)}")

                d_comp.geometry = new_geo
                d_comp.version += 1
                d_comp.status = "BUILT"
                self.dirty_tracker.mark_built(d_cid)
                rebuilt_components.append(d_cid)

            return {
                "success": True,
                "status": "completed",
                "component_id": comp.component_id,
                "rebuilt_components": rebuilt_components,
                "unaffected_components": [c.component_id for c in self.registry.list_components(comp.asset_id) if c.component_id not in rebuilt_components],
                "new_version": comp.version,
                "dimensions": comp.geometry.dimensions
            }

        except Exception as e:
            # Rollback automático ante cualquier error
            comp.parameters = snapshot_params
            comp.geometry = snapshot_geo
            self.dirty_tracker.mark_clean(comp.component_id)
            return {"success": False, "error_code": "GEOMETRY_BUILD_FAILED", "message": str(e)}

    def inspect_component(self, component_id: str) -> Dict[str, Any]:
        comp = self.registry.get(component_id)
        if not comp:
            return {"success": False, "error_code": "COMPONENT_NOT_FOUND", "message": f"Component '{component_id}' not found."}

        return {
            "success": True,
            "component_id": comp.component_id,
            "asset_id": comp.asset_id,
            "generator": comp.generator_type,
            "parameters": comp.parameters,
            "parent_id": comp.parent_id,
            "version": comp.version,
            "status": comp.status,
            "dimensions": comp.geometry.dimensions if comp.geometry else None,
            "triangle_count": comp.geometry.triangle_count if comp.geometry else 0,
            "vertices_count": len(comp.geometry.vertices) if comp.geometry else 0
        }
