"""
Unit tests for Part-Based Scene and Component Decomposition Engine.

Validates:
- ComponentSpec and DecompositionResult data validation.
- Missing image error handling.
- Decomposition of scenes into decoupled props and articulated character components.
- OBJ and PBR texture map generation per component.
"""

from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from backend.ai.component_decomposer import (
    ComponentSpec,
    DecompositionResult,
    decompose_scene_components,
)


def test_component_spec_model():
    """Verify ComponentSpec Pydantic model validation."""
    comp = ComponentSpec(
        name="Wing_L",
        role="wing_ventral",
        pivot_point=(-0.25, 0.40, 0.15),
        z_offset=0.10,
        mesh_path="/tmp/wing.obj",
        albedo_path="/tmp/wing_albedo.png",
        depth_path="/tmp/wing_depth.png",
        normal_path="/tmp/wing_normal.png",
        vertex_count=500,
        face_count=900,
        parent_bone="Wing_Shoulder_L",
        is_prop=False,
    )
    assert comp.name == "Wing_L"
    assert comp.is_prop is False
    assert comp.vertex_count == 500


def test_decompose_missing_image():
    """Verify graceful failure when input image is missing."""
    res = decompose_scene_components("missing_image.png", "/tmp/out")
    assert res.success is False
    assert "not found" in res.message


def test_decompose_synthetic_avian_scene(tmp_path: Path):
    """
    Test decomposition of a synthetic image with a red bird and dark branch on parchment.
    """
    img_arr = np.full((120, 120, 4), [248, 248, 242, 255], dtype=np.uint8)
    y, x = np.ogrid[:120, :120]

    # Draw dark brown branch along bottom diagonal
    branch = (y >= (0.6 * x + 40)) & (y <= (0.6 * x + 55))
    img_arr[branch] = [70, 50, 40, 255]

    # Draw red bird in center
    bird = ((x - 60) ** 2 + (y - 50) ** 2 <= 25 ** 2)
    img_arr[bird] = [210, 35, 35, 255]

    in_img = tmp_path / "synthetic_avian.png"
    Image.fromarray(img_arr).save(in_img)

    out_dir = tmp_path / "components"
    res = decompose_scene_components(str(in_img), str(out_dir), archetype="avian")

    assert res.success is True
    assert len(res.components) >= 2
    assert res.character_part_count >= 1

    # Verify component files exist on disk
    for c in res.components:
        assert Path(c.mesh_path).is_file()
        assert Path(c.albedo_path).is_file()
        assert Path(c.depth_path).is_file()
        assert Path(c.normal_path).is_file()
        assert c.vertex_count > 0
        assert c.face_count > 0

    # Verify physical depth stratification (no Z-layer inversion)
    comp_map = {c.name: c for c in res.components}
    if "Subject_Wing_Ventral" in comp_map and "Subject_Torso" in comp_map and "Subject_Wing_Dorsal" in comp_map:
        wing_v = comp_map["Subject_Wing_Ventral"]
        torso = comp_map["Subject_Torso"]
        wing_d = comp_map["Subject_Wing_Dorsal"]

        assert wing_v.z_offset > torso.z_offset, "Ventral wing must sit in front of torso on Z"
        assert wing_d.z_offset < torso.z_offset, "Dorsal wing must sit behind torso on Z"
        assert wing_v.pivot_point[2] > 0.0, "Ventral shoulder pivot must have positive depth offset"

        # Verify torso plumage texture integrity (non-zero variance and seamless inpainting)
        torso_img = np.array(Image.open(torso.albedo_path))
        assert torso_img.shape[2] == 4
        assert np.std(torso_img[:, :, :3]) > 0.0, "Torso albedo must contain non-zero textured plumage"


def test_decompose_bipedal_scene(tmp_path: Path):
    """
    Test decomposition of a bipedal character scene with Bipedal Depth Prior and PBR atlases.
    """
    # 120x60 figure on parchment background
    img_arr = np.full((120, 60, 4), [248, 248, 242, 255], dtype=np.uint8)
    y, x = np.ogrid[:120, :60]

    # Humanoid silhouette: Head (y 10..30, x 25..35), Torso (y 30..65, x 20..40), Legs (y 65..110)
    head = ((x - 30) ** 2 + (y - 20) ** 2 <= 10 ** 2)
    torso = (y >= 30) & (y <= 65) & (x >= 20) & (x <= 40)
    leg_l = (y >= 65) & (y <= 110) & (x >= 22) & (x <= 28)
    leg_r = (y >= 65) & (y <= 110) & (x >= 32) & (x <= 38)
    char_mask = head | torso | leg_l | leg_r
    img_arr[char_mask] = [40, 50, 70, 255]

    in_img = tmp_path / "synthetic_biped.png"
    Image.fromarray(img_arr).save(in_img)

    out_dir = tmp_path / "biped_components"
    res = decompose_scene_components(str(in_img), str(out_dir), archetype="bipedal")

    assert res.success is True
    assert len(res.components) >= 1
    assert res.character_part_count >= 1
    comp = res.components[0]
    assert comp.role == "humanoid"
    assert Path(comp.mesh_path).is_file()
    assert Path(comp.albedo_path).is_file()
    assert Path(comp.roughness_path).is_file()
    assert Path(comp.ao_path).is_file()
    assert comp.vertex_count > 0
    assert comp.face_count > 0

