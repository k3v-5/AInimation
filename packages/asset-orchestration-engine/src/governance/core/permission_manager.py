from enum import Enum
from typing import Set, List, Dict, Optional

class Permission(str, Enum):
    PROJECT_READ = "PROJECT_READ"
    PROJECT_WRITE = "PROJECT_WRITE"

    ASSET_READ = "ASSET_READ"
    ASSET_CREATE = "ASSET_CREATE"
    ASSET_WRITE = "ASSET_WRITE"
    ASSET_DELETE = "ASSET_DELETE"

    GEOMETRY_READ = "GEOMETRY_READ"
    GEOMETRY_CREATE = "GEOMETRY_CREATE"
    GEOMETRY_MODIFY = "GEOMETRY_MODIFY"
    GEOMETRY_DELETE = "GEOMETRY_DELETE"

    MATERIAL_READ = "MATERIAL_READ"
    MATERIAL_CREATE = "MATERIAL_CREATE"
    MATERIAL_MODIFY = "MATERIAL_MODIFY"
    MATERIAL_DELETE = "MATERIAL_DELETE"

    BLENDER_READ = "BLENDER_READ"
    BLENDER_EXECUTE = "BLENDER_EXECUTE"
    BLENDER_SCENE_MODIFY = "BLENDER_SCENE_MODIFY"

    REFERENCE_READ = "REFERENCE_READ"
    REFERENCE_ANALYZE = "REFERENCE_ANALYZE"

    VISUAL_EVALUATE = "VISUAL_EVALUATE"
    VISUAL_CORRECT = "VISUAL_CORRECT"

    EXPORT_ASSET = "EXPORT_ASSET"
    PACKAGE_ASSET = "PACKAGE_ASSET"

    JOB_READ = "JOB_READ"
    JOB_WRITE = "JOB_WRITE"
    JOB_CONTROL = "JOB_CONTROL"

    DIGITAL_TWIN_READ = "DIGITAL_TWIN_READ"
    DIGITAL_TWIN_WRITE = "DIGITAL_TWIN_WRITE"

    FILESYSTEM_READ = "FILESYSTEM_READ"
    FILESYSTEM_WRITE = "FILESYSTEM_WRITE"
    FILESYSTEM_DELETE = "FILESYSTEM_DELETE"

    PROCESS_EXECUTE = "PROCESS_EXECUTE"

class ResourceClassification(str, Enum):
    READ_ONLY = "READ_ONLY"
    PROTECTED = "PROTECTED"
    MODIFIABLE = "MODIFIABLE"
    GENERATED = "GENERATED"
    TEMPORARY = "TEMPORARY"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AuthorizationStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"

class PermissionManager:
    """Central permission registry with deny-by-default evaluation and destructive operation isolation."""
    
    DESTRUCTIVE_PERMISSIONS: Set[Permission] = {
        Permission.ASSET_DELETE,
        Permission.GEOMETRY_DELETE,
        Permission.MATERIAL_DELETE,
        Permission.FILESYSTEM_DELETE,
        Permission.PROJECT_WRITE,
        Permission.PROCESS_EXECUTE
    }

    @classmethod
    def is_destructive(cls, perm: Permission) -> bool:
        return perm in cls.DESTRUCTIVE_PERMISSIONS

    @classmethod
    def validate_permissions_subset(cls, granted: List[Permission], required: List[Permission]) -> bool:
        granted_set = set(granted)
        for req in required:
            if req not in granted_set:
                return False
        return True
