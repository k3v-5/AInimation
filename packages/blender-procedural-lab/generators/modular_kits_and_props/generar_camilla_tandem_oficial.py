"""
generar_camilla_tandem_oficial.py
===================================
Generador de Malla 3D y Asset Modular para Unreal Engine 5:
Camilla Plegable Tandem de Rescate (SM_TandemStretcher)
Proyecto: Astra Hazard - Rescue Squad

Genera:
1. Modelo 3D Low-Poly estilizado de camilla espacial para 2 bomberos:
   - Rieles tubulares de titanio aeroespacial.
   - Lona reforzada de alta resistencia con correas de sujeción.
   - 4 empuñaduras ergonómicas de goma de alto agarre (2 frontales, 2 traseras).
   - Patines plegables de apoyo con topes antideslizantes.
2. Materiales PBR estilizados (Naranja de seguridad, Amarillo de advertencia, Goma oscura, Metal pulido).
3. Exportación oficial FBX a 'Art/FBX/Equipment/SM_TandemStretcher.fbx'.
4. Renders multi-ángulo de alta resolución y collage de validación estética.
"""

import sys, os, math
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Equipment")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_mat(name, base_color, metallic=0.05, roughness=0.45, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_stretcher_model():
    clear_scene()

    # Materiales estilizados
    mat_metal = create_pbr_mat("M_Stretcher_Frame", (0.18, 0.20, 0.22, 1.0), metallic=0.75, roughness=0.35)
    mat_orange = create_pbr_mat("M_Stretcher_Canvas", (0.95, 0.35, 0.05, 1.0), metallic=0.02, roughness=0.65)
    mat_rubber = create_pbr_mat("M_Stretcher_Grip", (0.05, 0.05, 0.06, 1.0), metallic=0.0, roughness=0.85)
    mat_hazard = create_pbr_mat("M_Stretcher_Straps", (0.95, 0.75, 0.08, 1.0), metallic=0.1, roughness=0.5)
    mat_buckle = create_pbr_mat("M_Stretcher_Buckle", (0.85, 0.85, 0.88, 1.0), metallic=0.9, roughness=0.2)

    mesh = bpy.data.meshes.new("SM_TandemStretcher")
    bm = bmesh.new()

    # Rieles longitudinales (2 barras a lo largo de X)
    # Longitud: 210 cm (-105 a +105)
    # Ancho: 56 cm (Y = -28 y Y = +28)
    rail_radius = 0.022
    rail_len = 2.10

    # Riel izquierdo y derecho
    for y_pos in (-0.28, 0.28):
        m = Matrix.Translation((0.0, y_pos, 0.05)) @ Matrix.Rotation(R(90), 4, 'Y')
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=rail_radius, radius2=rail_radius, depth=rail_len, segments=12, matrix=m)

    # 4 Empuñaduras de goma (en los extremos de los rieles)
    grip_len = 0.22
    grip_radius = 0.027
    for y_pos in (-0.28, 0.28):
        # Empuñaduras frontales (+X)
        m_front = Matrix.Translation((0.92, y_pos, 0.05)) @ Matrix.Rotation(R(90), 4, 'Y')
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=grip_radius, radius2=grip_radius, depth=grip_len, segments=12, matrix=m_front)
        # Empuñaduras traseras (-X)
        m_rear = Matrix.Translation((-0.92, y_pos, 0.05)) @ Matrix.Rotation(R(90), 4, 'Y')
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=grip_radius, radius2=grip_radius, depth=grip_len, segments=12, matrix=m_rear)

    # Barras transversales (4 travesaños)
    cross_radius = 0.018
    cross_len = 0.56
    for x_pos in (-0.75, -0.25, 0.25, 0.75):
        m_cross = Matrix.Translation((x_pos, 0.0, 0.05)) @ Matrix.Rotation(R(90), 4, 'X')
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=cross_radius, radius2=cross_radius, depth=cross_len, segments=10, matrix=m_cross)

    # Patines de apoyo inferiores (U-shaped skids)
    skid_radius = 0.016
    for x_pos in (-0.60, 0.60):
        # Tubos verticales
        for y_pos in (-0.26, 0.26):
            m_v = Matrix.Translation((x_pos, y_pos, -0.02))
            bmesh.ops.create_cone(bm, cap_ends=True, radius1=skid_radius, radius2=skid_radius, depth=0.14, segments=8, matrix=m_v)
        # Barra horizontal del patín en el suelo
        m_h = Matrix.Translation((x_pos, 0.0, -0.09)) @ Matrix.Rotation(R(90), 4, 'X')
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=skid_radius, radius2=skid_radius, depth=0.52, segments=8, matrix=m_h)

    # Lona de soporte (Canvas bed)
    # Cubre de x=-0.75 a +0.75, y=-0.26 a +0.26
    canvas_mesh = Matrix.Translation((0.0, 0.0, 0.045))
    bmesh.ops.create_cube(bm, size=1.0, matrix=canvas_mesh @ Matrix.Scale(1.50, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.52, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.018, 4, Vector((0, 0, 1))))

    # Correas de seguridad transversales (2 cinturones de retención con hebillas)
    for x_strap in (-0.30, 0.30):
        # Correa amarilla
        m_strap = Matrix.Translation((x_strap, 0.0, 0.065))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m_strap @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.53, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.012, 4, Vector((0, 0, 1))))
        # Hebilla metálica en el centro
        m_buckle = Matrix.Translation((x_strap, 0.0, 0.075))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m_buckle @ Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.018, 4, Vector((0, 0, 1))))

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("SM_TandemStretcher", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_orange)
    obj.data.materials.append(mat_metal)
    obj.data.materials.append(mat_rubber)
    obj.data.materials.append(mat_hazard)
    obj.data.materials.append(mat_buckle)

    # Asignar índices de material por proximidad
    for poly in obj.data.polygons:
        center = poly.center
        # Si está en los extremos de agarre (|x| > 0.80) -> Goma oscura
        if abs(center.x) > 0.80 and abs(center.y) > 0.20:
            poly.material_index = 2
        # Si está en las correas (|x - 0.3| < 0.04 o |x + 0.3| < 0.04)
        elif (abs(center.x - 0.30) < 0.04 or abs(center.x + 0.30) < 0.04) and center.z > 0.055:
            if abs(center.y) < 0.07:
                poly.material_index = 4 # Hebilla
            else:
                poly.material_index = 3 # Correa
        # Si es la lona central
        elif abs(center.x) <= 0.75 and abs(center.y) <= 0.25 and center.z > 0.03:
            poly.material_index = 0 # Lona naranja
        else:
            poly.material_index = 1 # Marco de metal

    # Exportar FBX
    fbx_path = os.path.join(FBX_DIR, "SM_TandemStretcher.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"[OK] Exportado FBX: {fbx_path}")

    return obj

def setup_render_environment():
    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
        bg.inputs['Strength'].default_value = 0.5
    bpy.context.scene.world = world

    # Luces clave
    key_light = bpy.data.lights.new("KeyLight", type='AREA')
    key_light.energy = 450.0
    key_light.size = 2.5
    key_light.color = (1.0, 0.95, 0.90)
    key_obj = bpy.data.objects.new("KeyLight", key_light)
    key_obj.location = (2.2, -2.5, 2.5)
    key_obj.rotation_euler = (R(55), 0, R(40))
    bpy.context.collection.objects.link(key_obj)

    fill_light = bpy.data.lights.new("FillLight", type='AREA')
    fill_light.energy = 220.0
    fill_light.size = 3.0
    fill_light.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_light)
    fill_obj.location = (-2.5, 2.0, 1.8)
    fill_obj.rotation_euler = (R(60), 0, R(-130))
    bpy.context.collection.objects.link(fill_obj)

