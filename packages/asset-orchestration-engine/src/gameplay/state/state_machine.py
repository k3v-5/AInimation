from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

@dataclass
class StateDefinition:
    state_id: str
    allowed_transitions: List[str] = field(default_factory=list)

class StateMachine:
    def __init__(self, machine_id: str, initial_state: str):
        self.machine_id = machine_id
        self.current_state = initial_state
        self.states: Dict[str, StateDefinition] = {}

    def add_state(self, state_id: str, allowed_transitions: List[str]):
        self.states[state_id] = StateDefinition(state_id=state_id, allowed_transitions=allowed_transitions)

    def transition_to(self, new_state: str) -> Tuple[bool, Optional[str]]:
        current_def = self.states.get(self.current_state)
        if not current_def:
            return False, f"INVALID_STATE: Current state '{self.current_state}' not defined."

        if new_state not in current_def.allowed_transitions:
            return False, f"INVALID_STATE_TRANSITION: Cannot transition from '{self.current_state}' to '{new_state}'. Allowed: {current_def.allowed_transitions}."

        self.current_state = new_state
        return True, None
