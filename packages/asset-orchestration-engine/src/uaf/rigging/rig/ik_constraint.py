"""
IKConstraint and IKType models for kinematic solver chains.
UAF-81.5 Sections 22, 23, 24.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class IKType(str, Enum):
    TWO_BONE_IK = "TWO_BONE_IK"
    FABRIK = "FABRIK"
    CCD = "CCD"
    FOOT_IK = "FOOT_IK"
    HAND_IK = "HAND_IK"


@dataclass
class IKConstraint:
    chain_id: str
    ik_type: IKType
    root_bone: str
    mid_bone: str
    tip_bone: str
    target_socket: str
    pole_vector: Optional[List[float]] = None
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "ik_type": self.ik_type.value,
            "root_bone": self.root_bone,
            "mid_bone": self.mid_bone,
            "tip_bone": self.tip_bone,
            "target_socket": self.target_socket,
            "pole_vector": self.pole_vector,
            "weight": self.weight,
        }
