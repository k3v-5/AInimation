"""
Empirical Stress and Adversarial Challenge Test Suite for Milestone 2 (Unreal Engine 5 Bridge).

Written by Challenger Agent: challenger_m2_2.

Focus Areas:
1. AST-level Zero-Any verification across all files in `backend/ue5/`.
2. PBR material boundary conditions: out-of-bounds scalar inputs (<0, >1.0, NaN, Inf),
   value clamping, dict coercion, and texture path resolution.
3. Lumen lighting rig presets: 5 presets, intensity calibrations, scaling boundaries,
   and unknown preset fallbacks.
4. Dynamic asset import error handling on malformed/corrupt GLB files and non-existent paths.
"""

from __future__ import annotations

import ast
import glob
from pathlib import Path
from typing import Dict, List, Optional
import pytest
from pydantic import ValidationError

from backend.core.models import ColorRGB, PBRTextureSet, Rotator3D, Vector3D
from backend.ue5.client import UE5RestClient
from backend.ue5.lighting import (
    LightActorConfig,
    LightingRig,
    LumenLightingSetup,
    setup_lumen_lighting,
)
from backend.ue5.materials import (
    MaterialManager,
    PBRMaterialInstance,
    create_pbr_material,
)
from backend.ue5.mock_server import UE5MockServer
from tests.e2e.fixtures.synthetic_mesh import create_corrupt_glb, create_minimal_glb


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def challenge_mock_server() -> UE5MockServer:
    """Run an isolated UE5MockServer instance for challenger tests on dedicated ports."""
    server = UE5MockServer(host="127.0.0.1", port=30070, ws_port=30080)
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="module")
def challenge_client(challenge_mock_server: UE5MockServer) -> UE5RestClient:
    """Provide a UE5RestClient connected to the running challenge mock server."""
    return UE5RestClient(host=challenge_mock_server.host, port=challenge_mock_server.port)


# ---------------------------------------------------------------------------
# 1. AST-Level Zero-Any Compliance Verification
# ---------------------------------------------------------------------------

