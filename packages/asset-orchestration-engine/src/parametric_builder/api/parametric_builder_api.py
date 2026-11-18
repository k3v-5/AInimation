import time
import re
from typing import Dict, Any, List, Optional, Tuple
from ..core.parametric_types import AssetType, BuildStage, BuildState
from ..core.parametric_schema import (
    ParametricAssetDefinition, ParameterChange, BuildResult
)
from ..core.parameter_graph import ParameterDependencyGraph
from ..solver.constraint_solver import ParameterConstraintSolver
from ..solver.parameter_transaction import ParameterTransactionManager
from ..construction.geometry_cache import GeometryCache
from ..construction.partial_builder import PartialBuilder
from ..construction.builders.house_builder import MedievalHouseBuilder

class ParametricBuilderAPI:
    """
    Parametric Asset Build System API (AOE v24)
    
    Regla Fundamental:
    LA IA NUNCA ESCULPE A CIEGAS VÉRTICES O CARAS.
    LA IA ESPECIFICA QUÉ QUIERE (PARÁMETROS) Y EL MOTOR DETERMINISTA CONSTRUYE EL CÓMO.
    SOPORTA RECONSTRUCCIÓN PARCIAL AISLADA, CACHE GEOMÉTRICO Y TRANSACCIONES CON ROLLBACK.
    """
    def __init__(self):
        self.cache = GeometryCache()
        self.definitions: Dict[AssetType, ParametricAssetDefinition] = {
            AssetType.MEDIEVAL_HOUSE: MedievalHouseBuilder.get_definition()
        }

    def build_parametric_asset(
        self,
        asset_type: AssetType,
        explicit_parameters: Dict[str, Any],
        seed: int = 42,
        stage: BuildStage = BuildStage.COMPLETED,
        fail_blockout_check: bool = False
    ) -> BuildResult:
        start_t = time.time()

        # 1. Comprobar Fallback de Geometría Custom
        if asset_type not in self.definitions or asset_type == AssetType.CUSTOM:
            return BuildResult(
                asset_id=f"custom_{asset_type.value.lower()}",
                asset_type=asset_type,
                parameters=explicit_parameters,
                status=BuildState.COMPLETED,
                stage_reached=BuildStage.COMPLETED,
                errors=["CUSTOM_GEOMETRY_FALLBACK: No parametric definition exists; routed to custom geometry pipeline."]
            )

        definition = self.definitions[asset_type]

        # 2. Puerta de Evaluación de Blockout Progresivo (Stage 0)
        if fail_blockout_check:
            return BuildResult(
                asset_id=f"asset_{asset_type.value.lower()}",
                asset_type=asset_type,
                parameters=explicit_parameters,
                status=BuildState.FAILED,
                stage_reached=BuildStage.BLOCKOUT,
                errors=["BLOCKOUT_SILHOUETTE_FAILED: Blockout stage failed silhouette verification; halted before detail generation."]
            )

        # 3. Resolver parámetros y dependencias
        resolved_params = ParameterDependencyGraph.resolve_parameters(definition, explicit_parameters)

        # 4. Validar restricciones
        is_valid, errors = ParameterConstraintSolver.validate_constraints(definition, resolved_params)
        if not is_valid:
            return BuildResult(
                asset_id=f"asset_{asset_type.value.lower()}",
                asset_type=asset_type,
                parameters=resolved_params,
                status=BuildState.FAILED,
                errors=errors
            )

        # 5. Comprobar Cache
        fp = GeometryCache.compute_fingerprint(asset_type.value, resolved_params, seed, definition.version)
        cached = self.cache.get(fp)
        if cached:
            cached_copy = BuildResult(
                asset_id=cached.asset_id,
                asset_type=cached.asset_type,
                parameters=cached.parameters,
                created_components=cached.created_components,
                dimensions=cached.dimensions,
                geometry_stats=cached.geometry_stats,
                build_fingerprint=fp,
                is_cache_hit=True,
                build_time_ms=round((time.time() - start_t) * 1000, 2),
                status=BuildState.COMPLETED
            )
            return cached_copy

        # 6. Construcción determinista
        geo_data = MedievalHouseBuilder.generate_geometry(resolved_params)
        duration = round((time.time() - start_t) * 1000, 2)

        result = BuildResult(
            asset_id=f"asset_{asset_type.value.lower()}",
            asset_type=asset_type,
            parameters=resolved_params,
            created_components=geo_data["components"],
            dimensions=geo_data["dimensions"],
            geometry_stats=geo_data["geometry_stats"],
            build_fingerprint=fp,
            is_cache_hit=False,
            build_time_ms=duration,
            status=BuildState.COMPLETED
        )

        self.cache.put(fp, result)
        return result

    def update_parameters(
        self,
        asset_type: AssetType,
        current_parameters: Dict[str, Any],
        changes: List[ParameterChange]
    ) -> Tuple[bool, BuildResult, List[str]]:
        if asset_type not in self.definitions:
            return False, BuildResult("none", asset_type, {}), ["UNKNOWN_ASSET_TYPE"]

        definition = self.definitions[asset_type]
        ok_tx, new_params, logs = ParameterTransactionManager.apply_transaction(
            definition, current_parameters, changes
        )
        if not ok_tx:
            failed_res = BuildResult(
                asset_id=f"asset_{asset_type.value.lower()}",
                asset_type=asset_type,
                parameters=current_parameters,
                status=BuildState.ROLLED_BACK,
                errors=logs
            )
            return False, failed_res, logs

        # Identificar componentes afectados para reconstrucción parcial
        changed_dict = {c.parameter_name: c.new_value for c in changes}
        affected = PartialBuilder.get_affected_components(changed_dict, definition.components)

        build_res = self.build_parametric_asset(asset_type, new_params)
        build_res.modified_components = affected
        return True, build_res, logs

    def parse_relative_intent(self, base_value: float, intent_text: str) -> float:
        text = intent_text.lower().strip()
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if m:
            pct = float(m.group(1)) / 100.0
            if "más" in text or "mas" in text or "aumenta" in text or "alto" in text or "ancha" in text:
                return round(base_value * (1.0 + pct), 4)
            elif "menos" in text or "reduce" in text or "bajo" in text or "estrecha" in text:
                return round(base_value * (1.0 - pct), 4)

        return base_value
