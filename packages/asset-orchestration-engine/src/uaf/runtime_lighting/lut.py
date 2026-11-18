"""
Color Look-Up Tables (1D & 3D LUT) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LUT3D:
    """
    3D Color Look-Up Table with trilinear interpolation and size validation.
    """
    size: int = 16  # Typical sizes: 16, 32, 64
    data: List[Tuple[float, float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.size = max(2, min(64, int(self.size)))
        expected_elements = self.size ** 3
        if len(self.data) != expected_elements:
            # Generate neutral identity LUT
            self.data = []
            inv_size = 1.0 / float(self.size - 1)
            for b in range(self.size):
                for g in range(self.size):
                    for r in range(self.size):
                        self.data.append((r * inv_size, g * inv_size, b * inv_size))

    def sample(self, r: float, g: float, b: float) -> Tuple[float, float, float]:
        """Samples the 3D LUT with trilinear interpolation."""
        s = float(self.size - 1)
        cr = max(0.0, min(1.0, r)) * s
        cg = max(0.0, min(1.0, g)) * s
        cb = max(0.0, min(1.0, b)) * s

        r0, r1 = int(math.floor(cr)), int(math.ceil(cr))
        g0, g1 = int(math.floor(cg)), int(math.ceil(cg))
        b0, b1 = int(math.floor(cb)), int(math.ceil(cb))

        dr = cr - r0
        dg = cg - g0
        db = cb - b0

        def get_entry(ri: int, gi: int, bi: int) -> Tuple[float, float, float]:
            idx = bi * (self.size * self.size) + gi * self.size + ri
            return self.data[idx]

        c000 = get_entry(r0, g0, b0)
        c100 = get_entry(r1, g0, b0)
        c010 = get_entry(r0, g1, b0)
        c110 = get_entry(r1, g1, b0)
        c001 = get_entry(r0, g0, b1)
        c101 = get_entry(r1, g0, b1)
        c011 = get_entry(r0, g1, b1)
        c111 = get_entry(r1, g1, b1)

        def lerp3(c0: Tuple[float, float, float], c1: Tuple[float, float, float], t: float) -> Tuple[float, float, float]:
            return (c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, c0[2] + (c1[2] - c0[2]) * t)

        c00 = lerp3(c000, c100, dr)
        c10 = lerp3(c010, c110, dr)
        c01 = lerp3(c001, c101, dr)
        c11 = lerp3(c011, c111, dr)

        c0 = lerp3(c00, c10, dg)
        c1 = lerp3(c01, c11, dg)

        final = lerp3(c0, c1, db)
        return (round(final[0], 6), round(final[1], 6), round(final[2], 6))
