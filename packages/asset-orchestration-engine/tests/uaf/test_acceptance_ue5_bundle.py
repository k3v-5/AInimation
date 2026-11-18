"""
Acceptance Test Suite for AOE Portable UE5 Bundle Exporter & Automated Ingestion Pipeline.
"""

import os
import json
import zipfile
import tempfile
import pytest
from pathlib import Path

from uaf.golden_slice.manifest.models import GoldenSliceManifest
from uaf.golden_slice.packaging.bundle_exporter import UE5BundleExporter
from uaf.golden_slice.cli import run_cli


def test_ue5_bundle_exporter_directory_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = UE5BundleExporter()
        manifest = GoldenSliceManifest(project_id="TestProject_Export")

        bundle_dir = os.path.join(tmpdir, "AOE_Bundle_Dir")
        result = exporter.create_bundle(manifest, output_path=bundle_dir, as_zip=False)

        assert result["success"] is True
        assert result["is_zip"] is False
        assert os.path.isdir(bundle_dir)

        # Check Plugins structure
        uplugin_file = os.path.join(bundle_dir, "Plugins", "UAFBridge", "UAFBridge.uplugin")
        assert os.path.isfile(uplugin_file)

        # Check Content/AOE structure
        manifest_file = os.path.join(bundle_dir, "Content", "AOE", "Manifests", "golden_slice_manifest.json")
        assert os.path.isfile(manifest_file)
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["project_id"] == "TestProject_Export"

        # Check Instructions
        readme_file = os.path.join(bundle_dir, "LEEME_INSTRUCCIONES.txt")
        assert os.path.isfile(readme_file)

        # Check Bundle Manifest Checksums
        b_manifest = os.path.join(bundle_dir, "bundle_manifest.json")
        assert os.path.isfile(b_manifest)
        with open(b_manifest, "r", encoding="utf-8") as f:
            b_data = json.load(f)
            assert "files" in b_data
            assert len(b_data["files"]) > 0


def test_ue5_bundle_exporter_zip_archive_and_checksum():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = UE5BundleExporter()
        manifest = GoldenSliceManifest(project_id="TestProject_Zip")

        zip_path = os.path.join(tmpdir, "AOE_UE5_Bundle.zip")
        result = exporter.create_bundle(manifest, output_path=zip_path, as_zip=True)

        assert result["success"] is True
        assert result["is_zip"] is True
        assert os.path.isfile(zip_path)
        assert zip_path.endswith(".zip")
        assert result["bundle_bytes"] > 0
        assert len(result["sha256"]) == 64

        # Validate ZIP contents
        with zipfile.ZipFile(zip_path, "r") as zf:
            namelist = zf.namelist()
            # Normalize slashes
            normalized_names = [n.replace("\\", "/") for n in namelist]

            assert any("Plugins/UAFBridge/UAFBridge.uplugin" in n for n in normalized_names)
            assert any("Content/AOE/Manifests/golden_slice_manifest.json" in n for n in normalized_names)
            assert any("LEEME_INSTRUCCIONES.txt" in n for n in normalized_names)
            assert any("bundle_manifest.json" in n for n in normalized_names)


def test_ue5_ingest_script_syntax_and_standalone_validation():
    # Import the ingestion script outside Unreal
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "ue5_plugin" / "UAFBridge" / "Content" / "Python" / "aoe_editor_ingest.py"
    assert script_path.is_file()

    # Load and execute module namespace
    namespace = {}
    with open(script_path, "r", encoding="utf-8") as f:
        code = compile(f.read(), str(script_path), "exec")
        exec(code, namespace)

    pipeline_cls = namespace.get("AOEUnrealIngestionPipeline")
    assert pipeline_cls is not None

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create manifest
        manifests_dir = os.path.join(tmpdir, "Manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        manifest_file = os.path.join(manifests_dir, "golden_slice_manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump({"project_name": "StandaloneTest", "world": {}, "player": {}}, f)

        pipeline = pipeline_cls(bundle_root_dir=tmpdir)
        loaded = pipeline.load_manifest()
        assert loaded["project_name"] == "StandaloneTest"

        # Standalone execution outside Unreal should return False gracefully without raising exceptions
        res = pipeline.run_pipeline()
        assert res is False


def test_init_unreal_syntax_and_registration():
    repo_root = Path(__file__).resolve().parents[2]
    init_script_path = repo_root / "ue5_plugin" / "UAFBridge" / "Content" / "Python" / "init_unreal.py"
    assert init_script_path.is_file()

    namespace = {}
    with open(init_script_path, "r", encoding="utf-8") as f:
        code = compile(f.read(), str(init_script_path), "exec")
        exec(code, namespace)

    register_fn = namespace.get("register_aoe_menus")
    assert callable(register_fn)
    # Outside Unreal, register_fn should execute and return without error
    register_fn()


def test_cli_export_bundle_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_zip = os.path.join(tmpdir, "CliBundle.zip")
        ret = run_cli(["export-bundle", "--output", out_zip])
        assert ret == 0
        assert os.path.isfile(out_zip)
