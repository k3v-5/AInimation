"""
SpecificationMigrator supports schema version detection and backward-compatible migration.
UAF-81.1 Sections 55, 56.
"""

from typing import Dict, Any, Tuple
from ...core.specification.asset_specification import AssetSpecification


class SpecificationMigrator:
    """
    Detects version of raw specification payloads and migrates legacy schema structures.
    """
    CURRENT_VERSION = "1.0.0"

    @classmethod
    def detect_version(cls, data: Dict[str, Any]) -> str:
        return data.get("schema_version", "0.9.0")

    @classmethod
    def migrate(cls, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
        Migrates legacy specification dictionary to current schema version.
        Returns (migrated_dict, was_migrated).
        """
        version = cls.detect_version(data)
        if version == cls.CURRENT_VERSION:
            return dict(data), False

        migrated = dict(data)

        # Legacy 0.9.0 migrations
        if version in ["0.9.0", "legacy"]:
            if "spec_id" in migrated and "identity" not in migrated:
                migrated["identity"] = {
                    "asset_id": migrated["spec_id"],
                    "asset_type": migrated.get("type", "PROP"),
                    "namespace": "default",
                    "version": "1.0.0",
                }
            if "params" in migrated and "parameters" not in migrated:
                migrated["parameters"] = migrated.pop("params")

        migrated["schema_version"] = cls.CURRENT_VERSION
        return migrated, True
