from typing import Dict, Any, Callable
from ..core.amsl_schema import AssetSpecification

class SchemaRegistry:
    def __init__(self):
        self.registered_versions = {"1.0.0", "1.1.0"}
        self.migrations: Dict[str, Callable] = {}

    def register_migration(self, from_ver: str, to_ver: str, handler: Callable):
        self.migrations[f"{from_ver}->{to_ver}"] = handler

    def migrate(self, spec: AssetSpecification, target_ver: str) -> AssetSpecification:
        if spec.schema_version == target_ver:
            return spec

        key = f"{spec.schema_version}->{target_ver}"
        if key in self.migrations:
            return self.migrations[key](spec)

        spec.schema_version = target_ver
        return spec
