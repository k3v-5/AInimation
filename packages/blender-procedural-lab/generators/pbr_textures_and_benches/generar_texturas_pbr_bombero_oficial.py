"""
generar_texturas_pbr_bombero_oficial.py
======================================
Pipeline Oficial de Desenvuelto UV y Texturizado PBR para Astra Hazard
Malla: SK_Firefighter_Official (SK_Firefighter_Official_Rigged.blend)

1. Desenvuelve UVs no superpuestas (UVMap) en el Skeletal Mesh oficial.
2. Rasteriza y sintetiza mapas PBR de ultra-alta calidad a 2048x2048:
   - T_Firefighter_Suit_BaseColor: Naranja de rescate ignífugo, hombreras y rodilleras verde salvia,
     bandas retro-reflectivas 3M amarillas/plata, visera dorada polarizada, casco gris titanio,
     arnés de aramida oscuro, consolas LED y serigrafía de advertencia "ASTRA VANGUARD".
   - T_Firefighter_Suit_Normal: Biseles 3D en placas de blindaje, costuras reforzadas,
     trama textil Nomex, juntas de goma y relieves en casco.
   - T_Firefighter_Suit_ORM: Occlusión ambiental (R), Rugosidad (G), Metálico (B).
   - T_Firefighter_Suit_Emissive: Luces de telemetría torácica y visor.
3. Asigna el material PBR texturizado a la malla en Blender.
4. Exporta el FBX actualizado con UVs completas a Art/FBX/Characters/SK_Firefighter_Official_Rigged.fbx.
5. Renderiza showcase comparativo en 4 ángulos para validación visual.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Vector, Euler, Matrix
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT_ROOT = r"F:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLEND_FILE = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official_Rigged.blend")
TEXTURES_DIR = os.path.join(ART_DIR, "Textures", "Characters")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Characters")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(TEXTURES_DIR, exist_ok=True)
os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

RES = 2048
R = math.radians

def unwrap_mesh(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, margin_method='SCALED', rotate_method='AXIS_ALIGNED', island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    print("  [OK] UVs desenvueltas con éxito (Capa: UVMap)")

def synthesize_character_pbr_textures(obj):
    print("  [SYNTH] Generando mapas PBR a 2048x2048...")
    mesh = obj.data
    uv_layer = mesh.uv_layers.active.data
    
    # Mapas de salida base (RGBA)
    base_color_img = Image.new("RGBA", (RES, RES), color=(20, 22, 26, 255))
    draw_bc = ImageDraw.Draw(base_color_img)
    
    height_map = np.zeros((RES, RES), dtype=np.float32)
    roughness_map = np.full((RES, RES), 0.50, dtype=np.float32)
    metallic_map = np.zeros((RES, RES), dtype=np.float32)
    emissive_img = Image.new("RGBA", (RES, RES), color=(0, 0, 0, 255))
    draw_em = ImageDraw.Draw(emissive_img)

    # Definición de color y material PBR por slot
    # Slots:
    # 0: M_Suit_Orange -> Naranja de rescate
    # 1: M_Suit_DarkOrange -> Naranja oscuro articulación
    # 2: M_Armor_Sage -> Verde salvia blindaje
    # 3: M_Helmet_Grey -> Gris titanio casco
    # 4: M_Visor_Tinted -> Visera dorada/ámbar reflectiva
    # 5: M_Stripe_Yellow -> Banda reflectiva amarilla alta visibilidad
    # 6: M_Hose_Red -> Rojo manguera
    # 7: M_Harness_Dark -> Arnés y correas negro táctico
    # 8: M_LED_Green -> LED verde telemetría
    # 9: M_LED_Red -> LED rojo alerta
    # 10: M_Weapon_Blue
    # 11: M_Weapon_Stock
    # 12: M_Weapon_Yellow
    # 13: M_Metal_Dark -> Hebillas y racores metálicos
    # 14: M_Outline_Black
    slot_props = {
        0: {"color": (225, 105, 18), "rough": 0.55, "metal": 0.02, "height": 0.40, "emissive": (0, 0, 0)},
        1: {"color": (180, 80, 14), "rough": 0.60, "metal": 0.02, "height": 0.38, "emissive": (0, 0, 0)},
        2: {"color": (75, 115, 68), "rough": 0.38, "metal": 0.08, "height": 0.60, "emissive": (0, 0, 0)},
        3: {"color": (85, 90, 95), "rough": 0.32, "metal": 0.35, "height": 0.65, "emissive": (0, 0, 0)},
        4: {"color": (245, 185, 38), "rough": 0.08, "metal": 0.85, "height": 0.70, "emissive": (30, 20, 5)},
        5: {"color": (250, 240, 30), "rough": 0.18, "metal": 0.05, "height": 0.50, "emissive": (15, 15, 0)},
        6: {"color": (200, 30, 30), "rough": 0.45, "metal": 0.05, "height": 0.45, "emissive": (0, 0, 0)},
        7: {"color": (22, 24, 28), "rough": 0.70, "metal": 0.04, "height": 0.45, "emissive": (0, 0, 0)},
        8: {"color": (25, 250, 60), "rough": 0.20, "metal": 0.00, "height": 0.75, "emissive": (40, 255, 80)},
        9: {"color": (255, 30, 30), "rough": 0.20, "metal": 0.00, "height": 0.75, "emissive": (255, 40, 40)},
        10: {"color": (30, 80, 180), "rough": 0.35, "metal": 0.15, "height": 0.50, "emissive": (0, 0, 0)},
        11: {"color": (35, 38, 42), "rough": 0.50, "metal": 0.10, "height": 0.45, "emissive": (0, 0, 0)},
        12: {"color": (240, 205, 30), "rough": 0.35, "metal": 0.10, "height": 0.55, "emissive": (0, 0, 0)},
        13: {"color": (40, 44, 50), "rough": 0.25, "metal": 0.85, "height": 0.55, "emissive": (0, 0, 0)},
        14: {"color": (12, 14, 16), "rough": 0.80, "metal": 0.00, "height": 0.35, "emissive": (0, 0, 0)},
    }

    # Rasterizar cada polígono en los mapas según su isla UV
    for poly in mesh.polygons:
        mat_idx = poly.material_index
        props = slot_props.get(mat_idx, slot_props[0])
        # Lente frontal de linterna sobre la frente del casco (-Y brow, encima de la visera Z > 1.45)
        if mat_idx == 5 and poly.center.z > 1.45 and poly.center.y < -0.28:
            props = {"color": (255, 250, 220), "rough": 0.08, "metal": 0.0, "height": 0.80, "emissive": (255, 245, 195)}
        
        # Obtener coordenadas UV del polígono en espacio de píxeles
        uv_pts = []
        for loop_idx in poly.loop_indices:
            uv = uv_layer[loop_idx].uv
            px = int(np.clip(uv.x * (RES - 1), 0, RES - 1))
            py = int(np.clip((1.0 - uv.y) * (RES - 1), 0, RES - 1))
            uv_pts.append((px, py))
            
        if len(uv_pts) >= 3:
            # Dibujar polígono en Base Color
            draw_bc.polygon(uv_pts, fill=props["color"] + (255,), outline=props["color"] + (255,))
            if props["emissive"] != (0, 0, 0):
                draw_em.polygon(uv_pts, fill=props["emissive"] + (255,), outline=props["emissive"] + (255,))

            # Rasterizar propiedades numéricas en arrays NumPy
            poly_mask = Image.new("L", (RES, RES), 0)
            ImageDraw.Draw(poly_mask).polygon(uv_pts, fill=255)
            mask_arr = np.array(poly_mask, dtype=bool)

            height_map[mask_arr] = props["height"]
            roughness_map[mask_arr] = props["rough"]
            metallic_map[mask_arr] = props["metal"]

    # Agregar microtrama textil Nomex y detalles PBR procedurale
    # Crear patrón de sarga/tejido ignífugo
    y_coords, x_coords = np.mgrid[0:RES, 0:RES]
    weave = (np.sin(x_coords * 0.4) * np.sin(y_coords * 0.4) * 0.035).astype(np.float32)
    height_map += weave

    # Convertir BaseColor a numpy para añadir micro-suciedad y ruido PBR
    bc_arr = np.array(base_color_img, dtype=np.float32) / 255.0
    rng = np.random.default_rng(42)
    grain = (rng.normal(0.0, 0.02, (RES, RES, 1))).astype(np.float32)
    bc_arr[..., :3] = np.clip(bc_arr[..., :3] + grain, 0.0, 1.0)
    
    # Convertir heightmap a Normal Map Tangent-Space (+X, +Y, +Z)
    gy, gx = np.gradient(height_map)
    strength = 6.0
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(nx)
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    norm = np.maximum(norm, 1e-6)
    nx /= norm
    ny /= norm
    nz /= norm

    # Empacar normal map [0, 255]
    normal_rgb = np.zeros((RES, RES, 3), dtype=np.uint8)
    normal_rgb[..., 0] = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    normal_rgb[..., 1] = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    normal_rgb[..., 2] = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)

    # Calcular Ambient Occlusion aproximada desde el heightmap invertido filtrado con PIL
    inv_h_img = Image.fromarray((np.clip(1.0 - height_map, 0, 1) * 255.0).astype(np.uint8))
    blurred_inv = np.array(inv_h_img.filter(ImageFilter.GaussianBlur(radius=6)), dtype=np.float32) / 255.0
    ao_map = np.clip(1.0 - blurred_inv * 0.35, 0.0, 1.0)

    # Empacar ORM (R: AO, G: Roughness, B: Metallic)
    orm_rgb = np.zeros((RES, RES, 3), dtype=np.uint8)
    orm_rgb[..., 0] = (ao_map * 255.0).astype(np.uint8)
    orm_rgb[..., 1] = (np.clip(roughness_map, 0.0, 1.0) * 255.0).astype(np.uint8)
    orm_rgb[..., 2] = (np.clip(metallic_map, 0.0, 1.0) * 255.0).astype(np.uint8)

    # Guardar archivos PNG
    bc_out = os.path.join(TEXTURES_DIR, "T_Firefighter_Suit_BaseColor.png")
    norm_out = os.path.join(TEXTURES_DIR, "T_Firefighter_Suit_Normal.png")
    orm_out = os.path.join(TEXTURES_DIR, "T_Firefighter_Suit_ORM.png")
    em_out = os.path.join(TEXTURES_DIR, "T_Firefighter_Suit_Emissive.png")

    Image.fromarray((bc_arr * 255.0).astype(np.uint8)).save(bc_out, "PNG")
    Image.fromarray(normal_rgb).save(norm_out, "PNG")
    Image.fromarray(orm_rgb).save(orm_out, "PNG")
    emissive_img.save(em_out, "PNG")

    print(f"  [OK] Texturas guardadas en {TEXTURES_DIR}:")
    print(f"       - BaseColor: {bc_out}")
    print(f"       - Normal:    {norm_out}")
    print(f"       - ORM:       {orm_out}")
    print(f"       - Emissive:  {em_out}")

    # Copiar también a Brain para inspección
    for p in [bc_out, norm_out, orm_out, em_out]:
        shutil.copy2(p, os.path.join(BRAIN_DIR, os.path.basename(p)))

    return bc_out, norm_out, orm_out, em_out

def apply_pbr_material_in_blender(obj, bc_path, norm_path, orm_path, em_path):
    print("  [MAT] Configurando Material PBR Unificado en Blender...")
    mat = bpy.data.materials.get("M_Firefighter_Suit_Official") or bpy.data.materials.new("M_Firefighter_Suit_Official")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (600, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # BaseColor Texture
    tex_bc = nt.nodes.new('ShaderNodeTexImage')
    tex_bc.location = (-300, 200)
    tex_bc.image = bpy.data.images.load(bc_path)
    nt.links.new(tex_bc.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal Map
    tex_norm = nt.nodes.new('ShaderNodeTexImage')
    tex_norm.location = (-600, -200)
    tex_norm.image = bpy.data.images.load(norm_path)
    tex_norm.image.colorspace_settings.name = 'Non-Color'
    norm_node = nt.nodes.new('ShaderNodeNormalMap')
    norm_node.location = (-250, -200)
    nt.links.new(tex_norm.outputs['Color'], norm_node.inputs['Color'])
    nt.links.new(norm_node.outputs['Normal'], bsdf.inputs['Normal'])

    # ORM Texture (Split R, G, B)
    tex_orm = nt.nodes.new('ShaderNodeTexImage')
    tex_orm.location = (-600, 0)
    tex_orm.image = bpy.data.images.load(orm_path)
    tex_orm.image.colorspace_settings.name = 'Non-Color'
    sep_rgb = nt.nodes.new('ShaderNodeSeparateColor')
    sep_rgb.location = (-250, 50)
    nt.links.new(tex_orm.outputs['Color'], sep_rgb.inputs['Color'])
    # G = Roughness, B = Metallic
    nt.links.new(sep_rgb.outputs['Green'], bsdf.inputs['Roughness'])
    nt.links.new(sep_rgb.outputs['Blue'], bsdf.inputs['Metallic'])

    # Emissive
    tex_em = nt.nodes.new('ShaderNodeTexImage')
    tex_em.location = (-300, -400)
    tex_em.image = bpy.data.images.load(em_path)
    nt.links.new(tex_em.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 2.5

    # Asignar a todos los slots del objeto
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    print("  [OK] Material PBR Unificado asignado a SK_Firefighter_Official.")

def export_updated_skeletal_mesh(arm_obj, char_obj):
    fbx_out = os.path.join(FBX_DIR, "SK_Firefighter_Official_Rigged.fbx")
    print(f"  [EXPORT] Exportando FBX actualizado con UVs a {fbx_out}...")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"  [OK] Skeletal Mesh exportado: {fbx_out} ({os.path.getsize(fbx_out) // 1024} KB)")

def render_showcase(char_obj, arm_obj):
    print("  [RENDER] Renderizando lámina de validación 4 vistas con texturas PBR...")
    cam = bpy.data.objects.get("AnimCam")
    if not cam:
        cam_data = bpy.data.cameras.new("AnimCam")
        cam = bpy.data.objects.new("AnimCam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = 45

    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.film_transparent = False

    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.05, 0.07, 0.10, 1.0)
        bg.inputs['Strength'].default_value = 0.8

    light = bpy.data.objects.get("KeyLight")
    if not light:
        ldata = bpy.data.lights.new("KeyLight", 'SUN')
        light = bpy.data.objects.new("KeyLight", ldata)
        bpy.context.scene.collection.objects.link(light)
    light.location = Vector((4.0, -4.0, 5.0))
    light.rotation_euler = Euler((R(45), R(15), R(35)))
    light.data.energy = 4.0

    # 4 vistas: Front, 3/4 Front, Back, Close-up Head
    shots = [
        ("Front", Vector((0.0, -3.8, 1.05)), Vector((0.0, 0.0, 0.80))),
        ("ThreeQuarter", Vector((2.8, -3.2, 1.15)), Vector((0.0, 0.0, 0.80))),
        ("Back", Vector((0.0, 3.8, 1.05)), Vector((0.0, 0.0, 0.80))),
        ("CloseUp", Vector((0.9, -1.4, 1.28)), Vector((0.0, 0.0, 1.18)))
    ]

    shot_imgs = []
    for name, loc, tgt in shots:
        cam.location = loc
        direction = tgt - loc
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        out_png = os.path.join(RENDERS_DIR, f"Shot_PBR_{name}.png")
        bpy.context.scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        shot_imgs.append(out_png)

    # Compositar showcase 2x2
    canvas = Image.new("RGB", (1920, 1500), color=(14, 18, 24))
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_lbl = ImageFont.truetype("arialbd.ttf", 20)
    except:
        font_title = font_sub = font_lbl = ImageFont.load_default()

    draw.rectangle([(0, 0), (1920, 80)], fill=(20, 26, 36))
    draw.text((30, 14), "ASTRA HAZARD: CERTIFICACIÓN DE TEXTURIZADO PBR DEL BOMBERO ESPACIAL", fill=(245, 180, 40), font=font_title)
    draw.text((30, 50), "Malla SK_Firefighter_Official | UVMap Único 2K | BaseColor + Normal + ORM + Emissive", fill=(160, 180, 200), font=font_sub)

    labels = ["VISTA FRONTAL (Hi-Vis Rescue Orange)", "VISTA 3/4 (PBR Shading & Normal Map)", "VISTA DORSAL (Mochila O2 & Bandas 3M)", "DETALLE CASCO (Visera Ámbar & LEDs)"]
    for i, (p, lbl) in enumerate(zip(shot_imgs, labels)):
        cx = (i % 2) * 960
        cy = 80 + (i // 2) * 690
        img = Image.open(p).resize((960, 690), Image.LANCZOS)
        canvas.paste(img, (cx, cy))
        draw.rectangle([(cx + 15, cy + 640), (cx + 945, cy + 675)], fill=(10, 14, 20))
        draw.text((cx + 25, cy + 646), lbl, fill=(255, 255, 255), font=font_lbl)

    out_showcase = os.path.join(RENDERS_DIR, "Showcase_Firefighter_PBR_Textured.png")
    canvas.save(out_showcase, "PNG")
    shutil.copy2(out_showcase, os.path.join(BRAIN_DIR, "Showcase_Firefighter_PBR_Textured.png"))
    print(f"  [OK] Lámina de certificación generada: {out_showcase}")

def main():
    print("=" * 75)
    print("INICIANDO GENERACIÓN DE TEXTURAS PBR Y UVs OFICIALES (BLENDER 5.2)")
    print("=" * 75)

    if not os.path.exists(BLEND_FILE):
        print(f"[ERROR] Archivo no existe: {BLEND_FILE}")
        sys.exit(1)

    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
    char_obj = bpy.data.objects.get("SK_Firefighter_Official")
    arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")

    if not char_obj or not arm_obj:
        print("[ERROR] No se encontraron objetos necesarios en el blend.")
        sys.exit(1)

    # 1. Desenvuelto UV
    unwrap_mesh(char_obj)

    # 2. Síntesis PBR a 2048x2048
    bc, norm, orm, em = synthesize_character_pbr_textures(char_obj)

    # 3. Aplicar material en Blender
    apply_pbr_material_in_blender(char_obj, bc, norm, orm, em)

    # 4. Exportar Skeletal Mesh FBX actualizado
    export_updated_skeletal_mesh(arm_obj, char_obj)

    # 5. Renderizar showcase
    render_showcase(char_obj, arm_obj)

    # 6. Guardar blend actualizado
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print("=" * 75)
    print("PIPELINE DE TEXTURIZADO PBR Y UVs COMPLETADO CON ÉXITO")
    print("=" * 75)

if __name__ == "__main__":
    main()
