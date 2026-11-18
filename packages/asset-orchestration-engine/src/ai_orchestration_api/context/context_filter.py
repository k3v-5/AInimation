from typing import Dict, Any, List, Optional
from ..core.agent_types import AgentAssetStatus, AgentComponentStatus
from ..core.agent_schema import AgentAssetContext

class ContextFilter:
    @staticmethod
    def extract_asset_context(asset_id: str, full_asset_def: Any) -> AgentAssetContext:
        # Extrae solo la información relevante del activo (Ahorro masivo de tokens)
        comp_statuses: Dict[str, AgentComponentStatus] = {}
        for cname, comp in full_asset_def.components.items():
            comp_statuses[cname] = AgentComponentStatus.VALID if comp.state.value == "VALID" else AgentComponentStatus.DIRTY

        return AgentAssetContext(
            asset_id=asset_id,
            asset_type=full_asset_def.category,
            version=1,
            status=AgentAssetStatus.VALID,
            parameters=dict(full_asset_def.parameters),
            components=comp_statuses,
            validation_summary={"structural": "PASS", "component_count": len(full_asset_def.components)}
        )

class StructuredMemory:
    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}
        self.best_records: Dict[str, Dict[str, Any]] = {}
        self.applied_corrections: Dict[str, List[str]] = {}

    def record_iteration(self, asset_id: str, version: int, score: float, parameters: Dict[str, Any]) -> Optional[str]:
        if asset_id not in self.history:
            self.history[asset_id] = []
            self.applied_corrections[asset_id] = []

        record = {"version": version, "score": score, "parameters": dict(parameters)}
        self.history[asset_id].append(record)

        # Actualizar mejor versión conocida
        if asset_id not in self.best_records or score > self.best_records[asset_id]["score"]:
            self.best_records[asset_id] = record

        # Detección de Estancamiento (Stagnation / NO_PROGRESS)
        if len(self.history[asset_id]) >= 3:
            s1 = self.history[asset_id][-2]["score"]
            s2 = self.history[asset_id][-1]["score"]
            if abs(s2 - s1) < 0.005:
                return "NO_PROGRESS: Score improvement is below 0.5% threshold across consecutive iterations."

        return None

    def record_applied_correction(self, asset_id: str, param_name: str, new_val: Any) -> Optional[str]:
        if asset_id not in self.applied_corrections:
            self.applied_corrections[asset_id] = []
        sig = f"{param_name}_{new_val}"
        if self.applied_corrections[asset_id].count(sig) >= 2:
            return f"LOOP_DETECTED: Correction '{sig}' has been repeated multiple times without convergence."
        self.applied_corrections[asset_id].append(sig)
        return None

    def get_best_version(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.best_records.get(asset_id)