class TestASTZeroAnyStrict:
    """Rigorous AST-level static analysis checking all python files in backend/ue5/ for Any."""

    def test_ast_zero_any_across_backend_ue5(self) -> None:
        ue5_dir = Path("backend/ue5")
        py_files = sorted(list(ue5_dir.glob("*.py")))
        assert len(py_files) >= 6, f"Expected at least 6 files in backend/ue5, found {len(py_files)}"

        violations: List[str] = []

        class AnyDetector(ast.NodeVisitor):
            def __init__(self, filename: str) -> None:
                self.filename = filename

            def visit_Import(self, node: ast.Import) -> None:
                for alias in node.names:
                    if alias.name == "Any" or alias.name.endswith(".Any"):
                        violations.append(f"{self.filename}:{node.lineno} - ast.Import of '{alias.name}'")
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
                if node.module in ("typing", "typing_extensions"):
                    for alias in node.names:
                        if alias.name == "Any":
                            violations.append(f"{self.filename}:{node.lineno} - ast.ImportFrom 'Any' from {node.module}")
                self.generic_visit(node)

            def visit_Name(self, node: ast.Name) -> None:
                if node.id == "Any":
                    violations.append(f"{self.filename}:{node.lineno} - ast.Name 'Any' used in expression or type annotation")
                self.generic_visit(node)

            def visit_Constant(self, node: ast.Constant) -> None:
                if isinstance(node.value, str) and node.value.strip() == "Any":
                    violations.append(f"{self.filename}:{node.lineno} - ast.Constant 'Any' string annotation")
                self.generic_visit(node)

        for py_file in py_files:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
            AnyDetector(py_file.name).visit(tree)

        assert len(violations) == 0, (
            f"Zero-Any policy violated! Found {len(violations)} occurrences of 'Any' in backend/ue5/:\n"
            + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# 2. PBR Material Boundary Conditions & Clamping
# ---------------------------------------------------------------------------

class TestPBRMaterialBoundaries:
    """Stress-tests PBR material parameter bounds, value clamping, and texture resolution."""

    @pytest.mark.parametrize("bad_roughness", [-1.0, -0.0001, 1.0001, 2.0, float("nan"), float("inf"), float("-inf")])
    def test_pbr_material_instance_rejects_out_of_bounds_roughness(self, bad_roughness: float) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="M_BadRoughness", roughness=bad_roughness)

    @pytest.mark.parametrize("bad_metallic", [-1.0, -0.0001, 1.0001, 2.0, float("nan"), float("inf"), float("-inf")])
    def test_pbr_material_instance_rejects_out_of_bounds_metallic(self, bad_metallic: float) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="M_BadMetallic", metallic=bad_metallic)

    @pytest.mark.parametrize("bad_specular", [-1.0, -0.0001, 1.0001, 2.0, float("nan"), float("inf"), float("-inf")])
    def test_pbr_material_instance_rejects_out_of_bounds_specular(self, bad_specular: float) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="M_BadSpecular", specular=bad_specular)

    @pytest.mark.parametrize("bad_emissive_intensity", [-10.0, -0.001, float("-inf")])
    def test_pbr_material_instance_rejects_negative_emissive_intensity(self, bad_emissive_intensity: float) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="M_BadEmissive", emissive_intensity=bad_emissive_intensity)

    def test_pbr_material_instance_nominal_boundaries(self) -> None:
        mat_min = PBRMaterialInstance(material_name="M_Min", roughness=0.0, metallic=0.0, specular=0.0, emissive_intensity=0.0)
        assert mat_min.roughness == 0.0
        assert mat_min.metallic == 0.0
        assert mat_min.specular == 0.0

        mat_max = PBRMaterialInstance(material_name="M_Max", roughness=1.0, metallic=1.0, specular=1.0, emissive_intensity=5000.0)
        assert mat_max.roughness == 1.0
        assert mat_max.metallic == 1.0
        assert mat_max.specular == 1.0
        assert mat_max.emissive_intensity == 5000.0

    def test_material_manager_robust_clamping(self) -> None:
        mgr = MaterialManager()
        mat_neg = mgr.create_material(
            name="M_ClampedNeg",
            roughness=-999.0,
            metallic=-10.0,
            specular=-0.5,
        )
        assert mat_neg.roughness == 0.0
        assert mat_neg.metallic == 0.0
        assert mat_neg.specular == 0.0

        mat_pos = mgr.create_material(
            name="M_ClampedPos",
            roughness=999.0,
            metallic=10.0,
            specular=1.5,
        )
        assert mat_pos.roughness == 1.0
        assert mat_pos.metallic == 1.0
        assert mat_pos.specular == 1.0

    def test_create_pbr_material_facade_strict_dict_coercion(self) -> None:
        with pytest.raises(ValidationError):
            create_pbr_material(
                name="M_InvalidExtra",
                base_color={"r": 0.5, "g": 0.5, "b": 0.5, "alpha": 1.0},
            )

        with pytest.raises(ValidationError):
            create_pbr_material(
                name="M_InvalidColorRange",
                base_color={"r": -0.2, "g": 1.5, "b": 0.5},
            )

        with pytest.raises(ValidationError):
            create_pbr_material(
                name="M_InvalidTexturesExtra",
                textures={"albedo_path": "/tmp/a.png", "unknown_slot": "/tmp/b.png"},
            )

    def test_texture_path_resolution_and_parameter_serialization(self) -> None:
        textures = PBRTextureSet(
            albedo_path="/Game/Textures/T_Albedo_4K.png",
            normal_path="",
            roughness_path="/Game/Textures/T_Roughness.png",
            metallic_path=None,
            emissive_path="   ",
        )
        mat = create_pbr_material(
            name="M_Serialized",
            base_color=ColorRGB(r=0.9, g=0.8, b=0.7),
            roughness=0.35,
            metallic=0.85,
            specular=0.5,
            textures=textures,
        )
        params = mat.to_ue5_parameters()

        assert params["Roughness"] == 0.35
        assert params["Metallic"] == 0.85
        assert params["Specular"] == 0.5

        assert params.get("AlbedoMap") == "/Game/Textures/T_Albedo_4K.png"
        assert params.get("RoughnessMap") == "/Game/Textures/T_Roughness.png"
        assert "NormalMap" not in params
        assert "MetallicMap" not in params

        base_color_dict = params.get("BaseColor")
        assert isinstance(base_color_dict, dict)
        assert base_color_dict["R"] == 0.9
        assert base_color_dict["G"] == 0.8
        assert base_color_dict["B"] == 0.7
        assert base_color_dict["A"] == 1.0


