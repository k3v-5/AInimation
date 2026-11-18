"""Remodelado Orgánico del Cepo de Raíces de Flora Carnívora (SM_Flora_CepoRaices).

Corrige definitivamente:
1. Reemplazo de cubos apilados por geometría continua leñosa y garras orgánicas continuas.
2. Curvatura hacia ADENTRO (cerrando sobre el jugador en forma de jaula/trampa de depredador vegetal).
3. Espinas y colmillos apuntando al INTERIOR de la trampa.
4. Escala real en metros (diámetro ~3.2m, radio 1.6m, altura ~2.2m) con pivote exacto en Z=0.
5. Renderizado de 4 vistas (Frontal, Trasera, Acción/Cierre, FPS).
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FBX_OUT = r"E:\Darx_Proyect\Art\FBX\SM_Flora_CepoRaices.fbx"

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, base_rgb, rough=0.5, metal=0.0, emis=(0, 0, 0), emis_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if emis_str > 0.0:
            bsdf.inputs["Emission Color"].default_value = (*emis, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emis_str
    return m

def build_organic_cepo():
    clear_scene()
    
    me = bpy.data.meshes.new("SM_Flora_CepoRaices")
    obj = bpy.data.objects.new("SM_Flora_CepoRaices", me)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()

    M_WOOD = mat("M_Flora_WoodRoot", (0.11, 0.07, 0.04), rough=0.88, metal=0.02)
    M_THORNS = mat("M_Flora_Thorns", (0.75, 0.08, 0.95), rough=0.20, metal=0.15, emis=(0.85, 0.1, 1.0), emis_str=4.5)
    
    obj.data.materials.append(M_WOOD)    # Slot 0
    obj.data.materials.append(M_THORNS)  # Slot 1

    # Anillo basal de raíces enterradas en el suelo (Z=0.02)
    num_bases = 6
    radio_base = 1.60  # metros (coherente con RadioCepo = 180cm)
    
    # 1. Crear raíces rastreras perimetrales que conectan las bases
    num_puntos_anillo = 36
    anillo_verts = []
    for p in range(num_puntos_anillo):
        ang = (2.0 * math.pi / num_puntos_anillo) * p
        r_var = radio_base + math.sin(ang * num_bases) * 0.15
        x = math.cos(ang) * r_var
        y = math.sin(ang) * r_var
        anillo_verts.append(Vector((x, y, 0.04)))

    # Conectar anillo con segmentos tubulares
    for p in range(num_puntos_anillo):
        p_next = (p + 1) % num_puntos_anillo
        v1 = anillo_verts[p]
        v2 = anillo_verts[p_next]
        dir_vec = (v2 - v1).normalized()
        dist = (v2 - v1).length
        mid = (v1 + v2) * 0.5
        
        rot = dir_vec.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.08, radius2=0.08, depth=dist * 1.05, segments=6,
                              matrix=Matrix.Translation(mid) @ rot)

    # 2. Crear los 6 grandes zarcillos orgánicos arqueados hacia ADENTRO
    for i in range(num_bases):
        ang_base = (2.0 * math.pi / num_bases) * i
        
        # Generar puntos guía de la curva del zarcillo
        # Desde r = 1.6m en el suelo, subiendo y curvándose hacia el centro hasta r = 0.45m en Z = 2.1m
        num_segs = 9
        rings = []
        
        for s in range(num_segs):
            t = s / float(num_segs - 1)
            
            # Altura
            z = t * 2.15
            
            # Radio decrece conforme sube (curvatura hacia adentro)
            # t=0: r = 1.60
            # t=0.5: r = 1.35
            # t=0.8: r = 0.70
            # t=1.0: r = 0.38 (casi tocándose en la cúpula superior)
            curva_inward = math.pow(t, 1.6) * 1.25
            r_act = radio_base - curva_inward
            
            # Ligera torsión en espiral para apariencia visceral
            ang_act = ang_base + (t * 0.35)
            
            cx = math.cos(ang_act) * r_act
            cy = math.sin(ang_act) * r_act
            pos_centro = Vector((cx, cy, z))
            
            # Grosor de la rama (se adelgaza hacia la punta)
            grosor = 0.17 * (1.0 - t * 0.72)
            
            # Vector tangente para orientar el anillo
            if s == 0:
                tangente = Vector(( -math.cos(ang_act) * 0.4, -math.sin(ang_act) * 0.4, 1.0 )).normalized()
            else:
                prev_c = rings[-1]['center']
                tangente = (pos_centro - prev_c).normalized()
                
            quat = tangente.to_track_quat('Z', 'Y')
            
            # Crear anillo de vértices
            num_ring_pts = 8
            ring_verts = []
            for rp in range(num_ring_pts):
                phi = (2.0 * math.pi / num_ring_pts) * rp
                # Deformación ovalada para parecer corteza retorcida
                rx = math.cos(phi) * grosor * (1.0 + 0.15 * math.sin(phi * 2.0))
                ry = math.sin(phi) * grosor
                local_pt = Vector((rx, ry, 0.0))
                world_pt = pos_centro + quat @ local_pt
                v = bm.verts.new(world_pt)
                ring_verts.append(v)
                
            rings.append({'center': pos_centro, 'verts': ring_verts, 't': t, 'ang': ang_act})

        # Conectar anillos para formar el tronco continuo del zarcillo (Slot 0: Madera)
        for s in range(num_segs - 1):
            r1 = rings[s]['verts']
            r2 = rings[s + 1]['verts']
            n_pts = len(r1)
            for rp in range(n_pts):
                rp_next = (rp + 1) % n_pts
                f = bm.faces.new([r1[rp], r1[rp_next], r2[rp_next], r2[rp]])
                f.material_index = 0
                f.smooth = True
                
        # Tapar la punta superior en forma de espina afilada
        punta_pos = rings[-1]['center'] + Vector(( -math.cos(rings[-1]['ang']) * 0.15, -math.sin(rings[-1]['ang']) * 0.15, 0.12 ))
        v_punta = bm.verts.new(punta_pos)
        r_top = rings[-1]['verts']
        for rp in range(len(r_top)):
            rp_next = (rp + 1) % len(r_top)
            f = bm.faces.new([v_punta, r_top[rp_next], r_top[rp]])
            f.material_index = 0
            f.smooth = True

        # 3. Colmillos y espinas interiores apuntando DIRECTAMENTE AL CENTRO (hacia el jugador)
        # Se añaden 4 espinas internas en cada zarcillo
        indices_espinas = [2, 4, 6, 7]
        for s_idx in indices_espinas:
            r_data = rings[s_idx]
            pos_c = r_data['center']
            
            # Dirección hacia el centro exacto (0, 0, Z)
            dir_hacia_centro = Vector((-pos_c.x, -pos_c.y, 0.0)).normalized()
            # Inclinación ligeramente hacia abajo para apresar
            dir_espina = (dir_hacia_centro + Vector((0, 0, -0.25))).normalized()
            
            longitud_espina = 0.35 * (1.0 - r_data['t'] * 0.3)
            base_espina = pos_c + dir_espina * 0.10
            
            rot_espina = dir_espina.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            
            cone_geom = bmesh.ops.create_cone(
                bm, cap_ends=True, radius1=0.045, radius2=0.005, depth=longitud_espina, segments=6,
                matrix=Matrix.Translation(base_espina + dir_espina * (longitud_espina * 0.5)) @ rot_espina
            )
            # Asignar material Slot 1 (Espinas bioluminiscentes violetas)
            for elem in cone_geom['verts']:
                for face in elem.link_faces:
                    face.material_index = 1
                    face.smooth = True

    # 4. Raíces laterales en el suelo como patas estabilizadoras
    for i in range(num_bases):
        ang = (2.0 * math.pi / num_bases) * i + (math.pi / num_bases)
        p1 = Vector((math.cos(ang) * radio_base, math.sin(ang) * radio_base, 0.04))
        p2 = Vector((math.cos(ang) * (radio_base + 0.45), math.sin(ang) * (radio_base + 0.45), 0.01))
        dir_p = (p2 - p1).normalized()
        dist = (p2 - p1).length
        mid = (p1 + p2) * 0.5
        rot = dir_p.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.09, radius2=0.02, depth=dist, segments=6,
                              matrix=Matrix.Translation(mid) @ rot)

    bm.to_mesh(me)
    bm.free()

    # UV unwrapping
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Exportar FBX estricto Forward=-Y, Up=Z
    print(f"[Blender] Exportando FBX a {FBX_OUT}...")
    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
        use_selection=True,
        axis_forward='-Y',
        axis_up='Z',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL'
    )
    print(f"[Blender] Exportación FBX completada con éxito.")

    # Generar Previsualización de 4 Vistas (Regla 5)
    render_4_views(obj)

def render_4_views(target_obj):
    print("[Blender] Configurando render de 4 vistas...")
    
    # Suelo oscuro de apoyo para render
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
    plane = bpy.context.active_object
    m_floor = mat("M_Render_Floor", (0.04, 0.04, 0.05), rough=0.7)
    plane.data.materials.append(m_floor)

    # Crear cámara
    cam_data = bpy.data.cameras.new("Cam_Cepo")
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new("Cam_Cepo", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Configurar iluminación para preview de alta calidad
    sun_data = bpy.data.lights.new("Sun_Key", 'SUN')
    sun_data.energy = 3.5
    sun_obj = bpy.data.objects.new("Sun_Key", sun_data)
    sun_obj.location = (5, -6, 9)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(35))
    bpy.context.scene.collection.objects.link(sun_obj)
    
    fill_data = bpy.data.lights.new("Point_Fill", 'POINT')
    fill_data.energy = 800.0
    fill_data.color = (0.8, 0.2, 1.0)  # Luz violeta ambiental
    fill_obj = bpy.data.objects.new("Point_Fill", fill_data)
    fill_obj.location = (0, 0, 1.3)
    bpy.context.scene.collection.objects.link(fill_obj)

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngineEEVEENext') else 'BLENDER_EEVEE'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720

    views = [
        ("preview_cepo_raices_frontal.png", Vector((0.0, -6.0, 2.2)), Vector((math.radians(78), 0, 0))),
        ("preview_cepo_raices_trasera.png", Vector((0.0, 6.0, 2.2)), Vector((math.radians(102), 0, math.radians(180)))),
        ("preview_cepo_raices_accion_cierre.png", Vector((4.5, -4.5, 4.2)), Vector((math.radians(60), 0, math.radians(45)))),
        ("preview_cepo_raices_fps_interior.png", Vector((0.0, 0.0, 0.45)), Vector((math.radians(35), 0, 0))),
    ]

    for fname, loc, rot in views:
        cam_obj.location = loc
        cam_obj.rotation_euler = rot
        out_file = os.path.join(ARTIFACTS_DIR, fname)
        scene.render.filepath = out_file
        print(f"[Blender] Renderizando {fname}...")
        bpy.ops.render.render(write_still=True)
        print(f"[Blender] Render guardado en {out_file}")

if __name__ == "__main__":
    build_organic_cepo()
