"""
AnimationBlueprintContract, AnimStateMachine, and MontageDefinition models for Unreal Engine 5.
UAF-81.9 Sections 125, 126, 127, 128.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AnimState:
    state_id: str
    clip_id: Optional[str] = None
    is_looping: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "clip_id": self.clip_id,
            "is_looping": self.is_looping,
        }


@dataclass
class AnimTransition:
    from_state: str
    to_state: str
    condition_expression: str  # e.g. "Speed > 10.0"
    blend_time_seconds: float = 0.2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "condition_expression": self.condition_expression,
            "blend_time_seconds": self.blend_time_seconds,
        }


@dataclass
class AnimStateMachine:
    machine_id: str
    entry_state: str = "IDLE"
    states: Dict[str, AnimState] = field(default_factory=dict)
    transitions: List[AnimTransition] = field(default_factory=list)

    def add_state(self, state: AnimState) -> None:
        self.states[state.state_id] = state

    def add_transition(self, transition: AnimTransition) -> None:
        self.transitions.append(transition)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "entry_state": self.entry_state,
            "states": {k: v.to_dict() for k, v in sorted(self.states.items())},
            "transitions": [t.to_dict() for t in self.transitions],
        }


@dataclass
class MontageDefinition:
    montage_id: str
    clip_id: str
    blend_in_time: float = 0.15
    blend_out_time: float = 0.2
    slot_name: str = "DefaultGroup.UpperBody"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "montage_id": self.montage_id,
            "clip_id": self.clip_id,
            "blend_in_time": self.blend_in_time,
            "blend_out_time": self.blend_out_time,
            "slot_name": self.slot_name,
        }


@dataclass
class AnimationBlueprintContract:
    blueprint_id: str
    state_machine: AnimStateMachine
    parameters: Dict[str, str] = field(default_factory=dict)  # param_name -> type ("float", "bool", "vector")
    montages: List[MontageDefinition] = field(default_factory=list)
    ik_enabled: bool = True
    version: str = "1.0.0"

    @property
    def blueprint_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "state_machine": self.state_machine.to_dict(),
            "parameters": self.parameters,
            "montages": [m.to_dict() for m in self.montages],
            "ik_enabled": self.ik_enabled,
            "version": self.version,
        }

    @classmethod
    def create_standard_locomotion_contract(cls, blueprint_id: str = "ABP_Hero") -> "AnimationBlueprintContract":
        sm = AnimStateMachine(machine_id="LocomotionSM", entry_state="IDLE")
        sm.add_state(AnimState("IDLE", "A_Hero_Idle"))
        sm.add_state(AnimState("WALK", "A_Hero_Walk"))
        sm.add_state(AnimState("RUN", "A_Hero_Run"))

        sm.add_transition(AnimTransition("IDLE", "WALK", "Speed > 5.0", 0.2))
        sm.add_transition(AnimTransition("WALK", "IDLE", "Speed <= 5.0", 0.2))
        sm.add_transition(AnimTransition("WALK", "RUN", "Speed > 250.0", 0.2))
        sm.add_transition(AnimTransition("RUN", "WALK", "Speed <= 250.0", 0.2))

        params = {
            "Speed": "float",
            "Direction": "float",
            "IsCrouched": "bool",
            "IsAiming": "bool",
            "IsFalling": "bool",
        }

        montage = MontageDefinition("AM_Attack_Light", "A_Hero_Attack_01")
        return cls(blueprint_id=blueprint_id, state_machine=sm, parameters=params, montages=[montage])
