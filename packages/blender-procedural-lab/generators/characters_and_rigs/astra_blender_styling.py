# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Modulo Comun de Estilo Comic Cel-Shading, PBR Stylized y Pipeline de Renderizado
# Blender 5.2 LTS - EEVEE / Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def R(degrees):
    return math.radians(degrees)

def reset_comic_scene(bg_color=(0.02, 0.025, 0.035, 1.0), bg_strength=0.55, ink_thickness=2.6):
    MAT_CACHE.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    
    # Entorno cosmico de estudio
    world = bpy.data.worlds.new("World_ComicStudio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = bg_color
    w_bg.inputs['Strength'].default_value = bg_strength
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    # Freestyle Lineart (Estilo Novela Grafica / Comic con tinta negra)
    scene.render.use_freestyle = True
    rl = scene.view_layers["ViewLayer"]
    rl.use_freestyle = True
    rl.freestyle_settings.as_render_pass = False
    rl.freestyle_settings.crease_angle = math.radians(135.0)
    
    linesets = rl.freestyle_settings.linesets
    while linesets:
        linesets.remove(linesets[0])
    
    ls = linesets.new("ComicInkOutline")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_material_boundary = True
    
    linestyle = bpy.data.linestyles.new("InkStyle")
    linestyle.color = (0.02, 0.02, 0.03)
    linestyle.thickness = ink_thickness
    ls.linestyle = linestyle
    
    return scene

def create_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

def add_bevel(obj, width=0.015, segments=3, angle_limit=35.0):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle_limit)
    return mod

MAT_CACHE = {}

def get_comic_material(name, base_color=(0.5, 0.5, 0.5), roughness=0.4, metallic=0.0,
                       emissive_color=(0,0,0,1), emissive_strength=0.0,
                       alpha=1.0, is_transparent=False,
                       tex_pack=None, uv_scale=(1.0, 1.0, 1.0), tex_mix=0.35, blend_type='MIX'):
    if name in MAT_CACHE and MAT_CACHE[name].name in bpy.data.materials:
        return MAT_CACHE[name]
        
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (200, 0)
    node_bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    if emissive_strength > 0.0:
        node_bsdf.inputs['Emission Color'].default_value = emissive_color
        node_bsdf.inputs['Emission Strength'].default_value = emissive_strength
        
    if is_transparent:
        node_bsdf.inputs['Alpha'].default_value = alpha
        try:
            mat.surface_render_method = 'BLENDED'
        except:
            mat.blend_method = 'BLEND'
            
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    if tex_pack:
        basecolor_path = os.path.join(TEXTURES_MODULAR, f"{tex_pack}_BaseColor.png")
        normal_path = os.path.join(TEXTURES_MODULAR, f"{tex_pack}_Normal.png")
        
        coord = nodes.new(type='ShaderNodeTexCoord')
        coord.location = (-800, 150)
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 150)
        mapping.inputs['Scale'].default_value = uv_scale
        links.new(coord.outputs['Object'], mapping.inputs['Vector'])
        
        if os.path.exists(basecolor_path):
            tex_col = nodes.new(type='ShaderNodeTexImage')
            tex_col.location = (-350, 200)
            tex_col.projection = 'BOX'
            tex_col.projection_blend = 0.2
            tex_col.image = bpy.data.images.load(basecolor_path)
            links.new(mapping.outputs['Vector'], tex_col.inputs['Vector'])
            
            mix_rgb = nodes.new(type='ShaderNodeMix')
            mix_rgb.data_type = 'RGBA'
            if blend_type == 'MULTIPLY':
                mix_rgb.blend_type = 'MULTIPLY'
            mix_rgb.location = (-50, 200)
            mix_rgb.inputs['Factor'].default_value = tex_mix
            mix_rgb.inputs[6].default_value = (*base_color, 1.0)
            links.new(tex_col.outputs['Color'], mix_rgb.inputs[7])
            links.new(mix_rgb.outputs[2], node_bsdf.inputs['Base Color'])
            
        if os.path.exists(normal_path):
            tex_norm = nodes.new(type='ShaderNodeTexImage')
            tex_norm.location = (-350, -200)
            tex_norm.projection = 'BOX'
            tex_norm.projection_blend = 0.2
            img_norm = bpy.data.images.load(normal_path)
            img_norm.colorspace_settings.name = 'Non-Color'
            tex_norm.image = img_norm
            links.new(mapping.outputs['Vector'], tex_norm.inputs['Vector'])
            
            node_norm = nodes.new(type='ShaderNodeNormalMap')
            node_norm.location = (-100, -200)
            node_norm.inputs['Strength'].default_value = 0.35
            links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
            links.new(node_norm.outputs['Normal'], node_bsdf.inputs['Normal'])

    MAT_CACHE[name] = mat
    return mat

