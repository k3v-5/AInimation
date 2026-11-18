"""
generar_personaje_fiel_referencia_v3.py
Iteración V4: Ajustes milimétricos finales:
1. POSTURA EN 'A' CON PIERNAS EN ÁNGULO: Muslos y pantorrillas inclinados hacia afuera, pies separados en postura de combate sólida.
2. PROPORCIONES DEL CASCO: Cúpula más ancha y anidada en los hombros con visor panorámico envolvente.
3. ILUMINACIÓN CALIBRADA A 350W: Traje naranja #E0651A vibrante y armadura verde salvia completamente visibles sin empaste.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Characters")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# PALETA EXACTA DE MATERIALES PBR
# -------------------------------------------------------------
def create_pbr_mat(name, base_color, metallic=0.04, roughness=0.45, emission=None, emission_strength=1.0):
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
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        else:
            bsdf.inputs['Emission'].default_value = emission
            
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_unlit_mat(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = color
    emis.inputs['Strength'].default_value = 1.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mat.use_backface_culling = True
    return mat

def create_palette():
    return {
        # 0: Traje Naranja Oficial (#D9681E / #E26618)
        'suit_orange': create_pbr_mat("M_Suit_Orange", (0.88, 0.35, 0.05, 1.0), metallic=0.02, roughness=0.42),
        # 1: Armadura Verde Salvia (#556B52)
        'armor_sage': create_pbr_mat("M_Armor_Sage", (0.28, 0.38, 0.26, 1.0), metallic=0.08, roughness=0.38),
        # 2: Casco Gris Oscuro (#343942)
        'helmet_grey': create_pbr_mat("M_Helmet_Grey", (0.14, 0.16, 0.19, 1.0), metallic=0.20, roughness=0.30),
        # 3: Visor Ahumado Tintado (#26333D)
        'visor_tinted': create_pbr_mat("M_Visor_Tinted", (0.10, 0.15, 0.20, 1.0), metallic=0.12, roughness=0.06),
        # 4: Franjas Amarillo Lima (#DCE63C)
        'stripe_yellow': create_pbr_mat("M_Stripe_Yellow", (0.86, 0.92, 0.12, 1.0), metallic=0.02, roughness=0.20),
        # 5: Manguera Roja (#A21A16)
        'hose_red': create_pbr_mat("M_Hose_Red", (0.68, 0.08, 0.05, 1.0), metallic=0.04, roughness=0.48),
        # 6: Arnés y Gomas Carbón
        'harness_dark': create_pbr_mat("M_Harness_Dark", (0.05, 0.05, 0.06, 1.0), metallic=0.08, roughness=0.60),
        # 7: Pantalla Pectoral Verde LED
        'led_green': create_pbr_mat("M_LED_Green", (0.15, 0.98, 0.20, 1.0), metallic=0.0, roughness=0.1, emission=(0.15, 0.98, 0.20, 1.0), emission_strength=5.5),
        # 8: Botones Rojos LED
        'led_red': create_pbr_mat("M_LED_Red", (1.0, 0.08, 0.08, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.08, 0.08, 1.0), emission_strength=4.5),
        # 9: Cañón y Chasis Arma Azul-Gris (#4A6B7C)
        'tool_blue': create_pbr_mat("M_Tool_BlueGrey", (0.24, 0.36, 0.44, 1.0), metallic=0.45, roughness=0.28),
        # 10: Acero Oscuro / Culata
        'tool_dark': create_pbr_mat("M_Tool_DarkMetal", (0.08, 0.09, 0.10, 1.0), metallic=0.85, roughness=0.20),
        # 11: Ventana Amarilla Arma
        'tool_yellow': create_pbr_mat("M_Tool_AccentYellow", (0.92, 0.78, 0.10, 1.0), metallic=0.05, roughness=0.3, emission=(0.92, 0.78, 0.10, 1.0), emission_strength=3.0),
        # 12: Contorno Cel-Shading Tinta Negra
        'outline_black': create_unlit_mat("M_Outline_Black", (0.01, 0.01, 0.01, 1.0))
    }

# -------------------------------------------------------------
# CONSTRUCCIÓN DETALLADA DEL PERSONAJE CHUNKY (V4)
# -------------------------------------------------------------
def build_character(mats):
    mesh = bpy.data.meshes.new("SK_Firefighter_Chunky_Mesh")
    bm = bmesh.new()

    mat_order = [
        mats['suit_orange'],   # 0
        mats['armor_sage'],    # 1
        mats['helmet_grey'],   # 2
        mats['visor_tinted'],  # 3
        mats['stripe_yellow'], # 4
        mats['hose_red'],      # 5
        mats['harness_dark'],  # 6
        mats['led_green'],     # 7
        mats['led_red'],       # 8
        mats['tool_blue'],     # 9
        mats['tool_dark'],     # 10
        mats['tool_yellow'],   # 11
        mats['outline_black']  # 12
    ]

    def add_box(center, size, mat_idx, rot_x=0, rot_y=0, rot_z=0):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        if rot_x != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_x, 3, 'X'), verts=verts)
        if rot_y != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_y, 3, 'Y'), verts=verts)
        if rot_z != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_z, 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    def add_cylinder(center, radius, depth, mat_idx, segs=12, rot_x=0, rot_y=0, rot_z=0):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        if rot_x != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_x, 3, 'X'), verts=verts)
        if rot_y != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_y, 3, 'Y'), verts=verts)
        if rot_z != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_z, 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # =========================================================
    # 1. CASCO DOMO ESFÉRICO ANCHO ("REINFORCED VISOR")
    # =========================================================
    add_cylinder((0, 0.02, 1.55), 0.22, 0.30, 2, segs=16)
    add_cylinder((0, 0.02, 1.67), 0.19, 0.08, 2, segs=16)
    add_cylinder((0, 0.02, 1.71), 0.14, 0.04, 2, segs=14)

    # Cresta superior longitudinal
    add_box((0, 0.02, 1.73), (0.11, 0.34, 0.04), 2)
    # Insignia amarilla frontal sobre el visor
    add_box((0, -0.16, 1.73), (0.08, 0.02, 0.035), 4)

    # Marco del visor
    add_box((0, -0.15, 1.55), (0.32, 0.08, 0.20), 2)
    # Cristal ahumado tintado oscuro
    add_box((0, -0.18, 1.55), (0.28, 0.03, 0.16), 3)

    # Auriculares laterales
    add_cylinder((-0.22, 0.02, 1.55), 0.065, 0.04, 2, segs=10, rot_y=R(90))
    add_cylinder((0.22, 0.02, 1.55), 0.065, 0.04, 2, segs=10, rot_y=R(90))

    # Anillo del cuello / Gorget (Verde salvia)
    add_cylinder((0, 0.01, 1.38), 0.22, 0.08, 1, segs=16)

    # =========================================================
    # 2. TORSO Y CAJA DE CONTROL PECTORAL
    # =========================================================
    add_box((0, 0.01, 1.18), (0.50, 0.35, 0.38), 0)

    # Tirantes oscuros del arnés
    add_box((-0.15, -0.165, 1.20), (0.06, 0.02, 0.34), 6)
    add_box((0.15, -0.165, 1.20), (0.06, 0.02, 0.34), 6)
    add_box((0, -0.165, 1.22), (0.36, 0.02, 0.04), 6)
    add_box((0, -0.165, 1.02), (0.42, 0.02, 0.06), 6)

    # Franja amarilla de la cintura
    add_box((0, 0.01, 0.99), (0.51, 0.36, 0.05), 4)

    # Caja de Control en el Pecho (Verde salvia)
    add_box((0.02, -0.19, 1.20), (0.17, 0.03, 0.11), 1)
    add_box((-0.03, -0.208, 1.20), (0.055, 0.01, 0.065), 7)
    add_box((0.065, -0.208, 1.225), (0.026, 0.01, 0.026), 8)
    add_box((0.065, -0.208, 1.175), (0.026, 0.01, 0.026), 8)

    # =========================================================
    # 3. MOCHILA TRASERA ("BACKPACK UNIT")
    # =========================================================
    add_box((0, 0.27, 1.20), (0.38, 0.18, 0.44), 0)
    add_box((0, 0.28, 1.42), (0.36, 0.16, 0.04), 1)

    # Rejillas negras
    for z_off in [1.36, 1.32, 1.28, 1.24]:
        add_box((0.09, 0.365, z_off), (0.11, 0.01, 0.02), 6)

    # LED verde
    add_box((-0.10, 0.365, 1.33), (0.04, 0.01, 0.04), 7)

    # Panel gris inferior con botón rojo
    add_box((-0.04, 0.365, 1.12), (0.16, 0.01, 0.08), 1)
    add_box((-0.04, 0.372, 1.12), (0.05, 0.01, 0.03), 8)

    # Conector de manguera
    add_cylinder((0.10, 0.35, 1.03), 0.04, 0.05, 6, segs=10, rot_x=R(90))
    add_box((0.10, 0.37, 1.03), (0.05, 0.02, 0.05), 1)

    # =========================================================
    # 4. MANGUERA ROJA CURVA
    # =========================================================
    hose_pts = [
        Vector((0.10, 0.37, 1.03)),
        Vector((0.18, 0.39, 0.94)),
        Vector((0.29, 0.33, 0.83)),
        Vector((0.34, 0.19, 0.77)),
        Vector((0.36, 0.04, 0.78)),
        Vector((0.33, -0.12, 0.85)),
        Vector((0.27, -0.24, 0.93)),
        Vector((0.18, -0.34, 1.01))
    ]
    for i in range(len(hose_pts)-1):
        p1 = hose_pts[i]
        p2 = hose_pts[i+1]
        mid = (p1 + p2) * 0.5
        v = p2 - p1
        dist = v.length
        rot_axis = Vector((0, 0, 1)).cross(v.normalized())
        angle = math.acos(max(-1.0, min(1.0, Vector((0, 0, 1)).dot(v.normalized()))))
        
        cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.032, radius2=0.032, depth=dist)
        if rot_axis.length > 0.001:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(angle, 3, rot_axis.normalized()), verts=cyl['verts'])
        bmesh.ops.translate(bm, vec=mid, verts=cyl['verts'])
        for f in bm.faces:
            if f.verts[0] in cyl['verts']:
                f.material_index = 5

    # =========================================================
    # 5. ARMA TÁCTICA ("EQUIPMENT ISOLATED")
    # =========================================================
    gun_pos = Vector((0.02, -0.40, 1.03))

    add_cylinder((gun_pos.x - 0.22, gun_pos.y, gun_pos.z), 0.052, 0.30, 9, segs=12, rot_y=R(90))
    add_cylinder((gun_pos.x - 0.38, gun_pos.y, gun_pos.z), 0.064, 0.045, 10, segs=12, rot_y=R(90))

    add_box((gun_pos.x, gun_pos.y, gun_pos.z), (0.22, 0.11, 0.13), 9)
    add_box((gun_pos.x, gun_pos.y - 0.058, gun_pos.z), (0.08, 0.01, 0.045), 11)

    add_cylinder((gun_pos.x - 0.08, gun_pos.y, gun_pos.z - 0.10), 0.024, 0.12, 10, segs=8)

    add_box((gun_pos.x + 0.16, gun_pos.y, gun_pos.z - 0.04), (0.16, 0.06, 0.10), 10)
    add_box((gun_pos.x + 0.24, gun_pos.y, gun_pos.z - 0.08), (0.08, 0.05, 0.15), 10)

    add_cylinder((gun_pos.x + 0.16, gun_pos.y, gun_pos.z - 0.04), 0.032, 0.045, 5, segs=8, rot_x=R(90))

    # =========================================================
    # 6. BRAZOS SOSTENIENDO EL ARMA A DOS MANOS
    # =========================================================
    # Brazo Izquierdo
    add_box((-0.32, 0.01, 1.34), (0.20, 0.24, 0.14), 1)
    add_box((-0.32, 0.01, 1.21), (0.17, 0.20, 0.14), 0)
    add_box((-0.19, -0.22, 1.08), (0.17, 0.24, 0.17), 1, rot_x=R(35), rot_z=R(-30))
    add_box((-0.13, -0.30, 1.03), (0.17, 0.05, 0.17), 4, rot_x=R(35), rot_z=R(-30))
    add_box((-0.08, -0.38, 0.99), (0.14, 0.15, 0.14), 6)

    # Brazo Derecho
    add_box((0.32, 0.01, 1.34), (0.20, 0.24, 0.14), 1)
    add_box((0.32, 0.01, 1.21), (0.17, 0.20, 0.14), 0)
    add_box((0.24, -0.18, 1.10), (0.17, 0.24, 0.17), 1, rot_x=R(25), rot_z=R(20))
    add_box((0.20, -0.28, 1.04), (0.17, 0.05, 0.17), 4, rot_x=R(25), rot_z=R(20))
    add_box((0.16, -0.34, 1.01), (0.14, 0.15, 0.14), 6)

    # =========================================================
    # 7. PIERNAS EN POSTURA "A-STANCE" INCLINADA HACIA AFUERA
    # =========================================================
    add_box((0, 0.01, 0.94), (0.42, 0.29, 0.14), 0)

    for sign in [1, -1]:
        # Muslo inclinado hacia afuera (8 grados)
        add_box((0.14 * sign, 0.01, 0.74), (0.18, 0.22, 0.30), 0, rot_y=R(-8 * sign))

        # Rodillera rectangular verde salvia
        add_box((0.17 * sign, -0.10, 0.54), (0.18, 0.07, 0.15), 1)

        # Pantorrilla inclinada
        add_box((0.18 * sign, 0.01, 0.39), (0.17, 0.20, 0.22), 0, rot_y=R(-6 * sign))

        # Franja reflectante amarilla en el tobillo
        add_box((0.19 * sign, 0.01, 0.27), (0.18, 0.21, 0.05), 4)

        # Bota gruesa verde salvia plantada firmemente en el suelo
        add_box((0.21 * sign, -0.04, 0.14), (0.19, 0.28, 0.22), 1)
        add_box((0.21 * sign, -0.11, 0.05), (0.20, 0.16, 0.08), 2)
        add_box((0.21 * sign, -0.04, 0.02), (0.20, 0.29, 0.04), 2)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_MatchV4", mesh)
    bpy.context.scene.collection.objects.link(obj)

    sol = obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.010
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 12
    sol.use_rim = True

    return obj

# -------------------------------------------------------------
# ILUMINACIÓN CLARA Y VIBRANTE (350W KEY / 400W BACK)
# -------------------------------------------------------------
def setup_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    bg_mesh = bpy.data.meshes.new("StudioFloor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
    bm.to_mesh(bg_mesh)
    bm.free()
    bg_obj = bpy.data.objects.new("StudioFloor", bg_mesh)
    bg_obj.location = (0, 0, -0.01)
    scene.collection.objects.link(bg_obj)
    
    mat_floor = create_pbr_mat("M_StudioFloorDark", (0.025, 0.030, 0.038, 1.0), metallic=0.2, roughness=0.45)
    bg_obj.data.materials.append(mat_floor)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.95)
    scene.collection.objects.link(target)

    def add_light(name, pos, energy, color, size=3.0):
        ldata = bpy.data.lights.new(name, 'AREA')
        ldata.energy = energy
        ldata.size = size
        ldata.color = color
        lobj = bpy.data.objects.new(name, ldata)
        lobj.location = pos
        tt = lobj.constraints.new('TRACK_TO')
        tt.target = target
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
        scene.collection.objects.link(lobj)
        return lobj

    # Iluminación vibrante para colores nítidos como el screenshot
    add_light("FrontKey", (2.2, -3.2, 2.4), 320, (1.0, 0.98, 0.95), size=2.8)
    add_light("BackKey", (-2.0, 3.2, 2.4), 360, (0.95, 0.98, 1.0), size=2.8)
    add_light("RimLeft", (-3.2, -0.5, 1.8), 180, (0.2, 0.85, 1.0), size=2.0)
    add_light("FillRight", (3.2, 0.5, 1.6), 140, (1.0, 0.75, 0.35), size=2.5)

def render_camera_shot(cam_pos, target_pos, lens, out_path, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    empty = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(empty)
    empty.location = target_pos

    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)

def composite_model_sheet(v_front, v_back, v_side, v_action, out_final):
    im_front = Image.open(v_front)
    im_back = Image.open(v_back)
    im_side = Image.open(v_side)
    im_action = Image.open(v_action)

    quad = Image.new("RGBA", (1920, 1080), (14, 18, 24, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    
    line_col = (45, 65, 88, 220)
    draw.line([(960, 0), (960, 1080)], fill=line_col, width=2)
    draw.line([(0, 540), (1920, 540)], fill=line_col, width=2)

    labels = [
        ("VISTA 1: FRONT VIEW (CHEST UI / REINFORCED VISOR)", (25, 20)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE)", (985, 20)),
        ("VISTA 3: SIDE VIEW (PROFILE / POWER CONNECTOR)", (25, 560)),
        ("VISTA 4: ACTION 3/4 (MATCH 1:1 CON SCREENSHOT)", (985, 560))
    ]
    for lbl, pos in labels:
        draw.rectangle([pos[0]-6, pos[1]-4, pos[0]+470, pos[1]+24], fill=(12, 16, 24, 240), outline=(55, 75, 100, 255), width=1)
        draw.text(pos, lbl, fill=(245, 248, 255, 255))

    draw.rectangle([440, 515, 1480, 565], fill=(18, 22, 32, 245), outline=(235, 110, 20, 255), width=2)
    draw.text((465, 528), "ASTRA HAZARD - BOMBERO ESPACIAL V4 (MATCH 1:1 CON REFERENCIAS)", fill=(255, 180, 20, 255))

    quad.save(out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

def main():
    print("\n=======================================================")
    print(">>> GENERANDO PERSONAJE V4 CALIBRADO")
    print("=======================================================")
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    mats = create_palette()
    setup_lighting(scene)

    char_obj = build_character(mats)

    v1_front = os.path.join(RENDERS_DIR, "v4_front.png")
    v2_back = os.path.join(RENDERS_DIR, "v4_back.png")
    v3_side = os.path.join(RENDERS_DIR, "v4_side.png")
    v4_action = os.path.join(RENDERS_DIR, "v4_action.png")

    print("  Renderizando Vista Frontal...")
    render_camera_shot((0.0, -3.6, 0.95), (0.0, 0.0, 0.92), 34.0, v1_front)

    print("  Renderizando Vista Trasera...")
    render_camera_shot((0.0, 3.6, 0.95), (0.0, 0.0, 0.92), 34.0, v2_back)

    print("  Renderizando Vista Lateral...")
    render_camera_shot((3.6, 0.0, 0.95), (0.0, 0.0, 0.92), 34.0, v3_side)

    print("  Renderizando Vista Acción 3/4...")
    render_camera_shot((2.4, -2.4, 1.25), (0.0, 0.0, 0.92), 36.0, v4_action)

    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_MatchV4_4views.png")
    composite_model_sheet(v1_front, v2_back, v3_side, v4_action, out_final)

    brain_copy = os.path.join(BRAIN_DIR, "SK_Firefighter_MatchV4_4views.png")
    shutil.copy2(out_final, brain_copy)
    print(f"  [OK] Copiado a Brain: {brain_copy}")

    # Exportar FBX
    fbx_out = os.path.join(FBX_DIR, "SK_Firefighter_Official.fbx")
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = char_obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        check_existing=False,
        use_selection=True,
        axis_forward='-Y',
        axis_up='Z',
        apply_scale_options='FBX_SCALE_ALL'
    )
    print(f"  [OK] FBX Exportado: {fbx_out}")

    blend_out = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"  [OK] Blend guardado: {blend_out}")

if __name__ == "__main__":
    main()
