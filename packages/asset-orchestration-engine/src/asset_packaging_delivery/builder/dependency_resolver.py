from typing import Dict, Any, List
from ..core.package_types import DependencyState
from ..core.package_schema import PackageDependency

class DependencyResolver:
    @classmethod
    def resolve_dependencies(
        cls,
        ready_asset: Any, # F68 GameEngineReadyAsset
        context: Dict[str, Any]
    ) -> List[PackageDependency]:
        deps: List[PackageDependency] = []
        asset_id = getattr(ready_asset, "asset_id", "asset")

        # 1. Mesh Dependency
        deps.append(PackageDependency(
            dependency_id=f"DEP_{asset_id}_mesh",
            source=f"Meshes/{asset_id}.fbx",
            dep_type="STATIC_MESH",
            required=True,
            resolved_path=f"Meshes/{asset_id}.fbx",
            state=DependencyState.RESOLVED,
            hash_sha256=f"HASH_MESH_{asset_id}"
        ))

        # 2. Material Dependency
        deps.append(PackageDependency(
            dependency_id=f"DEP_{asset_id}_mat",
            source=f"Materials/M_{asset_id}.uasset",
            dep_type="MATERIAL",
            required=True,
            resolved_path=f"Materials/M_{asset_id}.uasset",
            state=DependencyState.RESOLVED,
            hash_sha256=f"HASH_MAT_{asset_id}"
        ))

        # 3. Collision Dependency
        deps.append(PackageDependency(
            dependency_id=f"DEP_{asset_id}_collision",
            source=f"Collision/UCX_{asset_id}.fbx",
            dep_type="COLLISION",
            required=False,
            resolved_path=f"Collision/UCX_{asset_id}.fbx",
            state=DependencyState.RESOLVED,
            hash_sha256=f"HASH_COL_{asset_id}"
        ))

        # Check for simulated missing required dependency
        if context.get("force_missing_required_dependency", False):
            deps.append(PackageDependency(
                dependency_id="DEP_MISSING_REQUIRED",
                source="Textures/T_Missing.png",
                dep_type="TEXTURE",
                required=True,
                resolved_path="",
                state=DependencyState.MISSING
            ))

        return deps
