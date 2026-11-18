"""
Universal Character, Creature, Rigging & Deformation System Domain Models.
UAF-81.54 Sections 1-136, 176, 177.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


# --- ENUMS ---

class CharacterSpecies(str, Enum):
    HUMAN = "HUMAN"
    HUMANOID = "HUMANOID"
    CREATURE = "CREATURE"
    ANIMAL = "ANIMAL"
    ROBOT = "ROBOT"
    ALIEN = "ALIEN"
    MONSTER = "MONSTER"
    CYBERNETIC = "CYBERNETIC"
    MUTANT = "MUTANT"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


class CharacterArchetype(str, Enum):
    HUMAN = "HUMAN"
    HUMANOID = "HUMANOID"
    QUADRUPED = "QUADRUPED"
    BIPED_CREATURE = "BIPED_CREATURE"
    MULTI_LIMB = "MULTI_LIMB"
    ROBOT = "ROBOT"
    SERPENT = "SERPENT"
    INSECTOID = "INSECTOID"
    CUSTOM = "CUSTOM"


class BodyShape(str, Enum):
    SLIM = "SLIM"
    AVERAGE = "AVERAGE"
    MUSCULAR = "MUSCULAR"
    HEAVY = "HEAVY"
    ATHLETIC = "ATHLETIC"
    LEAN = "LEAN"
    CUSTOM = "CUSTOM"


class ProportionNormalization(str, Enum):
    ABSOLUTE = "ABSOLUTE"
    RELATIVE_TO_HEIGHT = "RELATIVE_TO_HEIGHT"
    RELATIVE_TO_PARENT = "RELATIVE_TO_PARENT"
    NORMALIZED = "NORMALIZED"


class AnatomicalRegionType(str, Enum):
    HEAD = "HEAD"
    NECK = "NECK"
    TORSO = "TORSO"
    PELVIS = "PELVIS"
    UPPER_ARM_L = "UPPER_ARM_L"
    UPPER_ARM_R = "UPPER_ARM_R"
    FOREARM_L = "FOREARM_L"
    FOREARM_R = "FOREARM_R"
    HAND_L = "HAND_L"
    HAND_R = "HAND_R"
    THIGH_L = "THIGH_L"
    THIGH_R = "THIGH_R"
    CALF_L = "CALF_L"
    CALF_R = "CALF_R"
    FOOT_L = "FOOT_L"
    FOOT_R = "FOOT_R"
    CUSTOM = "CUSTOM"


class SymmetryType(str, Enum):
    BILATERAL = "BILATERAL"
    RADIAL = "RADIAL"
    NONE = "NONE"
    CUSTOM = "CUSTOM"


class SeamType(str, Enum):
    HIDDEN = "HIDDEN"
    VISIBLE = "VISIBLE"
    DEFORMATION = "DEFORMATION"
    MATERIAL = "MATERIAL"
    TOPOLOGY = "TOPOLOGY"
    CUSTOM = "CUSTOM"


class FootVariant(str, Enum):
    HUMAN = "HUMAN"
    PAW = "PAW"
    HOOF = "HOOF"
    CLAW = "CLAW"
    ROBOTIC = "ROBOTIC"
    CUSTOM = "CUSTOM"


class ClothingType(str, Enum):
    SHIRT = "SHIRT"
    PANTS = "PANTS"
    DRESS = "DRESS"
    COAT = "COAT"
    JACKET = "JACKET"
    BOOTS = "BOOTS"
    GLOVES = "GLOVES"
    HAT = "HAT"
    MASK = "MASK"
    CUSTOM = "CUSTOM"


class ClothingFit(str, Enum):
    TIGHT = "TIGHT"
    REGULAR = "REGULAR"
    LOOSE = "LOOSE"
    OVERSIZED = "OVERSIZED"
    CUSTOM = "CUSTOM"


class ArmorComponentType(str, Enum):
    HELMET = "HELMET"
    CHEST = "CHEST"
    SHOULDER = "SHOULDER"
    ARM = "ARM"
    FOREARM = "FOREARM"
    HAND = "HAND"
    THIGH = "THIGH"
    KNEE = "KNEE"
    SHIN = "SHIN"
    BOOT = "BOOT"
    BACK = "BACK"
    CUSTOM = "CUSTOM"


class AccessoryType(str, Enum):
    BELT = "BELT"
    POUCH = "POUCH"
    BACKPACK = "BACKPACK"
    JEWELRY = "JEWELRY"
    WEAPON_MOUNT = "WEAPON_MOUNT"
    HOLSTER = "HOLSTER"
    BADGE = "BADGE"
    CUSTOM = "CUSTOM"


class AccessorySocket(str, Enum):
    HEAD = "HEAD"
    CHEST = "CHEST"
    BACK = "BACK"
    WAIST = "WAIST"
    HAND = "HAND"
    THIGH = "THIGH"
    ANKLE = "ANKLE"
    CUSTOM = "CUSTOM"


class HairType(str, Enum):
    MESH_HAIR = "MESH_HAIR"
    CARD_HAIR = "CARD_HAIR"
    STRAND_REFERENCE = "STRAND_REFERENCE"
    CUSTOM = "CUSTOM"


class IKType(str, Enum):
    TWO_BONE = "TWO_BONE"
    FABRIK = "FABRIK"
    CCD = "CCD"
    CUSTOM = "CUSTOM"


class ConstraintType(str, Enum):
    AIM = "AIM"
    COPY_TRANSFORM = "COPY_TRANSFORM"
    LIMIT_ROTATION = "LIMIT_ROTATION"
    LIMIT_POSITION = "LIMIT_POSITION"
    PARENT = "PARENT"
    TRACK = "TRACK"
    IK = "IK"
    CUSTOM = "CUSTOM"


class SkinningMethod(str, Enum):
    LINEAR_BLEND = "LINEAR_BLEND"
    DUAL_QUATERNION = "DUAL_QUATERNION"
    CUSTOM = "CUSTOM"


class WeightStrategy(str, Enum):
    DISTANCE = "DISTANCE"
    HEAT = "HEAT"
    ENVELOPE = "ENVELOPE"
    TRANSFER = "TRANSFER"
    PAINTED = "PAINTED"
    CUSTOM = "CUSTOM"


class MorphType(str, Enum):
    BODY = "BODY"
    FACE = "FACE"
    CORRECTIVE = "CORRECTIVE"
    EXPRESSION = "EXPRESSION"
    CUSTOM = "CUSTOM"


class FacialExpressionPreset(str, Enum):
    NEUTRAL = "NEUTRAL"
    HAPPY = "HAPPY"
    SAD = "SAD"
    ANGRY = "ANGRY"
    SURPRISED = "SURPRISED"
    FEAR = "FEAR"
    DISGUST = "DISGUST"
    CUSTOM = "CUSTOM"


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class ValidationCategory(str, Enum):
    IDENTITY = "IDENTITY"
    ANATOMY = "ANATOMY"
    MESH = "MESH"
    TOPOLOGY = "TOPOLOGY"
    SKELETON = "SKELETON"
    RIG = "RIG"
    SKIN = "SKIN"
    WEIGHTS = "WEIGHTS"
    MORPHS = "MORPHS"
    FACIAL = "FACIAL"
    CLOTHING = "CLOTHING"
    ARMOR = "ARMOR"
    COLLISION = "COLLISION"
    LOD = "LOD"
    ANIMATION = "ANIMATION"
    EXPORT = "EXPORT"


# --- DATACLASSES ---

@dataclass
class BodyProportions:
    height: float = 180.0
    shoulder_width: float = 45.0
    chest_depth: float = 28.0
    waist_width: float = 32.0
    hip_width: float = 36.0
    arm_length: float = 75.0
    forearm_length: float = 45.0
    hand_size: float = 19.0
    leg_length: float = 90.0
    foot_length: float = 27.0
    head_size: float = 24.0
    neck_length: float = 12.0
    normalization_mode: ProportionNormalization = ProportionNormalization.ABSOLUTE

    @property
    def is_valid(self) -> bool:
        return (
            self.height > 0.0 and
            self.shoulder_width > 0.0 and
            self.chest_depth > 0.0 and
            self.waist_width > 0.0 and
            self.hip_width > 0.0 and
            self.arm_length > 0.0 and
            self.forearm_length > 0.0 and
            self.hand_size > 0.0 and
            self.leg_length > 0.0 and
            self.foot_length > 0.0 and
            self.head_size > 0.0 and
            self.neck_length > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height": self.height,
            "shoulder_width": self.shoulder_width,
            "chest_depth": self.chest_depth,
            "waist_width": self.waist_width,
            "hip_width": self.hip_width,
            "arm_length": self.arm_length,
            "forearm_length": self.forearm_length,
            "hand_size": self.hand_size,
            "leg_length": self.leg_length,
            "foot_length": self.foot_length,
            "head_size": self.head_size,
            "neck_length": self.neck_length,
            "normalization_mode": self.normalization_mode.value,
        }


@dataclass
class CustomAnatomicalRegion:
    name: str
    parent: str
    symmetry_group: str = "DEFAULT"
    mesh_components: List[str] = field(default_factory=list)
    bones: List[str] = field(default_factory=list)
    deformation_profile: str = "DEFAULT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parent": self.parent,
            "symmetry_group": self.symmetry_group,
            "mesh_components": self.mesh_components,
            "bones": self.bones,
            "deformation_profile": self.deformation_profile,
        }


@dataclass
class AttachmentPoint:
    name: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    parent_region: str = "TORSO"
    socket_type: str = "SOCKET"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "parent_region": self.parent_region,
            "socket_type": self.socket_type,
        }


@dataclass
class BodyComponent:
    component_id: str
    region: str
    mesh: str
    attachment_points: List[AttachmentPoint] = field(default_factory=list)
    symmetry: SymmetryType = SymmetryType.BILATERAL
    material_slots: List[str] = field(default_factory=lambda: ["M_Body"])
    deformation_profile: str = "STANDARD"
    lod_profile: str = "STANDARD"
    collision_profile: str = "CAPSULE"
    component_version: str = "1.0.0"
    generator_version: str = "1.0.0"
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "region": self.region,
            "mesh": self.mesh,
            "attachment_points": [ap.to_dict() for ap in self.attachment_points],
            "symmetry": self.symmetry.value,
            "material_slots": self.material_slots,
            "deformation_profile": self.deformation_profile,
            "lod_profile": self.lod_profile,
            "collision_profile": self.collision_profile,
            "component_version": self.component_version,
            "generator_version": self.generator_version,
            "schema_version": self.schema_version,
        }


@dataclass
class HeadDefinition:
    head_width: float = 16.0
    head_height: float = 24.0
    jaw_width: float = 12.0
    jaw_depth: float = 14.0
    cheek_width: float = 14.0
    brow_height: float = 18.0
    chin_size: float = 6.0
    eye_spacing: float = 6.5
    nose_width: float = 3.5
    nose_length: float = 5.0
    mouth_width: float = 5.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "head_width": self.head_width,
            "head_height": self.head_height,
            "jaw_width": self.jaw_width,
            "jaw_depth": self.jaw_depth,
            "cheek_width": self.cheek_width,
            "brow_height": self.brow_height,
            "chin_size": self.chin_size,
            "eye_spacing": self.eye_spacing,
            "nose_width": self.nose_width,
            "nose_length": self.nose_length,
            "mouth_width": self.mouth_width,
        }


@dataclass
class EyeDefinition:
    has_eyeball: bool = True
    has_iris: bool = True
    has_pupil: bool = True
    has_cornea: bool = True
    has_eyelid: bool = True
    has_tear_line: bool = True
    eye_alignment: float = 1.0  # 1.0 = perfectly aligned
    gaze_axis: Tuple[float, float, float] = (0.0, 1.0, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_eyeball": self.has_eyeball,
            "has_iris": self.has_iris,
            "has_pupil": self.has_pupil,
            "has_cornea": self.has_cornea,
            "has_eyelid": self.has_eyelid,
            "has_tear_line": self.has_tear_line,
            "eye_alignment": self.eye_alignment,
            "gaze_axis": self.gaze_axis,
        }


@dataclass
class EarDefinition:
    has_ear_l: bool = True
    has_ear_r: bool = True
    ear_scale: float = 1.0
    ear_type: str = "HUMAN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_ear_l": self.has_ear_l,
            "has_ear_r": self.has_ear_r,
            "ear_scale": self.ear_scale,
            "ear_type": self.ear_type,
        }


@dataclass
class NoseDefinition:
    nose_type: str = "INTEGRATED"  # INTEGRATED, MODULAR, CUSTOM
    bridge_height: float = 4.0
    nostril_flare: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nose_type": self.nose_type,
            "bridge_height": self.bridge_height,
            "nostril_flare": self.nostril_flare,
        }


@dataclass
class TeethDefinition:
    tooth_count: int = 32
    tooth_scale: float = 1.0
    tooth_spacing: float = 0.2
    tooth_profile: str = "HUMAN_STANDARD"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tooth_count": self.tooth_count,
            "tooth_scale": self.tooth_scale,
            "tooth_spacing": self.tooth_spacing,
            "tooth_profile": self.tooth_profile,
        }


@dataclass
class MouthDefinition:
    has_lips: bool = True
    has_teeth: bool = True
    has_tongue: bool = True
    has_gums: bool = True
    has_jaw: bool = True
    teeth_def: TeethDefinition = field(default_factory=TeethDefinition)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_lips": self.has_lips,
            "has_teeth": self.has_teeth,
            "has_tongue": self.has_tongue,
            "has_gums": self.has_gums,
            "has_jaw": self.has_jaw,
            "teeth_def": self.teeth_def.to_dict(),
        }


@dataclass
class HandDefinition:
    palm_length: float = 10.5
    palm_width: float = 8.5
    finger_length: float = 8.0
    finger_width: float = 1.8
    thumb_length: float = 6.0
    nail_length: float = 0.5
    fingers: List[str] = field(default_factory=lambda: ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"])
    segments_per_finger: int = 3  # PROXIMAL, INTERMEDIATE, DISTAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "palm_length": self.palm_length,
            "palm_width": self.palm_width,
            "finger_length": self.finger_length,
            "finger_width": self.finger_width,
            "thumb_length": self.thumb_length,
            "nail_length": self.nail_length,
            "fingers": self.fingers,
            "segments_per_finger": self.segments_per_finger,
        }


@dataclass
class FootDefinition:
    heel_length: float = 7.0
    arch_height: float = 2.5
    sole_width: float = 9.0
    toe_count: int = 5
    foot_variant: FootVariant = FootVariant.HUMAN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heel_length": self.heel_length,
            "arch_height": self.arch_height,
            "sole_width": self.sole_width,
            "toe_count": self.toe_count,
            "foot_variant": self.foot_variant.value,
        }


@dataclass
class CreatureComponentDefinition:
    component_type: str  # LIMB, TAIL, WING, HORN
    count: int = 1
    length: float = 50.0
    radius: float = 8.0
    segments: int = 5
    curvature: float = 0.1
    symmetry: SymmetryType = SymmetryType.BILATERAL
    chain_bones: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_type": self.component_type,
            "count": self.count,
            "length": self.length,
            "radius": self.radius,
            "segments": self.segments,
            "curvature": self.curvature,
            "symmetry": self.symmetry.value,
            "chain_bones": self.chain_bones,
        }


@dataclass
class ClothingDefinition:
    clothing_id: str
    clothing_type: ClothingType
    fit: ClothingFit = ClothingFit.REGULAR
    minimum_clearance: float = 0.5  # cm
    maximum_intersection: float = 0.0  # cm allowable penetration
    mesh: str = "SM_Shirt"
    material_slots: List[str] = field(default_factory=lambda: ["M_Cloth"])
    deformation_regions: List[str] = field(default_factory=lambda: ["TORSO"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clothing_id": self.clothing_id,
            "clothing_type": self.clothing_type.value,
            "fit": self.fit.value,
            "minimum_clearance": self.minimum_clearance,
            "maximum_intersection": self.maximum_intersection,
            "mesh": self.mesh,
            "material_slots": self.material_slots,
            "deformation_regions": self.deformation_regions,
        }


@dataclass
class ArmorDefinition:
    armor_id: str
    armor_type: ArmorComponentType
    attachment_socket: str = "SOCKET_Chest"
    clearance: float = 1.0  # cm
    mass_kg: float = 5.0
    material_slots: List[str] = field(default_factory=lambda: ["M_ArmorPlate"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "armor_id": self.armor_id,
            "armor_type": self.armor_type.value,
            "attachment_socket": self.attachment_socket,
            "clearance": self.clearance,
            "mass_kg": self.mass_kg,
            "material_slots": self.material_slots,
        }


@dataclass
class AccessoryDefinition:
    accessory_id: str
    accessory_type: AccessoryType
    socket: AccessorySocket = AccessorySocket.WAIST
    attachment_offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessory_id": self.accessory_id,
            "accessory_type": self.accessory_type.value,
            "socket": self.socket.value,
            "attachment_offset": self.attachment_offset,
        }


@dataclass
class HairDefinition:
    hair_id: str
    hair_type: HairType = HairType.MESH_HAIR
    scalp_coverage: float = 0.85
    penetration_tolerance: float = 0.2
    lod_supported: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hair_id": self.hair_id,
            "hair_type": self.hair_type.value,
            "scalp_coverage": self.scalp_coverage,
            "penetration_tolerance": self.penetration_tolerance,
            "lod_supported": self.lod_supported,
        }


@dataclass
class BoneDefinition:
    name: str
    parent: Optional[str] = None
    rest_transform: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    length: float = 10.0
    orientation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    semantic_role: str = "STRUCTURE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parent": self.parent,
            "rest_transform": self.rest_transform,
            "length": self.length,
            "orientation": self.orientation,
            "semantic_role": self.semantic_role,
        }


@dataclass
class RestPose:
    bone_transforms: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    is_frozen: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_transforms": self.bone_transforms,
            "is_frozen": self.is_frozen,
        }


@dataclass
class SkeletonDefinition:
    skeleton_id: str
    bones: List[BoneDefinition] = field(default_factory=list)
    rest_pose: RestPose = field(default_factory=RestPose)

    @property
    def bone_names(self) -> List[str]:
        return [b.name for b in self.bones]

    def has_duplicate_bones(self) -> bool:
        names = self.bone_names
        return len(names) != len(set(names))

    def has_cyclic_hierarchy(self) -> bool:
        parent_map = {b.name: b.parent for b in self.bones if b.parent}
        for start_bone in parent_map:
            visited = set()
            curr = start_bone
            while curr in parent_map:
                if curr in visited:
                    return True
                visited.add(curr)
                curr = parent_map[curr]
        return False

    def has_missing_parents(self) -> bool:
        names = set(self.bone_names)
        for b in self.bones:
            if b.parent is not None and b.parent not in names:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "bones": [b.to_dict() for b in self.bones],
            "rest_pose": self.rest_pose.to_dict(),
        }


@dataclass
class IKChain:
    name: str
    root: str
    effector: str
    pole: str
    chain_length: int = 2
    weight: float = 1.0
    ik_type: IKType = IKType.TWO_BONE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root": self.root,
            "effector": self.effector,
            "pole": self.pole,
            "chain_length": self.chain_length,
            "weight": self.weight,
            "ik_type": self.ik_type.value,
        }


@dataclass
class ConstraintDefinition:
    name: str
    constraint_type: ConstraintType
    source: str
    target: str
    influence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "constraint_type": self.constraint_type.value,
            "source": self.source,
            "target": self.target,
            "influence": self.influence,
        }


@dataclass
class RigDefinition:
    rig_id: str
    skeleton_id: str
    controls: List[str] = field(default_factory=list)
    ik_chains: List[IKChain] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    foot_ik_enabled: bool = True
    hand_ik_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rig_id": self.rig_id,
            "skeleton_id": self.skeleton_id,
            "controls": self.controls,
            "ik_chains": [ik.to_dict() for ik in self.ik_chains],
            "constraints": [c.to_dict() for c in self.constraints],
            "foot_ik_enabled": self.foot_ik_enabled,
            "hand_ik_enabled": self.hand_ik_enabled,
        }


@dataclass
class VertexWeight:
    bone_name: str
    weight: float


@dataclass
class SkinningDefinition:
    skinning_id: str
    method: SkinningMethod = SkinningMethod.LINEAR_BLEND
    strategy: WeightStrategy = WeightStrategy.DISTANCE
    max_influences_per_vertex: int = 4
    weights_per_vertex: Dict[int, List[VertexWeight]] = field(default_factory=dict)

    def is_normalized(self, tolerance: float = 1e-3) -> bool:
        for v_idx, influences in self.weights_per_vertex.items():
            s = sum(inf.weight for inf in influences)
            if abs(s - 1.0) > tolerance:
                return False
        return True

    def exceeds_influence_limit(self) -> bool:
        for v_idx, influences in self.weights_per_vertex.items():
            if len(influences) > self.max_influences_per_vertex:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skinning_id": self.skinning_id,
            "method": self.method.value,
            "strategy": self.strategy.value,
            "max_influences_per_vertex": self.max_influences_per_vertex,
            "vertex_count": len(self.weights_per_vertex),
        }


@dataclass
class JointDeformationScore:
    shoulder: float = 1.0
    elbow: float = 1.0
    wrist: float = 1.0
    hip: float = 1.0
    knee: float = 1.0
    ankle: float = 1.0
    neck: float = 1.0
    spine: float = 1.0

    @property
    def average_score(self) -> float:
        scores = [
            self.shoulder, self.elbow, self.wrist, self.hip,
            self.knee, self.ankle, self.neck, self.spine
        ]
        return round(sum(scores) / len(scores), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shoulder": self.shoulder,
            "elbow": self.elbow,
            "wrist": self.wrist,
            "hip": self.hip,
            "knee": self.knee,
            "ankle": self.ankle,
            "neck": self.neck,
            "spine": self.spine,
            "average_score": self.average_score,
        }


@dataclass
class CorrectiveShapeDefinition:
    shape_id: str
    trigger_joint: str
    trigger_angle_degrees: float
    blend_weight: float = 1.0
    delta_vertex_count: int = 240

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape_id": self.shape_id,
            "trigger_joint": self.trigger_joint,
            "trigger_angle_degrees": self.trigger_angle_degrees,
            "blend_weight": self.blend_weight,
            "delta_vertex_count": self.delta_vertex_count,
        }


@dataclass
class DeformationProfile:
    profile_id: str
    volume_loss_percent: float = 2.5
    surface_stretch_percent: float = 3.0
    surface_compression_percent: float = 2.0
    joint_scores: JointDeformationScore = field(default_factory=JointDeformationScore)
    preserve_volume: bool = True
    correctives: List[CorrectiveShapeDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "volume_loss_percent": self.volume_loss_percent,
            "surface_stretch_percent": self.surface_stretch_percent,
            "surface_compression_percent": self.surface_compression_percent,
            "joint_scores": self.joint_scores.to_dict(),
            "preserve_volume": self.preserve_volume,
            "correctives": [c.to_dict() for c in self.correctives],
        }


@dataclass
class MorphTarget:
    name: str
    morph_type: MorphType
    vertex_count: int
    delta_bounds_cm: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "morph_type": self.morph_type.value,
            "vertex_count": self.vertex_count,
            "delta_bounds_cm": self.delta_bounds_cm,
        }


@dataclass
class FacialRigDefinition:
    rig_id: str
    jaw_open: float = 0.0
    jaw_forward: float = 0.0
    jaw_side: float = 0.0
    eye_blink_l: float = 0.0
    eye_blink_r: float = 0.0
    eye_look_up: float = 0.0
    eye_look_down: float = 0.0
    eye_look_left: float = 0.0
    eye_look_right: float = 0.0
    mouth_smile_l: float = 0.0
    mouth_smile_r: float = 0.0
    mouth_frown_l: float = 0.0
    mouth_frown_r: float = 0.0
    brow_up_l: float = 0.0
    brow_up_r: float = 0.0
    brow_down_l: float = 0.0
    brow_down_r: float = 0.0
    active_preset: FacialExpressionPreset = FacialExpressionPreset.NEUTRAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rig_id": self.rig_id,
            "active_preset": self.active_preset.value,
            "jaw_open": self.jaw_open,
            "eye_blink_l": self.eye_blink_l,
            "eye_blink_r": self.eye_blink_r,
            "mouth_smile_l": self.mouth_smile_l,
            "mouth_smile_r": self.mouth_smile_r,
            "brow_up_l": self.brow_up_l,
            "brow_up_r": self.brow_up_r,
        }


@dataclass
class MorphTargetSystem:
    system_id: str
    base_vertex_count: int = 1200
    morphs: List[MorphTarget] = field(default_factory=list)
    facial_rig: FacialRigDefinition = field(default_factory=lambda: FacialRigDefinition("FacialRig_01"))

    def validate_morphs(self) -> Tuple[bool, List[str]]:
        errs = []
        names = set()
        for m in self.morphs:
            if m.name in names:
                errs.append(f"DUPLICATE_MORPH_NAME: {m.name}")
            names.add(m.name)
            if m.vertex_count != self.base_vertex_count:
                errs.append(f"MORPH_VERTEX_MISMATCH: {m.name} has {m.vertex_count} vs {self.base_vertex_count}")
        return len(errs) == 0, errs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "base_vertex_count": self.base_vertex_count,
            "morph_count": len(self.morphs),
            "morphs": [m.to_dict() for m in self.morphs],
            "facial_rig": self.facial_rig.to_dict(),
        }


@dataclass
class RetargetProfile:
    profile_id: str
    source_skeleton: str
    target_skeleton: str
    bone_mapping: Dict[str, str] = field(default_factory=dict)
    translation_policy: str = "ABSOLUTE"
    rotation_policy: str = "ORIENTATION"
    scale_policy: str = "UNIFORM"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "source_skeleton": self.source_skeleton,
            "target_skeleton": self.target_skeleton,
            "bone_mapping": self.bone_mapping,
            "translation_policy": self.translation_policy,
            "rotation_policy": self.rotation_policy,
            "scale_policy": self.scale_policy,
        }


@dataclass
class PoseDefinition:
    pose_name: str
    joint_rotations: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    is_valid_limits: bool = True
    mesh_penetration_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pose_name": self.pose_name,
            "joint_rotations": self.joint_rotations,
            "is_valid_limits": self.is_valid_limits,
            "mesh_penetration_detected": self.mesh_penetration_detected,
        }


@dataclass
class RagdollBody:
    bone: str
    shape: str = "CAPSULE"  # CAPSULE, BOX, CONVEX
    mass_kg: float = 10.0
    inertia: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    collision_group: str = "RAGDOLL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone": self.bone,
            "shape": self.shape,
            "mass_kg": self.mass_kg,
            "inertia": self.inertia,
            "collision_group": self.collision_group,
        }


@dataclass
class RagdollConstraint:
    joint: str
    angular_limits: Tuple[float, float] = (-45.0, 45.0)
    linear_limits: float = 0.0
    stiffness: float = 100.0
    damping: float = 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "joint": self.joint,
            "angular_limits": self.angular_limits,
            "linear_limits": self.linear_limits,
            "stiffness": self.stiffness,
            "damping": self.damping,
        }


@dataclass
class RagdollDefinition:
    ragdoll_id: str
    bodies: List[RagdollBody] = field(default_factory=list)
    constraints: List[RagdollConstraint] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ragdoll_id": self.ragdoll_id,
            "body_count": len(self.bodies),
            "constraint_count": len(self.constraints),
            "bodies": [b.to_dict() for b in self.bodies],
            "constraints": [c.to_dict() for c in self.constraints],
        }


@dataclass
class CharacterCollisionDefinition:
    collision_id: str
    capsules_count: int = 12
    boxes_count: int = 4
    convex_count: int = 0
    ragdoll: RagdollDefinition = field(default_factory=lambda: RagdollDefinition("Ragdoll_01"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collision_id": self.collision_id,
            "capsules_count": self.capsules_count,
            "boxes_count": self.boxes_count,
            "convex_count": self.convex_count,
            "ragdoll": self.ragdoll.to_dict(),
        }


@dataclass
class CharacterLODChain:
    lod_count: int = 4
    reduction_per_lod: List[float] = field(default_factory=lambda: [1.0, 0.6, 0.3, 0.15])
    preserves_face: bool = True
    preserves_hands: bool = True
    preserves_silhouette: bool = True
    skeletal_bone_reduction: List[int] = field(default_factory=lambda: [60, 50, 35, 20])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_count": self.lod_count,
            "reduction_per_lod": self.reduction_per_lod,
            "preserves_face": self.preserves_face,
            "preserves_hands": self.preserves_hands,
            "preserves_silhouette": self.preserves_silhouette,
            "skeletal_bone_reduction": self.skeletal_bone_reduction,
        }


@dataclass
class CharacterNanitePolicy:
    enabled_for_static_accessories: bool = True
    enabled_for_skinned_mesh: bool = False
    fallback_lod_bias: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled_for_static_accessories": self.enabled_for_static_accessories,
            "enabled_for_skinned_mesh": self.enabled_for_skinned_mesh,
            "fallback_lod_bias": self.fallback_lod_bias,
        }


@dataclass
class CharacterDefinition:
    character_id: str
    species: CharacterSpecies
    archetype: CharacterArchetype
    proportions: BodyProportions = field(default_factory=BodyProportions)
    body_shape: BodyShape = BodyShape.AVERAGE
    gender_presentation: str = "NEUTRAL"
    age_category: str = "ADULT"
    anatomical_profile: str = "HUMANOID_STANDARD"
    rig_profile: str = "BIPED_STANDARD"
    material_profile: str = "ORGANIC_PBR"
    seed: int = 42

    @property
    def is_valid(self) -> bool:
        return bool(self.character_id) and self.proportions.is_valid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "species": self.species.value,
            "archetype": self.archetype.value,
            "proportions": self.proportions.to_dict(),
            "body_shape": self.body_shape.value,
            "gender_presentation": self.gender_presentation,
            "age_category": self.age_category,
            "anatomical_profile": self.anatomical_profile,
            "rig_profile": self.rig_profile,
            "material_profile": self.material_profile,
            "seed": self.seed,
        }


@dataclass
class CharacterAssetGraph:
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
        }


@dataclass
class CharacterSnapshot:
    snapshot_id: str
    character_definition_hash: str
    component_hash: str
    skeleton_hash: str
    rig_hash: str
    generator_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "character_definition_hash": self.character_definition_hash,
            "component_hash": self.component_hash,
            "skeleton_hash": self.skeleton_hash,
            "rig_hash": self.rig_hash,
            "generator_version": self.generator_version,
        }


@dataclass
class CharacterDiff:
    diff_id: str
    changed_components: List[str] = field(default_factory=list)
    skeleton_changed: bool = False
    rig_changed: bool = False
    morphs_changed: bool = False
    lod_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diff_id": self.diff_id,
            "changed_components": self.changed_components,
            "skeleton_changed": self.skeleton_changed,
            "rig_changed": self.rig_changed,
            "morphs_changed": self.morphs_changed,
            "lod_changed": self.lod_changed,
        }
