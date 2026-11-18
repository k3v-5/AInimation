"""standardize_mob_files.py
Encapsula la creación de malla y rig de cada uno de los 10 mobs en `def build_all(col=None):`
y traslada la limpieza de escena, cámara, render y guardado a `if __name__ == "__main__":`.
"""

import os, sys, re

blender_dir = r"E:\Darx_Proyect\Art\Blender"
files = [
    "darx_acosador.py",
    "darx_artillero.py",
    "darx_bastion.py",
    "darx_detonador.py",
    "darx_interferente.py",
    "darx_observador.py",
    "darx_portador.py",
    "darx_repulsor.py",
    "darx_robot.py",
    "darx_static_shadow.py"
]

def refactor_file(fname):
    fpath = os.path.join(blender_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the split point between build code and lighting/camera
    cam_match = re.search(r"(\n#\s*-*\n#\s*\d*\.?\s*LIGHTING & CAMERA.*)", content, re.DOTALL)
    if not cam_match:
        cam_match = re.search(r"(\nif scene\.world is None:.*)", content, re.DOTALL)
    if not cam_match:
        print(f"FAILED TO FIND CAMERA SPLIT IN {fname}")
        return False

    split_idx = cam_match.start()
    pre_cam = content[:split_idx]
    post_cam = content[split_idx:]

    # In pre_cam, find where the clean scene code starts:
    # # Clean Scene
    # bpy.ops.wm.read_factory_settings(use_empty=True)
    # scene = ...
    # col = dl.coll(COL_NAME)
    clean_match = re.search(r"(# Clean Scene.*?col = dl\.coll\(COL_NAME\)\n)", pre_cam, re.DOTALL)
    if not clean_match:
        print(f"FAILED TO FIND CLEAN SCENE IN {fname}")
        return False

    clean_start = clean_match.start()
    clean_end = clean_match.end()

    header = pre_cam[:clean_start]
    build_body = pre_cam[clean_end:]

    # Remove trailing newlines and make sure build_all returns (mesh_obj, arm_obj)
    # In build_body, indent all lines by 4 spaces
    indented_body_lines = []
    for line in build_body.splitlines():
        if line.strip():
            indented_body_lines.append("    " + line)
        else:
            indented_body_lines.append("")

    indented_body = "\n".join(indented_body_lines)

    # In indented_body, make sure col is passed or checked:
    # We will declare:
    # def build_all(col=None):
    #     if col is None:
    #         col = dl.coll(COL_NAME)
    # And at the end:
    #     return mesh_obj, arm_obj

    new_code = header.strip() + "\n\n"
    new_code += "def build_all(col=None):\n"
    new_code += "    if col is None:\n"
    new_code += "        col = dl.coll(COL_NAME)\n"
    new_code += indented_body + "\n"
    new_code += "    return mesh_obj, arm_obj\n\n"
    new_code += 'if __name__ == "__main__":\n'
    new_code += "    bpy.ops.wm.read_factory_settings(use_empty=True)\n"
    new_code += "    scene = bpy.context.scene\n"
    new_code += "    scene.render.resolution_x = 960\n"
    new_code += "    scene.render.resolution_y = 960\n"
    new_code += "    scene.render.film_transparent = False\n"
    new_code += "    col = dl.coll(COL_NAME)\n"
    new_code += "    mesh_obj, arm_obj = build_all(col)\n"

    # Now post_cam lines indented by 4 spaces
    indented_cam_lines = []
    for line in post_cam.splitlines():
        if line.strip():
            indented_cam_lines.append("    " + line)
        else:
            indented_cam_lines.append("")
    new_code += "\n".join(indented_cam_lines) + "\n"

    # Save refactored file
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"Refactored: {fname}")
    return True

if __name__ == "__main__":
    for f in files:
        refactor_file(f)
    print("ALL 10 FILES STANDARDIZED WITH build_all()!")
