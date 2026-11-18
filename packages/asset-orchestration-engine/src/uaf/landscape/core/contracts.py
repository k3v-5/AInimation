"""
UAF-81.91: Core Landscape Contracts, Heightfields, Biome Types & Spline Data Structures.
Defines continuous 2D heightfields, binary 16-bit Unreal Landscape conversions,
climate data, and road spline geometries.
"""

from __future__ import annotations

import math
import struct
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field


class BiomeType(str, Enum):
    """Ecological biomes categorized by temperature and precipitation."""
    TUNDRA = "TUNDRA"
    ALPINE = "ALPINE"
    CONIFEROUS_FOREST = "CONIFEROUS_FOREST"
    TEMPERATE_FOREST = "TEMPERATE_FOREST"
    GRASSLAND = "GRASSLAND"
    DESERT = "DESERT"
    WETLAND = "WETLAND"


class RoadCategory(str, Enum):
    """Classification of road infrastructure."""
    HIGHWAY = "HIGHWAY"
    MAIN_ROAD = "MAIN_ROAD"
    DIRT_TRACK = "DIRT_TRACK"
    MOUNTAIN_TRAIL = "MOUNTAIN_TRAIL"


class SplineNode(BaseModel):
    """Discrete 3D spline point for roads, rivers, and paths."""
    node_id: str
    world_pos: Tuple[float, float, float]  # [X, Y, Z] in Unreal cm
    tangent: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    width_cm: float = 600.0  # Default 6 meters wide
    bank_angle_deg: float = 0.0


class RoadPath(BaseModel):
    """Complete spline path representing a road or transport link."""
    road_id: str
    name: str
    category: RoadCategory = RoadCategory.MAIN_ROAD
    nodes: List[SplineNode] = Field(default_factory=list)
    total_length_meters: float = 0.0
    max_gradient_pct: float = 0.0


class ClimateMap(BaseModel):
    """Dual-layer climate data mapping temperature (-20°C to +40°C) and precipitation (0 to 1)."""
    width: int
    height: int
    temperature: List[List[float]] = Field(default_factory=list)
    precipitation: List[List[float]] = Field(default_factory=list)


class TerrainLayerWeightmaps(BaseModel):
    """Alpha blend weightmaps for Unreal Engine Landscape material layers."""
    width: int
    height: int
    grass: List[List[float]] = Field(default_factory=list)
    rock: List[List[float]] = Field(default_factory=list)
    dirt: List[List[float]] = Field(default_factory=list)
    snow: List[List[float]] = Field(default_factory=list)
    sand: List[List[float]] = Field(default_factory=list)