def create_box(name, size=(1,1,1), loc=(0,0,0), rot=(0,0,0), mat=None, bevel=True, bevel_w=0.015, col=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = Euler(rot)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    if bevel:
        add_bevel(obj, width=bevel_w)
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(obj)
    return obj

def create_cylinder(name, radius=0.5, depth=1.0, segments=24, loc=(0,0,0), rot=(0,0,0), mat=None, bevel=True, bevel_w=0.015, col=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = Euler(rot)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    if bevel:
        add_bevel(obj, width=bevel_w)
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(obj)
    return obj

def create_cone(name, radius1=0.5, radius2=0.0, depth=1.0, segments=24, loc=(0,0,0), rot=(0,0,0), mat=None, col=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = Euler(rot)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius1, radius2=radius2, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(obj)
    return obj

def create_torus(name, major_r=1.0, minor_r=0.2, major_seg=32, minor_seg=16, loc=(0,0,0), rot=(0,0,0), mat=None, col=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = Euler(rot)
    bm = bmesh.new()
    verts = []
    for i in range(major_seg):
        u = 2.0 * math.pi * i / major_seg
        cos_u = math.cos(u)
        sin_u = math.sin(u)
        for j in range(minor_seg):
            v = 2.0 * math.pi * j / minor_seg
            x = (major_r + minor_r * math.cos(v)) * cos_u
            y = (major_r + minor_r * math.cos(v)) * sin_u
            z = minor_r * math.sin(v)
            verts.append(bm.verts.new((x, y, z)))
    bm.verts.ensure_lookup_table()
    for i in range(major_seg):
        next_i = (i + 1) % major_seg
        for j in range(minor_seg):
            next_j = (j + 1) % minor_seg
            v0 = verts[i * minor_seg + j]
            v1 = verts[next_i * minor_seg + j]
            v2 = verts[next_i * minor_seg + next_j]
            v3 = verts[i * minor_seg + next_j]
            bm.faces.new((v0, v1, v2, v3))
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(obj)
    return obj

def get_hazard_stripes_material():
    mat_name = "M_Cartoon_Hazard_Stripes"
    if mat_name in bpy.data.materials:
        return bpy.data.materials[mat_name]
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.interpolation = 'CONSTANT'
    node_ramp.color_ramp.elements[0].position = 0.0
    node_ramp.color_ramp.elements[0].color = (0.95, 0.70, 0.05, 1.0) # Amarillo Hazard
    node_ramp.color_ramp.elements[1].position = 0.5
    node_ramp.color_ramp.elements[1].color = (0.08, 0.09, 0.11, 1.0) # Negro Industrial
    
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'DIAGONAL'
    node_wave.inputs['Scale'].default_value = 8.0
    node_wave.inputs['Distortion'].default_value = 0.0
    
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    
    links.new(node_coord.outputs['Object'], node_wave.inputs['Vector'])
    links.new(node_wave.outputs['Color'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    node_bsdf.inputs['Roughness'].default_value = 0.35
    node_bsdf.inputs['Metallic'].default_value = 0.15
    return mat

def create_analog_gauge(name, loc=(0,0,0), rot=(0,0,0), radius=0.25, depth=0.12, col=None):
    root = bpy.data.objects.new(f"RootGauge_{name}", None)
    root.location = loc
    root.rotation_euler = Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])))
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(root)
    
    brass_mat = get_comic_material("Mat_Gauge_Brass", base_color=(0.85, 0.65, 0.15), roughness=0.3, metallic=0.85)
    dial_mat = get_comic_material("Mat_Gauge_Face", base_color=(0.95, 0.94, 0.90), roughness=0.2, metallic=0.0)
    needle_mat = get_comic_material("Mat_Gauge_Needle", base_color=(0.90, 0.10, 0.08), roughness=0.2, metallic=0.1,
                                    emissive_color=(1.0, 0.1, 0.05, 1.0), emissive_strength=1.5)
    
    # Bisel de laton
    bezel = create_cylinder(f"{name}_Bezel", radius=radius, depth=depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=brass_mat, col=col)
    bezel.parent = root
    
    # Cara del manometro
    face = create_cylinder(f"{name}_Face", radius=radius * 0.85, depth=0.02,
                           loc=(0, -depth * 0.45, 0), rot=(0, 0, 0), mat=dial_mat, col=col)
    face.parent = root
    
    # Aguja roja triangular cartoon
    needle = create_cone(f"{name}_Needle", radius1=radius * 0.12, radius2=0.01, depth=radius * 0.65,
                         loc=(0, -depth * 0.52, radius * 0.2), rot=(0, 0, math.radians(45)),
                         mat=needle_mat, col=col)
    needle.parent = root
    return root

def create_piston_joint(name, loc=(0,0,0), rot=(0,0,0), scale=1.0, col=None):
    root = bpy.data.objects.new(f"RootJoint_{name}", None)
    root.location = loc
    root.rotation_euler = Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])))
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(root)
    
    dark_metal = get_comic_material("Mat_Joint_Dark", base_color=(0.18, 0.20, 0.24), roughness=0.35, metallic=0.85)
    chrome_mat = get_comic_material("Mat_Joint_Chrome", base_color=(0.85, 0.88, 0.92), roughness=0.15, metallic=0.95)
    hazard_yellow = get_comic_material("Mat_Joint_Yellow", base_color=(0.95, 0.65, 0.10), roughness=0.30, metallic=0.2)
    
    # Esfera / cilindro de rotula
    hub = create_cylinder(f"{name}_PivotHub", radius=0.16 * scale, depth=0.28 * scale,
                          rot=(0, math.radians(90), 0), loc=(0, 0, 0), mat=dark_metal, col=col)
    hub.parent = root
    
    # Pasador central
    pin = create_cylinder(f"{name}_Pin", radius=0.06 * scale, depth=0.34 * scale,
                          rot=(0, math.radians(90), 0), loc=(0, 0, 0), mat=hazard_yellow, col=col)
    pin.parent = root
    
    # Cilindro hidraulico
    cyl_body = create_cylinder(f"{name}_HydCylinder", radius=0.09 * scale, depth=0.45 * scale,
                               rot=(math.radians(25), 0, 0), loc=(loc[0] + 0.12 * scale, loc[1] - 0.18 * scale, loc[2] - 0.2 * scale),
                               mat=dark_metal, col=col)
    cyl_body.parent = root
    
    # Vastago cromado del piston
    rod = create_cylinder(f"{name}_HydRod", radius=0.045 * scale, depth=0.38 * scale,
                          rot=(math.radians(25), 0, 0), loc=(loc[0] + 0.12 * scale, loc[1] - 0.02 * scale, loc[2] + 0.08 * scale),
                          mat=chrome_mat, col=col)
    rod.parent = root
    return root

