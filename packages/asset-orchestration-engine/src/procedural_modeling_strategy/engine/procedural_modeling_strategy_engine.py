import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from ..core.msp_types import (
    AssetCategoryTag, ComponentConstructionMethod, BasePrimitiveType,
    SymmetryType, DetailLevel, CollisionStrategyType, PivotStrategyType,
    StrategyRiskLevel, ReuseStrategyType
)
from ..core.msp_schema import (
    ParametricSpec, GeometricOperation, ModifierStrategySpec,
    GeometryNodesStrategySpec, ComponentStrategy, GlobalStrategySpec,
    GeometryBudgetDistribution, CostEstimate, ModelingStrategyPlan,
    StrategyValidationResult
)
from ..analyzers.component_classifier import ComponentClassifier
from ..analyzers.budget_distributor import BudgetDistributor
from ..analyzers.dag_builder import DAGBuilder
from ..analyzers.cost_estimator import CostEstimator

class ProceduralModelingStrategyEngine:
    """
    Procedural Modeling Strategy Engine (AOE v57)
    
    Regla Fundamental:
    NO GENERA GEOMETRÍA DIRECTAMENTE. TRANSFORMA LA VisualAssetSpecification (F56)
    EN UN ModelingStrategyPlan (MSP) DETERMINISTA, VALIDADO Y ESTRUCTURADO EN UN DAG
    QUE INDICA A F58 QUÉ OPERACIONES EJECUTAR, EN QUÉ ORDEN Y CON QUÉ PARÁMETROS.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version

    def plan(
        self,
        specification: Any, # VisualAssetSpecification from F56
        project_config: Optional[Dict[str, Any]] = None
    ) -> ModelingStrategyPlan:
        cfg = project_config or {}
        p_text = getattr(specification, "intent", {}).get("original_prompt", "")
        p_low = p_text.lower()
        asset_cls = getattr(specification, "asset_classification", "PROP")

        warnings: List[str] = []
        conflicts: List[str] = []

        # 1. Clasificación del Asset
        categories = []
        if "weapon" in asset_cls.lower() or "sword" in p_low or "espada" in p_low:
            categories.extend([AssetCategoryTag.WEAPON, AssetCategoryTag.HARD_SURFACE])
        elif "barrel" in p_low or "prop" in asset_cls.lower():
            categories.extend([AssetCategoryTag.PROP, AssetCategoryTag.HARD_SURFACE])
        else:
            categories.append(AssetCategoryTag.PROP)

        # 2. Descomposición y Clasificación de Componentes
        raw_components = getattr(specification, "components", [])
        if not raw_components:
            raw_components = [{"component_id": "comp_main", "semantic_type": "BODY", "is_primary": True, "visual_weight": 1.0}]

        # 3. Distribución de Presupuesto Geométrico
        total_tri_budget = getattr(specification, "production_budget", None)
        max_tris = getattr(total_tri_budget, "triangle_budget", 30000) if total_tri_budget else 30000
        budget_dist = BudgetDistributor.distribute_budget(max_tris, raw_components)

        # 4. Estrategias por Componente
        component_strategies: List[ComponentStrategy] = []
        dependencies: Dict[str, List[str]] = {}

        sym_type = SymmetryType.MIRROR if ("bilateral" in p_low or "espada" in p_low or "sword" in p_low or "simetr" in p_low) else SymmetryType.NONE

        for c in raw_components:
            cid = c.get("component_id", "comp_01")
            sem_type = c.get("semantic_type", "BODY")
            method, base_prim = ComponentClassifier.classify_component(c, p_text)
            comp_budget = budget_dist.component_budgets.get(cid, 2000)

            modifiers = []
            if sym_type == SymmetryType.MIRROR:
                modifiers.append(ModifierStrategySpec(
                    modifier_id=f"MOD_MIRROR_{cid.upper()}",
                    modifier_type="MIRROR",
                    order=1,
                    parameters={"axis": "X"},
                    reason="Bilateral symmetry preservation"
                ))

            modifiers.append(ModifierStrategySpec(
                modifier_id=f"MOD_BEVEL_{cid.upper()}",
                modifier_type="BEVEL",
                order=2,
                parameters={"width": 0.005, "segments": 2},
                reason="Hard surface edge definition"
            ))

            params = [
                ParametricSpec(f"{cid}_scale_x", "float", "meters", 1.0, 0.01, 10.0),
                ParametricSpec(f"{cid}_scale_y", "float", "meters", 1.0, 0.01, 10.0),
                ParametricSpec(f"{cid}_scale_z", "float", "meters", 1.0, 0.01, 10.0)
            ]

            comp_strat = ComponentStrategy(
                component_id=cid,
                parent_component_id=None if c.get("is_primary", False) else raw_components[0].get("component_id"),
                semantic_role=sem_type,
                method=method,
                base_geometry=base_prim,
                dimensions={"x": 1.0, "y": 1.0, "z": 1.0},
                proportions={"ratio": 1.0},
                parameters=params,
                modifiers=modifiers,
                triangle_budget=comp_budget,
                importance=1.0 if c.get("is_primary", False) else 0.8,
                visual_weight=float(c.get("visual_weight", 1.0)),
                symmetry=sym_type,
                fallback_method=ComponentConstructionMethod.PRIMITIVE
            )
            component_strategies.append(comp_strat)
            dependencies[cid] = []

        # 5. Construcción del DAG de Ejecución
        execution_dag = DAGBuilder.build_execution_dag(component_strategies)

        # 6. Detección de Conflictos de Presupuesto
        if max_tris <= 500 and len(component_strategies) > 3:
            conflicts.append(f"BUDGET_CONFLICT: Triangle budget ({max_tris}) is insufficient for {len(component_strategies)} components.")

        # 7. Estimación de Costes y Score
        cost_est = CostEstimator.estimate_cost(component_strategies, max_tris)

        # 8. Estrategias Globales y de Unreal
        global_strat = GlobalStrategySpec(
            construction_method="MODULAR" if len(component_strategies) > 1 else "PARAMETRIC",
            symmetry=sym_type
        )

        unreal_reqs = getattr(specification, "unreal_requirements", None)
        raw_col = str(getattr(unreal_reqs, "collision_type", "CUSTOM_UCX")) if unreal_reqs else "CUSTOM_UCX"
        unreal_interface = {
            "nanite": getattr(unreal_reqs, "nanite_enabled", True) if unreal_reqs else True,
            "lod_count": getattr(unreal_reqs, "lod_count", 3) if unreal_reqs else 3,
            "collision_type": "CUSTOM_UCX" if "ucx" in raw_col.lower() else raw_col
        }

        spec_id = getattr(specification, "specification_id", "VAS_DEFAULT")
        sem_id = getattr(specification, "semantic_identity", {}).get("semantic_id", "asset_42.root")

        msp = ModelingStrategyPlan(
            schema_version="1.0.0",
            strategy_id=f"MSP_{spec_id.replace('VAS_', '')}",
            semantic_id=sem_id,
            specification_id=spec_id,
            strategy_version="1.0.0",
            asset_classification=categories,
            global_strategy=global_strat,
            component_strategies=component_strategies,
            dependency_graph=dependencies,
            execution_graph=execution_dag,
            geometry_budget=budget_dist,
            symmetry_strategy=sym_type,
            unreal_interface=unreal_interface,
            cost_estimate=cost_est,
            warnings=warnings,
            conflicts=conflicts,
            confidence=0.95,
            traceability=[{"source": "VAS", "specification_id": spec_id}],
            compilation_metadata={"engine_version": self.engine_version}
        )

        # 9. Cálculo de Hash Lógico Determinista
        msp.strategy_hash = self.compute_hash(msp)
        return msp

    def validate(self, plan: ModelingStrategyPlan) -> StrategyValidationResult:
        errors = []
        warnings = []

        if not plan.strategy_id:
            errors.append("MISSING_STRATEGY_ID: Strategy ID is required.")
        if not plan.component_strategies:
            errors.append("EMPTY_COMPONENTS: At least one component strategy is required.")
        if not plan.execution_graph:
            errors.append("EMPTY_EXECUTION_GRAPH: Execution DAG cannot be empty.")

        if DAGBuilder.check_circular_dependencies(plan.dependency_graph):
            errors.append("CIRCULAR_DEPENDENCY: Detected circular dependency cycle in component graph.")

        for conf in plan.conflicts:
            errors.append(f"STRATEGY_CONFLICT: {conf}")

        for w in plan.warnings:
            warnings.append(w)

        return StrategyValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def rank_strategies(self, candidates: List[ModelingStrategyPlan]) -> List[ModelingStrategyPlan]:
        return sorted(candidates, key=lambda s: s.cost_estimate.strategy_score, reverse=True)

    def estimate_cost(self, plan: ModelingStrategyPlan) -> CostEstimate:
        return plan.cost_estimate

    def compute_hash(self, plan: ModelingStrategyPlan) -> str:
        excluded = {"strategy_id", "strategy_hash", "compilation_metadata", "timestamp"}
        raw = {k: v for k, v in plan.__dict__.items() if k not in excluded}
        serialized = json.dumps(raw, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
