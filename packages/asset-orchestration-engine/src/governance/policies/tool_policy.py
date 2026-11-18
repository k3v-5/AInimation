from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..core.permission_manager import Permission, RiskLevel

@dataclass
class ToolDefinition:
    tool_id: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    required_permissions: List[Permission] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    side_effects: List[str] = field(default_factory=list)

class ToolRegistry:
    """Registry of authorized tools available to agents."""
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition):
        self._tools[tool.tool_id] = tool

    def get(self, tool_id: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_id)

    def _register_default_tools(self):
        defaults = [
            ToolDefinition("reference_analyzer", capabilities=["perception.analyze_reference"], required_permissions=[Permission.REFERENCE_READ]),
            ToolDefinition("vision_decomposer", capabilities=["perception.decompose_parts"], required_permissions=[Permission.REFERENCE_ANALYZE]),
            ToolDefinition("vas_compiler", capabilities=["design.compile_specification"], required_permissions=[Permission.PROJECT_READ]),
            ToolDefinition("strategy_planner", capabilities=["strategy.plan_modeling"], required_permissions=[Permission.PROJECT_READ]),
            ToolDefinition("mesh_generator", capabilities=["geometry.generate_mesh"], required_permissions=[Permission.GEOMETRY_CREATE, Permission.ASSET_WRITE], risk_level=RiskLevel.MEDIUM),
            ToolDefinition("bmesh_ops", capabilities=["geometry.generate_mesh"], required_permissions=[Permission.GEOMETRY_CREATE, Permission.ASSET_WRITE], risk_level=RiskLevel.MEDIUM),
            ToolDefinition("shader_builder", capabilities=["material.create_pbr"], required_permissions=[Permission.MATERIAL_CREATE, Permission.ASSET_WRITE], risk_level=RiskLevel.MEDIUM),
            ToolDefinition("blender_capability_api", capabilities=["blender.assemble_asset"], required_permissions=[Permission.BLENDER_EXECUTE, Permission.ASSET_WRITE], risk_level=RiskLevel.MEDIUM),
            ToolDefinition("viewport_renderer", capabilities=["blender.render_viewport"], required_permissions=[Permission.BLENDER_READ]),
            ToolDefinition("visual_evaluator", capabilities=["critic.evaluate_visuals"], required_permissions=[Permission.VISUAL_EVALUATE, Permission.ASSET_READ]),
            ToolDefinition("defect_clusterer", capabilities=["critic.detect_defects"], required_permissions=[Permission.VISUAL_EVALUATE]),
            ToolDefinition("topology_qa_scanner", capabilities=["qa.validate_geometry"], required_permissions=[Permission.ASSET_READ]),
            ToolDefinition("impact_analyzer", capabilities=["correction.apply_surgical_fix"], required_permissions=[Permission.GEOMETRY_MODIFY, Permission.ASSET_WRITE], risk_level=RiskLevel.MEDIUM),
            ToolDefinition("package_sealer", capabilities=["packaging.deliver_package"], required_permissions=[Permission.PACKAGE_ASSET, Permission.EXPORT_ASSET]),
            ToolDefinition("filesystem_deleter", capabilities=["filesystem.delete"], required_permissions=[Permission.FILESYSTEM_DELETE], risk_level=RiskLevel.CRITICAL),
            ToolDefinition("process_runner", capabilities=["process.execute"], required_permissions=[Permission.PROCESS_EXECUTE], risk_level=RiskLevel.CRITICAL)
        ]
        for t in defaults:
            self.register(t)
