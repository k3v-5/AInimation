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
    parser.add_argument("--step", type=str, required=True, choices=["base", "components", "materials", "finalize", "render", "full"])
    parser.add_argument("--blend-file", type=str, default="")
    parser.add_argument("--preview-output", type=str, default="")
    return parser.parse_args(argv)

def get_or_create_collection(name="AOE_Generated"):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def get_or_create_material(name, base_color=(0.1, 0.1, 0.12, 1.0), metallic=0.9, roughness=0.35, emission_color=None, emission_strength=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
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
        return bpy.data.objects[name]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    build_fn(bm)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def build_receiver(bm):
    # Main receiver body: 0.32m long, 0.042m wide, 0.08m tall
    mat_body = Matrix.Translation((0.10, 0, 0.03)) @ Matrix.Diagonal((0.32, 0.042, 0.08, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_body)
    # Upper picatinny rail
    mat_rail = Matrix.Translation((0.10, 0, 0.075)) @ Matrix.Diagonal((0.30, 0.024, 0.015, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_rail)

def build_barrel(bm):
    # Handguard shroud: 0.32m long, octagonal
    mat_shroud = Matrix.Translation((0.40, 0, 0.03)) @ Matrix.Diagonal((0.30, 0.036, 0.036, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_shroud)
    # Exposed inner barrel
    mat_barrel = Matrix.Translation((0.58, 0, 0.03)) @ Matrix.Diagonal((0.12, 0.020, 0.020, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_barrel)
    # Aggressive Muzzle brake
    mat_brake = Matrix.Translation((0.66, 0, 0.03)) @ Matrix.Diagonal((0.06, 0.028, 0.032, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_brake)

def build_magazine(bm):
    # Curved banana mag
    mat_mag = Matrix.Translation((0.14, 0, -0.09)) @ Matrix.Rotation(math.radians(-12), 4, 'Y') @ Matrix.Diagonal((0.07, 0.026, 0.18, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mag)

def build_grip(bm):
    # Ergonomic pistol grip
    mat_grip = Matrix.Translation((-0.04, 0, -0.07)) @ Matrix.Rotation(math.radians(16), 4, 'Y') @ Matrix.Diagonal((0.045, 0.030, 0.12, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_grip)
    # Trigger guard
    mat_guard = Matrix.Translation((0.02, 0, -0.03)) @ Matrix.Diagonal((0.06, 0.012, 0.035, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_guard)

def build_stock(bm):
    # Skeletonized stock struts
    mat_strut = Matrix.Translation((-0.18, 0, 0.04)) @ Matrix.Diagonal((0.24, 0.022, 0.025, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_strut)
    # Lower strut
    mat_low = Matrix.Translation((-0.18, 0, -0.01)) @ Matrix.Diagonal((0.22, 0.018, 0.018, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_low)
    # Butt pad
    mat_pad = Matrix.Translation((-0.30, 0, 0.01)) @ Matrix.Diagonal((0.03, 0.035, 0.13, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_pad)

def build_sight(bm):
    # Holographic optic housing
    mat_optic = Matrix.Translation((0.08, 0, 0.105)) @ Matrix.Diagonal((0.09, 0.034, 0.045, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_optic)

def build_collision(bm):
    # Convex bounds of full rifle
    mat_ucx = Matrix.Translation((0.16, 0, 0.0)) @ Matrix.Diagonal((0.98, 0.06, 0.28, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ucx)

def apply_materials():
    mat_metal = get_or_create_material("M_DarX_GunMetal", base_color=(0.10, 0.11, 0.13, 1.0), metallic=0.95, roughness=0.28)
    mat_grip = get_or_create_material("M_DarX_PolymerGrip", base_color=(0.03, 0.03, 0.035, 1.0), metallic=0.05, roughness=0.80)
    mat_trim = get_or_create_material("M_DarX_AnodizedTrim", base_color=(0.25, 0.25, 0.30, 1.0), metallic=0.88, roughness=0.18)
    mat_emissive = get_or_create_material(
        "M_DarX_PlasmaGlow",
        base_color=(0.0, 0.85, 1.0, 1.0),
        metallic=0.1,
        roughness=0.1,
        emission_color=(0.0, 0.85, 1.0, 1.0),
        emission_strength=8.0
    )

    obj_mats = {
        "WP_Vandal_Receiver": [mat_metal, mat_trim],
        "WP_Vandal_Barrel": [mat_metal, mat_trim],
        "WP_Vandal_Magazine": [mat_metal, mat_emissive],
        "WP_Vandal_Grip": [mat_grip],
        "WP_Vandal_Stock": [mat_metal, mat_grip],
        "WP_Vandal_Sight": [mat_trim, mat_emissive]
    }

    for obj_name, mats in obj_mats.items():
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            obj.data.materials.clear()
            for m in mats:
                obj.data.materials.append(m)

def setup_camera_and_render(output_path):
    if not output_path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = False

    # Isolate AOE_Generated in render
    aoe_col = bpy.data.collections.get("AOE_Generated")
    aoe_objs = set(aoe_col.objects) if aoe_col else set()
    
    for obj in bpy.data.objects:
        if obj not in aoe_objs and not obj.name.startswith("AOE_Validation_"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    # Hide UCX collision from render
    if "UCX_WP_Vandal_01" in bpy.data.objects:
        bpy.data.objects["UCX_WP_Vandal_01"].hide_render = True

    # Camera with TrackTo
    cam_name = "AOE_Validation_Camera"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)
    
    cam_obj.location = (0.18, -1.35, 0.40)
    cam_obj.data.lens = 45.0
    cam_obj.constraints.clear()
    
    empty_name = "AOE_Target_Empty"
    if empty_name in bpy.data.objects:
        target_empty = bpy.data.objects[empty_name]
    else:
        target_empty = bpy.data.objects.new(empty_name, None)
        scene.collection.objects.link(target_empty)
    target_empty.location = (0.18, 0.0, 0.01)

    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = target_empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    scene.camera = cam_obj

    # 3-Point Studio Lighting
    # 1. Key Light
    key_name = "AOE_Validation_Key"
    if key_name in bpy.data.objects:
        key_obj = bpy.data.objects[key_name]
    else:
        k_data = bpy.data.lights.new(key_name, type='SUN')
        k_data.energy = 4.0
        k_data.color = (1.0, 0.95, 0.9)
        key_obj = bpy.data.objects.new(key_name, k_data)
        scene.collection.objects.link(key_obj)
    key_obj.location = (0.8, -1.2, 1.2)
    key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))

    # 2. Rim/Accent Light (Cyan)
    rim_name = "AOE_Validation_Rim"
    if rim_name in bpy.data.objects:
        rim_obj = bpy.data.objects[rim_name]
    else:
        r_data = bpy.data.lights.new(rim_name, type='SUN')
        r_data.energy = 3.0
        r_data.color = (0.2, 0.8, 1.0)
        rim_obj = bpy.data.objects.new(rim_name, r_data)
        scene.collection.objects.link(rim_obj)
    rim_obj.location = (-0.8, 1.2, 0.8)
    rim_obj.rotation_euler = (math.radians(-50), math.radians(-15), math.radians(-140))

    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDER_COMPLETED: {output_path}")

def main():
    args = parse_args()
    col = get_or_create_collection("AOE_Generated")

    if args.step == "base":
        create_mesh_object("WP_Vandal_Receiver", col, build_receiver)
        print("STEP_BASE_COMPLETED")

    elif args.step == "components":
        create_mesh_object("WP_Vandal_Receiver", col, build_receiver)
        create_mesh_object("WP_Vandal_Barrel", col, build_barrel)
        create_mesh_object("WP_Vandal_Magazine", col, build_magazine)
        create_mesh_object("WP_Vandal_Grip", col, build_grip)
        create_mesh_object("WP_Vandal_Stock", col, build_stock)
        create_mesh_object("WP_Vandal_Sight", col, build_sight)
        print("STEP_COMPONENTS_COMPLETED")

    elif args.step == "materials":
        apply_materials()
        print("STEP_MATERIALS_COMPLETED")

    elif args.step == "finalize":
        create_mesh_object("WP_Vandal_Receiver", col, build_receiver)
        create_mesh_object("WP_Vandal_Barrel", col, build_barrel)
        create_mesh_object("WP_Vandal_Magazine", col, build_magazine)
        create_mesh_object("WP_Vandal_Grip", col, build_grip)
        create_mesh_object("WP_Vandal_Stock", col, build_stock)
        create_mesh_object("WP_Vandal_Sight", col, build_sight)
        apply_materials()
        create_mesh_object("UCX_WP_Vandal_01", col, build_collision)
        if args.preview_output:
            setup_camera_and_render(args.preview_output)
        print("STEP_FINALIZE_COMPLETED")

    elif args.step == "render":
        if args.preview_output:
            setup_camera_and_render(args.preview_output)
        print("STEP_RENDER_COMPLETED")

    if args.blend_file:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend_file)
        print(f"FILE_SAVED: {args.blend_file}")

if __name__ == "__main__":
    main()
