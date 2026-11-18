from typing import Dict, Any, List, Set, Optional
from ..core.parametric_types import (
    ParamType, UnitType, RoofType, ComponentState, PivotType,
    GenerationStrategy, ParametricErrorType
)
from ..core.parametric_schema import (
    ParamDefinition, ResolvedParameters, GeneratedComponent,
    AssetSnapshot, AssetDefinition
)
from ..solver.parameter_resolver import ParameterResolver, ConstraintSolver
from ..generators.architectural_generators import GeneratorRegistry
from ..engine.parametric_engine import ParametricAssetEngine, DirtyTracker

class ParametricAssetAPI:
    """
    Parametric Asset Generation Engine API (AOE v40)
    
    Regla Fundamental:
    LA IA DECIDE (Parámetros), EL MOTOR CONSTRUYE (Generadores Paramétricos Deterministas)
    Y EL MCP DE BLENDER EJECUTA. CERO IMPROVISACIÓN DE VÉRTICES O COMANDOS CIEGOS EN BLENDER.
    """
    def __init__(self):
        self.engine = ParametricAssetEngine()

    def create_asset(self, asset_id: str, parameters: Optional[Dict[str, Any]] = None, seed: int = 42) -> AssetDefinition:
        return self.engine.generate_full_asset(asset_id, parameters or {}, seed)

    def update_asset(self, asset_id: str, parameters: Dict[str, Any]) -> AssetDefinition:
        return self.engine.update_parameters(asset_id, parameters)

    def interpret_request(self, asset_id: str, request_text: str) -> Dict[str, Any]:
        return self.engine.interpret_ai_request(asset_id, request_text)

    def undo_asset(self, asset_id: str) -> AssetDefinition:
        return self.engine.undo_operation(asset_id)

    def reconcile_scene(self, asset_id: str, actual_objects: Set[str]):
        self.engine.reconcile_with_blender(asset_id, actual_objects)

    def get_component(self, asset_id: str, component_name: str) -> GeneratedComponent:
        if asset_id in self.engine.assets and component_name in self.engine.assets[asset_id].components:
            return self.engine.assets[asset_id].components[component_name]
        raise KeyError(f"Component '{component_name}' not found for asset '{asset_id}'.")
