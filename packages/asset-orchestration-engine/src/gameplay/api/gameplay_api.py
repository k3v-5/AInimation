from typing import Dict, Any, Optional, List, Tuple
from ..core.gameplay_engine import GameplayEngine
from ..capabilities.capability_schema import CapabilityType

class GameplayAPI:
    def __init__(self, gameplay_engine: GameplayEngine):
        self.engine = gameplay_engine

    def add_capability(
        self,
        actor_id: str,
        capability: str,
        parameters: Optional[Dict[str, Any]] = None,
        auto_resolve: bool = True,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        return self.engine.add_capability(
            actor_id=actor_id,
            capability_type_str=capability,
            parameters=parameters,
            auto_resolve_dependencies=auto_resolve,
            scope=scope,
            dry_run=dry_run
        )

    def set_data(self, actor_id: str, attribute: str, value: Any, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.set_gameplay_data(actor_id, attribute, value, dry_run=dry_run)

    def register_interaction(
        self,
        actor_id: str,
        verb: str,
        conditions: Optional[List[Dict[str, Any]]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        priority: int = 50
    ) -> Dict[str, Any]:
        return self.engine.register_interaction(actor_id, verb, conditions, actions, priority)

    def simulate(self, interaction_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.engine.simulate_interaction(interaction_id, context)

    def get_manifest(self, actor_id: str) -> Dict[str, Any]:
        return self.engine.get_gameplay_manifest(actor_id)
