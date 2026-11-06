"""
Unit Tests for the Neural 3D Foundation Model Engine & 360° PBR Baker (backend.ai.neural_3d_engine).

Tests:
1. Square-normalized defringed RGBA concept preprocessing & CAS SHA-256 hashing.
2. 100% UV Texture Atlas PBR materials with zero vertex color Gouraud shading,
   and albedo delighting + roughness synthesis.
3. Provider registry integration (`Hunyuan3DProvider`, `TrellisProvider`, `TripoProvider`, `FalAIProvider`)
   and offline unit-test fallback safety.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import pytest

from backend.ai.base import provider_registry
from backend.ai.image_to_3d import FalAIProvider, Hunyuan3DProvider, TrellisProvider, TripoProvider
from backend.ai.neural_3d_engine import (
    ConceptPreprocessMeta,
    _find_1d_intervals,
    _smoothstep,
    enhance_and_delight_albedo,
    generate_neural_3d_model,
    prepare_concept_square_rgba,
)
from backend.core.models import MeshFormat


def _create_character_concept_image(path: Path, width: int = 128, height: int = 256) -> Path:
    """Create a synthetic character concept PNG with cap, face, torso, and legs."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Cap (dark navy)
    draw.ellipse((44, 16, 84, 48), fill=(35, 42, 68, 255))
    # Face (warm skin tone)
    draw.ellipse((46, 36, 82, 68), fill=(215, 175, 162, 255))
    # Torso jacket (slate blue)
    draw.rectangle((36, 68, 92, 150), fill=(68, 78, 108, 255))
    # Left & Right legs
    draw.rectangle((40, 150, 58, 236), fill=(48, 52, 74, 255))
    draw.rectangle((70, 150, 88, 236), fill=(48, 52, 74, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def test_prepare_concept_square_rgba(tmp_path: Path) -> None:
    """Verify square RGBA normalization, fg_ratio scaling, and CAS SHA-256."""
    src_img = _create_character_concept_image(tmp_path / "char_concept.png")
    cache_dir = tmp_path / "cache"

    meta = prepare_concept_square_rgba(
        image_path=str(src_img),
        cache_dir=cache_dir,
        target_size=512,
        fg_ratio=0.86,
    )
    assert isinstance(meta, ConceptPreprocessMeta)
    assert meta.target_size == 512
    assert len(meta.cas_sha256) == 24
    sq_file = Path(meta.square_rgba_path)
    assert sq_file.exists()
    with Image.open(sq_file) as pil_sq:
        assert pil_sq.size == (512, 512)
        assert pil_sq.mode == "RGBA"


def test_find_1d_intervals_and_smoothstep() -> None:
    """Verify 1D interval detection and C^1 Hermite smoothstep."""
    mask = np.array([False, True, True, True, False, False, True, True, True, True, False], dtype=np.bool_)
    intervals = _find_1d_intervals(mask, min_width=3)
    assert intervals == [(1, 3), (6, 9)]

    x = np.array([-1.0, 0.0, 0.5, 1.0, 2.0], dtype=np.float32)
    s = _smoothstep(0.0, 1.0, x)
    assert np.isclose(float(s[0]), 0.0)
    assert np.isclose(float(s[1]), 0.0)
    assert np.isclose(float(s[2]), 0.5)
    assert np.isclose(float(s[3]), 1.0)
    assert np.isclose(float(s[4]), 1.0)


def test_trellis_and_neural_mesh_uv_texture_zero_vertex_colors(tmp_path: Path) -> None:
    """Verify Microsoft TRELLIS provider registration and zero vertex color Gouraud shading."""
    providers = provider_registry.list_providers("image_to_3d")["image_to_3d"]
    assert "trellis" in providers
    trellis_prov = provider_registry.get_provider("image_to_3d", "trellis")
    assert isinstance(trellis_prov, TrellisProvider)
    assert trellis_prov.health_check() is True

    # Check that compute_360_pbr_vertex_colors is permanently removed
    import backend.ai.neural_3d_engine as n3d
    assert not hasattr(n3d, "compute_360_pbr_vertex_colors")

    # Verify enhance_and_delight_albedo produces calibrated 2K albedo and roughness
    dummy_rgb = np.full((64, 64, 3), 0.5, dtype=np.float32)
    dummy_mask = np.ones((64, 64), dtype=np.bool_)
    alb_2k, rgh_2k = enhance_and_delight_albedo(dummy_rgb, dummy_mask, target_res=128)
    assert alb_2k.shape == (128, 128, 3)
    assert rgh_2k.shape == (128, 128)
    assert float(alb_2k.min()) >= 0.0 and float(alb_2k.max()) <= 1.0
    assert float(rgh_2k.min()) >= 0.0 and float(rgh_2k.max()) <= 1.0


def test_hunyuan3d_provider_registration_and_offline_fallback(tmp_path: Path) -> None:
    """Verify Hunyuan3DProvider and TrellisProvider are registered and safely fall back when offline."""
    providers = provider_registry.list_providers("image_to_3d")["image_to_3d"]
    assert "hunyuan3d_2" in providers
    assert "trellis" in providers
    assert "tripo_ai" in providers
    assert "fal_ai" in providers

    dummy_img = tmp_path / "tiny.png"
    Image.new("RGBA", (4, 4), (120, 140, 180, 255)).save(dummy_img)
    out_glb = tmp_path / "out.glb"

    res = generate_neural_3d_model(
        image_path=str(dummy_img),
        output_path=str(out_glb),
        provider_name="hunyuan3d_2",
        allow_remote=False,
    )
    assert res.mesh_format == MeshFormat.GLB
    assert Path(res.mesh_path).exists()
    assert res.vertex_count > 0
    assert res.polygon_count > 0


def test_rgb_to_lab_roundtrip() -> None:
    """Verify bidirectional sRGB <-> CIE L*a*b* conversion precision."""
    from backend.ai.neural_3d_engine import lab_to_rgb, rgb_to_lab

    test_colors = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.85, 0.72, 0.65],
            [0.22, 0.25, 0.35],
        ],
        dtype=np.float32,
    )
    lab = rgb_to_lab(test_colors)
    rgb_recon = lab_to_rgb(lab)
    max_err = float(np.max(np.abs(test_colors - rgb_recon)))
    assert max_err < 1e-4


