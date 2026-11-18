from typing import Dict, Any, Tuple
from ...correction_execution.providers.blender_provider import IBlenderProvider
from ..core.governance_schema import StateSnapshot

class PostActionValidator:
    @staticmethod
    def verify_parameter_state(
        provider: IBlenderProvider,
        target_entity: str,
        expected_params: Dict[str, Any]
    ) -> Tuple[bool, str]:
        asset = provider.assets.get(target_entity)
        if not asset:
            return False, f"VERIFICATION_FAILED: Asset '{target_entity}' does not exist in provider after action."

        # Verificar dimensiones modificadas
        dims = asset.get("dimensions") or asset.get("components", {}).get("root", {}).get("dimensions")
        if dims and "roof_height" in expected_params:
            # Si el proveedor no actualizó la altura, fallar verificación
            exp_h = expected_params["roof_height"]
            if abs(dims[2] - exp_h) > 0.05:
                return False, f"VERIFICATION_FAILED: State in provider did not match target parameter (Expected: {exp_h}, Actual: {dims[2]})."

        return True, "State verified."

class RollbackManager:
    @staticmethod
    def take_snapshot(snapshot_id: str, provider: IBlenderProvider) -> StateSnapshot:
        import copy
        return StateSnapshot(snapshot_id=snapshot_id, assets_data=copy.deepcopy(provider.assets))

    @staticmethod
    def restore_snapshot(snapshot: StateSnapshot, provider: IBlenderProvider):
        import copy
        provider.assets = copy.deepcopy(snapshot.assets_data)
