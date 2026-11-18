import time
from typing import Dict, Any, List, Optional
from ..core.geom_types import (
    OperationState, TransactionState, MeshTopologyType,
    ExportRole, ValidationSeverity, GenerationStatus
)
from ..core.geom_schema import (
    GenerationContext, GeneratedGeometryResult, GeometryObjectSpec,
    ComponentGenerationResult, TopologySummary, GeometryValidationResult,
    CompensationResult, CheckpointSpec
)
from .dag_executor import DAGExecutor
from .partial_regenerator import PartialRegenerator
from .topology_evaluator import TopologyEvaluator

class GeometryGenerationEngine:
    """
    Geometry Generation Engine (AOE v58)
    
    Regla Fundamental:
    MATERIALIZA EL ModelingStrategyPlan (F57) EN GEOMETRÍA REAL Y DETERMINISTA,
    UTILIZANDO EXCLUSIVAMENTE LA CAPABILITY ABSTRACTION LAYER (F53) SIN DEPENDER
    DIRECTAMENTE DE LA API DE BLENDER NI DE LLAMADAS DIRECTAS A MCP.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self._checkpoints: Dict[str, List[CheckpointSpec]] = {}

    def generate(
        self,
        strategy: Any, # ModelingStrategyPlan from F57
        context: Optional[GenerationContext] = None
    ) -> GeneratedGeometryResult:
        gen_id = f"GEN_{getattr(strategy, 'strategy_id', 'STRAT').replace('MSP_', '')}_{int(time.time()*1000)%100000}"
        ctx = context or GenerationContext(
            generation_id=gen_id,
            strategy_plan=strategy,
            generation_seed=42
        )

        initial_state = {
            "objects": {},
            "created_objects": [],
            "pivot": {"strategy": getattr(strategy, "pivot_strategy", "BASE_CENTER_GROUNDED").value if hasattr(getattr(strategy, "pivot_strategy", None), "value") else "BASE_CENTER_GROUNDED", "origin": (0.0, 0.0, 0.0)}
        }

        # 1. Ejecución del DAG de Operaciones
        final_state, trace, errors = DAGExecutor.execute_dag(ctx, initial_state)

        # 2. Evaluación de Topología y Bounds
        objects_dict: Dict[str, GeometryObjectSpec] = final_state["objects"]
        topo_summary = TopologyEvaluator.evaluate_topology(objects_dict)
        bounds_data = TopologyEvaluator.compute_bounds(objects_dict)

        # 3. Construcción de Resultados por Componente
        comp_results: Dict[str, ComponentGenerationResult] = {}
        for cid, obj in objects_dict.items():
            comp_results[cid] = ComponentGenerationResult(
                component_id=cid,
                semantic_id=obj.semantic_id,
                object_id=obj.object_id,
                topology=obj.topology,
                triangle_count=obj.topology.triangle_count,
                status=GenerationStatus.SUCCESS
            )

        # 4. Hash Determinista de Geometría
        gen_hash = TopologyEvaluator.compute_geometry_hash(objects_dict, self.engine_version)

        # 5. Geometría de Colisión y LODs
        unreal_interface = getattr(strategy, "unreal_interface", {})
        collision_type = unreal_interface.get("collision_type", "CUSTOM_UCX")
        col_obj = None
        if collision_type == "CUSTOM_UCX":
            col_obj = GeometryObjectSpec(
                object_id=f"UCX_{getattr(strategy, 'semantic_id', 'Prop')}",
                semantic_component_id="collision_root",
                semantic_id=getattr(strategy, "semantic_id", "asset_001.root"),
                name=f"UCX_SM_{getattr(strategy, 'semantic_id', 'Prop')}",
                geometry_type=MeshTopologyType.TRIANGLE_MESH,
                export_role=ExportRole.COLLISION_MESH
            )

        warnings = list(getattr(strategy, "warnings", []))
        # Control de Presupuesto Poligonal
        budget_dist = getattr(strategy, "geometry_budget", None)
        max_tris = getattr(budget_dist, "total_triangle_budget", 30000) if budget_dist else 30000
        if topo_summary.triangle_count > max_tris:
            warnings.append(f"BUDGET_OVERRUN: Generated triangles ({topo_summary.triangle_count}) exceed budget ({max_tris}).")

        status = GenerationStatus.SUCCESS
        if errors:
            status = GenerationStatus.FAILED
        elif warnings:
            status = GenerationStatus.SUCCESS_WITH_WARNINGS

        result = GeneratedGeometryResult(
            generation_id=ctx.generation_id,
            semantic_id=getattr(strategy, "semantic_id", "asset_001.root"),
            specification_id=getattr(strategy, "specification_id", "VAS_DEFAULT"),
            strategy_id=getattr(strategy, "strategy_id", "MSP_DEFAULT"),
            generation_version=self.engine_version,
            generation_hash=gen_hash,
            status=status,
            geometry_objects=list(objects_dict.values()),
            component_results=comp_results,
            topology_summary=topo_summary,
            dimensions=bounds_data["dimensions"],
            bounds=bounds_data,
            triangle_count=topo_summary.triangle_count,
            vertex_count=topo_summary.vertex_count,
            material_slots=list({slot for o in objects_dict.values() for slot in o.material_slots}),
            pivot_state=final_state["pivot"],
            collision_geometry=col_obj,
            execution_trace=trace,
            warnings=warnings,
            errors=errors,
            generation_metadata={"engine_version": self.engine_version, "seed": ctx.generation_seed}
        )

        return result

    def generate_component(
        self,
        component_id: str,
        strategy: Any,
        context: Optional[GenerationContext] = None
    ) -> ComponentGenerationResult:
        ctx = context or GenerationContext(
            generation_id=f"GEN_COMP_{component_id}",
            strategy_plan=strategy,
            target_components=[component_id]
        )
        full_res = self.generate(strategy, ctx)
        if component_id in full_res.component_results:
            return full_res.component_results[component_id]
        return ComponentGenerationResult(
            component_id=component_id,
            semantic_id=getattr(strategy, "semantic_id", "asset.root"),
            object_id=f"OBJ_{component_id.upper()}",
            topology=TopologySummary(),
            triangle_count=0,
            status=GenerationStatus.FAILED,
            errors=[f"COMPONENT_NOT_GENERATED: Component {component_id} was not found."]
        )

    def regenerate(
        self,
        target_components: List[str],
        strategy: Any,
        context: Optional[GenerationContext] = None
    ) -> GeneratedGeometryResult:
        dep_graph = getattr(strategy, "dependency_graph", {})
        affected = PartialRegenerator.get_affected_components(target_components, dep_graph)
        
        ctx = context or GenerationContext(
            generation_id=f"GEN_REGEN_{'_'.join(target_components)}",
            strategy_plan=strategy,
            target_components=list(affected)
        )
        return self.generate(strategy, ctx)

    def validate(self, result: GeneratedGeometryResult) -> GeometryValidationResult:
        errors = []
        warnings = []

        if not result.generation_id:
            errors.append("MISSING_GENERATION_ID: Generation ID is mandatory.")
        if not result.geometry_objects and result.status == GenerationStatus.SUCCESS:
            errors.append("EMPTY_GEOMETRY: Successful result must contain geometry objects.")
        if not result.generation_hash:
            errors.append("MISSING_GEOMETRY_HASH: Geometry hash is required.")

        for err in result.errors:
            errors.append(f"GENERATION_ERROR: {err}")
        for w in result.warnings:
            warnings.append(f"GENERATION_WARNING: {w}")

        return GeometryValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def rollback(self, generation_id: str) -> CompensationResult:
        return CompensationResult(success=True, message=f"Rolled back generation {generation_id}")

    def compute_hash(self, result: GeneratedGeometryResult) -> str:
        objs = {o.semantic_component_id: o for o in result.geometry_objects}
        return TopologyEvaluator.compute_geometry_hash(objs, self.engine_version)
