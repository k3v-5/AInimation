"""
Alpha Matting, Edge Defringing, and Color Bleed (Despill) Engine for IANIMATION.

Eliminates background color bleed, halo artifacts, and edge fringing on 2D concept cutouts
before 3D projection by performing Euclidean Distance Transform (EDT) color dilation,
morphological boundary erosion, and subpixel alpha matting.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion, distance_transform_edt


def defringe_alpha(
    image: Union[np.ndarray, Image.Image],
    bg_mask: Optional[np.ndarray] = None,
    erosion_pixels: int = 2,
    alpha_feather: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove background color fringing and dilate pure interior albedo into edge pixels.

    Args:
        image: Input RGBA image as NumPy array (H, W, 4) or PIL Image.
        bg_mask: Optional boolean mask where True = background pixels. If None, auto-detected.
        erosion_pixels: Number of pixels to erode foreground to discard contaminated fringe.
        alpha_feather: Feathering falloff distance in pixels for anti-aliasing.

    Returns:
        Tuple of (clean_rgba_uint8, clean_alpha_mask_bool).
    """
    if isinstance(image, Image.Image):
        arr = np.array(image.convert("RGBA")).astype(np.float32)
    else:
        arr = image.astype(np.float32) if image.dtype != np.float32 else image.copy()

    h, w = arr.shape[:2]
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    orig_a = arr[:, :, 3] if arr.shape[2] == 4 else np.full((h, w), 255.0, dtype=np.float32)

    # Auto-detect background if not explicitly provided
    if bg_mask is None:
        # Detect solid or parchment backgrounds (high luminance, low chromatic variance)
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        chroma = max_c - min_c

        # Sample border pixels to detect background color
        border_samples = np.concatenate([
            arr[0:8, :, :3].reshape(-1, 3),
            arr[h - 8 : h, :, :3].reshape(-1, 3),
            arr[:, 0:8, :3].reshape(-1, 3),
            arr[:, w - 8 : w, :3].reshape(-1, 3),
        ], axis=0)
        bg_color = np.median(border_samples, axis=0)

        # Distance to detected background color
        color_dist = np.sqrt(
            (r - bg_color[0]) ** 2 + (g - bg_color[1]) ** 2 + (b - bg_color[2]) ** 2
        )
        # Background is close in color to borders OR high luminance low chroma OR transparent
        is_parchment = (r > 215) & (g > 215) & (b > 205) & (chroma < 22)

        # Detect high-chroma studio cycloramas (blue screen / green screen / gradient cycloramas)
        border_is_blue = (bg_color[2] > bg_color[0] + 25) and (bg_color[2] > bg_color[1] + 5)
        border_is_green = (bg_color[1] > bg_color[0] + 25) and (bg_color[1] > bg_color[2] + 25)

        sat = np.zeros_like(max_c)
        valid_c = max_c > 1e-4
        sat[valid_c] = chroma[valid_c] / max_c[valid_c]

        min_border_b = float(np.percentile(border_samples[:, 2], 5)) - 25.0
        min_border_g = float(np.percentile(border_samples[:, 1], 5)) - 25.0
        max_border_r = float(np.percentile(border_samples[:, 0], 95)) + 25.0

        is_blue_studio = (
            border_is_blue
            & (b > min_border_b)
            & (b > r + 60)
            & (b > g + 25)
            & (r < max_border_r)
        )
        is_green_studio = (
            border_is_green
            & (g > min_border_g)
            & (g > r + 50)
            & (g > b + 35)
            & (r < max_border_r)
        )

        bg_mask = (color_dist < 32.0) | is_parchment | is_blue_studio | is_green_studio | (orig_a < 30.0)

    fg_mask = ~bg_mask

    # 1. Morphological erosion of foreground to discard background-contaminated transition border
    if erosion_pixels > 0:
        clean_core = binary_erosion(fg_mask, iterations=erosion_pixels)
        # Ensure we didn't eliminate small features completely
        if np.sum(clean_core) < 100:
            clean_core = fg_mask
    else:
        clean_core = fg_mask

    # 2. Nearest-Neighbor Color Bleed (EDT with return_indices=True)
    # Outside the clean core, replace RGB with the exact color of the nearest interior pixel.
    distances, indices = distance_transform_edt(~clean_core, return_indices=True)
    clean_rgb = arr[:, :, :3][indices[0], indices[1]]

    # 3. Continuous subpixel anti-aliased alpha matte
    dist_inside = distance_transform_edt(clean_core)
    dist_outside = distance_transform_edt(~clean_core)
    alpha = np.clip((dist_inside - dist_outside + alpha_feather * 0.5) / max(0.1, alpha_feather), 0.0, 1.0)
    alpha[clean_core] = 1.0
    alpha[dist_outside > (alpha_feather + 0.5)] = 0.0

    # Also respect original alpha if the input already had transparent regions
    if np.any(orig_a < 250.0):
        alpha = np.minimum(alpha, orig_a / 255.0)

    result_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    result_rgba[:, :, :3] = np.clip(clean_rgb, 0, 255).astype(np.uint8)
    result_rgba[:, :, 3] = (alpha * 255.0).astype(np.uint8)

    final_mask = alpha > 0.05
    return result_rgba, final_mask