def create_gear_cog(name, loc=(0,0,0), rot=(0,0,0), radius=0.35, teeth=8, depth=0.08, mat=None, col=None):
    root = bpy.data.objects.new(f"RootGear_{name}", None)
    root.location = loc
    root.rotation_euler = Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])))
    target_col = col if col else bpy.context.scene.collection
    target_col.objects.link(root)
    
    gear_mat = mat if mat else get_comic_material("Mat_Gear_Brass", base_color=(0.80, 0.60, 0.18), roughness=0.35, metallic=0.8)
    
    # Disco central
    hub = create_cylinder(f"{name}_Hub", radius=radius * 0.8, depth=depth, rot=rot, loc=loc, mat=gear_mat, col=col)
    hub.parent = root
    
    # Dientes del engranaje
    for t in range(teeth):
        ang = t * (2.0 * math.pi / teeth)
        tx = loc[0] + math.cos(ang) * radius * 0.85
        tz = loc[2] + math.sin(ang) * radius * 0.85
        tooth = create_box(f"{name}_Tooth_{t}", size=(radius * 0.28, depth * 0.95, radius * 0.28),
                           rot=(0, -ang, 0), loc=(tx, loc[1], tz), mat=gear_mat, col=col)
        tooth.parent = root
    return root

def setup_studio_lighting(sun_energy=3.5, rim_energy=2.2, fill_energy=1.2,
                           sun_rot=(48, 18, -32), rim_rot=(-60, -15, 140),
                           sun_color=(1.0, 0.98, 0.94), rim_color=(0.70, 0.88, 1.0)):
    # Key Sun (Luz principal uniforme estilo cómic sin decaimiento cuadrático)
    key_data = bpy.data.lights.new(name="Key_Sun", type='SUN')
    key_data.energy = sun_energy
    key_data.color = sun_color
    key_data.angle = math.radians(12.0)
    key_obj = bpy.data.objects.new("Key_Sun", key_data)
    key_obj.rotation_euler = Euler((math.radians(sun_rot[0]), math.radians(sun_rot[1]), math.radians(sun_rot[2])))
    bpy.context.scene.collection.objects.link(key_obj)

    # Rim Sun (Contraluz azulada para silueta y volumen)
    rim_data = bpy.data.lights.new(name="Rim_Sun", type='SUN')
    rim_data.energy = rim_energy
    rim_data.color = rim_color
    rim_data.angle = math.radians(20.0)
    rim_obj = bpy.data.objects.new("Rim_Sun", rim_data)
    rim_obj.rotation_euler = Euler((math.radians(rim_rot[0]), math.radians(rim_rot[1]), math.radians(rim_rot[2])))
    bpy.context.scene.collection.objects.link(rim_obj)

    # Fill Sun (Luz difusa de relleno suave)
    fill_data = bpy.data.lights.new(name="Fill_Sun", type='SUN')
    fill_data.energy = fill_energy
    fill_data.color = (0.85, 0.90, 0.95)
    fill_data.angle = math.radians(35.0)
    fill_obj = bpy.data.objects.new("Fill_Sun", fill_data)
    fill_obj.rotation_euler = Euler((math.radians(65), math.radians(-30), math.radians(45)))
    bpy.context.scene.collection.objects.link(fill_obj)

def setup_camera(name="Camera_Main", loc=(0, -16, 8), target=(0, 0, 1.5), focal_length=50):
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = focal_length
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = loc
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Orient camera towards target
    dir_vec = Vector(target) - Vector(loc)
    rot_quat = dir_vec.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = cam_obj
    return cam_obj

def render_and_save(filename, res_x=2560, res_y=1440):
    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.image_settings.compression = 15
    
    out_path = os.path.join(RENDERS_DIR, filename)
    scene.render.filepath = out_path
    print(f"[*] Rendering to {out_path} ({res_x}x{res_y})...")
    bpy.ops.render.render(write_still=True)
    
    # Mirror to artifact directory
    art_path = os.path.join(ARTIFACT_DIR, filename)
    shutil.copy2(out_path, art_path)
    print(f"[+] Render complete & copied to artifact: {art_path}")
    return out_path
