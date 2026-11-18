from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..core.permission_manager import Permission, RiskLevel

@dataclass
class CapabilityDefinition:
    capability_id: str
    version: str = "1.0.0"
    description: str = ""
    required_permissions: List[Permission] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    rollback_supported: bool = True
    idempotent: bool = True

class CapabilityRegistry:
    """Catalog of registered system capabilities and their permission/risk requirements."""
    def __init__(self):
        self._capabilities: Dict[str, CapabilityDefinition] = {}
        self._register_default_capabilities()

    def register(self, cap: CapabilityDefinition):
        self._capabilities[cap.capability_id] = cap

    def get(self, capability_id: str) -> Optional[CapabilityDefinition]:
        return self._capabilities.get(capability_id)

    def _register_default_capabilities(self):
        defaults = [
            CapabilityDefinition("perception.analyze_reference", required_permissions=[Permission.REFERENCE_READ, Permission.REFERENCE_ANALYZE], risk_level=RiskLevel.LOW),
            CapabilityDefinition("perception.decompose_parts", required_permissions=[Permission.REFERENCE_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("design.compile_specification", required_permissions=[Permission.PROJECT_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("strategy.plan_modeling", required_permissions=[Permission.PROJECT_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("geometry.generate_mesh", required_permissions=[Permission.GEOMETRY_CREATE, Permission.ASSET_WRITE], side_effects=["ASSET_MODIFY"], risk_level=RiskLevel.MEDIUM),
            CapabilityDefinition("material.create_pbr", required_permissions=[Permission.MATERIAL_CREATE, Permission.ASSET_WRITE], side_effects=["ASSET_MODIFY"], risk_level=RiskLevel.MEDIUM),
            CapabilityDefinition("blender.assemble_asset", required_permissions=[Permission.BLENDER_EXECUTE, Permission.BLENDER_SCENE_MODIFY, Permission.ASSET_WRITE], side_effects=["BLENDER_SCENE_MODIFY"], risk_level=RiskLevel.MEDIUM),
            CapabilityDefinition("blender.render_viewport", required_permissions=[Permission.BLENDER_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("critic.evaluate_visuals", required_permissions=[Permission.VISUAL_EVALUATE, Permission.ASSET_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("critic.detect_defects", required_permissions=[Permission.VISUAL_EVALUATE], risk_level=RiskLevel.LOW),
            CapabilityDefinition("qa.validate_geometry", required_permissions=[Permission.ASSET_READ], risk_level=RiskLevel.LOW),
            CapabilityDefinition("correction.apply_surgical_fix", required_permissions=[Permission.GEOMETRY_MODIFY, Permission.ASSET_WRITE], side_effects=["ASSET_MODIFY"], risk_level=RiskLevel.MEDIUM),
            CapabilityDefinition("packaging.deliver_package", required_permissions=[Permission.PACKAGE_ASSET, Permission.EXPORT_ASSET], risk_level=RiskLevel.LOW),
            CapabilityDefinition("asset.delete", required_permissions=[Permission.ASSET_DELETE], side_effects=["ASSET_DELETED"], risk_level=RiskLevel.HIGH),
            CapabilityDefinition("filesystem.delete", required_permissions=[Permission.FILESYSTEM_DELETE], side_effects=["FILES_DELETED"], risk_level=RiskLevel.CRITICAL),
            CapabilityDefinition("process.execute", required_permissions=[Permission.PROCESS_EXECUTE], risk_level=RiskLevel.CRITICAL)
        ]
        for d in defaults:
            self.register(d)
