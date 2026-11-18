from typing import Dict, Any, Optional
import subprocess
import os

class BlenderMcpClient:
    def __init__(self, blender_executable: str = r"E:\Blender\blender.exe"):
        self.blender_executable = blender_executable

    def execute_python_code(self, code: str, blend_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta un script de Blender en segundo plano o vía MCP.
        """
        # Modo fallback determinista por CLI de Blender
        tmp_script = os.path.join(os.path.dirname(__file__), "_tmp_exec.py")
        with open(tmp_script, "w", encoding="utf-8") as f:
            f.write(code)

        cmd = [self.blender_executable]
        if blend_file and os.path.exists(blend_file):
            cmd.append(blend_file)
        cmd.extend(["--background", "--python", tmp_script])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if os.path.exists(tmp_script):
                try: os.remove(tmp_script)
                except: pass
            return {
                "success": res.returncode == 0,
                "output": res.stdout,
                "error": res.stderr if res.returncode != 0 else None
            }
        except Exception as e:
            if os.path.exists(tmp_script):
                try: os.remove(tmp_script)
                except: pass
            return {"success": False, "error": str(e)}
