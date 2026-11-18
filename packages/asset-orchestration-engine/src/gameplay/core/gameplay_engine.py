import uuid
import copy
from typing import Dict, Any, Optional, List, Tuple
from ..capabilities.capability_schema import CapabilityType, CapabilityDefinition, CapabilityInstance, CapabilityRegistry
from ..capabilities.capability_resolver import CapabilityResolver
from ..interactions.interaction_system import InteractionSystem, InteractionDefinition, GameplayCondition, GameplayAction
from ..events.event_bus import EventBus, GameplayEvent
from ..state.state_machine import StateMachine
from ..data.gameplay_data import ActorGameplayData
from ..planning.gameplay_diff import GameplayDiff

class GameplayEngine:
    """
    Gameplay & Interaction Orchestration Engine (AOE v8)
    
    Principio Fundamental:
    GAMEPLAY SHOULD BE COMPOSED, NOT REGENERATED.
    """
    def __init__(self):
        self.capability_registry = CapabilityRegistry()
        self.interaction_system = InteractionSystem()
        self.event_bus = EventBus()
        self.actor_capabilities: Dict[str, Dict[CapabilityType, CapabilityInstance]] = {} # actor_id -> {cap_type: inst}
        self.actor_data: Dict[str, ActorGameplayData] = {} # actor_id -> ActorGameplayData
        self.state_machines: Dict[str, StateMachine] = {}

    def add_capability(
        self,
        actor_id: str,
        capability_type_str: str,
        parameters: Optional[Dict[str, Any]] = None,
        auto_resolve_dependencies: bool = True,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        # 1. Scope check
        if scope and actor_id not in scope:
            return {"success": False, "error_code": "GAMEPLAY_SCOPE_VIOLATION", "message": f"Actor '{actor_id}' is outside allowed scope {scope}."}

        try:
            target_cap = CapabilityType(capability_type_str.upper())
        except ValueError:
            return {"success": False, "error_code": "CAPABILITY_NOT_FOUND", "message": f"Capability '{capability_type_str}' is not recognized."}

        # 2. Resolución de dependencias
        if auto_resolve_dependencies:
            needed = CapabilityResolver.resolve_hierarchy([target_cap], self.capability_registry)
        else:
            needed = [target_cap]

        if actor_id not in self.actor_capabilities:
            self.actor_capabilities[actor_id] = {}

        cur_caps = self.actor_capabilities[actor_id]
        added_list = []
        diff = GameplayDiff()

        for c in needed:
            if c not in cur_caps:
                inst = CapabilityInstance(capability_type=c, parameters=parameters or {})
                if not dry_run:
                    cur_caps[c] = inst
                added_list.append(c.value)
                diff.added_capabilities.append(c.value)

        # Si ya existían todas las capabilities requeridas -> NO_OP
        if not added_list:
            return {"success": True, "status": "NO_OP", "actor_id": actor_id, "capabilities": [c.value for c in cur_caps.keys()]}

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        return {
            "success": True,
            "status": "completed",
            "actor_id": actor_id,
            "added_capabilities": added_list,
            "all_capabilities": [c.value for c in cur_caps.keys()],
            "diff": diff.to_dict()
        }

    def set_gameplay_data(
        self,
        actor_id: str,
        attribute_name: str,
        value: Any,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        if actor_id not in self.actor_data:
            self.actor_data[actor_id] = ActorGameplayData(actor_id=actor_id)

        data = self.actor_data[actor_id]
        prev_val = data.get_effective(attribute_name)

        if prev_val == value:
            return {"success": True, "status": "NO_OP", "actor_id": actor_id}

        diff = GameplayDiff()
        diff.modified_data.append({
            "attribute": attribute_name,
            "before": prev_val,
            "after": value
        })

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        data.instance_overrides[attribute_name] = value

        return {
            "success": True,
            "status": "completed",
            "actor_id": actor_id,
            "attribute": attribute_name,
            "value": value,
            "diff": diff.to_dict()
        }

    def register_interaction(
        self,
        actor_id: str,
        verb: str,
        conditions: Optional[List[Dict[str, Any]]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        priority: int = 50
    ) -> Dict[str, Any]:
        cond_objs = [GameplayCondition(c["type"], c.get("params", {})) for c in (conditions or [])]
        act_objs = [GameplayAction(a["type"], a.get("params", {})) for a in (actions or [])]

        inter_id = f"inter_{verb.lower()}_{actor_id}"
        inter_def = InteractionDefinition(
            interaction_id=inter_id,
            verb=verb.upper(),
            target_actor_id=actor_id,
            conditions=cond_objs,
            actions=act_objs,
            priority=priority
        )
        self.interaction_system.register_interaction(inter_def)

        return {"success": True, "interaction_id": inter_id, "verb": verb.upper()}

    def simulate_interaction(
        self,
        interaction_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        ctx = context or {}
        ok, actions, err = self.interaction_system.execute_interaction(interaction_id, ctx)
        return {
            "success": ok,
            "interaction_id": interaction_id,
            "executed_actions": actions,
            "failure_reason": err
        }

    def get_actor_capabilities(self, actor_id: str) -> List[str]:
        caps = self.actor_capabilities.get(actor_id, {})
        return [c.value for c in caps.keys()]

    def get_gameplay_manifest(self, actor_id: str) -> Dict[str, Any]:
        caps = self.get_actor_capabilities(actor_id)
        data = self.actor_data.get(actor_id)
        inters = self.interaction_system.get_interactions_for_target(actor_id)

        return {
            "actor_id": actor_id,
            "capabilities": caps,
            "data": data.instance_overrides if data else {},
            "interactions": [i.verb for i in inters]
        }
