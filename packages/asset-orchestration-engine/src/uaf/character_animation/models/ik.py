"""
IKSolverType and IKChain models for kinematic rigs.
UAF-81.17 Sections 25, 26, 27, 28, 29, 30.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class IKSolverType(str, Enum):
    TWO_BONE = "TWO_BONE"
    FABRIK = "FABRIK"
    CCD = "CCD"


@dataclass
class IKChain:
    chain_id: str
    chain_type: str  # "LEFT_ARM", "RIGHT_ARM", "LEFT_LEG", "RIGHT_LEG", "LOOK_AT"
    start_bone: str
    end_effector: str
    solver: IKSolverType = IKSolverType.TWO_BONE
    pole_vector_bone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "chain_type": self.chain_type,
            "start_bone": self.start_bone,
            "end_effector": self.end_effector,
            "solver": self.solver.value,
            "pole_vector_bone": self.pole_vector_bone,
        }

    @classmethod
    def create_humanoid_ik_set(cls) -> List["IKChain"]:
        return [
            cls("IK_Arm_L", "LEFT_ARM", "upperarm_l", "hand_l", IKSolverType.TWO_BONE),
            cls("IK_Arm_R", "RIGHT_ARM", "upperarm_r", "hand_r", IKSolverType.TWO_BONE),
            cls("IK_Leg_L", "LEFT_LEG", "thigh_l", "foot_l", IKSolverType.TWO_BONE),
            cls("IK_Leg_R", "RIGHT_LEG", "thigh_r", "foot_r", IKSolverType.TWO_BONE),
            cls("IK_LookAt", "LOOK_AT", "neck_01", "head", IKSolverType.CCD),
        ]
