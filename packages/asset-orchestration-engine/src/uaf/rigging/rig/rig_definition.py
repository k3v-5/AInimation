"""
RigDefinition abstracts control rigs, IK setups, and animation interfaces.
UAF-81.5 Sections 18, 19, 21.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .ik_constraint import IKConstraint, IKType
from ...core.hashing.canonical_hasher import CanonicalHasher


class RigLayer(str, Enum):
    DEFORMATION = "DEFORMATION"
    CONTROL = "CONTROL"
    IK = "IK"
    FACIAL = "FACIAL"
    AUXILIARY = "AUXILIARY"
    EXPORT = "EXPORT"


@dataclass
class RigDefinition:
    rig_id: str
    skeleton_id: str
    ik_chains: List[IKConstraint] = field(default_factory=list)
    control_bones: List[str] = field(default_factory=list)
    layers: List[RigLayer] = field(
        default_factory=lambda: [RigLayer.DEFORMATION, RigLayer.CONTROL, RigLayer.IK, RigLayer.EXPORT]
    )
    version: str = "1.0.0"

    @property
    def rig_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rig_id": self.rig_id,
            "skeleton_id": self.skeleton_id,
            "ik_chains": [c.to_dict() for c in self.ik_chains],
            "control_bones": self.control_bones,
            "layers": [l.value for l in self.layers],
            "version": self.version,
        }

    @classmethod
    def create_standard_humanoid_rig(cls, rig_id: str, skeleton_id: str) -> "RigDefinition":
        ik_chains = [
            IKConstraint(
                chain_id="IK_Arm_L",
                ik_type=IKType.HAND_IK,
                root_bone="upperarm_L",
                mid_bone="lowerarm_L",
                tip_bone="hand_L",
                target_socket="weapon_hand_L",
                pole_vector=[0.0, -1.0, 0.0],
            ),
            IKConstraint(
                chain_id="IK_Arm_R",
                ik_type=IKType.HAND_IK,
                root_bone="upperarm_R",
                mid_bone="lowerarm_R",
                tip_bone="hand_R",
                target_socket="weapon_hand_R",
                pole_vector=[0.0, -1.0, 0.0],
            ),
            IKConstraint(
                chain_id="IK_Leg_L",
                ik_type=IKType.FOOT_IK,
                root_bone="thigh_L",
                mid_bone="calf_L",
                tip_bone="foot_L",
                target_socket="foot_socket_L",
                pole_vector=[0.0, 1.0, 0.0],
            ),
            IKConstraint(
                chain_id="IK_Leg_R",
                ik_type=IKType.FOOT_IK,
                root_bone="thigh_R",
                mid_bone="calf_R",
                tip_bone="foot_R",
                target_socket="foot_socket_R",
                pole_vector=[0.0, 1.0, 0.0],
            ),
        ]
        controls = ["root_ctrl", "pelvis_ctrl", "chest_ctrl", "head_ctrl", "hand_IK_L", "hand_IK_R", "foot_IK_L", "foot_IK_R"]
        return cls(
            rig_id=rig_id,
            skeleton_id=skeleton_id,
            ik_chains=ik_chains,
            control_bones=controls,
        )
