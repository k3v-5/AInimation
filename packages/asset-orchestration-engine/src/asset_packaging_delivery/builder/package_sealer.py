import hashlib
import json
from typing import List
from ..core.package_schema import PackageFileEntry, PackageManifest

class PackageSealer:
    @classmethod
    def compute_content_hash(cls, files: List[PackageFileEntry]) -> str:
        # Deterministic hashing: sort file relative paths
        sorted_files = sorted(files, key=lambda f: f.relative_path)
        data = [{"rel_path": f.relative_path, "hash": f.hash_sha256, "size": f.size_bytes} for f in sorted_files]
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def seal_manifest(cls, manifest: PackageManifest) -> str:
        manifest.package_content_hash = cls.compute_content_hash(manifest.files)
        # Seal hash is hash of manifest itself
        manifest_dict = {
            "pkg_id": manifest.package_id,
            "asset_id": manifest.asset_id,
            "content_hash": manifest.package_content_hash,
            "version": manifest.package_version
        }
        return hashlib.sha256(json.dumps(manifest_dict, sort_keys=True).encode("utf-8")).hexdigest()
