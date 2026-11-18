"""
UAF-81.91: Procedural Multi-Octave Fractal Noise and Macro-Terrain Generation.
Provides deterministic Perlin noise, Ridge Multifractal for sharp mountain peaks,
Voronoi cellular noise for plateaus, domain warping, and composite terrain synthesis.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

from uaf.landscape.core.contracts import Heightfield2D


class PerlinNoise2D:
    """
    Deterministic 2D Perlin noise generator with gradient hashing.
    Outputs values in continuous range [-1.0, 1.0].
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        rng = random.Random(seed)
        p = list(range(256))
        rng.shuffle(p)
        self.perm = p + p  # Duplicate to avoid wrapping index modulo

    @staticmethod
    def _fade(t: float) -> float:
        # 6t^5 - 15t^4 + 10t^3 (quintic curve with zero 1st and 2nd derivatives at endpoints)
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    @staticmethod
    def _grad(hash_val: int, x: float, y: float) -> float:
        # 4 gradient directions: (1, 1), (-1, 1), (1, -1), (-1, -1)
        h = hash_val & 3
        u = x if h & 1 == 0 else -x
        v = y if h & 2 == 0 else -y
        return u + v

    def sample(self, x: float, y: float) -> float:
        """Samples 2D Perlin noise at continuous coordinates (x, y)."""
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255

        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self._fade(xf)
        v = self._fade(yf)

        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]

        x1 = (1.0 - u) * self._grad(aa, xf, yf) + u * self._grad(ba, xf - 1.0, yf)
        x2 = (1.0 - u) * self._grad(ab, xf, yf - 1.0) + u * self._grad(bb, xf - 1.0, yf - 1.0)

        # Scale to approximately [-1.0, 1.0]
        return ((1.0 - v) * x1 + v * x2) * 1.41421356


class FractalNoise2D:
    """
    Multi-octave Fractal Brownian Motion (FBM) and Ridge Multifractal.
    """

    def __init__(self, seed: int = 42, octaves: int = 6, persistence: float = 0.5, lacunarity: float = 2.0):
        self.noise = PerlinNoise2D(seed=seed)
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

    def fbm(self, x: float, y: float) -> float:
        """Standard Fractal Brownian Motion. Output in [-1.0, 1.0]."""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_amp = 0.0

        for _ in range(self.octaves):
            total += self.noise.sample(x * frequency, y * frequency) * amplitude
            max_amp += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total / max_amp if max_amp > 0 else 0.0

    def ridge(self, x: float, y: float, offset: float = 1.0, gain: float = 2.0) -> float:
        """
        Ridge Multifractal: creates sharp mountain spines, ridges, and valleys.
        Outputs in range [0.0, 1.0].
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        weight = 1.0

        for _ in range(self.octaves):
            signal = self.noise.sample(x * frequency, y * frequency)
            signal = abs(signal)
            signal = offset - signal
            signal = signal * signal

            signal *= weight
            weight = max(0.0, min(1.0, signal * gain))

            total += signal * amplitude
            frequency *= self.lacunarity
            amplitude *= self.persistence

        # Normalize to [0.0, 1.0]
        return max(0.0, min(1.0, total * 0.45))


class VoronoiCellularNoise2D:
    """
    Cellular / Worley noise: calculates distance to nearest feature points.
    Creates terraced mesas, cracked canyons, and flat basin cells.
    """

    def __init__(self, seed: int = 42, cell_size: float = 16.0):
        self.seed = seed
        self.cell_size = cell_size
        self.rng = random.Random(seed)

    def sample(self, x: float, y: float) -> float:
        """Returns distance to nearest Voronoi seed point normalized in [0.0, 1.0]."""
        gx = x / self.cell_size
        gy = y / self.cell_size

        xi = int(math.floor(gx))
        yi = int(math.floor(gy))

        min_dist = float("inf")

        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                cx = xi + ox
                cy = yi + oy

                # Pseudo-random offset based on integer cell coordinates
                cell_hash = hash((cx, cy, self.seed)) & 0xFFFFFFFF
                rand_x = (cell_hash & 0xFFFF) / 65535.0
                rand_y = ((cell_hash >> 16) & 0xFFFF) / 65535.0

                px = cx + rand_x
                py = cy + rand_y

                dist = math.hypot(gx - px, gy - py)
                if dist < min_dist:
                    min_dist = dist

        return min(1.0, min_dist / 1.414)


class MacroTerrainGenerator:
    """
    Synthesizes macroscopic outdoor landscapes combining continental landmass curves,
    ridge multifractals, rolling hills, and organic domain warping.
    """

    def __init__(
        self,
        seed: int = 42,
        mountain_scale: float = 0.003,
        hills_scale: float = 0.012,
        roughness_scale: float = 0.04,
    ):
        self.seed = seed
        self.mountain_scale = mountain_scale
        self.hills_scale = hills_scale
        self.roughness_scale = roughness_scale

        self.fbm_mountains = FractalNoise2D(seed=seed, octaves=6, persistence=0.5, lacunarity=2.0)
        self.fbm_hills = FractalNoise2D(seed=seed + 101, octaves=4, persistence=0.45, lacunarity=2.1)
        self.fbm_roughness = FractalNoise2D(seed=seed + 202, octaves=3, persistence=0.4, lacunarity=2.2)
        self.warp_x = FractalNoise2D(seed=seed + 303, octaves=3, persistence=0.5, lacunarity=2.0)
        self.warp_y = FractalNoise2D(seed=seed + 404, octaves=3, persistence=0.5, lacunarity=2.0)

    def generate(self, heightfield: Heightfield2D) -> Heightfield2D:
        """
        Fills the heightfield with continuous natural terrain elevation [0.0, 1.0].
        """
        w, h = heightfield.width, heightfield.height
        warp_intensity = 30.0

        for y in range(h):
            for x in range(w):
                # 1. Domain warping: perturb sampling coordinates to produce organic geological swirls
                wx = x + self.warp_x.fbm(x * 0.005, y * 0.005) * warp_intensity
                wy = y + self.warp_y.fbm(x * 0.005, y * 0.005) * warp_intensity

                # 2. Continental base landform: gentle sweeping gradient
                base_val = (self.fbm_mountains.fbm(wx * 0.001, wy * 0.001) + 1.0) * 0.5

                # 3. Mountain ridges (sharp peaks)
                ridge_val = self.fbm_mountains.ridge(wx * self.mountain_scale, wy * self.mountain_scale)

                # 4. Rolling hills
                hills_val = (self.fbm_hills.fbm(wx * self.hills_scale, wy * self.hills_scale) + 1.0) * 0.5

                # 5. Micro roughness
                rough_val = self.fbm_roughness.fbm(wx * self.roughness_scale, wy * self.roughness_scale) * 0.05

                # Composite height:
                # Ridge is masked by high base landform so valleys remain flatter
                elevation = (base_val * 0.35) + (ridge_val * base_val * 0.45) + (hills_val * 0.15) + rough_val
                heightfield.set_elevation(x, y, elevation)

        return heightfield
