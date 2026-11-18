"""
GarmentLayer and GarmentDefinition models for clothing, armor, and layered wearables.
UAF-81.10 Sections 65, 66, 67, 70, 75, 149.
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Dict, Any


class GarmentLayer(IntEnum):
    UNDERWEAR = 0
    INNER_LAYER = 1      # Shirts, undersuits, thermals
    OUTER_GARMENT = 2    # Jackets, pants, coats
    ARMOR_PLATE = 3      # Cuirass, pauldrons, greaves
    TACTICAL_RIG = 4     # Holsters, ammo pouches, webbings
    ACCESSORY = 5        # Capes, cloaks, badges


@dataclass
class GarmentDefinition:
    garment_id: str
    name: str
    layer: GarmentLayer
    target_body_components: List[str]
    material_family: str = "FABRIC"
    thickness_cm: float = 0.5
    is_rigid: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "garment_id": self.garment_id,
            "name": self.name,
            "layer": self.layer.value,
            "target_body_components": self.target_body_components,
            "material_family": self.material_family,
            "thickness_cm": self.thickness_cm,
            "is_rigid": self.is_rigid,
        }

    @classmethod
    def create_tactical_chestplate(cls, garment_id: str = "Arm_Chest_01") -> "GarmentDefinition":
        return cls(
            garment_id=garment_id,
            name="Tactical Chest Armor Plate",
            layer=GarmentLayer.ARMOR_PLATE,
            target_body_components=["body.torso"],
            material_family="CERAMIC_ARMOR",
            thickness_cm=1.2,
            is_rigid=True,
        )
