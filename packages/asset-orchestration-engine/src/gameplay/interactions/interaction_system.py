from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

@dataclass
class GameplayCondition:
    condition_type: str # PLAYER_NEAR, HAS_ITEM, HAS_SPACE, STATE_IS
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GameplayAction:
    action_type: str # ADD_ITEM, REMOVE_ITEM, EQUIP_ITEM, DEAL_DAMAGE, HEAL, PLAY_ANIMATION
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InteractionDefinition:
    interaction_id: str
    verb: str # PICK_UP, OPEN, EQUIP, ATTACK, USE
    target_actor_id: str
    conditions: List[GameplayCondition] = field(default_factory=list)
    actions: List[GameplayAction] = field(default_factory=list)
    priority: int = 50
    cooldown: float = 0.0

class InteractionSystem:
    def __init__(self):
        self.interactions: Dict[str, InteractionDefinition] = {} # id -> InteractionDefinition

    def register_interaction(self, interaction: InteractionDefinition):
        self.interactions[interaction.interaction_id] = interaction

    def get_interactions_for_target(self, target_actor_id: str) -> List[InteractionDefinition]:
        return [i for i in self.interactions.values() if i.target_actor_id == target_actor_id]

    def execute_interaction(
        self,
        interaction_id: str,
        context: Dict[str, Any]
    ) -> Tuple[bool, List[str], Optional[str]]:
        """
        Evalúa condiciones y ejecuta acciones en cascada.
        Devuelve (success, executed_actions, failure_reason).
        """
        inter = self.interactions.get(interaction_id)
        if not inter:
            return False, [], "INTERACTION_NOT_FOUND"

        # 1. Evaluar Condiciones
        for cond in inter.conditions:
            if cond.condition_type == "PLAYER_NEAR":
                dist = context.get("player_distance", 9999.0)
                max_dist = cond.parameters.get("max_distance", 200.0)
                if dist > max_dist:
                    return False, [], "PLAYER_TOO_FAR"

            elif cond.condition_type == "HAS_ITEM":
                inv = context.get("player_inventory", [])
                req_item = cond.parameters.get("item_id")
                if req_item and req_item not in inv:
                    return False, [], f"MISSING_REQUIRED_ITEM_{req_item}"

            elif cond.condition_type == "HAS_SPACE":
                has_space = context.get("inventory_has_space", True)
                if not has_space:
                    return False, [], "INVENTORY_FULL"

        # 2. Ejecutar Acciones
        executed = []
        for act in inter.actions:
            executed.append(act.action_type)

        return True, executed, None
