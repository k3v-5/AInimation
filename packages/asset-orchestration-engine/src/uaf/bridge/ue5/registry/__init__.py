"""Object and asset registries and Unreal Engine path mappings."""

from uaf.bridge.ue5.registry.objects import (
    UE5ObjectEntry,
    UE5ObjectRegistry,
)
from uaf.bridge.ue5.registry.assets import (
    UE5AssetEntry,
    UE5AssetRegistry,
)
from uaf.bridge.ue5.registry.mappings import (
    PathSecurityError,
    PREFIX_MAP,
    sanitize_name,
    generate_asset_name,
    resolve_package_path,
)

__all__ = [
    "UE5ObjectEntry",
    "UE5ObjectRegistry",
    "UE5AssetEntry",
    "UE5AssetRegistry",
    "PathSecurityError",
    "PREFIX_MAP",
    "sanitize_name",
    "generate_asset_name",
    "resolve_package_path",
]