# ---------------------------------------------------------------------------
# 3. Lumen Lighting Rig Presets & Fallbacks
# ---------------------------------------------------------------------------

class TestLumenLightingRigStress:
    """Stress-tests Lumen lighting preset resolutions, boundary scaling, and fallbacks."""

    def test_all_5_presets_unique_and_calibrated(self) -> None:
        preset_names = [
            "studio_3point",
            "cyberpunk_neon",
            "dramatic",
            "outdoor_sunlight",
            "night_moonlight",
        ]
        setups: Dict[str, LumenLightingSetup] = {}
        for p in preset_names:
            setup = setup_lumen_lighting(p)
            assert setup.preset_name == p
            assert len(setup.lights) >= 2
            assert setup.lumen_global_illumination is True
            assert setup.lumen_reflections is True
            assert setup.indirect_lighting_intensity >= 1.0
            setups[p] = setup

        sun_light = next(l for l in setups["outdoor_sunlight"].lights if l.name == "Directional_Sun")
        assert sun_light.intensity == 75000.0
        assert sun_light.light_type == "Directional"

        moon_light = next(l for l in setups["night_moonlight"].lights if l.name == "Directional_Moon")
        assert moon_light.intensity == 1500.0
        assert moon_light.temperature_kelvin == 8500.0

        cyan_light = next(l for l in setups["cyberpunk_neon"].lights if l.name == "Key_NeonCyan")
        assert cyan_light.intensity == 8000.0
        assert cyan_light.color.b == 1.0

        dramatic_key = next(l for l in setups["dramatic"].lights if l.name == "Key_Chiaroscuro")
        assert dramatic_key.intensity == 15000.0

    @pytest.mark.parametrize("unknown_preset", [
        "unknown_preset",
        "",
        "   ",
        "random_rig_12345",
        "CUSTOM_LIGHTING",
        "!@#$%^&*",
        "123456789",
    ])
    def test_unknown_preset_fallback_to_studio_3point(self, unknown_preset: str) -> None:
        setup = setup_lumen_lighting(unknown_preset)
        assert setup.preset_name == "studio_3point"
        assert len(setup.lights) == 4
        light_names = [l.name for l in setup.lights]
        assert "Key_Light" in light_names
        assert "Fill_Light" in light_names
        assert "Rim_Backlight" in light_names
        assert "Sky_Ambient" in light_names

    @pytest.mark.parametrize("preset_input,expected_preset", [
        ("  CYBERPUNK_NEON  ", "cyberpunk_neon"),
        ("neon_lights", "cyberpunk_neon"),
        ("DRAMATIC_STAGE", "dramatic"),
        ("chiaroscuro_noir", "dramatic"),
        ("OUTDOOR_SUNLIGHT", "outdoor_sunlight"),
        ("bright_sunlight", "outdoor_sunlight"),
        ("NIGHT_MOONLIGHT", "night_moonlight"),
        ("moonlight_sky", "night_moonlight"),
        ("night_sky", "night_moonlight"),
        ("STUDIO_3POINT", "studio_3point"),
    ])
    def test_preset_case_and_substring_matching(self, preset_input: str, expected_preset: str) -> None:
        setup = setup_lumen_lighting(preset_input)
        assert setup.preset_name == expected_preset

    def test_light_actor_config_intensity_boundary(self) -> None:
        zero_light = LightActorConfig(name="Off_Light", light_type="Point", intensity=0.0)
        assert zero_light.intensity == 0.0

        high_light = LightActorConfig(name="Flash_Light", light_type="Directional", intensity=1000000.0)
        assert high_light.intensity == 1000000.0


