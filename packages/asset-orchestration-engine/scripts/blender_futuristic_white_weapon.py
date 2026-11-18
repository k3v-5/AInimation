import bpy
import bmesh
import math
from mathutils import Matrix, Vector
import os
import sys
import argparse

def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-file", type=str, default="")
    parser.add_argument("--preview-output", type=str, default="")
    return parser.parse_args(argv)

def get_or_create_collection(name="AOE_Generated"):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def create_pbr_material(name, base_color=(0.90, 0.90, 0.92, 1.0), metallic=0.1, roughness=0.22, emission_color=None, emission_strength=0.0):
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color and emission_strength > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_color
    return mat

def create_mesh_object(name, col, build_fn):
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        mesh = obj.data
        bm = bmesh.new()
        build_fn(bm)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        return obj
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    build_fn(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

# -------------------------------------------------------------
# GEOMETRY BUILDERS WITH FUTURISTIC SLEEK WHITE & ANGULAR DESIGN
# -------------------------------------------------------------

def build_futuristic_receiver(bm):
    # Main White Ceramic Body: Sleek angular receiver
    mat_body = Matrix.Translation((0.10, 0, 0.03)) @ Matrix.Diagonal((0.34, 0.044, 0.082, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_body)

    # Upper Picatinny / Energy Rail
    mat_rail = Matrix.Translation((0.10, 0, 0.076)) @ Matrix.Diagonal((0.32, 0.022, 0.012, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_rail)

    # Angular Upper Shroud Facets
    mat_shroud = Matrix.Translation((0.18, 0, 0.062)) @ Matrix.Diagonal((0.16, 0.048, 0.024, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_shroud)

    # Side Ejection Port / Cooling Chamber
    mat_port = Matrix.Translation((0.08, 0.023, 0.04)) @ Matrix.Diagonal((0.08, 0.008, 0.028, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_port)

def build_futuristic_barrel(bm):
    # Futuristic Vented Handguard (White Ceramic)
    mat_guard = Matrix.Translation((0.38, 0, 0.032)) @ Matrix.Diagonal((0.26, 0.038, 0.042, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_guard)

    # Top Heat-Shield Fin
    mat_fin = Matrix.Translation((0.38, 0, 0.058)) @ Matrix.Diagonal((0.22, 0.014, 0.014, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_fin)

    # Inner High-Tech Barrel (Dark Carbon/Titanium)
    mat_barrel = Matrix.Translation((0.56, 0, 0.032)) @ Matrix.Diagonal((0.16, 0.018, 0.018, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_barrel)

    # Futuristic Linear Compensator / Muzzle Shroud
    mat_muzzle = Matrix.Translation((0.66, 0, 0.032)) @ Matrix.Diagonal((0.07, 0.030, 0.036, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_muzzle)

def build_futuristic_magazine(bm):
    # Angular Polymeric White Magazine Body
    mat_mag = Matrix.Translation((0.13, 0, -0.095)) @ Matrix.Rotation(math.radians(-14), 4, 'Y') @ Matrix.Diagonal((0.075, 0.028, 0.19, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mag)

    # Extended Mag Baseplate (Black Polymer)
    mat_base = Matrix.Translation((0.17, 0, -0.19)) @ Matrix.Rotation(math.radians(-14), 4, 'Y') @ Matrix.Diagonal((0.082, 0.032, 0.022, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_base)

def build_futuristic_grip(bm):
    # Ergonomic Skeletal Grip (Carbon Fiber & White Inset)
    mat_grip = Matrix.Translation((-0.045, 0, -0.075)) @ Matrix.Rotation(math.radians(18), 4, 'Y') @ Matrix.Diagonal((0.046, 0.032, 0.13, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_grip)

    # Extended Trigger Guard & Trigger
    mat_guard = Matrix.Translation((0.02, 0, -0.035)) @ Matrix.Diagonal((0.065, 0.012, 0.038, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_guard)
    mat_trigger = Matrix.Translation((0.01, 0, -0.032)) @ Matrix.Rotation(math.radians(-15), 4, 'Y') @ Matrix.Diagonal((0.012, 0.006, 0.025, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_trigger)

def build_futuristic_stock(bm):
    # Upper Titanium Buffer Tube
    mat_tube = Matrix.Translation((-0.18, 0, 0.045)) @ Matrix.Diagonal((0.26, 0.024, 0.026, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_tube)

    # Lower Structural Strut
    mat_strut = Matrix.Translation((-0.17, 0, -0.012)) @ Matrix.Diagonal((0.23, 0.016, 0.016, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_strut)

    # White Cheek-Rest Riser
    mat_riser = Matrix.Translation((-0.16, 0, 0.065)) @ Matrix.Diagonal((0.14, 0.036, 0.018, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_riser)

    # Ergonomic Recoil Butt Pad
    mat_pad = Matrix.Translation((-0.31, 0, 0.018)) @ Matrix.Diagonal((0.032, 0.038, 0.14, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_pad)

def build_futuristic_sight(bm):
    # Holographic Sight Base & Housing
    mat_base = Matrix.Translation((0.07, 0, 0.095)) @ Matrix.Diagonal((0.08, 0.036, 0.025, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_base)

    # Optic Hood / Protective Frame
    mat_hood = Matrix.Translation((0.07, 0, 0.118)) @ Matrix.Diagonal((0.065, 0.032, 0.032, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_hood)

def build_futuristic_emissive_strips(bm):
    # Cyber Light Lines along Receiver Top
    mat_strip_top = Matrix.Translation((0.12, 0.023, 0.055)) @ Matrix.Diagonal((0.20, 0.003, 0.006, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_strip_top)

    mat_strip_top_l = Matrix.Translation((0.12, -0.023, 0.055)) @ Matrix.Diagonal((0.20, 0.003, 0.006, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_strip_top_l)

    # Handguard Vent Glow Strips
    mat_vent_r = Matrix.Translation((0.36, 0.020, 0.032)) @ Matrix.Diagonal((0.16, 0.003, 0.008, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_vent_r)

    mat_vent_l = Matrix.Translation((0.36, -0.020, 0.032)) @ Matrix.Diagonal((0.16, 0.003, 0.008, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_vent_l)

    # Mag Ammo Level Glow Gauge
    mat_mag_gauge = Matrix.Translation((0.135, 0.015, -0.095)) @ Matrix.Rotation(math.radians(-14), 4, 'Y') @ Matrix.Diagonal((0.012, 0.003, 0.12, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mag_gauge)

    # Holographic Reticle Lens
    mat_reticle = Matrix.Translation((0.07, 0, 0.118)) @ Matrix.Diagonal((0.002, 0.024, 0.024, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_reticle)

def build_collision(bm):
    mat_ucx = Matrix.Translation((0.16, 0, 0.0)) @ Matrix.Diagonal((1.02, 0.065, 0.29, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ucx)

# -------------------------------------------------------------
# SHADER APPLICATION: PBR WHITE CERAMIC, CARBON, & NEON CYAN
# -------------------------------------------------------------

def apply_futuristic_white_materials():
    # 1. Primary White Ceramic PBR (Crisp, High-Tech Satin White)
    mat_white = create_pbr_material(
        "M_DarX_WhiteCeramic",
        base_color=(0.82, 0.83, 0.85, 1.0),
        metallic=0.15,
        roughness=0.38
    )

    # 2. Secondary Dark Carbon Fiber / Titanium
    mat_carbon = create_pbr_material(
        "M_DarX_DarkCarbon",
        base_color=(0.04, 0.04, 0.05, 1.0),
        metallic=0.85,
        roughness=0.30
    )

    # 3. High-Tech Anodized Gunmetal Accent
    mat_accent = create_pbr_material(
        "M_DarX_TitaniumAccent",
        base_color=(0.14, 0.15, 0.18, 1.0),
        metallic=0.92,
        roughness=0.22
    )

    # 4. Futuristic Cyber Cyan Plasma Glow
    mat_cyan_glow = create_pbr_material(
        "M_DarX_CyberCyanGlow",
        base_color=(0.0, 0.90, 1.0, 1.0),
        metallic=0.05,
        roughness=0.10,
        emission_color=(0.0, 0.90, 1.0, 1.0),
        emission_strength=8.0
    )

    obj_mats = {
        "WP_Vandal_Receiver": [mat_white, mat_carbon],
        "WP_Vandal_Barrel": [mat_white, mat_accent, mat_carbon],
        "WP_Vandal_Magazine": [mat_white, mat_carbon],
        "WP_Vandal_Grip": [mat_carbon, mat_white],
        "WP_Vandal_Stock": [mat_accent, mat_white, mat_carbon],
        "WP_Vandal_Sight": [mat_carbon, mat_white],
        "WP_Vandal_CyberStrips": [mat_cyan_glow]
    }

    for obj_name, mats in obj_mats.items():
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            obj.data.materials.clear()
            for m in mats:
                obj.data.materials.append(m)

# -------------------------------------------------------------
# CAMERA & CINEMATIC STUDIO RENDER
# -------------------------------------------------------------

def setup_camera_and_render(output_path):
    if not output_path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    # Background color: Elegant neutral dark-slate studio
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.05, 0.055, 0.065, 1.0)
            bg.inputs["Strength"].default_value = 0.6

    # Isolate AOE_Generated in render
    aoe_col = bpy.data.collections.get("AOE_Generated")
    aoe_objs = set(aoe_col.objects) if aoe_col else set()

    for obj in bpy.data.objects:
        if obj not in aoe_objs and not obj.name.startswith("AOE_Studio_"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    if "UCX_WP_Vandal_01" in bpy.data.objects:
        bpy.data.objects["UCX_WP_Vandal_01"].hide_render = True

    # Camera with perfect wide framing
    cam_name = "AOE_Studio_Camera"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = (0.18, -1.75, 0.42)
    cam_obj.data.lens = 55.0
    cam_obj.constraints.clear()

    empty_name = "AOE_Studio_Target"
    if empty_name in bpy.data.objects:
        target_empty = bpy.data.objects[empty_name]
    else:
        target_empty = bpy.data.objects.new(empty_name, None)
        scene.collection.objects.link(target_empty)
    target_empty.location = (0.18, 0.0, 0.0)

    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = target_empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    scene.camera = cam_obj

    # Studio Lighting Setup
    # 1. Main Key Light (Soft Warm Key)
    key_name = "AOE_Studio_Key"
    if key_name in bpy.data.objects:
        key_obj = bpy.data.objects[key_name]
    else:
        k_data = bpy.data.lights.new(key_name, type='SUN')
        key_obj = bpy.data.objects.new(key_name, k_data)
        scene.collection.objects.link(key_obj)
    key_obj.data.energy = 2.4
    key_obj.data.color = (1.0, 0.98, 0.96)
    key_obj.location = (1.2, -1.8, 1.6)
    key_obj.rotation_euler = (math.radians(45), math.radians(18), math.radians(35))

    # 2. Rim Accent Light (Cyber Cyan)
    rim_name = "AOE_Studio_Rim"
    if rim_name in bpy.data.objects:
        rim_obj = bpy.data.objects[rim_name]
    else:
        r_data = bpy.data.lights.new(rim_name, type='SUN')
        rim_obj = bpy.data.objects.new(rim_name, r_data)
        scene.collection.objects.link(rim_obj)
    rim_obj.data.energy = 2.0
    rim_obj.data.color = (0.0, 0.85, 1.0)
    rim_obj.location = (-1.2, 1.5, 0.8)
    rim_obj.rotation_euler = (math.radians(-50), math.radians(-15), math.radians(-140))

    # 3. Soft Top Fill
    fill_name = "AOE_Studio_Fill"
    if fill_name in bpy.data.objects:
        fill_obj = bpy.data.objects[fill_name]
    else:
        f_data = bpy.data.lights.new(fill_name, type='SUN')
        fill_obj = bpy.data.objects.new(fill_name, f_data)
        scene.collection.objects.link(fill_obj)
    fill_obj.data.energy = 1.2
    fill_obj.data.color = (0.75, 0.80, 0.90)
    fill_obj.location = (0.2, -1.5, 1.8)

    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDER_COMPLETED: {output_path}")

def main():
    args = parse_args()
    col = get_or_create_collection("AOE_Generated")

    # Build all components
    create_mesh_object("WP_Vandal_Receiver", col, build_futuristic_receiver)
    create_mesh_object("WP_Vandal_Barrel", col, build_futuristic_barrel)
    create_mesh_object("WP_Vandal_Magazine", col, build_futuristic_magazine)
    create_mesh_object("WP_Vandal_Grip", col, build_futuristic_grip)
    create_mesh_object("WP_Vandal_Stock", col, build_futuristic_stock)
    create_mesh_object("WP_Vandal_Sight", col, build_futuristic_sight)
    create_mesh_object("WP_Vandal_CyberStrips", col, build_futuristic_emissive_strips)
    create_mesh_object("UCX_WP_Vandal_01", col, build_collision)

    # Apply White & Futuristic Cyber Materials
    apply_futuristic_white_materials()

    if args.preview_output:
        setup_camera_and_render(args.preview_output)

    if args.blend_file:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend_file)
        print(f"FILE_SAVED: {args.blend_file}")

if __name__ == "__main__":
    main()
