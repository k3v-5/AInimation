"""
BodyPartType, EquipmentLayerType, and ModularEquipmentLayer models.
UAF-81.21 Sections 18, 19, 20, 147.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class BodyPartType(str, Enum):
    HEAD = "HEAD"
    TORSO = "TORSO"
    PELVIS = "PELVIS"
    UPPER_ARM = "UPPER_ARM"
    LOWER_ARM = "LOWER_ARM"
    HAND = "HAND"
    UPPER_LEG = "UPPER_LEG"
    LOWER_LEG = "LOWER_LEG"
    FOOT = "FOOT"


class EquipmentLayerType(str, Enum):
    BODY = "BODY"
    UNDERWEAR = "UNDERWEAR"
    SHIRT = "SHIRT"
    PANTS = "PANTS"
    ARMOR_CHEST = "ARMOR_CHEST"
    ARMOR_LIMBS = "ARMOR_LIMBS"
    HELMET = "HELMET"
    BACKPACK = "BACKPACK"
    WEAPON = "WEAPON"


@dataclass
class ModularEquipmentLayer:
    layer_id: str
    layer_type: EquipmentLayerType
    is_rigid: bool = False
    clearance_mm: float = 3.0
    material_id: str = "M_Fabric_Nylon"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type.value,
            "is_rigid": self.is_rigid,
            "clearance_mm": self.clearance_mm,
            "material_id": self.material_id,
        }
