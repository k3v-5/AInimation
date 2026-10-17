"""
Unit tests for Alpha Matting, Defringing, and Color Bleed (Despill) Engine.
"""

import numpy as np
from PIL import Image
import pytest

from backend.ai.defringe import defringe_alpha


def test_defringe_alpha_basic():
    """Verify defringing dilates interior colors and cleans edge borders."""
    # 100x100 image with cream parchment background (245, 245, 240)
    img = np.full((100, 100, 4), [245, 245, 240, 255], dtype=np.uint8)
    y, x = np.ogrid[:100, :100]
    # Solid blue circle inside
    circle = (x - 50) ** 2 + (y - 50) ** 2 <= 30 ** 2
    img[circle] = [20, 50, 220, 255]

    # Contaminated transition fringe
    fringe = ((x - 50) ** 2 + (y - 50) ** 2 <= 32 ** 2) & ~circle
    img[fringe] = [180, 180, 230, 255]  # Blend with background

    clean_rgba, mask = defringe_alpha(img, erosion_pixels=2)
    assert clean_rgba.shape == (100, 100, 4)
    assert np.sum(mask) > 1000

    # Outside the circle, RGB should be blue (dilated from inside), not cream!
    outer_points = ((x - 50) ** 2 + (y - 50) ** 2 == 33 ** 2)
    dilated_colors = clean_rgba[outer_points, :3]
    # Dilated blue channel should be high (> 180), and red/green should be low (< 80)
    assert dilated_colors[:, 2].mean() > 180
    assert dilated_colors[:, 0].mean() < 80


def test_defringe_with_pil_input():
    """Verify defringe_alpha accepts PIL Images and returns consistent results."""
    pil_img = Image.new("RGBA", (80, 80), (250, 250, 250, 255))
    clean_rgba, mask = defringe_alpha(pil_img)
    assert isinstance(clean_rgba, np.ndarray)
    assert isinstance(mask, np.ndarray)
    assert clean_rgba.shape == (80, 80, 4)