class Heightfield2D:
    """
    Continuous 2D heightfield representation.
    Elevation values are normalized in [0.0, 1.0], mapped to real-world meters and Unreal cm.
    """

    def __init__(
        self,
        width: int,
        height: int,
        meters_per_cell: float = 2.0,
        min_elevation_meters: float = -100.0,
        max_elevation_meters: float = 1500.0,
        initial_elevation: float = 0.5,
    ):
        if width <= 0 or height <= 0:
            raise ValueError(f"Heightfield dimensions must be positive, got {width}x{height}")

        self.width = width
        self.height = height
        self.meters_per_cell = meters_per_cell
        self.min_elevation_meters = min_elevation_meters
        self.max_elevation_meters = max_elevation_meters

        # 2D grid stored row-major: data[y][x]
        self.data: List[List[float]] = [
            [initial_elevation for _ in range(width)] for _ in range(height)
        ]

    def get_elevation(self, x: int, y: int) -> float:
        """Retrieves normalized elevation [0.0, 1.0] at integer grid coordinate."""
        cx = max(0, min(self.width - 1, x))
        cy = max(0, min(self.height - 1, y))
        return self.data[cy][cx]

    def set_elevation(self, x: int, y: int, value: float) -> None:
        """Sets normalized elevation clamped to [0.0, 1.0]."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = max(0.0, min(1.0, value))

    def get_world_elevation_meters(self, x: int, y: int) -> float:
        """Computes real-world altitude in meters."""
        norm_h = self.get_elevation(x, y)
        return self.min_elevation_meters + norm_h * (self.max_elevation_meters - self.min_elevation_meters)

    def get_world_coords_cm(self, x: int, y: int) -> Tuple[float, float, float]:
        """Returns 3D coordinate [X, Y, Z] in Unreal centimeters."""
        world_x_cm = x * self.meters_per_cell * 100.0
        world_y_cm = y * self.meters_per_cell * 100.0
        world_z_cm = self.get_world_elevation_meters(x, y) * 100.0
        return (world_x_cm, world_y_cm, world_z_cm)

    def sample_bilinear(self, u: float, v: float) -> float:
        """
        Bilinear interpolation at normalized continuous coordinates u, v in [0.0, 1.0].
        """
        gx = u * (self.width - 1)
        gy = v * (self.height - 1)

        x0 = int(math.floor(gx))
        y0 = int(math.floor(gy))
        x1 = min(self.width - 1, x0 + 1)
        y1 = min(self.height - 1, y0 + 1)

        fx = gx - x0
        fy = gy - y0

        h00 = self.get_elevation(x0, y0)
        h10 = self.get_elevation(x1, y0)
        h01 = self.get_elevation(x0, y1)
        h11 = self.get_elevation(x1, y1)

        top = h00 * (1.0 - fx) + h10 * fx
        bottom = h01 * (1.0 - fx) + h11 * fx
        return top * (1.0 - fy) + bottom * fy

    def compute_gradient(self, x: int, y: int) -> Tuple[float, float]:
        """
        Computes local elevation gradient vector (dh/dx, dh/dy).
        Uses central differences where possible.
        """
        left = self.get_elevation(x - 1, y)
        right = self.get_elevation(x + 1, y)
        down = self.get_elevation(x, y - 1)
        up = self.get_elevation(x, y + 1)

        dx = (right - left) / (2.0 * self.meters_per_cell)
        dy = (up - down) / (2.0 * self.meters_per_cell)
        return (dx, dy)

    def compute_slope_angle_deg(self, x: int, y: int) -> float:
        """Calculates slope angle in degrees from horizontal."""
        gx, gy = self.compute_gradient(x, y)
        mag = math.hypot(gx, gy)
        # Scale by real-world vertical range vs horizontal cell spacing
        vertical_range = self.max_elevation_meters - self.min_elevation_meters
        real_gradient = mag * vertical_range
        return math.degrees(math.atan(real_gradient))

    def to_uint16_array(self) -> List[int]:
        """Converts normalized elevation to 16-bit unsigned integers [0, 65535]."""
        result: List[int] = []
        for y in range(self.height):
            for x in range(self.width):
                val = int(round(self.data[y][x] * 65535.0))
                result.append(max(0, min(65535, val)))
        return result

    def to_raw16_bytes(self) -> bytes:
        """
        Encodes heightfield as little-endian unsigned 16-bit raw binary data (.r16)
        directly consumable by Unreal Engine 5 Landscape import.
        """
        uint16_vals = self.to_uint16_array()
        return struct.pack(f"<{len(uint16_vals)}H", *uint16_vals)

    @classmethod
    def from_raw16_bytes(
        cls,
        raw_bytes: bytes,
        width: int,
        height: int,
        meters_per_cell: float = 2.0,
        min_elevation_meters: float = -100.0,
        max_elevation_meters: float = 1500.0,
    ) -> Heightfield2D:
        """Constructs a Heightfield2D instance from raw little-endian uint16 binary data."""
        expected_len = width * height * 2
        if len(raw_bytes) != expected_len:
            raise ValueError(f"Expected {expected_len} bytes for {width}x{height} raw16, got {len(raw_bytes)}")

        vals = struct.unpack(f"<{width * height}H", raw_bytes)
        hf = cls(
            width=width,
            height=height,
            meters_per_cell=meters_per_cell,
            min_elevation_meters=min_elevation_meters,
            max_elevation_meters=max_elevation_meters,
        )
        idx = 0
        for y in range(height):
            for x in range(width):
                hf.data[y][x] = vals[idx] / 65535.0
                idx += 1
        return hf
