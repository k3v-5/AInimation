import os
import json
import subprocess
from typing import Dict, Any, Optional

class BlenderEvidenceCollector:
    """Extracts diagnostic evidence directly from a Blender process or .blend file."""
    
    @staticmethod
    def extract_scene_evidence(blend_file: str, blender_exe: str = r"E:\Blender\blender.exe") -> Dict[str, Any]:
        if not os.path.exists(blend_file) or not os.path.exists(blender_exe):
            return {"error": "Blender or file not found"}

        py_script = """
import bpy
import json

data = {
    "objects": [o.name for o in bpy.data.objects],
    "object_count": len(bpy.data.objects),
    "materials": [m.name for m in bpy.data.materials],
    "material_count": len(bpy.data.materials),
    "collections": [c.name for c in bpy.data.collections],
    "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
    "transforms": {o.name: [round(v, 4) for v in o.scale] for o in bpy.data.objects if o.type == 'MESH'}
}
print("---DIAGNOSTIC_JSON_START---")
print(json.dumps(data))
print("---DIAGNOSTIC_JSON_END---")
"""
        cmd = [blender_exe, "-b", blend_file, "--python-expr", py_script]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        stdout = res.stdout
        stderr = res.stderr

        if "---DIAGNOSTIC_JSON_START---" in stdout:
            try:
                part = stdout.split("---DIAGNOSTIC_JSON_START---")[1].split("---DIAGNOSTIC_JSON_END---")[0].strip()
                parsed = json.loads(part)
                parsed["returncode"] = res.returncode
                parsed["stderr"] = stderr
                return parsed
            except Exception as e:
                return {"parse_error": str(e), "stdout": stdout, "stderr": stderr}

        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": res.returncode
        }
