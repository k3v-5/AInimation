import os
import subprocess
from typing import Dict, Any, Optional
from .corrective_action import CorrectiveAction
from ..integration.governance_bridge import GovernanceBridge

class CorrectionExecutor:
    """Executes corrective actions in Blender or pipeline runtime under F72 Governance."""

    def __init__(self, gov_bridge: Optional[GovernanceBridge] = None):
        self.gov = gov_bridge or GovernanceBridge()

    def execute(
        self,
        action: CorrectiveAction,
        blend_file: str,
        blender_exe: str = r"E:\Blender\blender.exe",
        agent_id: str = "agent.geometry"
    ) -> Dict[str, Any]:
        # 1. Check F72 Governance
        authorized = True
        for cap in action.required_capabilities:
            if not self.gov.check_correction_permission(agent_id, cap):
                authorized = False
                break

        if not authorized:
            return {
                "success": False,
                "error": f"Governance denied: Agent '{agent_id}' lacks required capabilities {action.required_capabilities}",
                "status": "GOVERNANCE_DENIED"
            }

        # 2. Execute in Blender if blend_file exists
        if os.path.exists(blend_file) and os.path.exists(blender_exe):
            return self._execute_in_blender(action, blend_file, blender_exe)
        
        # Test synthetic execution
        return {
            "success": True,
            "action_type": action.action_type,
            "target": action.target,
            "simulated": True
        }

    def _execute_in_blender(self, action: CorrectiveAction, blend_file: str, blender_exe: str) -> Dict[str, Any]:
        act_type = action.action_type
        if act_type == "FIX_SCALE":
            py_expr = """
import bpy
for o in bpy.data.objects:
    if o.type == 'MESH':
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.select_set(False)
bpy.ops.wm.save_mainfile()
print("---CORRECTION_FIX_SCALE_SUCCESS---")
"""
        elif act_type == "REASSIGN_MATERIAL":
            py_expr = """
import bpy
mat = bpy.data.materials.get("M_Dark_Titanium")
if not mat:
    mat = bpy.data.materials.new(name="M_Dark_Titanium")
    mat.use_nodes = True

for o in bpy.data.objects:
    if o.type == 'MESH':
        if len(o.data.materials) == 0:
            o.data.materials.append(mat)
        else:
            o.data.materials[0] = mat
bpy.ops.wm.save_mainfile()
print("---CORRECTION_REASSIGN_MATERIAL_SUCCESS---")
"""
        else:
            py_expr = """
import bpy
bpy.ops.wm.save_mainfile()
print("---CORRECTION_GENERIC_SUCCESS---")
"""

        cmd = [blender_exe, "-b", blend_file, "--python-expr", py_expr]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return {
            "success": (res.returncode == 0 and "---CORRECTION_" in res.stdout),
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
