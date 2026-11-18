"""
Universal Asset Processing Products & Derived Resource Generation Models.
Complies with UAF-81.71 specification.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class ResourceType(str, Enum):
    TEXTURE = "TEXTURE"
    MESH = "MESH"
    AUDIO = "AUDIO"
    MATERIAL = "MATERIAL"
    SHADER = "SHADER"
    GENERIC = "GENERIC"


class TextureFormat(str, Enum):
    RGBA8 = "RGBA8"
    BGRA8 = "BGRA8"
    R8 = "R8"
    BC1 = "BC1"
    BC3 = "BC3"
    BC4 = "BC4"
    BC5 = "BC5"
    BC7 = "BC7"
    ASTC_4x4 = "ASTC_4x4"
    ASTC_6x6 = "ASTC_6x6"


class ColorSpace(str, Enum):
    LINEAR = "LINEAR"
    SRGB = "SRGB"
    HDR = "HDR"
    DATA = "DATA"


class ResizeFilter(str, Enum):
    NEAREST = "NEAREST"
    BILINEAR = "BILINEAR"
    BICUBIC = "BICUBIC"
    LANCZOS = "LANCZOS"


class MipFilter(str, Enum):
    BOX = "BOX"
    KAISER = "KAISER"


class IndexFormat(str, Enum):
    UINT16 = "UINT16"
    UINT32 = "UINT32"


class DecimationStrategy(str, Enum):
    QUADRIC_ERROR_METRIC = "QUADRIC_ERROR_METRIC"
    EDGE_COLLAPSE = "EDGE_COLLAPSE"
    VERTEX_CLUSTER = "VERTEX_CLUSTER"


class AudioFormat(str, Enum):
    PCM16 = "PCM16"
    PCM24 = "PCM24"
    IEEE_FLOAT = "IEEE_FLOAT"
    VORBIS = "VORBIS"
    OPUS = "OPUS"


class ShaderStage(str, Enum):
    VERTEX = "VERTEX"
    PIXEL = "PIXEL"
    COMPUTE = "COMPUTE"
    GEOMETRY = "GEOMETRY"
    HULL = "HULL"
    DOMAIN = "DOMAIN"


class ShaderTarget(str, Enum):
    SM5 = "SM5"
    SM6 = "SM6"
    VULKAN_SPIRV = "VULKAN_SPIRV"
    METAL = "METAL"


class PlatformVariant(str, Enum):
    DESKTOP = "DESKTOP"
    MOBILE = "MOBILE"
    CONSOLE = "CONSOLE"
    WEB = "WEB"
    VR = "VR"
    CUSTOM = "CUSTOM"
    DEFAULT = "DEFAULT"


class QualityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    ULTRA = "ULTRA"
    CUSTOM = "CUSTOM"


class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


def normalize_processing_path(path: str) -> str:
    """Normalizes path into canonical form: /Game/... or forward slashes, rejecting traversal and illegal characters."""
    if not path or not isinstance(path, str):
        raise ValueError("INVALID_PATH: Path must be a non-empty string.")
    
    p = path.replace("\\", "/").strip()
    # Check traversal
    parts = p.split("/")
    if ".." in parts:
        raise ValueError("PATH_TRAVERSAL_DETECTED: Path contains '..' segments.")
    
    # Check illegal characters
    illegal = set('<>:"|?*')
    # If windows drive letter like E:/, allow colon at pos 1
    clean_p = p
    if len(p) >= 2 and p[1] == ":" and p[0].isalpha():
        clean_p = p[2:]
    
    for ch in clean_p:
        if ch in illegal or ord(ch) < 32:
            raise ValueError(f"ILLEGAL_PATH_CHARACTER: Forbidden character '{ch}' in path.")
    
    # Squeeze slashes
    p = re.sub(r"/+", "/", p)
    if not p.startswith("/"):
        p = "/" + p
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


@dataclass
class ProcessingProfile:
    profile_id: str
    name: str = "DefaultProfile"
    quality: QualityLevel = QualityLevel.HIGH
    platform: PlatformVariant = PlatformVariant.DEFAULT
    settings: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def compute_hash(self) -> str:
        payload = f"{self.profile_id}:{self.quality.value}:{self.platform.value}:{self.version}:{json.dumps(self.settings, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class TextureProcessingProfile(ProcessingProfile):
    target_format: TextureFormat = TextureFormat.RGBA8
    color_space: ColorSpace = ColorSpace.SRGB
    max_width: int = 4096
    max_height: int = 4096
    generate_mipmaps: bool = True
    mip_filter: MipFilter = MipFilter.BOX
    resize_filter: ResizeFilter = ResizeFilter.BILINEAR
    is_normal_map: bool = False
    channel_packing: Dict[str, str] = field(default_factory=dict)  # {"R": "src1:R", "G": "src2:G"}
    compression_quality: int = 85

    def compute_hash(self) -> str:
        base_h = super().compute_hash()
        payload = f"{base_h}:{self.target_format.value}:{self.color_space.value}:{self.max_width}x{self.max_height}:{self.generate_mipmaps}:{self.is_normal_map}:{json.dumps(self.channel_packing, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class MeshProcessingProfile(ProcessingProfile):
    target_triangles: Optional[int] = None
    target_ratio: float = 1.0
    error_threshold: float = 0.01
    generate_normals: bool = True
    generate_tangents: bool = True
    optimize_vertex_cache: bool = True
    remove_degenerates: bool = True
    decimation_strategy: DecimationStrategy = DecimationStrategy.QUADRIC_ERROR_METRIC
    lod_levels: List[Dict[str, Any]] = field(default_factory=list)  # [{"level": 1, "ratio": 0.5, "screen_size": 0.5}]
    index_format: IndexFormat = IndexFormat.UINT32

    def compute_hash(self) -> str:
        base_h = super().compute_hash()
        payload = f"{base_h}:{self.target_ratio}:{self.generate_normals}:{self.generate_tangents}:{self.optimize_vertex_cache}:{json.dumps(self.lod_levels, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class AudioProcessingProfile(ProcessingProfile):
    target_sample_rate: int = 48000
    target_channels: int = 2
    bit_depth: int = 16
    normalize_loudness: bool = True
    target_db: float = -14.0
    codec: AudioFormat = AudioFormat.VORBIS
    preserve_loop_metadata: bool = True

    def compute_hash(self) -> str:
        base_h = super().compute_hash()
        payload = f"{base_h}:{self.target_sample_rate}:{self.target_channels}:{self.target_db}:{self.codec.value}:{self.preserve_loop_metadata}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class MaterialProcessingProfile(ProcessingProfile):
    shader_reference: str = "DefaultPBR"
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)
    texture_slots: Dict[str, str] = field(default_factory=dict)
    variant_defines: Dict[str, str] = field(default_factory=dict)

    def compute_hash(self) -> str:
        base_h = super().compute_hash()
        payload = f"{base_h}:{self.shader_reference}:{json.dumps(self.parameter_overrides, sort_keys=True)}:{json.dumps(self.texture_slots, sort_keys=True)}:{json.dumps(self.variant_defines, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ShaderProcessingProfile(ProcessingProfile):
    target_stage: ShaderStage = ShaderStage.PIXEL
    target_profile: ShaderTarget = ShaderTarget.SM6
    entry_point: str = "Main"
    defines: Dict[str, str] = field(default_factory=dict)
    include_paths: List[str] = field(default_factory=list)
    max_variants: int = 128

    def compute_hash(self) -> str:
        base_h = super().compute_hash()
        payload = f"{base_h}:{self.target_stage.value}:{self.target_profile.value}:{self.entry_point}:{json.dumps(self.defines, sort_keys=True)}:{json.dumps(sorted(self.include_paths))}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class DerivedResource:
    derived_resource_id: str
    source_asset_id: str
    resource_type: ResourceType
    processor_id: str
    processor_version: str
    profile_id: str
    fingerprint: str
    output_hash: str
    platform: PlatformVariant = PlatformVariant.DEFAULT
    quality: QualityLevel = QualityLevel.HIGH
    data: bytes = field(default_factory=bytes)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "derived_resource_id": self.derived_resource_id,
            "source_asset_id": self.source_asset_id,
            "resource_type": self.resource_type.value,
            "processor_id": self.processor_id,
            "processor_version": self.processor_version,
            "profile_id": self.profile_id,
            "fingerprint": self.fingerprint,
            "output_hash": self.output_hash,
            "platform": self.platform.value,
            "quality": self.quality.value,
            "size_bytes": len(self.data),
            "metadata": self.metadata,
        }


@dataclass
class LODLevel:
    level: int
    triangle_ratio: float
    screen_size: float
    vertex_count: int
    triangle_count: int
    output_hash: str


@dataclass
class LODChain:
    chain_id: str
    source_mesh_id: str
    levels: List[LODLevel] = field(default_factory=list)


@dataclass
class ShaderReflectionData:
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    uniforms: List[Dict[str, Any]] = field(default_factory=list)
    samplers: List[Dict[str, Any]] = field(default_factory=list)
    bindings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ShaderVariant:
    variant_id: str
    defines: Dict[str, str]
    bytecode_hash: str
    reflection: ShaderReflectionData = field(default_factory=ShaderReflectionData)


@dataclass
class OptimizationPass:
    pass_id: str
    version: str
    supported_types: List[ResourceType]
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildArtifact:
    artifact_id: str
    source_id: str
    derived_resource_id: str
    platform: PlatformVariant
    quality: QualityLevel
    output_path: str
    content_hash: str
    size_bytes: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildManifest:
    manifest_id: str
    artifacts: List[BuildArtifact] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    signature: str = ""

    def compute_signature(self) -> str:
        sorted_arts = sorted(self.artifacts, key=lambda a: a.artifact_id)
        art_hashes = [f"{a.artifact_id}:{a.content_hash}:{a.platform.value}:{a.quality.value}" for a in sorted_arts]
        payload = f"{self.manifest_id}:{self.timestamp}:{','.join(art_hashes)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.compute_signature()


@dataclass
class ProcessingTelemetry:
    processed_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    failure_count: int = 0
    cancelled_count: int = 0
    processing_time_ms: float = 0.0
    total_output_bytes: int = 0


@dataclass
class ProcessingStateSnapshot:
    snapshot_id: str
    timestamp: float
    resources: Dict[str, Dict[str, Any]]
    artifacts: Dict[str, Dict[str, Any]]
    state_hash: str = ""

    def compute_state_hash(self) -> str:
        payload = f"{self.snapshot_id}:{self.timestamp}:{json.dumps(self.resources, sort_keys=True)}:{json.dumps(self.artifacts, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_state_hash()


@dataclass
class ProcessingDiagnosticBundle:
    bundle_id: str
    timestamp: float
    snapshot: ProcessingStateSnapshot
    telemetry: ProcessingTelemetry
    signature: str = ""

    def compute_signature(self) -> str:
        payload = f"{self.bundle_id}:{self.timestamp}:{self.snapshot.state_hash}:{self.telemetry.processed_count}:{self.telemetry.cache_hits}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.compute_signature()
