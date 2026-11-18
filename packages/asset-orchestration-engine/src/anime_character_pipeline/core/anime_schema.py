"""
Anime Character Pipeline Schemas
================================
Universal data contracts for anime character geometry, bezier hair, and NPR shaders.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from .anime_types import (
    AnimeProportionsPreset,
    AnimeEyeStyle,
    AnimeHairStyle,
    NPROutlineMode,
    AnimeShadingModel
)


@dataclass
class AnimeHeadTopologySpec:
    """Specification for continuous anime head with integrated sockets."""
    head_height: float = 0.23         # meters
    head_width: float = 0.19          # meters
    chin_sharpness: float = 0.65      # 0 = round, 1 = sharp anime V
    eye_socket_depth: float = 0.015   # meters
    eye_width: float = 0.038          # meters
    eye_height: float = 0.048         # meters
    subdivision_levels: int = 2       # Catmull-Clark subdivision level


@dataclass
class AnimeBodyTopologySpec:
    """Specification for organic continuous anime body."""
    total_height: float = 1.68        # meters
    head_ratio: float = 7.2           # 1:7.2 heads
    shoulder_width: float = 0.33      # meters
    waist_width: float = 0.15         # meters
    hip_width: float = 0.24           # meters
    leg_length: float = 0.98          # meters
    arm_length: float = 0.68          # meters
    subdivision_levels: int = 2


@dataclass
class AnimeHairStrandSpec:
    """Specification for a single bezier curve hair strand with taper."""
    strand_id: str
    category: str                     # "bangs", "sideburns", "ponytail", "back"
    control_points: List[Tuple[float, float, float]] = field(default_factory=list)
    bevel_radius_root: float = 0.022  # Root thickness
    bevel_radius_tip: float = 0.002   # Sharp tip thickness
    resolution: int = 12              # Spline curve resolution


@dataclass
class NPROutlineSpec:
    """Specification for Inverted Hull Solidify outline configuration."""
    mode: NPROutlineMode = NPROutlineMode.INVERTED_HULL_SOLIDIFY
    thickness: float = 0.0035         # meters (3.5mm line width)
    offset: float = 1.0               # Extrusion along normals
    outline_color: Tuple[float, float, float, float] = (0.04, 0.02, 0.08, 1.0)
    use_backface_culling: bool = True


@dataclass
class AnimeCharacterSpec:
    """Comprehensive blueprint for generating an authentic anime character."""
    character_id: str
    character_name: str
    proportions_preset: AnimeProportionsPreset = AnimeProportionsPreset.CYBER_OPERATIVE
    eye_style: AnimeEyeStyle = AnimeEyeStyle.OVAL_LARGE
    hair_style: AnimeHairStyle = AnimeHairStyle.HIGH_PONYTAIL_LAYERED
    shading_model: AnimeShadingModel = AnimeShadingModel.TWO_TONE_BANDED
    head_spec: AnimeHeadTopologySpec = field(default_factory=AnimeHeadTopologySpec)
    body_spec: AnimeBodyTopologySpec = field(default_factory=AnimeBodyTopologySpec)
    outline_spec: NPROutlineSpec = field(default_factory=NPROutlineSpec)
    include_tactical_katana: bool = True
    include_cyber_scarf: bool = True
    include_ceramic_armor: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnimeCharacterBuildResult:
    """Result report from building or exporting an anime character."""
    character_id: str
    success: bool
    total_objects: int = 0
    total_vertices: int = 0
    total_faces: int = 0
    has_inverted_hull: bool = False
    has_bezier_hair: bool = False
    has_continuous_topology: bool = False
    blend_filepath: Optional[str] = None
    fbx_filepath: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
