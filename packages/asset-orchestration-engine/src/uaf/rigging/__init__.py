"""
Universal Asset Factory (UAF) - Character Rigging, Skinning & Deformation Fabric (UAF-81.5)
"""

from .skeleton import (
    BoneRole,
    BoneDefinition,
    BindPoseType,
    SkeletonArchetype,
    CharacterSkeletonDefinition,
    SkeletonBuilder,
)

from .rig import (
    IKType,
    IKConstraint,
    RigLayer,
    RigDefinition,
)

from .skinning import (
    WeightMethod,
    VertexWeights,
    SkinningDefinition,
    WeightNormalizer,
    WeightGenerator,
)

from .deformation import (
    DeformationZone,
    DeformationTestPose,
    CorrectiveBlendshape,
    DeformationScore,
    DeformationEvaluator,
)

from .facial import (
    FacialRigDefinition,
    STANDARD_FACIAL_BLENDSHAPES,
)

from .physics import (
    PhysicsBody,
    PhysicsConstraint,
    PhysicsAssetDefinition,
)

from .retargeting import (
    RetargetProfile,
    UE5_MANNEQUIN_BONE_MAP,
    UnrealCharacterPackage,
)

from .validation import (
    RigValidator,
    RigValidationReport,
)

__all__ = [
    "BoneRole",
    "BoneDefinition",
    "BindPoseType",
    "SkeletonArchetype",
    "CharacterSkeletonDefinition",
    "SkeletonBuilder",
    "IKType",
    "IKConstraint",
    "RigLayer",
    "RigDefinition",
    "WeightMethod",
    "VertexWeights",
    "SkinningDefinition",
    "WeightNormalizer",
    "WeightGenerator",
    "DeformationZone",
    "DeformationTestPose",
    "CorrectiveBlendshape",
    "DeformationScore",
    "DeformationEvaluator",
    "FacialRigDefinition",
    "STANDARD_FACIAL_BLENDSHAPES",
    "PhysicsBody",
    "PhysicsConstraint",
    "PhysicsAssetDefinition",
    "RetargetProfile",
    "UE5_MANNEQUIN_BONE_MAP",
    "UnrealCharacterPackage",
    "RigValidator",
    "RigValidationReport",
]
