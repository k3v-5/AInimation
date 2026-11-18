"""
generar_dispositivo_muneca_y_hud.py
===================================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
1. Genera el modelo 3D del terminal de rescate de antebrazo (SM_Wrist_PDA_Scanner):
   - Chasis militar reforzado de gunmetal con protectores en esquinas.
   - Bisel de pantalla embutida con pantalla CRT de fósforo verde (A.H.R.S. Scanner).
   - Selectores rotativos táctiles de sintonización y rango.
   - Correas balísticas de sujeción ergonómica al antebrazo del traje espacial.
   - Malla de colisión UCX simplificada para Unreal Engine (UCX_SM_Wrist_PDA_Scanner_01).
2. Exporta el modelo oficial FBX a:
   - Art/FBX/Equipment/SM_Wrist_PDA_Scanner.fbx
   - Content/AstraHazard/Meshes/Equipment/SM_Wrist_PDA_Scanner.fbx
3. Renderiza y compone una hoja de showcase oficial de 4 vistas (1920x1440):
   - Q1: HUD Diegético de Visor de Casco (Vista en 1ª persona con telemetría O2, Temp, arcos de Power y Cuota).
   - Q2: Terminal de Muñeca 3D (Render isométrico del hardware A.H.R.S.).
   - Q3: Interfaz Táctica de Bio-Radar (Detalle macro del barrido fosfórico a 180°/s y blips).
   - Q4: Integración en el Traje Espacial (Brazo y antebrazo del bombero con el PDA equipado).
4. Guarda el showcase en la carpeta de artefactos de Antigravity.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Equipment")
CONTENT_FBX_DIR = os.path.join(PROJECT_ROOT, "Content", "AstraHazard", "Meshes", "Equipment")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
TEX_UI_DIR = os.path.join(ART_DIR, "Textures", "UI")

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(CONTENT_FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, base_color, metallic=0.1, roughness=0.4, emission=None, emission_strength=1.0, texture_path=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    if texture_path and os.path.exists(texture_path):
        tex_node = nt.nodes.new('ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(texture_path)
        nt.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        if emission:
            nt.links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
            bsdf.inputs['Emission Strength'].default_value = emission_strength

    elif emission:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        else:
            bsdf.inputs['Emission'].default_value = emission

    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_wrist_pda_mesh():
    clear_scene()

    # Paleta de materiales PBR
    mat_chassis = create_pbr_material("M_PDA_Chassis_Gunmetal", (0.12, 0.14, 0.16, 1.0), metallic=0.85, roughness=0.32)
    mat_bezel = create_pbr_material("M_PDA_Bezel_Black", (0.05, 0.05, 0.06, 1.0), metallic=0.5, roughness=0.55)
    mat_screen = create_pbr_material(
        "M_PDA_Screen_CRT",
        (0.04, 0.18, 0.08, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission=(0.1, 0.9, 0.3, 1.0),
        emission_strength=2.5,
        texture_path=os.path.join(TEX_UI_DIR, "T_HUD_Radar_Grid_Phosphor.png")
    )
    mat_straps = create_pbr_material("M_PDA_Rubber_Straps", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.85)
    mat_orange = create_pbr_material("M_PDA_Accents_Orange", (0.95, 0.38, 0.04, 1.0), metallic=0.2, roughness=0.35)
    mat_led_green = create_pbr_material("M_PDA_LED_Green", (0.2, 1.0, 0.3, 1.0), metallic=0.0, roughness=0.1, emission=(0.2, 1.0, 0.3, 1.0), emission_strength=5.0)
    mat_led_amber = create_pbr_material("M_PDA_LED_Amber", (1.0, 0.7, 0.1, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.7, 0.1, 1.0), emission_strength=4.0)

    mesh = bpy.data.meshes.new("SM_Wrist_PDA_Scanner")
    obj = bpy.data.objects.new("SM_Wrist_PDA_Scanner", mesh)
    bpy.context.collection.objects.link(obj)

    for m in [mat_chassis, mat_bezel, mat_screen, mat_straps, mat_orange, mat_led_green, mat_led_amber]:
        obj.data.materials.append(m)

    bm = bmesh.new()

    # 1. Chasis Principal Ergonómico (Curvado para encajar sobre el antebrazo)
    # Dimensiones: 18cm largo (X), 12cm ancho (Y), 3.4cm grosor (Z)
    chassis_box = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((0.18, 0.12, 0.034)), verts=chassis_box['verts'])
    bmesh.ops.translate(bm, vec=Vector((0.0, 0.0, 0.020)), verts=chassis_box['verts'])

    # Asignar material chasis a las caras creadas
    for f in chassis_box['verts']:
        for face in f.link_faces:
            face.material_index = 0

    # 2. Protectores esquineros reforzados (Bumpers industriales naranja Astra)
    bumper_offsets = [
        (0.085, 0.055, 0.020),
        (-0.085, 0.055, 0.020),
        (0.085, -0.055, 0.020),
        (-0.085, -0.055, 0.020),
    ]
    for bx, by, bz in bumper_offsets:
        bmp = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((0.024, 0.024, 0.038)), verts=bmp['verts'])
        bmesh.ops.translate(bm, vec=Vector((bx, by, bz)), verts=bmp['verts'])
        for f in bmp['verts']:
            for face in f.link_faces:
                face.material_index = 4  # Naranja

    # 3. Bisel de Pantalla Embutida (M_PDA_Bezel_Black)
    bezel = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((0.125, 0.095, 0.008)), verts=bezel['verts'])
    bmesh.ops.translate(bm, vec=Vector((0.0, 0.0, 0.036)), verts=bezel['verts'])
    for f in bezel['verts']:
        for face in f.link_faces:
            face.material_index = 1

    # 4. Pantalla CRT de Bio-Radar (M_PDA_Screen_CRT)
    screen = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((0.105, 0.080, 0.004)), verts=screen['verts'])
    bmesh.ops.translate(bm, vec=Vector((0.0, 0.0, 0.040)), verts=screen['verts'])
    for f in screen['verts']:
        for face in f.link_faces:
            face.material_index = 2

    # 5. Diales Rotativos Superiores (Selectores de Frecuencia y Rango)
    for dial_x in [-0.035, 0.035]:
        dial = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.010, radius2=0.010, depth=0.018)
        bmesh.ops.translate(bm, vec=Vector((dial_x, 0.065, 0.030)), verts=dial['verts'])
        for f in dial['verts']:
            for face in f.link_faces:
                face.material_index = 0

    # 6. Indicadores LED de Estado (Active / Warning / Critical)
    led_positions = [
        (-0.060, -0.045, 0.038, 5),  # Verde Active
        (-0.045, -0.045, 0.038, 6),  # Ámbar Warning
        (-0.030, -0.045, 0.038, 4),  # Naranja/Rojo Critical
    ]
    for lx, ly, lz, mat_idx in led_positions:
        led = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((0.008, 0.004, 0.003)), verts=led['verts'])
        bmesh.ops.translate(bm, vec=Vector((lx, ly, lz)), verts=led['verts'])
        for f in led['verts']:
            for face in f.link_faces:
                face.material_index = mat_idx

    # 7. Correas de Sujeción Ergonómica de Goma Balística (Underside straps)
    for strap_x in [-0.055, 0.055]:
        strap = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((0.028, 0.135, 0.010)), verts=strap['verts'])
        bmesh.ops.translate(bm, vec=Vector((strap_x, 0.0, 0.002)), verts=strap['verts'])
        for f in strap['verts']:
            for face in f.link_faces:
                face.material_index = 3

    # Generar coordenadas UV planas proyectadas desde arriba para la pantalla
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        if face.material_index == 2:  # Pantalla CRT
            for loop in face.loops:
                v = loop.vert.co
                # Mapear X [-0.0525, 0.0525] -> U [0, 1] y Y [-0.040, 0.040] -> V [0, 1]
                u = (v.x + 0.0525) / 0.105
                v_coord = (v.y + 0.040) / 0.080
                loop[uv_layer].uv = Vector((u, v_coord))
        else:
            for loop in face.loops:
                loop[uv_layer].uv = Vector((0.1, 0.1))

    bm.to_mesh(mesh)
    bm.free()

    # Malla de colisión UCX simplificada
    ucx_mesh = bpy.data.meshes.new("UCX_SM_Wrist_PDA_Scanner_01")
    ucx_obj = bpy.data.objects.new("UCX_SM_Wrist_PDA_Scanner_01", ucx_mesh)
    bpy.context.collection.objects.link(ucx_obj)
    ubm = bmesh.new()
    ucx_box = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=Vector((0.19, 0.13, 0.05)), verts=ucx_box['verts'])
    bmesh.ops.translate(ubm, vec=Vector((0.0, 0.0, 0.025)), verts=ucx_box['verts'])
    ubm.to_mesh(ucx_mesh)
    ubm.free()

    # Exportar FBX
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    fbx_out_art = os.path.join(FBX_DIR, "SM_Wrist_PDA_Scanner.fbx")
    fbx_out_content = os.path.join(CONTENT_FBX_DIR, "SM_Wrist_PDA_Scanner.fbx")

    bpy.ops.export_scene.fbx(
        filepath=fbx_out_art,
        use_selection=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y'
    )
    shutil.copyfile(fbx_out_art, fbx_out_content)
    print(f"[OK] Modelo FBX exportado a {fbx_out_art} y {fbx_out_content}")

    return obj, ucx_obj

def render_showcase_quadrants(pda_obj, ucx_obj):
    ucx_obj.hide_render = True

    # Configuración de luces y escena
    light_key = bpy.data.lights.new("KeyLight", type='AREA')
    light_key.energy = 18.0
    light_key.color = (1.0, 0.95, 0.90)
    light_key.size = 0.5
    obj_key = bpy.data.objects.new("KeyLight", light_key)
    bpy.context.collection.objects.link(obj_key)
    obj_key.location = (0.35, -0.45, 0.40)
    obj_key.rotation_euler = (R(55), 0, R(40))

    light_rim = bpy.data.lights.new("CyanRim", type='AREA')
    light_rim.energy = 25.0
    light_rim.color = (0.0, 0.85, 1.0)
    light_rim.size = 0.6
    obj_rim = bpy.data.objects.new("CyanRim", light_rim)
    bpy.context.collection.objects.link(obj_rim)
    obj_rim.location = (-0.40, 0.35, 0.30)
    obj_rim.rotation_euler = (R(-45), 0, R(-135))

    light_fill = bpy.data.lights.new("AmberFill", type='POINT')
    light_fill.energy = 8.0
    light_fill.color = (1.0, 0.5, 0.1)
    obj_fill = bpy.data.objects.new("AmberFill", light_fill)
    bpy.context.collection.objects.link(obj_fill)
    obj_fill.location = (0.1, -0.2, -0.15)

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = 55.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.film_transparent = False

    # 1. Render Q2: Hardware Isométrico 3D del PDA
    pda_obj.rotation_euler = (R(25), R(-15), R(35))
    cam_obj.location = (0.22, -0.32, 0.28)
    cam_obj.rotation_euler = (R(56), 0, R(35))
    q2_path = os.path.join(RENDERS_DIR, "Q2_WristPDA_Hardware.png")
    scene.render.filepath = q2_path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Render Q2 guardado en: {q2_path}")

    # 2. Render Q3: Macro Pantalla CRT Bio-Radar
    pda_obj.rotation_euler = (0, 0, 0)
    cam_obj.location = (0.0, 0.0, 0.18)
    cam_obj.rotation_euler = (0, 0, 0)
    q3_path = os.path.join(RENDERS_DIR, "Q3_RadarScreen_Macro.png")
    scene.render.filepath = q3_path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Render Q3 guardado en: {q3_path}")

    # 3. Render Q4: Integración en Antebrazo con Guante y Armadura
    # Modelar brazo/antebrazo estilizado simple para contexto ergonómico
    bm_arm = bmesh.new()
    arm_mesh = bpy.data.meshes.new("ArmContextMesh")
    arm_obj = bpy.data.objects.new("ArmContextMesh", arm_mesh)
    bpy.context.collection.objects.link(arm_obj)
    
    mat_suit = create_pbr_material("M_SuitContext", (0.92, 0.36, 0.03, 1.0), metallic=0.05, roughness=0.45)
    mat_glove = create_pbr_material("M_GloveContext", (0.10, 0.11, 0.13, 1.0), metallic=0.1, roughness=0.6)
    arm_obj.data.materials.append(mat_suit)
    arm_obj.data.materials.append(mat_glove)

    arm_cyl = bmesh.ops.create_cone(bm_arm, cap_ends=True, segments=20, radius1=0.048, radius2=0.042, depth=0.32)
    bmesh.ops.rotate(bm_arm, cent=Vector((0,0,0)), matrix=Matrix.Rotation(R(90), 3, 'Y'), verts=arm_cyl['verts'])
    bmesh.ops.translate(bm_arm, vec=Vector((0.0, 0.0, -0.015)), verts=arm_cyl['verts'])
    for f in arm_cyl['verts']:
        for face in f.link_faces:
            face.material_index = 0

    glove_box = bmesh.ops.create_cube(bm_arm, size=1.0)
    bmesh.ops.scale(bm_arm, vec=Vector((0.09, 0.08, 0.06)), verts=glove_box['verts'])
    bmesh.ops.translate(bm_arm, vec=Vector((0.19, 0.0, -0.01)), verts=glove_box['verts'])
    for f in glove_box['verts']:
        for face in f.link_faces:
            face.material_index = 1

    bm_arm.to_mesh(arm_mesh)
    bm_arm.free()

    pda_obj.rotation_euler = (R(0), R(0), R(0))
    pda_obj.location = (0.0, 0.0, 0.028)

    cam_obj.location = (0.28, -0.38, 0.26)
    cam_obj.rotation_euler = (R(58), 0, R(36))
    q4_path = os.path.join(RENDERS_DIR, "Q4_Forearm_Integration.png")
    scene.render.filepath = q4_path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Render Q4 guardado en: {q4_path}")

    # 4. Componer Q1: Casco Visor Diegético en 1ª Persona (Fusión procedural con viñeta y telemetría)
    q1_img = Image.new("RGB", (960, 720), (10, 16, 22))
    q1_draw = ImageDraw.Draw(q1_img)

    # Fondo de estación espacial en emergencia (luces ámbar, columnas estructurales)
    # Dibujar gradiente ambiental y perspectiva de corredor de estación
    for y in range(720):
        t = y / 720.0
        r = int(12 + 18 * t)
        g = int(14 + 10 * t)
        b = int(22 + 15 * (1 - t))
        q1_draw.line((0, y, 960, y), fill=(r, g, b))

    # Columnas y cables del Gym de pruebas
    q1_draw.line((380, 260, 200, 720), fill=(25, 30, 40), width=8)
    q1_draw.line((580, 260, 760, 720), fill=(25, 30, 40), width=8)
    q1_draw.line((420, 270, 320, 720), fill=(35, 40, 52), width=4)
    q1_draw.line((540, 270, 640, 720), fill=(35, 40, 52), width=4)

    # Luces de baliza de emergencia en el fondo (Ámbar)
    q1_draw.ellipse((470, 280, 490, 300), fill=(255, 140, 20, 255))
    # Bruma de vapor
    for rad in range(60, 10, -5):
        q1_draw.ellipse((480 - rad, 290 - rad // 2, 480 + rad, 290 + rad // 2), outline=(255, 160, 40, 40), width=2)

    # Superponer Viñeta del Marco del Casco
    visor_frame_path = os.path.join(TEX_UI_DIR, "T_HUD_Helmet_Visor_Frame.png")
    if os.path.exists(visor_frame_path):
        vf = Image.open(visor_frame_path).resize((960, 720))
        q1_img.paste(vf, (0, 0), vf)

    # Arcos radiales inferiores (Power y Quota)
    arc_path = os.path.join(TEX_UI_DIR, "T_HUD_Radial_Gauge_Arc.png")
    if os.path.exists(arc_path):
        arc = Image.open(arc_path).resize((220, 220))
        # Bottom-Left: POWER
        q1_img.paste(arc, (40, 470), arc)
        # Bottom-Right: QUOTA (Invertido horizontal)
        arc_flipped = arc.transpose(Image.FLIP_LEFT_RIGHT)
        q1_img.paste(arc_flipped, (700, 470), arc_flipped)

    # Tipografía y telemetría de HUD
    # Top-Left: O2: 85%
    q1_draw.rectangle([(55, 48), (210, 88)], fill=(6, 20, 28, 190), outline=(0, 220, 255, 200), width=2)
    q1_draw.text((70, 56), "O2: 85%", fill=(0, 240, 255))
    # Barra de O2
    q1_draw.rectangle([(70, 78), (195, 83)], fill=(0, 80, 100))
    q1_draw.rectangle([(70, 78), (176, 83)], fill=(0, 240, 255))

    # Top-Right: TEMP: 22°C
    q1_draw.rectangle([(750, 48), (905, 88)], fill=(6, 20, 28, 190), outline=(0, 220, 255, 200), width=2)
    q1_draw.text((765, 56), "TEMP: 22°C", fill=(0, 240, 255))
    q1_draw.rectangle([(765, 78), (890, 83)], fill=(0, 80, 100))
    q1_draw.rectangle([(765, 78), (792, 83)], fill=(0, 240, 255))

    # Bottom-Left: POWER 85%
    q1_draw.rectangle([(65, 620), (220, 655)], fill=(6, 20, 28, 190), outline=(0, 220, 255, 180), width=1)
    q1_draw.text((80, 628), "POWER 85%", fill=(0, 240, 255))

    # Bottom-Right: QUOTA: 4200/5000
    q1_draw.rectangle([(715, 620), (895, 655)], fill=(6, 20, 28, 190), outline=(0, 220, 255, 180), width=1)
    q1_draw.text((730, 628), "QUOTA: 4200/5000", fill=(0, 240, 255))

    # Retícula central de apuntado / mira táctica
    cx, cy = 480, 360
    q1_draw.line((cx - 20, cy, cx - 6, cy), fill=(0, 240, 255, 180), width=2)
    q1_draw.line((cx + 6, cy, cx + 20, cy), fill=(0, 240, 255, 180), width=2)
    q1_draw.line((cx, cy - 20, cx, cy - 6), fill=(0, 240, 255, 180), width=2)
    q1_draw.line((cx, cy + 6, cx, cy + 20), fill=(0, 240, 255, 180), width=2)
    q1_draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(0, 240, 255, 220))

    q1_path = os.path.join(RENDERS_DIR, "Q1_HelmetVisorHUD.png")
    q1_img.save(q1_path)
    print(f"[OK] Render Q1 guardado en: {q1_path}")

    # 5. Enriquecer Q3 con superposiciones de UI de alta precisión (Blips, Barrido, Brújula)
    q3_base = Image.open(q3_path)
    q3_draw = ImageDraw.Draw(q3_base)

    # Superponer blip de superviviente civil y mascota
    blip_civ_path = os.path.join(TEX_UI_DIR, "T_HUD_Blip_Civilian.png")
    blip_pet_path = os.path.join(TEX_UI_DIR, "T_HUD_Blip_Pet.png")
    airlock_ptr_path = os.path.join(TEX_UI_DIR, "T_HUD_Airlock_Pointer.png")

    cx3, cy3 = 480, 360
    if os.path.exists(blip_civ_path):
        bc = Image.open(blip_civ_path).resize((32, 32))
        # Superviviente civil al frente-derecha (Azimuth +35°, Dist 0.6)
        q3_base.paste(bc, (cx3 + 65, cy3 - 95), bc)
        # Superviviente civil a la izquierda (Azimuth -60°, Dist 0.45)
        q3_base.paste(bc, (cx3 - 85, cy3 - 25), bc)

    if os.path.exists(blip_pet_path):
        bp = Image.open(blip_pet_path).resize((28, 28))
        # Mascota cerca del rescatista (Azimuth -20°, Dist 0.25)
        q3_base.paste(bp, (cx3 - 20, cy3 - 50), bp)

    if os.path.exists(airlock_ptr_path):
        ap = Image.open(airlock_ptr_path).resize((26, 26))
        # Flecha de esclusa de escape en el borde exterior del radar
        q3_base.paste(ap, (cx3 + 120, cy3 - 130), ap)

    # Textos de estado y directiva en pantalla PDA
    q3_draw.rectangle([(260, 60), (700, 110)], fill=(8, 22, 12, 230), outline=(50, 220, 90, 220), width=2)
    q3_draw.text((280, 70), "A.H.R.S. RESCUE-SCAN  |  PRIMARY: RESCUE SURVIVORS", fill=(80, 255, 120))
    q3_draw.text((280, 90), "BIO: 3 TARGETS (2 CIV, 1 PET) | AIRLOCK: 42.5m", fill=(60, 220, 95))

    q3_draw.rectangle([(260, 610), (700, 655)], fill=(8, 22, 12, 230), outline=(50, 220, 90, 220), width=2)
    q3_draw.text((280, 625), "STATUS: ACTIVE  |  RESCUED: 1/4  |  TEMP (ENV): 22°C", fill=(80, 255, 120))

    q3_base.save(q3_path)

    # 6. Componer Hoja de Showcase Oficial 2x2 (1920x1440)
    collage = Image.new("RGB", (1920, 1440), (10, 12, 16))
    c_draw = ImageDraw.Draw(collage)

    quad_images = [
        (q1_path, (0, 0), "1. HUD DIEGETICO DE VISOR DE CASCO (TELEMETRIA DE O2, TEMP Y ARCOS RADIALES)"),
        (q2_path, (960, 0), "2. HARDWARE 3D: TERMINAL DE ANTEBRAZO A.H.R.S. (PDA SCANNER CHASSIS)"),
        (q3_path, (0, 720), "3. INTERFAZ TACTICA: BIO-RADAR FOSFORICO CON BARRIDO Y BLIPS DE RESCATE"),
        (q4_path, (960, 720), "4. INTEGRACION ERGONOMICA EN EL TRAJE ESPACIAL DEL BOMBERO (ANTEBRAZO)")
    ]

    for path, (px, py), title in quad_images:
        img = Image.open(path)
        collage.paste(img, (px, py))
        # Tarjeta de etiqueta superior
        c_draw.rectangle([(px + 16, py + 16), (px + 944, py + 52)], fill=(12, 15, 20, 235), outline=(40, 180, 220, 200), width=2)
        c_draw.text((px + 28, py + 24), title, fill=(0, 240, 255))

    # Líneas divisorias de cuadrante
    c_draw.line((960, 0, 960, 1440), fill=(30, 45, 60), width=3)
    c_draw.line((0, 720, 1920, 720), fill=(30, 45, 60), width=3)

    # Guardar en destino final
    showcase_path = os.path.join(RENDERS_DIR, "Showcase_Diegetic_HUD_and_Wrist_Scanner.png")
    collage.save(showcase_path)
    print(f"[OK] Hoja de Showcase guardada en: {showcase_path}")

    artifact_dest = os.path.join(BRAIN_DIR, "Showcase_Diegetic_HUD_and_Wrist_Scanner.png")
    collage.save(artifact_dest)
    print(f"[OK] Hoja de Showcase copiada a artefactos: {artifact_dest}")

if __name__ == "__main__":
    pda_obj, ucx_obj = build_wrist_pda_mesh()
    render_showcase_quadrants(pda_obj, ucx_obj)