# ---------------------------------------------------------------------------
# 4. Dynamic Asset Import Error Handling & Adversarial Challenge
# ---------------------------------------------------------------------------

class TestDynamicAssetImportErrorHandling:
    """Stress-tests asset import error paths: missing files, empty paths, and corrupt GLB containers."""

    def test_import_asset_non_existent_path(self, challenge_client: UE5RestClient) -> None:
        res = challenge_client.import_asset("/does/not/exist/mesh.glb")
        assert res.get("Success") is False
        assert "does not exist" in str(res.get("Error", ""))

    def test_import_asset_valid_glb_success(self, challenge_client: UE5RestClient, tmp_path: Path) -> None:
        valid_glb = create_minimal_glb(tmp_path / "valid_model.glb", mesh_name="ValidMesh")
        assert valid_glb.exists()
        res = challenge_client.import_asset(str(valid_glb), "/Game/Imported/Models")
        assert res.get("Success") is True
        assert "/Game/Imported/Models/valid_model" in str(res.get("AssetPath", ""))

    def test_mock_server_direct_call_missing_source_path(self, challenge_mock_server: UE5MockServer) -> None:
        res = challenge_mock_server.state.call_function(
            object_path="/Script/UnrealEd.Default__EditorAssetLibrary",
            function_name="ImportAsset",
            parameters={"SourcePath": "/path/that/does/not/exist/model.glb"},
        )
        assert res.get("Success") is False
        assert "Source asset not found" in str(res.get("Error", ""))

    def test_import_asset_empty_string_path(self, challenge_client: UE5RestClient) -> None:
        res = challenge_client.import_asset("")
        assert res.get("Success") is False

    def test_challenge_directory_path_rejected(self, challenge_client: UE5RestClient, tmp_path: Path) -> None:
        """
        CHALLENGE: Directories must NOT be imported as 3D asset meshes.
        import_asset(str(tmp_path)) must return Success: False.
        """
        dir_path = tmp_path / "some_folder"
        dir_path.mkdir(parents=True, exist_ok=True)
        res = challenge_client.import_asset(str(dir_path))
        assert res.get("Success") is False, f"Directory import unexpectedly succeeded: {res}"

    def test_challenge_corrupt_glb_container_handling(self, challenge_client: UE5RestClient, tmp_path: Path) -> None:
        """
        CHALLENGE: Malformed or corrupt GLB containers (0-byte, invalid magic, truncated)
        must return structured error responses (Success=False) instead of fictitious success.
        """
        # 1. Zero-byte empty file with .glb extension
        empty_glb = tmp_path / "empty_corrupt.glb"
        empty_glb.write_bytes(b"")

        # 2. Corrupt GLB with invalid magic bytes
        bad_magic_glb = tmp_path / "bad_magic.glb"
        bad_magic_glb.write_bytes(b"NOT_A_GLTF_BINARY_FILE_GARBAGE")

        # 3. Truncated GLB via create_corrupt_glb
        truncated_glb = create_corrupt_glb(tmp_path / "truncated.glb")

        res_empty = challenge_client.import_asset(str(empty_glb))
        res_bad_magic = challenge_client.import_asset(str(bad_magic_glb))
        res_truncated = challenge_client.import_asset(str(truncated_glb))

        failures: List[str] = []
        if res_empty.get("Success") is True:
            failures.append(f"0-byte GLB returned Success=True ({res_empty.get('AssetPath')})")
        if res_bad_magic.get("Success") is True:
            failures.append(f"Bad magic GLB returned Success=True ({res_bad_magic.get('AssetPath')})")
        if res_truncated.get("Success") is True:
            failures.append(f"Truncated GLB returned Success=True ({res_truncated.get('AssetPath')})")

        assert len(failures) == 0, (
            "BUG CONFIRMED: UE5 asset importer lacks GLB binary container integrity validation!\n"
            + "\n".join(failures)
        )
