"""
UAF-81.91: Ecological Climate Modeling, Whittaker Biomes & Terrain Weightmaps.
Synthesizes temperature and precipitation matrices, classifies biomes,
and generates normalized alpha blend layer weightmaps for Unreal Engine Landscape materials.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from uaf.landscape.core.contracts import (
    BiomeType,
    ClimateMap,
    TerrainLayerWeightmaps,
    Heightfield2D,
)
from uaf.landscape.generation.noise import PerlinNoise2D


class ClimateModeler:
    """
    Computes realistic temperature and precipitation fields from terrain altitude
    using standard meteorological lapse rates and orographic rain-shadow modeling.
    """

    def __init__(
        self,
        sea_level_temperature_c: float = 24.0,
        lapse_rate_c_per_meter: float = 0.0065,
        wind_direction: Tuple[float, float] = (1.0, 0.0),  # Prevailing wind from West to East
        seed: int = 42,
    ):
        self.sea_level_temp = sea_level_temperature_c
        self.lapse_rate = lapse_rate_c_per_meter

        wx, wy = wind_direction
        mag = math.hypot(wx, wy)
        self.wind_dir = (wx / mag, wy / mag) if mag > 1e-5 else (1.0, 0.0)

        self.noise_temp = PerlinNoise2D(seed=seed + 501)
        self.noise_precip = PerlinNoise2D(seed=seed + 601)

    def generate_climate(self, heightfield: Heightfield2D) -> ClimateMap:
        """Computes continuous temperature (°C) and precipitation [0.0, 1.0] grids."""
        w, h = heightfield.width, heightfield.height
        temp_grid: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        precip_grid: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]

        wx, wy = self.wind_dir

        for y in range(h):
            for x in range(w):
                alt_m = heightfield.get_world_elevation_meters(x, y)

                # 1. Temperature from altitude lapse rate + slight noise variation
                t_noise = self.noise_temp.sample(x * 0.03, y * 0.03) * 2.5
                temp = self.sea_level_temp - (self.lapse_rate * max(0.0, alt_m)) + t_noise
                temp_grid[y][x] = round(temp, 2)

                # 2. Precipitation from base noise + orographic windward lift
                gx, gy = heightfield.compute_gradient(x, y)
                windward_lift = (gx * wx + gy * wy) * 25.0

                base_precip = (self.noise_precip.sample(x * 0.02, y * 0.02) + 1.0) * 0.5
                precip = base_precip + windward_lift

                # Coastal/lowland humidity boost
                if alt_m < 150.0:
                    precip += 0.15

                precip_grid[y][x] = max(0.0, min(1.0, round(precip, 4)))

        return ClimateMap(width=w, height=h, temperature=temp_grid, precipitation=precip_grid)


class WhittakerBiomeClassifier:
    """
    Classifies ecological biomes on a 2D Whittaker matrix of temperature and precipitation.
    """

    @staticmethod
    def classify(temperature_c: float, precipitation: float, altitude_m: float) -> BiomeType:
        """Returns BiomeType for given temperature, precipitation, and altitude."""
        if altitude_m >= 1500.0 or temperature_c < -2.0:
            return BiomeType.ALPINE if altitude_m > 800.0 else BiomeType.TUNDRA

        if temperature_c < 10.0:
            if precipitation > 0.4:
                return BiomeType.CONIFEROUS_FOREST
            return BiomeType.TUNDRA if precipitation < 0.2 else BiomeType.GRASSLAND

        if temperature_c < 22.0:
            if precipitation > 0.65 and altitude_m < 200.0:
                return BiomeType.WETLAND
            if precipitation > 0.45:
                return BiomeType.TEMPERATE_FOREST
            return BiomeType.GRASSLAND if precipitation > 0.18 else BiomeType.DESERT

        # Warm / Tropical
        if precipitation < 0.22:
            return BiomeType.DESERT
        if precipitation > 0.70 and altitude_m < 150.0:
            return BiomeType.WETLAND
        return BiomeType.TEMPERATE_FOREST


class TerrainWeightmapGenerator:
    """
    Generates normalized 5-layer material weightmaps (Grass, Rock, Dirt, Snow, Sand)
    for Unreal Engine Landscape Materials.
    """

    @staticmethod
    def generate_weightmaps(heightfield: Heightfield2D, climate: ClimateMap) -> TerrainLayerWeightmaps:
        """Calculates normalized layer blend weights for every terrain vertex."""
        w, h = heightfield.width, heightfield.height

        grass_map: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        rock_map: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        dirt_map: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        snow_map: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        sand_map: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]

        for y in range(h):
            for x in range(w):
                alt_m = heightfield.get_world_elevation_meters(x, y)
                slope_deg = heightfield.compute_slope_angle_deg(x, y)
                temp = climate.temperature[y][x]
                precip = climate.precipitation[y][x]

                # Weight heuristic scores:
                # 1. Rock: proportional to slope steepness (> 28 deg)
                w_rock = max(0.0, (slope_deg - 25.0) / 25.0) if slope_deg > 25.0 else 0.0

                # 2. Snow: sub-zero temperatures and high peaks
                w_snow = 0.0
                if temp < 0.0:
                    w_snow = min(1.0, abs(temp) / 10.0 + (alt_m / 1500.0) * 0.5)

                # 3. Sand: low beach elevations or extreme arid zones
                w_sand = 0.0
                if alt_m < 50.0:
                    w_sand = max(0.0, (50.0 - alt_m) / 50.0)
                elif temp > 25.0 and precip < 0.15:
                    w_sand = 0.8

                # 4. Dirt: transitional soil, forest sub-layer, moderate slopes
                w_dirt = 0.15
                if 18.0 <= slope_deg <= 32.0:
                    w_dirt += 0.45

                # 5. Grass: flat/gentle slopes, temperate climate
                w_grass = 0.0
                if slope_deg < 25.0 and temp > 0.0 and precip > 0.2:
                    w_grass = max(0.0, (1.0 - (slope_deg / 25.0))) * min(1.0, precip * 1.5)

                # Normalize weights to sum to 1.0
                total = w_rock + w_snow + w_sand + w_dirt + w_grass
                if total <= 1e-6:
                    w_dirt = 1.0
                    total = 1.0

                grass_map[y][x] = round(w_grass / total, 4)
                rock_map[y][x] = round(w_rock / total, 4)
                dirt_map[y][x] = round(w_dirt / total, 4)
                snow_map[y][x] = round(w_snow / total, 4)
                sand_map[y][x] = round(w_sand / total, 4)

        return TerrainLayerWeightmaps(
            width=w,
            height=h,
            grass=grass_map,
            rock=rock_map,
            dirt=dirt_map,
            snow=snow_map,
            sand=sand_map,
        )
