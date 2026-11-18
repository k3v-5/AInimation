from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class CapabilityType(str, Enum):
    INTERACTABLE = "INTERACTABLE"
    PICKUP = "PICKUP"
    EQUIPPABLE = "EQUIPPABLE"
    DAMAGE_DEALER = "DAMAGE_DEALER"
    DAMAGE_RECEIVER = "DAMAGE_RECEIVER"
    HEALTH = "HEALTH"
    OPENABLE = "OPENABLE"
    LOCKABLE = "LOCKABLE"
    DESTRUCTIBLE = "DESTRUCTIBLE"

@dataclass
class CapabilityDefinition:
    capability_type: CapabilityType
    version: str = "1.0"
    required_capabilities: List[CapabilityType] = field(default_factory=list)
    parameters_schema: Dict[str, Any] = field(default_factory=dict) # param_name -> schema
    required_components: List[str] = field(default_factory=list)

@dataclass
class CapabilityInstance:
    capability_type: CapabilityType
    version: str = "1.0"
    parameters: Dict[str, Any] = field(default_factory=dict)

class CapabilityRegistry:
    def __init__(self):
        self.definitions: Dict[CapabilityType, CapabilityDefinition] = {}
        self._register_default_capabilities()

    def _register_default_capabilities(self):
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.INTERACTABLE,
            version="1.0",
            required_components=["InteractionComponent"],
            parameters_schema={"interaction_distance": float, "prompt_text": str}
        ))
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.PICKUP,
            version="1.0",
            required_capabilities=[CapabilityType.INTERACTABLE],
            required_components=["PickupComponent"],
            parameters_schema={"pickup_mode": str, "auto_equip": bool}
        ))
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.EQUIPPABLE,
            version="1.0",
            required_capabilities=[CapabilityType.INTERACTABLE, CapabilityType.PICKUP],
            required_components=["EquipmentComponent"],
            parameters_schema={"equip_slot": str, "socket_name": str}
        ))
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.DAMAGE_DEALER,
            version="1.0",
            required_components=["DamageDealerComponent"],
            parameters_schema={"base_damage": float, "damage_type": str}
        ))
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.OPENABLE,
            version="1.0",
            required_capabilities=[CapabilityType.INTERACTABLE],
            required_components=["OpenableComponent"],
            parameters_schema={"initial_state": str, "auto_close": bool}
        ))
        self.register(CapabilityDefinition(
            capability_type=CapabilityType.LOCKABLE,
            version="1.0",
            required_capabilities=[CapabilityType.OPENABLE],
            required_components=["LockableComponent"],
            parameters_schema={"required_key": str, "is_locked": bool}
        ))

    def register(self, definition: CapabilityDefinition):
        self.definitions[definition.capability_type] = definition

    def get(self, cap_type: CapabilityType) -> Optional[CapabilityDefinition]:
        return self.definitions.get(cap_type)