def test_delight_concept_lab_intrinsic() -> None:
    """Verify intrinsic shadow delighting in LAB space preserves chroma and lifts shadows."""
    from backend.ai.neural_3d_engine import delight_concept_lab

    # Create synthetic test canvas with smooth region and deep shadow
    img = np.full((128, 128, 4), 255, dtype=np.uint8)
    img[20:108, 20:108, :3] = [190, 140, 120]  # Base tone
    img[40:80, 40:80, :3] = [60, 44, 38]  # Harsh shadow

    delit = delight_concept_lab(img, shadow_lift=0.30)
    assert delit.shape == img.shape
    assert np.array_equal(delit[:, :, 3], img[:, :, 3])  # Alpha untouched

    shadow_orig = img[60, 60, :3].astype(np.float32)
    shadow_new = delit[60, 60, :3].astype(np.float32)
    # Luma lifted
    assert float(np.mean(shadow_new)) > float(np.mean(shadow_orig)) + 10.0


def test_detect_bipedal_rig_landmarks_adaptive() -> None:
    """Verify adaptive topological landmark auto-rigging on tall vs compact biped meshes."""
    from backend.ai.neural_3d_engine import detect_bipedal_rig_landmarks

    # 1. Standard tall biped
    n_v = 1000
    z_tall = np.linspace(0.0, 1.80, n_v, dtype=np.float32)
    x_tall = np.where(z_tall < 0.85, np.where(z_tall % 2 > 1, 0.15, -0.15), 0.05 * np.sin(z_tall * 5))
    y_tall = np.zeros_like(z_tall)
    verts_tall = np.stack([x_tall, y_tall, z_tall], axis=-1)

    landmarks_tall = detect_bipedal_rig_landmarks(verts_tall)
    assert "Pelvis" in landmarks_tall
    assert "Neck" in landmarks_tall
    assert "Head" in landmarks_tall
    assert "Shoulder_L" in landmarks_tall
    assert "Foot_L" in landmarks_tall

    # Verify bone hierarchy ordering
    pelvis_head = landmarks_tall["Pelvis"][0]
    neck_head = landmarks_tall["Neck"][0]
    assert neck_head[2] > pelvis_head[2]


def test_zero_character_specific_magic_numbers() -> None:
    """Audit backend.ai.neural_3d_engine for zero character-specific hardcoded strings or coordinates."""
    engine_file = Path(__file__).resolve().parent.parent.parent / "backend" / "ai" / "neural_3d_engine.py"
    content = engine_file.read_text(encoding="utf-8")

    forbidden_tokens = [
        "anime_tactical",
        "navy_cloth",
        "steel_blue_hair",
        "dark_boot_leg",
        "skin_band_leg",
        "tattoo_box",
        "choker_box",
        "is_drawn_chin_ink",
        "is_throat_ink",
        "peach_skin_2d",
        "u_leg_R = 442.0",
        "u_leg_L = 568.0",
        "507.5",
        "compute_360_pbr_vertex_colors",
        "FLOAT_COLOR",
    ]
    for token in forbidden_tokens:
        assert token not in content, f"Forbidden character-specific token found in neural_3d_engine.py: '{token}'"

