"""
Universal World Models & Definitions for UAF-81.56.
Covers World, Biome, Terrain, Water, Vegetation, Architecture, Navigation, Streaming, HLOD, and Environment models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import math
from ...core.hashing.canonical_hasher import CanonicalHasher


# --- SECTION 6: WORLD DIMENSION TYPE ---
class WorldDimensionType(Enum):
    FINITE = "FINITE"
    INFINITE = "INFINITE"
    TILED = "TILED"
    STREAMED = "STREAMED"


# --- SECTION 7: WORLD BOUNDS ---
@dataclass
class WorldBounds:
    min_x: float = -50000.0
    max_x: float = 50000.0
    min_y: float = -50000.0
    max_y: float = 50000.0
    min_z: float = -10000.0
    max_z: float = 10000.0

    @property
    def size_x(self) -> float:
        return self.max_x - self.min_x

    @property
    def size_y(self) -> float:
        return self.max_y - self.min_y

    @property
    def size_z(self) -> float:
        return self.max_z - self.min_z

    def contains_point(self, x: float, y: float, z: float) -> bool:
        return (
            self.min_x <= x <= self.max_x
            and self.min_y <= y <= self.max_y
            and self.min_z <= z <= self.max_z
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
            "min_z": self.min_z,
            "max_z": self.max_z,
        }


# --- SECTION 8: WORLD COORDINATE SYSTEM ---
@dataclass
class WorldCoordinateSystem:
    up_axis: str = "Z"
    forward_axis: str = "X"
    handedness: str = "LEFT_HANDED"
    unit_scale: float = 100.0  # cm per unit (Unreal standard)
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "up_axis": self.up_axis,
            "forward_axis": self.forward_axis,
            "handedness": self.handedness,
            "unit_scale": self.unit_scale,
            "origin": list(self.origin),
        }


# --- SECTION 11, 12, 13: WORLD CELL ---
@dataclass
class WorldCell:
    cell_id: str
    cell_x: int
    cell_y: int
    cell_z: int = 0
    bounds: WorldBounds = field(default_factory=WorldBounds)
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    lod: int = 0
    assets: List[str] = field(default_factory=list)
    terrain_reference: Optional[str] = None
    streaming_state: str = "UNLOADED"
    size: float = 10000.0  # Configurable cell size

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "cell_x": self.cell_x,
            "cell_y": self.cell_y,
            "cell_z": self.cell_z,
            "bounds": self.bounds.to_dict(),
            "origin": list(self.origin),
            "lod": self.lod,
            "assets": list(self.assets),
            "terrain_reference": self.terrain_reference,
            "streaming_state": self.streaming_state,
            "size": self.size,
        }


# --- SECTION 9, 10: WORLD REGION ---
@dataclass
class WorldRegion:
    region_id: str
    name: str
    bounds: WorldBounds = field(default_factory=WorldBounds)
    biomes: List[str] = field(default_factory=list)
    terrain: Optional[str] = None
    assets: List[str] = field(default_factory=list)
    streaming_policy: str = "DISTANCE"
    navigation_policy: str = "DYNAMIC"
    parent_id: Optional[str] = None
    subregions: List[str] = field(default_factory=list)
    cells: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "name": self.name,
            "bounds": self.bounds.to_dict(),
            "biomes": list(self.biomes),
            "terrain": self.terrain,
            "assets": list(self.assets),
            "streaming_policy": self.streaming_policy,
            "navigation_policy": self.navigation_policy,
            "parent_id": self.parent_id,
            "subregions": list(self.subregions),
            "cells": list(self.cells),
        }


# --- SECTION 18: SCENE NODE TYPES ---
class SceneNodeType(Enum):
    WORLD = "WORLD"
    REGION = "REGION"
    CELL = "CELL"
    TERRAIN = "TERRAIN"
    WATER = "WATER"
    VEGETATION = "VEGETATION"
    STRUCTURE = "STRUCTURE"
    ROAD = "ROAD"
    PROP = "PROP"
    LIGHT = "LIGHT"
    VOLUME = "VOLUME"
    NAVIGATION = "NAVIGATION"
    CUSTOM = "CUSTOM"


# --- SECTION 19: TRANSFORM REPRESENTATION ---
@dataclass
class WorldTransform:
    translation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Euler Pitch, Yaw, Roll
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "translation": [round(v, 6) for v in self.translation],
            "rotation": [round(v, 6) for v in self.rotation],
            "scale": [round(v, 6) for v in self.scale],
        }


# --- SECTION 17: SCENE NODE ---
@dataclass
class SceneNode:
    node_id: str
    parent_id: Optional[str] = None
    node_type: SceneNodeType = SceneNodeType.CUSTOM
    transform: WorldTransform = field(default_factory=WorldTransform)
    bounds: WorldBounds = field(default_factory=WorldBounds)
    asset_reference: Optional[str] = None
    children: List[str] = field(default_factory=list)
    visibility: bool = True
    streaming: str = "ALWAYS_LOADED"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "node_type": self.node_type.value,
            "transform": self.transform.to_dict(),
            "bounds": self.bounds.to_dict(),
            "asset_reference": self.asset_reference,
            "children": list(self.children),
            "visibility": self.visibility,
            "streaming": self.streaming,
            "metadata": dict(self.metadata),
        }


# --- SECTION 16, 20: SCENE GRAPH ---
@dataclass
class WorldSceneGraph:
    root_id: str = "ROOT_WORLD"
    nodes: Dict[str, SceneNode] = field(default_factory=dict)

    def add_node(self, node: SceneNode) -> None:
        self.nodes[node.node_id] = node
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node.node_id not in parent.children:
                parent.children.append(node.node_id)

    def validate_hierarchy(self) -> List[str]:
        issues = []
        for node_id, node in self.nodes.items():
            if node.parent_id and node.parent_id not in self.nodes:
                issues.append(f"missing_parent:{node_id}->{node.parent_id}")

            # Cyclic check
            curr = node.parent_id
            path = {node_id}
            while curr:
                if curr in path:
                    issues.append(f"cyclic_parent:{node_id}")
                    break
                path.add(curr)
                curr = self.nodes[curr].parent_id if curr in self.nodes else None

            # Check scale validity
            if any(s <= 0.0 for s in node.transform.scale):
                issues.append(f"invalid_transform:{node_id}")

            # Check orphan (non-root without parent)
            if node_id != self.root_id and node.parent_id is None:
                issues.append(f"orphan_node:{node_id}")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_id": self.root_id,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
        }


# --- SECTION 23: BIOME TYPES ---
class BiomeType(Enum):
    DESERT = "DESERT"
    SAVANNA = "SAVANNA"
    GRASSLAND = "GRASSLAND"
    FOREST = "FOREST"
    RAINFOREST = "RAINFOREST"
    TUNDRA = "TUNDRA"
    SNOW = "SNOW"
    MOUNTAIN = "MOUNTAIN"
    SWAMP = "SWAMP"
    COAST = "COAST"
    URBAN = "URBAN"
    CUSTOM = "CUSTOM"


# --- SECTION 21, 22: BIOME DEFINITION ---
@dataclass
class BiomeDefinition:
    biome_id: str
    name: str
    biome_type: BiomeType = BiomeType.GRASSLAND
    temperature_range: Tuple[float, float] = (10.0, 25.0)  # Celsius
    humidity_range: Tuple[float, float] = (0.3, 0.8)       # 0..1
    altitude_range: Tuple[float, float] = (0.0, 1000.0)    # meters
    slope_range: Tuple[float, float] = (0.0, 45.0)         # degrees
    terrain_profile: str = "DEFAULT_TERRAIN"
    vegetation_profile: str = "DEFAULT_VEGETATION"
    rock_profile: str = "DEFAULT_ROCK"
    structure_profile: str = "DEFAULT_STRUCTURE"
    color_profile: Tuple[float, float, float] = (0.2, 0.6, 0.2)
    priority: int = 1
    weight: float = 1.0

    def evaluate_fit(self, altitude: float, slope: float, temp: float, humidity: float) -> float:
        if not (self.altitude_range[0] <= altitude <= self.altitude_range[1]):
            return 0.0
        if not (self.slope_range[0] <= slope <= self.slope_range[1]):
            return 0.0
        if not (self.temperature_range[0] <= temp <= self.temperature_range[1]):
            return 0.0
        if not (self.humidity_range[0] <= humidity <= self.humidity_range[1]):
            return 0.0
        return self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "biome_id": self.biome_id,
            "name": self.name,
            "biome_type": self.biome_type.value,
            "temperature_range": list(self.temperature_range),
            "humidity_range": list(self.humidity_range),
            "altitude_range": list(self.altitude_range),
            "slope_range": list(self.slope_range),
            "terrain_profile": self.terrain_profile,
            "vegetation_profile": self.vegetation_profile,
            "rock_profile": self.rock_profile,
            "structure_profile": self.structure_profile,
            "color_profile": list(self.color_profile),
            "priority": self.priority,
            "weight": self.weight,
        }


# --- SECTION 29: BIOME MASK CHANNELS ---
class BiomeMaskChannel(Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"
    TRANSITION = "TRANSITION"
    EXCLUSION = "EXCLUSION"


# --- SECTION 28: BIOME MASK ---
@dataclass
class BiomeMask:
    mask_id: str
    biome_id: str
    resolution_x: int = 64
    resolution_y: int = 64
    channel: BiomeMaskChannel = BiomeMaskChannel.PRIMARY
    values: List[float] = field(default_factory=list)  # Row-major 0..1 weights

    def sample(self, u: float, v: float) -> float:
        if not self.values:
            return 0.0
        x = min(int(u * self.resolution_x), self.resolution_x - 1)
        y = min(int(v * self.resolution_y), self.resolution_y - 1)
        idx = max(0, min(y * self.resolution_x + x, len(self.values) - 1))
        return self.values[idx]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mask_id": self.mask_id,
            "biome_id": self.biome_id,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "channel": self.channel.value,
            "value_count": len(self.values),
        }


# --- SECTION 32: TERRAIN REPRESENTATION ---
class TerrainRepresentation(Enum):
    HEIGHTFIELD = "HEIGHTFIELD"
    VOXEL = "VOXEL"
    MESH = "MESH"
    HYBRID = "HYBRID"


# --- SECTION 35: TERRAIN GENERATORS ---
class TerrainGeneratorType(Enum):
    FLAT = "FLAT"
    HILLS = "HILLS"
    MOUNTAIN = "MOUNTAIN"
    VALLEY = "VALLEY"
    RIDGED = "RIDGED"
    FRACTAL = "FRACTAL"
    NOISE = "NOISE"
    CUSTOM = "CUSTOM"


# --- SECTION 38: NOISE TYPES ---
class NoiseType(Enum):
    VALUE = "VALUE"
    PERLIN = "PERLIN"
    SIMPLEX = "SIMPLEX"
    WORLEY = "WORLEY"
    RIDGED = "RIDGED"
    FRACTAL = "FRACTAL"
    CUSTOM = "CUSTOM"


# --- SECTION 36, 37: NOISE DEFINITION ---
@dataclass
class NoiseDefinition:
    seed: int = 1337
    frequency: float = 0.005
    amplitude: float = 1000.0
    octaves: int = 4
    lacunarity: float = 2.0
    gain: float = 0.5
    domain_scale: float = 1.0
    noise_type: NoiseType = NoiseType.SIMPLEX

    def sample_2d(self, x: float, y: float) -> float:
        """
        Deterministic pseudo-noise function without external random state.
        """
        if self.frequency <= 0.0 or self.amplitude <= 0.0:
            return 0.0
        val = 0.0
        amp = self.amplitude
        freq = self.frequency
        for i in range(self.octaves):
            nx = (x * freq * self.domain_scale) + (self.seed * 0.1337)
            ny = (y * freq * self.domain_scale) + (self.seed * 0.7331)
            octave_val = math.sin(nx) * math.cos(ny) + math.sin(nx * 0.5 + ny * 0.5)
            val += (octave_val * 0.5) * amp
            freq *= self.lacunarity
            amp *= self.gain
        return val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "octaves": self.octaves,
            "lacunarity": self.lacunarity,
            "gain": self.gain,
            "domain_scale": self.domain_scale,
            "noise_type": self.noise_type.value,
        }


# --- SECTION 40: TERRAIN LAYERS ---
@dataclass
class TerrainLayer:
    layer_id: str
    layer_type: str = "base_height"  # base_height, detail_height, erosion, depression, ridge, flatten
    weight: float = 1.0
    values: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type,
            "weight": self.weight,
            "value_count": len(self.values),
        }


# --- SECTION 41: TERRAIN OPERATORS ---
class TerrainOperator(Enum):
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    MIN = "MIN"
    MAX = "MAX"
    LERP = "LERP"
    CLAMP = "CLAMP"
    SMOOTH = "SMOOTH"


# --- SECTION 42: TERRAIN MODIFIERS ---
class TerrainModifierType(Enum):
    TERRACE = "TERRACE"
    EROSION = "EROSION"
    SMOOTH = "SMOOTH"
    STAMP = "STAMP"
    CRATER = "CRATER"
    RIDGE = "RIDGE"
    VALLEY = "VALLEY"
    FLATTEN = "FLATTEN"
    CUSTOM = "CUSTOM"


# --- SECTION 43: TERRAIN STAMP ---
@dataclass
class TerrainStamp:
    shape: str = "CIRCLE"  # CIRCLE, BOX, CRATER
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: float = 0.0
    scale: Tuple[float, float, float] = (100.0, 100.0, 50.0)
    strength: float = 1.0
    falloff: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape": self.shape,
            "position": list(self.position),
            "rotation": self.rotation,
            "scale": list(self.scale),
            "strength": self.strength,
            "falloff": self.falloff,
        }


# --- SECTION 45: SPLAT CHANNELS ---
class TerrainSplatChannel(Enum):
    GRASS = "grass"
    DIRT = "dirt"
    ROCK = "rock"
    SAND = "sand"
    SNOW = "snow"
    MUD = "mud"
    CUSTOM = "custom"


# --- SECTION 44: TERRAIN SPLATMAP DEFINITION ---
@dataclass
class TerrainSplatDefinition:
    splat_id: str
    channels: List[str] = field(default_factory=lambda: ["grass", "dirt", "rock", "sand", "snow"])
    resolution_x: int = 64
    resolution_y: int = 64
    weights: Dict[str, List[float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "splat_id": self.splat_id,
            "channels": list(self.channels),
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "channel_counts": {k: len(v) for k, v in self.weights.items()},
        }


# --- SECTION 48, 49: SLOPE FIELD ---
@dataclass
class SlopeField:
    resolution_x: int = 64
    resolution_y: int = 64
    unit: str = "degrees"  # "degrees" or "normalized"
    values: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "unit": self.unit,
            "value_count": len(self.values),
        }


# --- SECTION 53: COLLISION MODES ---
class TerrainCollisionMode(Enum):
    HEIGHTFIELD = "HEIGHTFIELD"
    COMPLEX_MESH = "COMPLEX_MESH"
    SIMPLIFIED = "SIMPLIFIED"
    CUSTOM = "CUSTOM"


# --- SECTION 52: TERRAIN COLLISION PROFILE ---
@dataclass
class TerrainCollisionProfile:
    mode: TerrainCollisionMode = TerrainCollisionMode.HEIGHTFIELD
    enabled: bool = True
    trace_complex: bool = False
    collision_layers: List[str] = field(default_factory=lambda: ["WORLD", "TERRAIN"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "enabled": self.enabled,
            "trace_complex": self.trace_complex,
            "collision_layers": list(self.collision_layers),
        }


# --- SECTION 57: EROSION TYPES ---
class ErosionType(Enum):
    HYDRAULIC = "HYDRAULIC"
    THERMAL = "THERMAL"
    WIND = "WIND"
    CUSTOM = "CUSTOM"


# --- SECTION 56: EROSION PROFILE ---
@dataclass
class ErosionProfile:
    erosion_type: ErosionType = ErosionType.HYDRAULIC
    iterations: int = 5
    rain_amount: float = 0.01
    solubility: float = 0.02
    evaporation: float = 0.1
    sediment_capacity: float = 0.5
    seed: int = 42

    def to_dict(self) -> Dict[str, Any]:
        return {
            "erosion_type": self.erosion_type.value,
            "iterations": self.iterations,
            "rain_amount": self.rain_amount,
            "solubility": self.solubility,
            "evaporation": self.evaporation,
            "sediment_capacity": self.sediment_capacity,
            "seed": self.seed,
        }


# --- SECTION 33: TERRAIN DEFINITION ---
@dataclass
class TerrainDefinition:
    terrain_id: str
    representation: TerrainRepresentation = TerrainRepresentation.HEIGHTFIELD
    resolution_x: int = 64
    resolution_y: int = 64
    height_scale: float = 2000.0
    bounds: WorldBounds = field(default_factory=WorldBounds)
    samples: List[float] = field(default_factory=list)  # Normalized 0..1 or scaled heights
    layers: List[TerrainLayer] = field(default_factory=list)
    splatmap: Optional[TerrainSplatDefinition] = None
    slope_field: Optional[SlopeField] = None
    collision_profile: TerrainCollisionProfile = field(default_factory=TerrainCollisionProfile)
    erosion_profile: Optional[ErosionProfile] = None

    def get_height_at(self, u: float, v: float) -> float:
        if not self.samples:
            return 0.0
        x = min(int(u * (self.resolution_x - 1)), self.resolution_x - 1)
        y = min(int(v * (self.resolution_y - 1)), self.resolution_y - 1)
        idx = max(0, min(y * self.resolution_x + x, len(self.samples) - 1))
        return self.samples[idx] * self.height_scale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terrain_id": self.terrain_id,
            "representation": self.representation.value,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "height_scale": self.height_scale,
            "bounds": self.bounds.to_dict(),
            "sample_count": len(self.samples),
            "layers": [l.to_dict() for l in self.layers],
            "splatmap": self.splatmap.to_dict() if self.splatmap else None,
            "slope_field": self.slope_field.to_dict() if self.slope_field else None,
            "collision_profile": self.collision_profile.to_dict(),
        }


# --- SECTION 60: WATER TYPES ---
class WaterType(Enum):
    OCEAN = "OCEAN"
    SEA = "SEA"
    LAKE = "LAKE"
    RIVER = "RIVER"
    STREAM = "STREAM"
    POND = "POND"
    WATERFALL = "WATERFALL"
    CUSTOM = "CUSTOM"


# --- SECTION 61: WATER BODY ---
@dataclass
class WaterBody:
    water_id: str
    water_type: WaterType = WaterType.LAKE
    bounds: WorldBounds = field(default_factory=WorldBounds)
    surface_level: float = 0.0
    depth: float = 100.0
    material_reference: str = "/Game/Materials/Water/M_Water.uasset"
    flow_speed: float = 1.0
    shore_profile: str = "SANDY_SHORE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "water_id": self.water_id,
            "water_type": self.water_type.value,
            "bounds": self.bounds.to_dict(),
            "surface_level": self.surface_level,
            "depth": self.depth,
            "material_reference": self.material_reference,
            "flow_speed": self.flow_speed,
            "shore_profile": self.shore_profile,
        }


# --- SECTION 64: RIVER DATA ---
@dataclass
class RiverDefinition:
    river_id: str
    source: Tuple[float, float, float]
    destination: Tuple[float, float, float]
    control_points: List[Tuple[float, float, float]] = field(default_factory=list)
    width: float = 500.0
    depth: float = 50.0
    flow: float = 2.0
    slope: float = 0.02

    def to_dict(self) -> Dict[str, Any]:
        return {
            "river_id": self.river_id,
            "source": list(self.source),
            "destination": list(self.destination),
            "control_points": [list(p) for p in self.control_points],
            "width": self.width,
            "depth": self.depth,
            "flow": self.flow,
            "slope": self.slope,
        }


# --- SECTION 66: FLOW FIELD ---
@dataclass
class FlowField:
    flow_id: str
    resolution_x: int = 32
    resolution_y: int = 32
    vectors: List[Tuple[float, float]] = field(default_factory=list)  # (vx, vy)
    speed: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "vector_count": len(self.vectors),
            "speed": self.speed,
        }


# --- SECTION 68: SHORELINE DEFINITION ---
@dataclass
class ShorelineDefinition:
    shoreline_id: str
    water_id: str
    points: List[Tuple[float, float, float]] = field(default_factory=list)
    material: str = "/Game/Materials/Terrain/M_ShoreSand.uasset"
    width: float = 200.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shoreline_id": self.shoreline_id,
            "water_id": self.water_id,
            "point_count": len(self.points),
            "material": self.material,
            "width": self.width,
        }


# --- SECTION 59: WATER DEFINITION ---
@dataclass
class WaterDefinition:
    water_bodies: List[WaterBody] = field(default_factory=list)
    rivers: List[RiverDefinition] = field(default_factory=list)
    flow_fields: List[FlowField] = field(default_factory=list)
    shorelines: List[ShorelineDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "water_bodies": [wb.to_dict() for wb in self.water_bodies],
            "rivers": [r.to_dict() for r in self.rivers],
            "flow_fields": [ff.to_dict() for ff in self.flow_fields],
            "shorelines": [s.to_dict() for s in self.shorelines],
        }


# --- SECTION 72: VEGETATION CATEGORIES ---
class VegetationCategory(Enum):
    TREE = "TREE"
    SHRUB = "SHRUB"
    GRASS = "GRASS"
    FLOWER = "FLOWER"
    FERN = "FERN"
    MUSHROOM = "MUSHROOM"
    CACTUS = "CACTUS"
    CROP = "CROP"
    CUSTOM = "CUSTOM"


# --- SECTION 73: VEGETATION SPECIES ---
@dataclass
class VegetationSpecies:
    species_id: str
    category: VegetationCategory = VegetationCategory.TREE
    asset_variants: List[str] = field(default_factory=list)
    scale_range: Tuple[float, float] = (0.8, 1.3)
    rotation_range: Tuple[float, float] = (0.0, 360.0)
    density: float = 0.05
    biome_rules: List[str] = field(default_factory=list)
    slope_rules: Tuple[float, float] = (0.0, 35.0)
    height_rules: Tuple[float, float] = (0.0, 2000.0)
    water_rules: Tuple[float, float] = (50.0, 5000.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "species_id": self.species_id,
            "category": self.category.value,
            "asset_variants": list(self.asset_variants),
            "scale_range": list(self.scale_range),
            "rotation_range": list(self.rotation_range),
            "density": self.density,
            "biome_rules": list(self.biome_rules),
            "slope_rules": list(self.slope_rules),
            "height_rules": list(self.height_rules),
            "water_rules": list(self.water_rules),
        }


# --- SECTION 76, 77, 78, 79: SCATTER DISTRIBUTION TYPE ---
class ScatterDistributionType(Enum):
    POISSON = "POISSON"
    GRID = "GRID"
    JITTERED_RANDOM = "JITTERED_RANDOM"
    CLUSTER = "CLUSTER"


# --- SECTION 74, 75: SCATTER PROFILE ---
@dataclass
class VegetationScatterProfile:
    profile_id: str = "DEFAULT_VEGETATION_SCATTER"
    density: float = 0.1
    seed: int = 101
    min_distance: float = 200.0
    scale_min: float = 0.8
    scale_max: float = 1.2
    rotation_mode: str = "RANDOM_YAW"
    slope_min: float = 0.0
    slope_max: float = 40.0
    height_min: float = -1000.0
    height_max: float = 5000.0
    distribution_type: ScatterDistributionType = ScatterDistributionType.POISSON

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "density": self.density,
            "seed": self.seed,
            "min_distance": self.min_distance,
            "scale_min": self.scale_min,
            "scale_max": self.scale_max,
            "rotation_mode": self.rotation_mode,
            "slope_min": self.slope_min,
            "slope_max": self.slope_max,
            "height_min": self.height_min,
            "height_max": self.height_max,
            "distribution_type": self.distribution_type.value,
        }


# --- SECTION 84: FOLIAGE LAYERS ---
class FoliageLayer(Enum):
    GROUND_COVER = "GROUND_COVER"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    CANOPY = "CANOPY"
    UNDERSTORY = "UNDERSTORY"


# --- SECTION 86: FOLIAGE LOD ---
class FoliageLODType(Enum):
    INSTANCE = "INSTANCE"
    BILLBOARD = "BILLBOARD"
    IMPOSTOR = "IMPOSTOR"
    DISABLED = "DISABLED"


# --- SECTION 83: FOLIAGE DEFINITION ---
@dataclass
class FoliageDefinition:
    foliage_id: str
    layer: FoliageLayer = FoliageLayer.GROUND_COVER
    density: float = 0.2
    lod_type: FoliageLODType = FoliageLODType.INSTANCE
    cull_distance: float = 15000.0
    asset_reference: str = "/Game/Vegetation/Foliage_Grass.uasset"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "foliage_id": self.foliage_id,
            "layer": self.layer.value,
            "density": self.density,
            "lod_type": self.lod_type.value,
            "cull_distance": self.cull_distance,
            "asset_reference": self.asset_reference,
        }


# --- SECTION 71: VEGETATION DEFINITION ---
@dataclass
class VegetationDefinition:
    species: List[VegetationSpecies] = field(default_factory=list)
    scatter_profiles: List[VegetationScatterProfile] = field(default_factory=list)
    foliage: List[FoliageDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "species": [s.to_dict() for s in self.species],
            "scatter_profiles": [sp.to_dict() for sp in self.scatter_profiles],
            "foliage": [f.to_dict() for f in self.foliage],
        }


# --- SECTION 88: ROCK TYPES ---
class RockType(Enum):
    BOULDER = "BOULDER"
    CLIFF = "CLIFF"
    PEBBLE = "PEBBLE"
    OUTCROP = "OUTCROP"
    COLUMN = "COLUMN"
    CUSTOM = "CUSTOM"


# --- SECTION 90: ROCK ORIENTATION ---
class RockOrientation(Enum):
    RANDOM = "RANDOM"
    SURFACE_ALIGNED = "SURFACE_ALIGNED"
    GRAVITY_ALIGNED = "GRAVITY_ALIGNED"
    CUSTOM = "CUSTOM"


# --- SECTION 87: ROCK DEFINITION ---
@dataclass
class RockDefinition:
    rock_id: str
    rock_type: RockType = RockType.BOULDER
    asset_variants: List[str] = field(default_factory=list)
    orientation: RockOrientation = RockOrientation.SURFACE_ALIGNED
    scale_range: Tuple[float, float] = (0.5, 3.0)
    density: float = 0.02

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rock_id": self.rock_id,
            "rock_type": self.rock_type.value,
            "asset_variants": list(self.asset_variants),
            "orientation": self.orientation.value,
            "scale_range": list(self.scale_range),
            "density": self.density,
        }


# --- SECTION 93: PROP CATEGORIES ---
class PropCategory(Enum):
    FENCE = "FENCE"
    SIGN = "SIGN"
    LAMP = "LAMP"
    BENCH = "BENCH"
    CONTAINER = "CONTAINER"
    DECORATION = "DECORATION"
    DEBRIS = "DEBRIS"
    VEHICLE_PROXY = "VEHICLE_PROXY"
    CUSTOM = "CUSTOM"


# --- SECTION 94: PROP PLACEMENT ---
class PropPlacementMode(Enum):
    SURFACE = "SURFACE"
    ROAD = "ROAD"
    BUILDING = "BUILDING"
    WATER = "WATER"
    CUSTOM = "CUSTOM"


# --- SECTION 96: EXCLUSION VOLUME TYPE ---
class ExclusionVolumeType(Enum):
    CIRCLE = "CIRCLE"
    BOX = "BOX"
    CAPSULE = "CAPSULE"
    POLYGON = "POLYGON"
    HEIGHTFIELD = "HEIGHTFIELD"
    CUSTOM = "CUSTOM"


# --- SECTION 95: EXCLUSION VOLUME ---
@dataclass
class ExclusionVolume:
    volume_id: str
    volume_type: ExclusionVolumeType = ExclusionVolumeType.CIRCLE
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    radius: float = 500.0
    bounds: Optional[WorldBounds] = None

    def contains(self, x: float, y: float, z: float) -> bool:
        if self.volume_type == ExclusionVolumeType.CIRCLE:
            dist_sq = (x - self.center[0]) ** 2 + (y - self.center[1]) ** 2
            return dist_sq <= (self.radius ** 2)
        elif self.bounds:
            return self.bounds.contains_point(x, y, z)
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "volume_id": self.volume_id,
            "volume_type": self.volume_type.value,
            "center": list(self.center),
            "radius": self.radius,
            "bounds": self.bounds.to_dict() if self.bounds else None,
        }


# --- SECTION 92: PROP DEFINITION ---
@dataclass
class PropDefinition:
    prop_id: str
    category: PropCategory = PropCategory.CONTAINER
    asset_variants: List[str] = field(default_factory=list)
    placement_mode: PropPlacementMode = PropPlacementMode.SURFACE
    scale_range: Tuple[float, float] = (0.9, 1.1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prop_id": self.prop_id,
            "category": self.category.value,
            "asset_variants": list(self.asset_variants),
            "placement_mode": self.placement_mode.value,
            "scale_range": list(self.scale_range),
        }


# --- SECTION 99: SCATTER CONSTRAINT TYPE ---
class ScatterConstraintType(Enum):
    MIN_DISTANCE = "MIN_DISTANCE"
    MAX_DISTANCE = "MAX_DISTANCE"
    SLOPE = "SLOPE"
    HEIGHT = "HEIGHT"
    BIOME = "BIOME"
    WATER_DISTANCE = "WATER_DISTANCE"
    ROAD_DISTANCE = "ROAD_DISTANCE"
    EXCLUSION = "EXCLUSION"
    CUSTOM = "CUSTOM"


# --- SECTION 100, 101: SCATTER INSTANCE ---
@dataclass
class ScatterInstance:
    instance_id: str
    asset_id: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    variant: int = 0
    cell_id: str = "CELL_0_0"
    seed_path: str = "0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "asset_id": self.asset_id,
            "position": [round(p, 4) for p in self.position],
            "rotation": [round(r, 4) for r in self.rotation],
            "scale": [round(s, 4) for s in self.scale],
            "variant": self.variant,
            "cell_id": self.cell_id,
            "seed_path": self.seed_path,
        }


# --- SECTION 104: BUILDING TYPES ---
class BuildingType(Enum):
    HOUSE = "HOUSE"
    APARTMENT = "APARTMENT"
    OFFICE = "OFFICE"
    WAREHOUSE = "WAREHOUSE"
    SHOP = "SHOP"
    INDUSTRIAL = "INDUSTRIAL"
    RUIN = "RUIN"
    CUSTOM = "CUSTOM"


# --- SECTION 103, 105: BUILDING DEFINITION ---
@dataclass
class BuildingDefinition:
    building_id: str
    building_type: BuildingType = BuildingType.HOUSE
    footprint: List[Tuple[float, float]] = field(default_factory=list)  # 2D Polygon
    floors: int = 2
    height: float = 600.0  # cm
    roof_type: str = "PITCHED"  # FLAT, PITCHED, DOME
    wall_material: str = "/Game/Materials/Architecture/M_Wall.uasset"
    roof_material: str = "/Game/Materials/Architecture/M_Roof.uasset"
    window_profile: str = "STANDARD_WINDOW"
    door_profile: str = "STANDARD_DOOR"
    variation: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_id": self.building_id,
            "building_type": self.building_type.value,
            "footprint": [list(p) for p in self.footprint],
            "floors": self.floors,
            "height": self.height,
            "roof_type": self.roof_type,
            "wall_material": self.wall_material,
            "roof_material": self.roof_material,
            "window_profile": self.window_profile,
            "door_profile": self.door_profile,
            "variation": self.variation,
        }


# --- SECTION 110: ROAD TYPES ---
class RoadType(Enum):
    HIGHWAY = "HIGHWAY"
    ROAD = "ROAD"
    STREET = "STREET"
    LANE = "LANE"
    PATH = "PATH"
    TRAIL = "TRAIL"
    BRIDGE = "BRIDGE"
    CUSTOM = "CUSTOM"


# --- SECTION 114: ROAD CUT / FILL ---
class RoadCutFillMode(Enum):
    CUT = "CUT"
    FILL = "FILL"
    BLEND = "BLEND"


# --- SECTION 109, 111: ROAD DEFINITION ---
@dataclass
class RoadDefinition:
    road_id: str
    road_type: RoadType = RoadType.ROAD
    control_points: List[Tuple[float, float, float]] = field(default_factory=list)
    width: float = 600.0
    banking: float = 0.0
    slope_limit: float = 15.0  # degrees
    surface_profile: str = "/Game/Materials/Road/M_Asphalt.uasset"
    cut_fill_mode: RoadCutFillMode = RoadCutFillMode.BLEND

    def to_dict(self) -> Dict[str, Any]:
        return {
            "road_id": self.road_id,
            "road_type": self.road_type.value,
            "control_points": [list(p) for p in self.control_points],
            "width": self.width,
            "banking": self.banking,
            "slope_limit": self.slope_limit,
            "surface_profile": self.surface_profile,
            "cut_fill_mode": self.cut_fill_mode.value,
        }


# --- SECTION 116: BRIDGE DEFINITION ---
@dataclass
class BridgeDefinition:
    bridge_id: str
    start: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    end: Tuple[float, float, float] = (1000.0, 0.0, 0.0)
    span: float = 1000.0
    height: float = 500.0
    width: float = 800.0
    support_profile: str = "CONCRETE_PILLARS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "start": list(self.start),
            "end": list(self.end),
            "span": self.span,
            "height": self.height,
            "width": self.width,
            "support_profile": self.support_profile,
        }


# --- SECTION 120: PATH TYPES ---
class PathType(Enum):
    ROAD = "ROAD"
    FOOTPATH = "FOOTPATH"
    TRAIL = "TRAIL"
    SERVICE = "SERVICE"
    NAVIGATION = "NAVIGATION"
    CUSTOM = "CUSTOM"


# --- SECTION 119: PATH NODE ---
@dataclass
class PathNode:
    node_id: str
    position: Tuple[float, float, float]
    path_type: PathType = PathType.ROAD
    connections: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "position": list(self.position),
            "path_type": self.path_type.value,
            "connections": list(self.connections),
        }


# --- SECTION 118: PATH NETWORK ---
@dataclass
class PathNetwork:
    nodes: Dict[str, PathNode] = field(default_factory=dict)

    def add_node(self, node: PathNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, n1: str, n2: str) -> None:
        if n1 in self.nodes and n2 not in self.nodes[n1].connections:
            self.nodes[n1].connections.append(n2)
        if n2 in self.nodes and n1 not in self.nodes[n2].connections:
            self.nodes[n2].connections.append(n1)

    def to_dict(self) -> Dict[str, Any]:
        return {"nodes": {nid: n.to_dict() for nid, n in self.nodes.items()}}


# --- SECTION 123: NAVIGATION SOURCES ---
class NavigationSource(Enum):
    TERRAIN = "TERRAIN"
    ROAD = "ROAD"
    BUILDING = "BUILDING"
    WATER = "WATER"
    PROP = "PROP"
    CUSTOM = "CUSTOM"


# --- SECTION 124: NAVIGATION FLAGS ---
class NavigationFlag(Enum):
    WALKABLE = "WALKABLE"
    BLOCKED = "BLOCKED"
    WATER = "WATER"
    CLIMBABLE = "CLIMBABLE"
    JUMPABLE = "JUMPABLE"
    DANGEROUS = "DANGEROUS"
    CUSTOM = "CUSTOM"


# --- SECTION 122: NAVIGATION DEFINITION ---
@dataclass
class NavigationDefinition:
    nav_id: str
    regions: List[str] = field(default_factory=lambda: ["MAIN_NAV_REGION"])
    sources: List[NavigationSource] = field(default_factory=lambda: [NavigationSource.TERRAIN, NavigationSource.ROAD])
    flags: List[NavigationFlag] = field(default_factory=lambda: [NavigationFlag.WALKABLE, NavigationFlag.BLOCKED])
    connectivity: bool = True
    nav_polygons: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nav_id": self.nav_id,
            "regions": list(self.regions),
            "sources": [s.value for s in self.sources],
            "flags": [f.value for f in self.flags],
            "connectivity": self.connectivity,
            "polygon_count": len(self.nav_polygons),
        }


# --- SECTION 129: COLLISION LAYERS ---
class CollisionLayer(Enum):
    WORLD = "WORLD"
    TERRAIN = "TERRAIN"
    VEGETATION = "VEGETATION"
    STRUCTURE = "STRUCTURE"
    ROAD = "ROAD"
    WATER = "WATER"
    PROP = "PROP"
    NAVIGATION = "NAVIGATION"
    CUSTOM = "CUSTOM"


# --- SECTION 130: COLLISION COMPLEXITY ---
class CollisionComplexity(Enum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"
    HYBRID = "HYBRID"


# --- SECTION 128: WORLD COLLISION PROFILE ---
@dataclass
class WorldCollisionProfile:
    profile_id: str = "DEFAULT_WORLD_COLLISION"
    layers: List[CollisionLayer] = field(
        default_factory=lambda: [
            CollisionLayer.WORLD,
            CollisionLayer.TERRAIN,
            CollisionLayer.STRUCTURE,
            CollisionLayer.VEGETATION,
            CollisionLayer.PROP,
        ]
    )
    complexity: CollisionComplexity = CollisionComplexity.HYBRID
    block_all: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "layers": [l.value for l in self.layers],
            "complexity": self.complexity.value,
            "block_all": self.block_all,
        }


# --- SECTION 133: STREAMING STATES ---
class StreamingState(Enum):
    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    LOADED = "LOADED"
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"
    UNLOADING = "UNLOADING"


# --- SECTION 135: LEVEL STREAMING ---
class LevelStreamingMode(Enum):
    ON_DEMAND = "ON_DEMAND"
    DISTANCE = "DISTANCE"
    PRIORITY = "PRIORITY"
    MANUAL = "MANUAL"


# --- SECTION 132: WORLD PARTITION CELL ---
@dataclass
class WorldPartitionCell:
    cell_id: str
    bounds: WorldBounds
    load_distance: float = 25000.0
    unload_distance: float = 30000.0
    priority: int = 1
    runtime_state: StreamingState = StreamingState.UNLOADED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "bounds": self.bounds.to_dict(),
            "load_distance": self.load_distance,
            "unload_distance": self.unload_distance,
            "priority": self.priority,
            "runtime_state": self.runtime_state.value,
        }


# --- SECTION 131: WORLD PARTITION PROFILE ---
@dataclass
class WorldPartitionProfile:
    grid_size: float = 10000.0
    streaming_mode: LevelStreamingMode = LevelStreamingMode.DISTANCE
    cells: List[WorldPartitionCell] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_size": self.grid_size,
            "streaming_mode": self.streaming_mode.value,
            "cell_count": len(self.cells),
            "cells": [c.to_dict() for c in self.cells],
        }


# --- SECTION 137: HLOD LEVELS ---
class HLODLevel(Enum):
    HLOD0 = "HLOD0"
    HLOD1 = "HLOD1"
    HLOD2 = "HLOD2"
    HLOD3 = "HLOD3"


# --- SECTION 138: HLOD GROUPING ---
class HLODGroupingMode(Enum):
    CELL = "cell"
    MATERIAL = "material"
    ASSET_TYPE = "asset_type"
    DISTANCE = "distance"
    REGION = "region"


# --- SECTION 136: WORLD HLOD PROFILE ---
@dataclass
class WorldHLODProfile:
    profile_id: str = "DEFAULT_HLOD"
    levels: List[HLODLevel] = field(default_factory=lambda: [HLODLevel.HLOD0, HLODLevel.HLOD1, HLODLevel.HLOD2])
    grouping_mode: HLODGroupingMode = HLODGroupingMode.CELL
    reduction_per_level: float = 0.5  # 50% triangle reduction
    max_draw_distance: float = 50000.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "levels": [lvl.value for lvl in self.levels],
            "grouping_mode": self.grouping_mode.value,
            "reduction_per_level": self.reduction_per_level,
            "max_draw_distance": self.max_draw_distance,
        }


# --- SECTION 140: IMPOSTOR DEFINITION ---
@dataclass
class ImpostorDefinition:
    impostor_id: str
    source_asset_id: str
    resolution: int = 512
    directions: int = 16
    billboard_count: int = 8
    distance: float = 30000.0
    alpha_threshold: float = 0.33

    def to_dict(self) -> Dict[str, Any]:
        return {
            "impostor_id": self.impostor_id,
            "source_asset_id": self.source_asset_id,
            "resolution": self.resolution,
            "directions": self.directions,
            "billboard_count": self.billboard_count,
            "distance": self.distance,
            "alpha_threshold": self.alpha_threshold,
        }


# --- SECTION 142: LIGHTING PROFILE ---
@dataclass
class LightingProfile:
    sun_intensity: float = 100000.0  # Lux
    sun_color: Tuple[float, float, float] = (1.0, 0.95, 0.85)
    moon_intensity: float = 0.25
    moon_color: Tuple[float, float, float] = (0.5, 0.6, 0.9)
    sky_light_intensity: float = 1.0
    ambient_color: Tuple[float, float, float] = (0.2, 0.2, 0.25)
    volumetric_fog: bool = True
    local_lights_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sun_intensity": self.sun_intensity,
            "sun_color": list(self.sun_color),
            "moon_intensity": self.moon_intensity,
            "moon_color": list(self.moon_color),
            "sky_light_intensity": self.sky_light_intensity,
            "ambient_color": list(self.ambient_color),
            "volumetric_fog": self.volumetric_fog,
            "local_lights_enabled": self.local_lights_enabled,
        }


# --- SECTION 143, 144: TIME OF DAY PROFILE ---
@dataclass
class TimeOfDayProfile:
    time: float = 12.0  # 0.0 - 24.0 hours
    sun_direction: Tuple[float, float, float] = (0.0, 0.7071, -0.7071)
    sun_intensity: float = 1.0
    sky_color: Tuple[float, float, float] = (0.4, 0.6, 1.0)
    ambient_intensity: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "sun_direction": list(self.sun_direction),
            "sun_intensity": self.sun_intensity,
            "sky_color": list(self.sky_color),
            "ambient_intensity": self.ambient_intensity,
        }


# --- SECTION 146: WEATHER TYPES ---
class WeatherType(Enum):
    CLEAR = "CLEAR"
    CLOUDY = "CLOUDY"
    RAIN = "RAIN"
    STORM = "STORM"
    SNOW = "SNOW"
    FOG = "FOG"
    DUST = "DUST"
    CUSTOM = "CUSTOM"


# --- SECTION 145: WEATHER PROFILE ---
@dataclass
class WeatherProfile:
    weather_type: WeatherType = WeatherType.CLEAR
    precipitation: float = 0.0  # 0..1
    wind_speed: float = 5.0     # m/s
    wind_direction: Tuple[float, float] = (1.0, 0.0)
    cloud_coverage: float = 0.2 # 0..1
    fog_density: float = 0.01

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weather_type": self.weather_type.value,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
            "wind_direction": list(self.wind_direction),
            "cloud_coverage": self.cloud_coverage,
            "fog_density": self.fog_density,
        }


# --- SECTION 148: ENVIRONMENT PROFILE ---
@dataclass
class EnvironmentProfile:
    lighting: LightingProfile = field(default_factory=LightingProfile)
    time_of_day: TimeOfDayProfile = field(default_factory=TimeOfDayProfile)
    weather: WeatherProfile = field(default_factory=WeatherProfile)
    ambient_soundtrack: str = "/Game/Audio/Ambience/AMB_Nature.uasset"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lighting": self.lighting.to_dict(),
            "time_of_day": self.time_of_day.to_dict(),
            "weather": self.weather.to_dict(),
            "ambient_soundtrack": self.ambient_soundtrack,
        }


# --- SECTION 150: AUDIO ZONE TYPE ---
class WorldAudioZoneType(Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    POLYGON = "POLYGON"
    CUSTOM = "CUSTOM"


# --- SECTION 149: WORLD AUDIO PROFILE ---
@dataclass
class WorldAudioProfile:
    audio_id: str = "DEFAULT_AUDIO"
    ambient_zones: List[Dict[str, Any]] = field(default_factory=list)
    reverb_preset: str = "OUTDOOR_VALLEY"
    sound_occlusion: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio_id": self.audio_id,
            "ambient_zones": list(self.ambient_zones),
            "reverb_preset": self.reverb_preset,
            "sound_occlusion": self.sound_occlusion,
        }


# --- SECTION 151: WORLD VFX PROFILE ---
@dataclass
class WorldVFXProfile:
    vfx_id: str = "DEFAULT_VFX"
    effects: List[str] = field(default_factory=lambda: ["dust", "leaves", "rain", "mist"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vfx_id": self.vfx_id,
            "effects": list(self.effects),
        }


# --- SECTION 153: WORLD ANCHOR ---
class WorldAnchorType(Enum):
    SPAWN = "spawn"
    LANDMARK = "landmark"
    QUEST = "quest"
    CAMERA = "camera"
    NAVIGATION = "navigation"
    STREAMING = "streaming"
    CUSTOM = "custom"


@dataclass
class WorldAnchor:
    anchor_id: str
    anchor_type: WorldAnchorType = WorldAnchorType.SPAWN
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "anchor_type": self.anchor_type.value,
            "position": list(self.position),
            "rotation": list(self.rotation),
            "tags": list(self.tags),
        }


# --- SECTION 154, 155: SPAWN PROFILE ---
@dataclass
class SpawnProfile:
    spawn_id: str = "SPAWN_HERO_01"
    biome_rules: List[str] = field(default_factory=lambda: ["GRASSLAND", "FOREST"])
    height_range: Tuple[float, float] = (0.0, 1500.0)
    slope_range: Tuple[float, float] = (0.0, 20.0)
    distance_rules: float = 1000.0
    seed: int = 777

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spawn_id": self.spawn_id,
            "biome_rules": list(self.biome_rules),
            "height_range": list(self.height_range),
            "slope_range": list(self.slope_range),
            "distance_rules": self.distance_rules,
            "seed": self.seed,
        }


# --- SECTION 157: LANDMARK TYPES ---
class LandmarkType(Enum):
    MOUNTAIN = "MOUNTAIN"
    TOWER = "TOWER"
    BUILDING = "BUILDING"
    MONUMENT = "MONUMENT"
    TREE = "TREE"
    WATER_BODY = "WATER_BODY"
    ROAD_JUNCTION = "ROAD_JUNCTION"
    CUSTOM = "CUSTOM"


# --- SECTION 156: LANDMARK DEFINITION ---
@dataclass
class LandmarkDefinition:
    landmark_id: str
    name: str
    landmark_type: LandmarkType = LandmarkType.MOUNTAIN
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounds: WorldBounds = field(default_factory=WorldBounds)
    visible_distance: float = 50000.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "landmark_id": self.landmark_id,
            "name": self.name,
            "landmark_type": self.landmark_type.value,
            "position": list(self.position),
            "bounds": self.bounds.to_dict(),
            "visible_distance": self.visible_distance,
        }


# --- SECTION 160: WORLD QUERY TYPES ---
class WorldQueryType(Enum):
    HEIGHT_AT = "HEIGHT_AT"
    SLOPE_AT = "SLOPE_AT"
    BIOME_AT = "BIOME_AT"
    WATER_AT = "WATER_AT"
    ASSET_AT = "ASSET_AT"
    NAVIGATION_AT = "NAVIGATION_AT"
    CELL_AT = "CELL_AT"
    NEAREST_ASSET = "NEAREST_ASSET"
    NEAREST_ROAD = "NEAREST_ROAD"


# --- SECTION 159: WORLD QUERY ---
@dataclass
class WorldQuery:
    query_type: WorldQueryType
    position: Tuple[float, float, float]
    radius: float = 1000.0
    filter_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_type": self.query_type.value,
            "position": list(self.position),
            "radius": self.radius,
            "filter_tags": list(self.filter_tags),
        }


# --- SECTION 162: WORLD SNAPSHOT ---
@dataclass
class WorldSnapshot:
    world_hash: str
    cells: List[str]
    scene_graph_hash: str
    terrain_hash: str
    vegetation_hash: str
    water_hash: str
    structure_hash: str
    navigation_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_hash": self.world_hash,
            "cells": list(self.cells),
            "scene_graph_hash": self.scene_graph_hash,
            "terrain_hash": self.terrain_hash,
            "vegetation_hash": self.vegetation_hash,
            "water_hash": self.water_hash,
            "structure_hash": self.structure_hash,
            "navigation_hash": self.navigation_hash,
        }


# --- SECTION 164: WORLD DIFF CATEGORIES ---
class WorldDiffCategory(Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    MOVED = "MOVED"
    REPLACED = "REPLACED"
    LOD_CHANGED = "LOD_CHANGED"
    STREAMING_CHANGED = "STREAMING_CHANGED"


# --- SECTION 163: WORLD DIFF ---
@dataclass
class WorldDiff:
    changes: List[Dict[str, Any]] = field(default_factory=list)

    def add_change(self, category: WorldDiffCategory, element_id: str, details: Dict[str, Any]) -> None:
        self.changes.append({
            "category": category.value,
            "element_id": element_id,
            "details": details,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {"changes": list(self.changes)}


# --- SECTION 170: WORLD CACHE KEY ---
@dataclass(frozen=True)
class WorldCacheKey:
    world_hash: str
    cell_id: str
    generator_version: str = "1.0.0"
    profile_hash: str = "DEFAULT_PROFILE"
    asset_library_hash: str = "DEFAULT_LIB"


# --- SECTION 169: WORLD CACHE ---
class WorldCache:
    def __init__(self):
        self._cache: Dict[WorldCacheKey, Any] = {}
        self._cell_dependencies: Dict[str, List[WorldCacheKey]] = {}

    def get(self, key: WorldCacheKey) -> Optional[Any]:
        return self._cache.get(key)

    def put(self, key: WorldCacheKey, value: Any) -> None:
        self._cache[key] = value
        if key.cell_id not in self._cell_dependencies:
            self._cell_dependencies[key.cell_id] = []
        self._cell_dependencies[key.cell_id].append(key)

    def invalidate_cell(self, cell_id: str) -> int:
        keys = self._cell_dependencies.pop(cell_id, [])
        for k in keys:
            self._cache.pop(k, None)
        return len(keys)

    def clear(self) -> None:
        self._cache.clear()
        self._cell_dependencies.clear()

    def size(self) -> int:
        return len(self._cache)


# --- SECTION 172-175: BUDGETS ---
@dataclass
class MemoryBudget:
    max_instances: int = 100000
    max_cells: int = 1024
    max_memory_mb: float = 4096.0
    max_texture_memory_mb: float = 2048.0
    max_collision_memory_mb: float = 512.0
    max_navigation_memory_mb: float = 256.0


@dataclass
class InstanceBudget:
    vegetation: int = 80000
    rocks: int = 10000
    props: int = 5000
    buildings: int = 1000
    roads: int = 500
    water: int = 100
    custom: int = 1000


@dataclass
class TriangleBudget:
    terrain: int = 5000000
    structures: int = 2000000
    vegetation: int = 3000000
    rocks: int = 1000000
    props: int = 500000
    water: int = 200000
    hlod: int = 1000000


@dataclass
class StreamingBudget:
    load_cost_ms: float = 5.0
    unload_cost_ms: float = 2.0
    visible_memory_mb: float = 1024.0
    resident_memory_mb: float = 2048.0


# --- SECTION 176, 177: WORLD PERFORMANCE REPORT ---
@dataclass
class WorldPerformanceReport:
    generation_time_ms: float = 0.0
    terrain_time_ms: float = 0.0
    scatter_time_ms: float = 0.0
    structure_time_ms: float = 0.0
    water_time_ms: float = 0.0
    navigation_time_ms: float = 0.0
    hlod_time_ms: float = 0.0
    export_time_ms: float = 0.0
    validation_time_ms: float = 0.0
    total_triangles: int = 0
    total_instances: int = 0
    memory_usage_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_time_ms": self.generation_time_ms,
            "terrain_time_ms": self.terrain_time_ms,
            "scatter_time_ms": self.scatter_time_ms,
            "structure_time_ms": self.structure_time_ms,
            "water_time_ms": self.water_time_ms,
            "navigation_time_ms": self.navigation_time_ms,
            "hlod_time_ms": self.hlod_time_ms,
            "export_time_ms": self.export_time_ms,
            "validation_time_ms": self.validation_time_ms,
            "total_triangles": self.total_triangles,
            "total_instances": self.total_instances,
            "memory_usage_mb": self.memory_usage_mb,
        }


# --- SECTION 178: WORLD DIAGNOSTIC REPORT ---
@dataclass
class WorldDiagnosticReport:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    budgets_ok: bool = True
    connectivity_ok: bool = True
    streaming_ok: bool = True
    lod_ok: bool = True
    navigation_ok: bool = True
    collision_ok: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "statistics": dict(self.statistics),
            "budgets_ok": self.budgets_ok,
            "connectivity_ok": self.connectivity_ok,
            "streaming_ok": self.streaming_ok,
            "lod_ok": self.lod_ok,
            "navigation_ok": self.navigation_ok,
            "collision_ok": self.collision_ok,
        }


# --- SECTION 180: EXPORT TARGETS ---
class ExportTarget(Enum):
    ENGINE_RUNTIME = "ENGINE_RUNTIME"
    EDITOR = "EDITOR"
    OFFLINE = "OFFLINE"
    DATASET = "DATASET"
    CUSTOM = "CUSTOM"


# --- SECTION 3, 81: TOP-LEVEL WORLD DEFINITION ---
@dataclass
class WorldDefinition:
    world_id: str
    name: str
    seed: int = 12345
    dimensions: WorldDimensionType = WorldDimensionType.FINITE
    bounds: WorldBounds = field(default_factory=WorldBounds)
    coordinate_system: WorldCoordinateSystem = field(default_factory=WorldCoordinateSystem)
    regions: List[WorldRegion] = field(default_factory=list)
    cells: List[WorldCell] = field(default_factory=list)
    biomes: List[BiomeDefinition] = field(default_factory=list)
    terrain: Optional[TerrainDefinition] = None
    water: Optional[WaterDefinition] = None
    roads: List[RoadDefinition] = field(default_factory=list)
    bridges: List[BridgeDefinition] = field(default_factory=list)
    path_network: Optional[PathNetwork] = None
    structures: List[BuildingDefinition] = field(default_factory=list)
    vegetation: Optional[VegetationDefinition] = None
    rocks: List[RockDefinition] = field(default_factory=list)
    props: List[PropDefinition] = field(default_factory=list)
    scatter_instances: List[ScatterInstance] = field(default_factory=list)
    exclusion_volumes: List[ExclusionVolume] = field(default_factory=list)
    navigation: Optional[NavigationDefinition] = None
    collision: WorldCollisionProfile = field(default_factory=WorldCollisionProfile)
    partition: Optional[WorldPartitionProfile] = None
    hlod: Optional[WorldHLODProfile] = None
    impostors: List[ImpostorDefinition] = field(default_factory=list)
    lighting: LightingProfile = field(default_factory=LightingProfile)
    environment: EnvironmentProfile = field(default_factory=EnvironmentProfile)
    anchors: List[WorldAnchor] = field(default_factory=list)
    spawn: SpawnProfile = field(default_factory=SpawnProfile)
    landmarks: List[LandmarkDefinition] = field(default_factory=list)
    generator_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def world_hash(self) -> str:
        payload = {
            "world_id": self.world_id,
            "seed": self.seed,
            "dimensions": self.dimensions.value,
            "bounds": self.bounds.to_dict(),
            "region_count": len(self.regions),
            "cell_count": len(self.cells),
            "biome_count": len(self.biomes),
            "structure_count": len(self.structures),
            "road_count": len(self.roads),
            "generator_version": self.generator_version,
        }
        return CanonicalHasher.compute_hash(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "seed": self.seed,
            "dimensions": self.dimensions.value,
            "bounds": self.bounds.to_dict(),
            "coordinate_system": self.coordinate_system.to_dict(),
            "regions": [r.to_dict() for r in self.regions],
            "cells": [c.to_dict() for c in self.cells],
            "biomes": [b.to_dict() for b in self.biomes],
            "terrain": self.terrain.to_dict() if self.terrain else None,
            "water": self.water.to_dict() if self.water else None,
            "roads": [r.to_dict() for r in self.roads],
            "bridges": [b.to_dict() for b in self.bridges],
            "structures": [s.to_dict() for s in self.structures],
            "vegetation": self.vegetation.to_dict() if self.vegetation else None,
            "rocks": [rk.to_dict() for rk in self.rocks],
            "props": [p.to_dict() for p in self.props],
            "scatter_count": len(self.scatter_instances),
            "navigation": self.navigation.to_dict() if self.navigation else None,
            "collision": self.collision.to_dict(),
            "partition": self.partition.to_dict() if self.partition else None,
            "hlod": self.hlod.to_dict() if self.hlod else None,
            "environment": self.environment.to_dict(),
            "world_hash": self.world_hash,
            "generator_version": self.generator_version,
            "metadata": dict(self.metadata),
        }
