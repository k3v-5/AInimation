"""
Tests for Artifact, ArtifactLocation, and ArtifactManifest.
Verifies integrity checking, content hash verification, and dependency provenance graph.
UAF-81.0 Sections 22, 23, 24, 25, 26.
"""

import tempfile
import pytest
from pathlib import Path
from uaf.core.artifacts.artifact import Artifact
from uaf.core.artifacts.artifact_location import ArtifactLocation, StorageBackend
from uaf.core.artifacts.artifact_manifest import ArtifactManifest


def test_artifact_file_creation_and_integrity():
    with tempfile.TemporaryDirectory() as tmp:
        sample_file = Path(tmp) / "mesh_cube.obj"
        sample_file.write_bytes(b"v 0 0 0\nv 1 1 1\nf 1 2 3\n")

        artifact = Artifact.create_from_file(
            file_path=sample_file,
            artifact_id="art_cube",
            artifact_type="STATIC_MESH",
            asset_id="asset_cube",
            producer="test_suite",
        )

        assert artifact.size == sample_file.stat().st_size
        assert len(artifact.content_hash) == 64
        assert artifact.verify_integrity() is True


def test_artifact_tampered_content_fails_integrity():
    with tempfile.TemporaryDirectory() as tmp:
        sample_file = Path(tmp) / "mesh_tamper.obj"
        sample_file.write_bytes(b"original payload data")

        artifact = Artifact.create_from_file(
            file_path=sample_file,
            artifact_id="art_tamper",
            artifact_type="STATIC_MESH",
            asset_id="asset_tamper",
            producer="test_suite",
        )
        assert artifact.verify_integrity() is True

        # Tamper the underlying file
        sample_file.write_bytes(b"tampered corrupted payload")
        assert artifact.verify_integrity() is False


def test_artifact_manifest_provenance_and_dependencies():
    with tempfile.TemporaryDirectory() as tmp:
        f1 = Path(tmp) / "base_mesh.obj"
        f1.write_bytes(b"v 1 2 3")
        f2 = Path(tmp) / "lod1_mesh.obj"
        f2.write_bytes(b"v 1 2 3 lod1")

        art1 = Artifact.create_from_file(f1, "art_base", "MESH", "asset_tree", "producer")
        art2 = Artifact.create_from_file(f2, "art_lod1", "LOD", "asset_tree", "producer")

        manifest = ArtifactManifest(
            manifest_id="manifest_tree_01",
            asset_id="asset_tree",
            production_id="prod_tree",
            artifacts=[art1, art2],
            operations=["op_base_gen", "op_lod_gen"],
            depends_on=["material_bark"],
            derived_from=["raw_photogrammetry_scan"],
        )

        assert len(manifest.artifacts) == 2
        assert manifest.verify_all_artifacts() is True

        # Verify serialization roundtrip
        data = manifest.to_dict()
        reconstructed = ArtifactManifest.from_dict(data)

        assert reconstructed.manifest_id == "manifest_tree_01"
        assert len(reconstructed.artifacts) == 2
        assert reconstructed.depends_on == ["material_bark"]
        assert reconstructed.derived_from == ["raw_photogrammetry_scan"]
