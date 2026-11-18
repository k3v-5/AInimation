from typing import Dict, Any, List, Optional
from ..core.agent_types import ToolCategory, PermissionLevel, AgentErrorCode
from ..core.agent_schema import ToolDefinition

class ToolRegistry:
    FORBIDDEN_TOOLS = {"execute_python", "raw_bpy_eval", "direct_shell_exec"}

    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. Discovery
        self.register(ToolDefinition("get_capabilities", ToolCategory.DISCOVERY, PermissionLevel.READ, "List available engine capabilities"))
        self.register(ToolDefinition("list_asset_types", ToolCategory.DISCOVERY, PermissionLevel.READ, "List supported asset archetypes"))
        self.register(ToolDefinition("list_generators", ToolCategory.DISCOVERY, PermissionLevel.READ, "List registered procedural generators"))
        self.register(ToolDefinition("get_project_rules", ToolCategory.DISCOVERY, PermissionLevel.READ, "Get active engine and project constraints"))

        # 2. Planning
        self.register(ToolDefinition("create_plan", ToolCategory.PLANNING, PermissionLevel.PLAN, "Build execution plan for asset generation/modification"))
        self.register(ToolDefinition("validate_plan", ToolCategory.PLANNING, PermissionLevel.PLAN, "Validate plan constraints and fresh state hash"))
        self.register(ToolDefinition("explain_plan", ToolCategory.PLANNING, PermissionLevel.PLAN, "Provide human/AI explainability for plan operations"))

        # 3. Asset
        self.register(ToolDefinition("create_asset", ToolCategory.ASSET, PermissionLevel.MODIFY, "Create new parametric asset with typed parameters"))
        self.register(ToolDefinition("update_asset", ToolCategory.ASSET, PermissionLevel.MODIFY, "Update specific asset parameters with surgical regeneration"))
        self.register(ToolDefinition("delete_asset", ToolCategory.ASSET, PermissionLevel.DELETE, "Delete managed asset (Requires Approval)"))

        # 4. Inspection
        self.register(ToolDefinition("inspect_asset", ToolCategory.INSPECTION, PermissionLevel.READ, "Inspect focused asset state without scene clutter"))
        self.register(ToolDefinition("inspect_component", ToolCategory.INSPECTION, PermissionLevel.READ, "Inspect specific component parameters and status"))

        # 5. Validation & Critic
        self.register(ToolDefinition("validate_asset", ToolCategory.VALIDATION, PermissionLevel.READ, "Run structural and geometric validation on asset"))
        self.register(ToolDefinition("run_visual_critic", ToolCategory.VALIDATION, PermissionLevel.READ, "Run quantitative visual critic against reference image"))

        # 6. Correction
        self.register(ToolDefinition("suggest_corrections", ToolCategory.CORRECTION, PermissionLevel.PLAN, "Propose parameter changes from critic diagnosis"))
        self.register(ToolDefinition("apply_correction", ToolCategory.CORRECTION, PermissionLevel.MODIFY, "Apply bounded parameter correction to asset"))

        # 7. Execution
        self.register(ToolDefinition("execute_plan", ToolCategory.EXECUTION, PermissionLevel.MODIFY, "Execute validated plan through Gateway"))

        # 8. Recovery
        self.register(ToolDefinition("get_operation_status", ToolCategory.RECOVERY, PermissionLevel.READ, "Check status of long running operation"))
        self.register(ToolDefinition("cancel_operation", ToolCategory.RECOVERY, PermissionLevel.MODIFY, "Cancel ongoing asynchronous operation"))

        # 9. Export
        self.register(ToolDefinition("export_asset", ToolCategory.EXPORT, PermissionLevel.EXPORT, "Export asset to configured Unreal Engine path"))

    def register(self, tool: ToolDefinition):
        if tool.name in self.FORBIDDEN_TOOLS:
            raise PermissionError(f"SECURITY_VIOLATION: Tool '{tool.name}' is forbidden by Agent Sandboxing Policy.")
        self.tools[tool.name] = tool

    def validate_tool_access(self, tool_name: str, agent_permission: PermissionLevel):
        if tool_name in self.FORBIDDEN_TOOLS:
            raise PermissionError(f"SECURITY_VIOLATION: Execution of '{tool_name}' is forbidden.")
        if tool_name not in self.tools:
            raise ValueError(f"UNKNOWN_TOOL: Tool '{tool_name}' is not registered.")
        
        tool = self.tools[tool_name]
        # Validar permisos
        perm_hierarchy = [PermissionLevel.READ, PermissionLevel.PLAN, PermissionLevel.MODIFY, PermissionLevel.DELETE, PermissionLevel.EXPORT, PermissionLevel.ADMIN]
        req_idx = perm_hierarchy.index(tool.permission_level)
        agent_idx = perm_hierarchy.index(agent_permission)
        if agent_idx < req_idx:
            raise PermissionError(f"PERMISSION_DENIED: Agent permission [{agent_permission.value}] is insufficient for tool '{tool_name}' (requires [{tool.permission_level.value}]).")
