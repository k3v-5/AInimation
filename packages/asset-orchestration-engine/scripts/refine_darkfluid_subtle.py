"""refine_darkfluid_subtle.py
Refina el material M_DarX_DarkFluid_PurpleSparks en DarX_Player_Rigged_Canonical.blend
para cumplir con la directiva del usuario:
- Menos color morado dominante (95% fluido negro obsidiana reflectante).
- Destellos y vetas púrpuras muy sutiles, elegantes y puntuales.
- Emisión controlada y no abrumadora.
- Renderiza 3 vistas de previsualización para aprobación visual del usuario (Directiva 4).
"""

import os
import math
import bpy
from mathutils import Vector, Euler
from math import radians as R

CANONICAL_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
OUTPUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)
scene = bpy.context.scene

# Configurar motor de render (Cycles o Eevee Next)
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'

# Buscar material M_DarX_DarkFluid_PurpleSparks
mat = bpy.data.materials.get("M_DarX_DarkFluid_PurpleSparks")
if not mat:
    raise ValueError("Material M_DarX_DarkFluid_PurpleSparks no encontrado")

nt = mat.node_tree
cr_base = nt.nodes.get("Color Ramp")
cr_emit = nt.nodes.get("Color Ramp.001")
math_emit = nt.nodes.get("Math")

# 1. REFINAR COLOR RAMP BASE (95% Obsidiana, 5% Púrpura Sutil)
if cr_base:
    cr = cr_base.color_ramp
    while len(cr.elements) < 5:
        cr.elements.new(0.9)
    while len(cr.elements) > 5:
        cr.elements.remove(cr.elements[-1])
    
    # Elemento 0: Negro Obsidiana Profundo (0.00 a 0.60)
    cr.elements[0].position = 0.60
    cr.elements[0].color = (0.002, 0.002, 0.003, 1.0)
    
    # Elemento 1: Transición Amatista Oscura Muy Sutil (0.66)
    cr.elements[1].position = 0.66
    cr.elements[1].color = (0.10, 0.008, 0.22, 1.0)
    
    # Elemento 2: Púrpura Violeta Fino (0.72)
    cr.elements[2].position = 0.72
    cr.elements[2].color = (0.48, 0.04, 0.85, 1.0)
    
    # Elemento 3: Micro-destello Lavanda Sutil (0.78)
    cr.elements[3].position = 0.78
    cr.elements[3].color = (0.78, 0.35, 0.98, 1.0)

    # Elemento 4: Puntas Finas (0.85)
    cr.elements[4].position = 0.85
    cr.elements[4].color = (0.92, 0.70, 1.0, 1.0)

# 2. REFINAR COLOR RAMP DE EMISIÓN (Solo emiten los picos exactos)
if cr_emit:
    cr_e = cr_emit.color_ramp
    while len(cr_e.elements) > 2:
        cr_e.elements.remove(cr_e.elements[-1])
    
    # 0.0 hasta 0.67 completamente negro (cero emisión)
    cr_e.elements[0].position = 0.67
    cr_e.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    
    # Picos sutiles en 0.80
    cr_e.elements[1].position = 0.80
    cr_e.elements[1].color = (0.65, 0.20, 0.95, 1.0)

# 3. MODERAR FUERZA DE EMISIÓN
# Encontrar nodo de multiplicación de emisión
for n in nt.nodes:
    if n.type == 'MATH' and n.operation == 'MULTIPLY':
        # Si se conecta a Emission Strength
        for out in n.outputs:
            for l in out.links:
                if l.to_socket.name == "Emission Strength":
                    n.inputs[1].default_value = 2.5 # Reducido de 8.5 a 2.5 sutil
                    print("[Shader] Emission Strength ajustado a 2.5")

# 4. REFINAR ESPECULARIDAD Y ROUGHNESS
bsdf = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
bsdf.inputs["Roughness"].default_value = 0.09 # Acabado húmedo obsidiana
if "Coat Weight" in bsdf.inputs:
    bsdf.inputs["Coat Weight"].default_value = 0.95
    bsdf.inputs["Coat Roughness"].default_value = 0.03

# Guardar cambios en el blend canónico
bpy.ops.wm.save_mainfile(filepath=CANONICAL_BLEND)
print(f"[Shader] Guardado con éxito en: {CANONICAL_BLEND}")

# 5. CONFIGURAR ILUMINACIÓN DE ESTUDIO NEUTRA Y ELEGANTE
for obj in list(scene.collection.objects):
    if obj.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(obj, do_unlink=True)

# Key Light
l1_d = bpy.data.lights.new("Key", 'AREA')
l1_d.energy = 220.0
l1_d.size = 2.0
l1_d.color = (1.0, 0.98, 0.96)
l1 = bpy.data.objects.new("Key", l1_d)
l1.location = (1.5, -2.5, 2.0)
l1.rotation_euler = (R(50), R(10), R(30))
scene.collection.objects.link(l1)

# Fill Light
l2_d = bpy.data.lights.new("Fill", 'AREA')
l2_d.energy = 90.0
l2_d.size = 2.5
l2_d.color = (0.88, 0.92, 1.0)
l2 = bpy.data.objects.new("Fill", l2_d)
l2.location = (-1.8, -2.0, 1.4)
l2.rotation_euler = (R(55), R(-15), R(-35))
scene.collection.objects.link(l2)

# Rim Light Neutro/Plata
l3_d = bpy.data.lights.new("Rim", 'AREA')
l3_d.energy = 160.0
l3_d.size = 2.0
l3_d.color = (0.92, 0.95, 1.0)
l3 = bpy.data.objects.new("Rim", l3_d)
l3.location = (-1.6, 2.0, 1.8)
l3.rotation_euler = (R(-45), R(-15), R(140))
scene.collection.objects.link(l3)

# 6. CREAR CÁMARA Y RENDERIZAR 3 VISTAS
cam_data = bpy.data.cameras.new("Cam_Preview")
cam_obj = bpy.data.objects.new("Cam_Preview", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

views = [
    {
        'name': 'darkfluid_subtle_full_front.png',
        'cam_pos': Vector((0.0, -3.2, 1.25)),
        'target': Vector((0.0, 0.0, 1.05)),
        'lens': 45
    },
    {
        'name': 'darkfluid_subtle_perspective_34.png',
        'cam_pos': Vector((1.6, -2.6, 1.35)),
        'target': Vector((0.0, 0.0, 1.10)),
        'lens': 42
    },
    {
        'name': 'darkfluid_subtle_torso_closeup.png',
        'cam_pos': Vector((0.3, -1.35, 1.35)),
        'target': Vector((0.05, 0.0, 1.30)),
        'lens': 55
    }
]

rendered_paths = []
scene.render.resolution_x = 720
scene.render.resolution_y = 960

for v in views:
    cam_obj.location = v['cam_pos']
    direction = v['target'] - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.data.lens = v['lens']
    
    out_path = os.path.join(OUTPUT_DIR, v['name'])
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    rendered_paths.append(out_path)
    print(f"[Render] Vista generada: {out_path}")

print("[Render] Las 3 vistas fueron renderizadas con éxito.")