def render_views(obj):
    setup_render_environment()

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720

    views = {
        "perspective": ((2.2, -2.2, 1.4), (R(65), 0, R(45))),
        "top": ((0.0, 0.0, 3.2), (0, 0, 0)),
        "side": ((0.0, -2.8, 0.3), (R(85), 0, 0)),
        "action_tilt": ((1.8, -1.8, 1.1), (R(60), 0, R(45)))
    }

    image_paths = []
    for name, (loc, rot) in views.items():
        cam_obj.location = loc
        cam_obj.rotation_euler = rot
        
        # En action tilt, inclinamos levemente la camilla para simular carga
        if name == "action_tilt":
            obj.rotation_euler = (R(8), R(-12), R(15))
        else:
            obj.rotation_euler = (0, 0, 0)
            
        out_path = os.path.join(RENDERS_DIR, f"SM_TandemStretcher_{name}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        image_paths.append(out_path)
        print(f"[OK] Renderizado: {out_path}")

    # Collage 2x2
    collage = Image.new("RGB", (1920, 1440), (12, 14, 18))
    labels = ["VISTA PERSPECTIVA 3D", "VISTA SUPERIOR (LONA Y CORREAS)", "VISTA LATERAL (PATINES Y REFUERZOS)", "SIMULACIÓN DE TRANSPORTE EN TÁNDEM"]
    
    positions = [(0, 0), (960, 0), (0, 720), (960, 720)]
    for i, path in enumerate(image_paths):
        img = Image.open(path)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(20, 20), (580, 65)], fill=(15, 18, 24, 220))
        draw.text((30, 28), labels[i], fill=(255, 180, 50))
        collage.paste(img, positions[i])

    collage_path = os.path.join(RENDERS_DIR, "SM_TandemStretcher_4views.png")
    collage.save(collage_path)

    brain_dest = os.path.join(BRAIN_DIR, "SM_TandemStretcher_4views.png")
    collage.save(brain_dest)
    print(f"[OK] Collage guardado en: {collage_path} y {brain_dest}")

if __name__ == "__main__":
    stretcher = create_stretcher_model()
    render_views(stretcher)
