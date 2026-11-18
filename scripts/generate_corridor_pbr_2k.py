"""Generate 2048x2048 Industrial Emergency Corridor PBR Textures (BaseColor, Normal DirectX, ORM, Emissive).

Follows the texture encoding standard of packages/blender-procedural-lab:
- corridor_basecolor.png (sRGB 2048x2048)
- corridor_normal.png (Tangent-space DirectX Normal map via Sobel height gradient)
- corridor_orm.png (R=Ambient Occlusion, G=Roughness, B=Metallic)
- corridor_emissive.png (Industrial cyan & hazard orange/crimson light strips)
"""

from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
TEX_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo" / "textures"
TEX_DIR.mkdir(parents=True, exist_ok=True)

RES = 2048


def compute_normal_map(height_map: np.ndarray, strength: float = 3.2) -> np.ndarray:
    """Compute tangent-space DirectX normal map from normalized height field."""
    sx = cv2.Sobel(height_map, cv2.CV_32F, 1, 0, ksize=5)
    sy = cv2.Sobel(height_map, cv2.CV_32F, 0, 1, ksize=5)
    dx = -sx * strength
    dy = sy * strength
    dz = np.ones_like(height_map, dtype=np.float32)
    length = np.sqrt(dx * dx + dy * dy + dz * dz) + 1e-6
    r = ((dx / length * 0.5 + 0.5) * 255.0).clip(0, 255).astype(np.uint8)
    g = ((dy / length * 0.5 + 0.5) * 255.0).clip(0, 255).astype(np.uint8)
    b = ((dz / length * 0.5 + 0.5) * 255.0).clip(0, 255).astype(np.uint8)
    return np.stack([r, g, b], axis=-1)


def compute_ao_map(height_map: np.ndarray) -> np.ndarray:
    """Compute physical cavity/crevice Ambient Occlusion map."""
    blur = cv2.GaussianBlur(height_map, (35, 35), 9.0)
    ao = np.clip(0.80 + (height_map - blur) * 1.4, 0.25, 1.0)
    return (ao * 255.0).astype(np.uint8)


def generate_textures() -> None:
    """Synthesize seamless 2048x2048 industrial emergency deck PBR maps."""
    rng = np.random.default_rng(2026)

    # Multi-scale steel grain & panel grime
    noise_lo = cv2.resize(rng.random((64, 64), dtype=np.float32), (RES, RES), interpolation=cv2.INTER_CUBIC)
    noise_hi = cv2.resize(rng.random((512, 512), dtype=np.float32), (RES, RES), interpolation=cv2.INTER_LINEAR)
    grime = noise_lo * 0.65 + noise_hi * 0.35

    yy, xx = np.mgrid[0:RES, 0:RES]

    # Modular floor armor tiles (4x4 grid across 2048px)
    tile = 512
    tx = xx % tile
    ty = yy % tile
    seam = (tx < 10) | (tx > tile - 10) | (ty < 10) | (ty > tile - 10)

    # Raised industrial diamond/ribbed tread in central aisle (x in 384..1664)
    in_aisle = (xx > 320) & (xx < RES - 320)
    rib_u = (xx + yy) % 64 < 22
    rib_v = ((xx - yy) % 64) < 22
    tread = in_aisle & (rib_u ^ rib_v)

    # Hazard yellow/black chevron border strips along x in 200..310 and 1738..1848
    in_hazard = ((xx >= 200) & (xx <= 310)) | ((xx >= RES - 310) & (xx <= RES - 200))
    chevron = ((xx + yy) // 72) % 2 == 0

    # LED conduit recessed channels along x in 140..176 and 1872..1908
    in_led = ((xx >= 140) & (xx <= 176)) | ((xx >= RES - 176) & (xx <= RES - 140))

    # Height map in [0, 1]
    height = 0.55 + (grime - 0.5) * 0.14
    height[tread] += 0.18
    height[seam] -= 0.32
    height[in_led] -= 0.20
    height = np.clip(height, 0.0, 1.0).astype(np.float32)

    # BaseColor RGB
    base = np.zeros((RES, RES, 3), dtype=np.float32)
    # Dark gunmetal steel panels
    base[:, :, 0] = 0.14 + grime * 0.08
    base[:, :, 1] = 0.16 + grime * 0.08
    base[:, :, 2] = 0.19 + grime * 0.09

    # Worn metallic edge highlights on tread ribs
    base[tread] = np.clip(base[tread] + np.array([0.07, 0.08, 0.09]), 0.0, 1.0)
    # Subtle rust smudges near seams
    rust_mask = (grime > 0.62) & (~in_hazard) & (~in_led)
    base[rust_mask] = base[rust_mask] * 0.72 + np.array([0.24, 0.11, 0.05]) * 0.28

    # Yellow / Charcoal industrial caution stripes
    yellow_stripe = in_hazard & chevron
    dark_stripe = in_hazard & (~chevron)
    base[yellow_stripe] = np.array([0.85, 0.64, 0.06]) * (0.75 + grime[yellow_stripe, None] * 0.35)
    base[dark_stripe] = np.array([0.07, 0.07, 0.08])

    # Rivets at corners of 512px tiles
    for ry in range(42, RES, tile):
        for rx in range(42, RES, tile):
            for ox, oy in [(0, 0), (tile - 84, 0), (0, tile - 84), (tile - 84, tile - 84)]:
                cx, cy = rx + ox, ry + oy
                cv2.circle(height, (cx, cy), 12, 0.92, -1)
                cv2.circle(base, (cx, cy), 12, (0.34, 0.37, 0.40), -1)

    base[seam] *= 0.35
    base_u8 = np.clip(base * 255.0, 0, 255).astype(np.uint8)

    # Normal & AO
    normal_u8 = compute_normal_map(height, strength=3.4)
    ao_u8 = compute_ao_map(height)

    # Roughness & Metallic
    rough = 0.34 + grime * 0.32
    rough[in_hazard] = 0.52 + grime[in_hazard] * 0.20
    rough[tread] = 0.24 + grime[tread] * 0.15
    rough[seam] = 0.75
    rough_u8 = np.clip(rough * 255.0, 0, 255).astype(np.uint8)

    metal = np.full((RES, RES), 0.78, dtype=np.float32)
    metal[in_hazard] = 0.08
    metal[rust_mask] = 0.25
    metal[seam] = 0.20
    metal_u8 = np.clip(metal * 255.0, 0, 255).astype(np.uint8)

    orm_u8 = np.stack([ao_u8, rough_u8, metal_u8], axis=-1)

    # Emissive strips (cyan & crimson intermittent warning segments)
    emissive = np.zeros((RES, RES, 3), dtype=np.uint8)
    seg_cyan = in_led & ((yy // 256) % 2 == 0)
    seg_crimson = in_led & ((yy // 256) % 2 == 1)
    emissive[seg_cyan] = (15, 225, 255)
    emissive[seg_crimson] = (255, 24, 42)
    emissive = cv2.GaussianBlur(emissive, (9, 9), 2.5)

    Image.fromarray(base_u8, mode="RGB").save(str(TEX_DIR / "corridor_basecolor.png"))
    Image.fromarray(normal_u8, mode="RGB").save(str(TEX_DIR / "corridor_normal.png"))
    Image.fromarray(orm_u8, mode="RGB").save(str(TEX_DIR / "corridor_orm.png"))
    Image.fromarray(emissive, mode="RGB").save(str(TEX_DIR / "corridor_emissive.png"))
    print(f"Generated 4 2048x2048 PBR maps in {TEX_DIR}")


if __name__ == "__main__":
    generate_textures()
