import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from ..core.failure_types import FailureType, FailureSeverity, FailureStatus
from ..core.failure_models import FailureRecord

class BlenderFailureDetector:
    """Specialized detector evaluating real Blender execution, scene state, and logs."""

    @staticmethod
    def inspect_scene(blend_file: str, blender_exe: str = r"E:\Blender\blender.exe") -> Dict[str, Any]:
        if not os.path.exists(blend_file) or not os.path.exists(blender_exe):
            return {"error": "Blender binary or file not found"}

        py_expr = """
import bpy
import json

objects = [o.name for o in bpy.data.objects]
meshes = [m.name for m in bpy.data.meshes]
materials = [m.name for m in bpy.data.materials]
collections = [c.name for c in bpy.data.collections]

scales = {o.name: list(o.scale) for o in bpy.data.objects if o.type == 'MESH'}
has_scale_error = any(s[0] != s[1] or s[1] != s[2] or any(v != 1.0 for v in s) for s in scales.values())

data = {
    "objects": objects,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "material_count": len(materials),
    "materials": materials,
    "collections": collections,
    "has_scale_error": has_scale_error,
    "scales": scales
}
print("---BLENDER_DETECTION_JSON---")
print(json.dumps(data))
print("---BLENDER_DETECTION_END---")
"""
        cmd = [blender_exe, "-b", blend_file, "--python-expr", py_expr]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        
        if "---BLENDER_DETECTION_JSON---" in res.stdout:
            try:
                raw = res.stdout.split("---BLENDER_DETECTION_JSON---")[1].split("---BLENDER_DETECTION_END---")[0].strip()
                parsed = json.loads(raw)
                parsed["returncode"] = res.returncode
                return parsed
            except Exception as e:
                return {"error": str(e), "stdout": res.stdout, "stderr": res.stderr}

        return {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
