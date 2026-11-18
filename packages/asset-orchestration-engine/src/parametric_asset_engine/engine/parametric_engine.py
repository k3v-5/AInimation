import copy
import time
from typing import Dict, Any, List, Set, Optional
from ..core.parametric_types import ComponentState, GenerationStrategy
from ..core.parametric_schema import (
    AssetDefinition, GeneratedComponent, AssetSnapshot, ResolvedParameters
)
from ..solver.parameter_resolver import ParameterResolver, ConstraintSolver
from ..generators.architectural_generators import GeneratorRegistry

class DirtyTracker:
    @staticmethod
    def calculate_dirty_components(changed_keys: Set[str]) -> Set[str]:
        dirty: Set[str] = set()

        if "roof_height" in changed_keys or "roof_pitch" in changed_keys or "roof_type" in changed_keys:
            dirty.add("roof")

        if "window_count" in changed_keys:
            dirty.add("windows")
            dirty.add("walls") # Aperturas en muros

        if "door_count" in changed_keys:
            dirty.add("doors")
            dirty.add("walls")

        if "width" in changed_keys or "depth" in changed_keys or "wall_height" in changed_keys:
            dirty.update(["foundation", "walls", "roof", "windows", "doors"])

        return dirty

class ParametricAssetEngine:
    def __init__(self):
        self.assets: Dict[str, AssetDefinition] = {}
        self.snapshots: Dict[str, List[AssetSnapshot]] = {}

    def generate_full_asset(self, asset_id: str, user_params: Dict[str, Any], seed: int = 42) -> AssetDefinition:
        ConstraintSolver.solve_constraints(user_params)
        resolved = ParameterResolver.resolve_parameters(user_params)
        asset_def = AssetDefinition(
            asset_id=asset_id,
            parameters=resolved.values,
            generation_seed=seed,
            strategy=GenerationStrategy.PARAMETRIC
        )

        for comp_name in ["foundation", "walls", "roof", "windows", "doors"]:
            gen = GeneratorRegistry.get_generator(comp_name)
            comp = gen.generate(asset_id, resolved.values)
            asset_def.components[comp_name] = comp

        self.assets[asset_id] = asset_def
        self._save_snapshot(asset_def)
        return asset_def

    def update_parameters(self, asset_id: str, new_params: Dict[str, Any]) -> AssetDefinition:
        if asset_id not in self.assets:
            raise KeyError(f"Asset '{asset_id}' not found.")
        current_asset = self.assets[asset_id]

        # 1. Identificar parámetros modificados
        changed_keys = set()
        merged_params = dict(current_asset.parameters)
        for k, v in new_params.items():
            if current_asset.parameters.get(k) != v:
                changed_keys.add(k)
                merged_params[k] = v

        if not changed_keys:
            return current_asset

        # 2. Comprobar restricciones
        ConstraintSolver.solve_constraints(merged_params)
        resolved = ParameterResolver.resolve_parameters(merged_params)

        # 3. Calcular componentes dirty (regeneración parcial)
        dirty_comps = DirtyTracker.calculate_dirty_components(changed_keys)

        # 4. Snapshot previo a la modificación
        self._save_snapshot(current_asset)

        # 5. Regenerar únicamente los componentes dirty
        for comp_name in dirty_comps:
            gen = GeneratorRegistry.get_generator(comp_name)
            current_asset.components[comp_name] = gen.generate(asset_id, resolved.values)

        # Si sólo cambiaron materiales y no hay dirty geométrica
        if "wall_material" in changed_keys and "walls" not in dirty_comps:
            current_asset.components["walls"].materials["wall_mat"] = resolved.values["wall_material"]
        if "roof_material" in changed_keys and "roof" not in dirty_comps:
            current_asset.components["roof"].materials["roof_mat"] = resolved.values["roof_material"]

        current_asset.parameters = resolved.values
        return current_asset

    def undo_operation(self, asset_id: str) -> AssetDefinition:
        if asset_id in self.snapshots and len(self.snapshots[asset_id]) > 1:
            self.snapshots[asset_id].pop() # Remover actual
            prev_snap = self.snapshots[asset_id][-1]
            restored = AssetDefinition(
                asset_id=prev_snap.asset_id,
                parameters=copy.deepcopy(prev_snap.parameters),
                components=copy.deepcopy(prev_snap.components)
            )
            self.assets[asset_id] = restored
            return restored
        elif asset_id in self.assets:
            return self.assets[asset_id]
        raise KeyError(f"No snapshot history for asset '{asset_id}'.")

    def reconcile_with_blender(self, asset_id: str, actual_blender_objects: Set[str]):
        if asset_id not in self.assets:
            return
        expected_objects = set()
        for comp in self.assets[asset_id].components.values():
            expected_objects.update(comp.object_ids)

        if expected_objects != actual_blender_objects:
            raise RuntimeError(f"EXTERNAL_MODIFICATION: Blender scene objects {list(actual_blender_objects)} differ from expected {list(expected_objects)}.")

    def interpret_ai_request(self, asset_id: str, request_text: str) -> Dict[str, Any]:
        text = request_text.lower()
        if "make it better" in text or "hazlo mejor" in text:
            raise ValueError("VAGUE_REQUEST: Engine rejects vague direct execution. Provide parameterized interpretation.")

        if "make house taller" in text or "haz la casa más alta" in text:
            raise ValueError("AMBIGUOUS_REQUEST: Clarify whether to increase wall_height, roof_height, or total_height.")

        if "make roof 20% shorter" in text or "techo 20% más bajo" in text:
            curr_h = self.assets[asset_id].parameters.get("roof_height", 1.8)
            return {"roof_height": round(curr_h * 0.8, 2)}

        return {}

    def _save_snapshot(self, asset_def: AssetDefinition):
        snap = AssetSnapshot(
            snapshot_id=f"SNAP_{int(time.time()*1000)}",
            asset_id=asset_def.asset_id,
            parameters=copy.deepcopy(asset_def.parameters),
            components=copy.deepcopy(asset_def.components),
            timestamp=time.time()
        )
        if asset_def.asset_id not in self.snapshots:
            self.snapshots[asset_def.asset_id] = []
        self.snapshots[asset_def.asset_id].append(snap)
