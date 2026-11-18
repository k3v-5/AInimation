"""
Anime Tactical Props and Accessories Generator
==============================================
Generates stylized hard-surface weaponry and flowing tactical accessories
(Katana, Cyber Scarf, Pauldrons) designed for seamless integration with anime bodies.
"""

from typing import Dict, Any, Tuple


class TacticalPropsGenerator:
    """Constructs stylized anime weapons and tactical accessories."""

    def __init__(self, include_katana: bool = True, include_scarf: bool = True):
        self.include_katana = include_katana
        self.include_scarf = include_scarf

    def get_blender_props_code(self) -> str:
        """Returns Blender Python code to generate the anime accessories."""
        code = '''
# 1. BUFANDA CIBERNÉTICA ONDEANTE DE ALTO VUELO (CYBER SCARF)
# Construida con una curva Bézier extruida con grosor
scarf_curve = bpy.data.curves.new("CH_Kira_Scarf_Curve", type='CURVE')
scarf_curve.dimensions = '3D'
scarf_curve.resolution_u = 16
scarf_curve.bevel_resolution = 2
scarf_curve.bevel_depth = 0.012
scarf_curve.extrude = 0.045 # Cinta ancha ondeante

spline_s = scarf_curve.splines.new('BEZIER')
scarf_points = [
    (0.00, -0.05, 1.45),   # Cuello frontal
    (0.08, -0.03, 1.44),   # Vuelta lateral cuello
    (0.06,  0.07, 1.45),   # Nudo trasero
    (0.09,  0.18, 1.40),   # Vuelo hacia atrás
    (0.14,  0.30, 1.34),   # Caída aerodinámica
    (0.18,  0.42, 1.25),   # Punta ondeante
]
spline_s.bezier_points.add(len(scarf_points) - 1)
for i, pt in enumerate(scarf_points):
    bp = spline_s.bezier_points[i]
    bp.co = pt
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'

obj_scarf = bpy.data.objects.new("CH_Kira_Scarf", scarf_curve)
obj_scarf.data.materials.append(m_scarf)
col.objects.link(obj_scarf)

# 2. KATANA CIBERNÉTICA EN CADERA IZQUIERDA (CYBER KATANA)
# Vaina (Saya) con ligera curvatura sutil
bm_saya = bmesh.new()
bmesh.ops.create_cone(bm_saya, cap_ends=True, segments=12, radius1=0.015, radius2=0.012, depth=0.78)
for v in bm_saya.verts:
    v.co.x *= 0.45 # perfil plano
    t = (v.co.z + 0.39) / 0.78
    v.co.y += (t**1.6) * 0.040
bmesh.ops.recalc_face_normals(bm_saya, faces=bm_saya.faces)
mesh_saya = bpy.data.meshes.new("WP_Katana_Saya_Mesh")
bm_saya.to_mesh(mesh_saya)
bm_saya.free()
obj_saya = bpy.data.objects.new("WP_Katana_Saya", mesh_saya)
obj_saya.location = (-0.14, 0.03, 0.86)
obj_saya.rotation_euler = (math.radians(25), math.radians(-15), math.radians(15))
obj_saya.data.materials.append(m_suit)
mesh_saya.shade_smooth()
col.objects.link(obj_saya)

# Guardamano (Tsuba) Dorado
bm_tsuba = bmesh.new()
bmesh.ops.create_cone(bm_tsuba, cap_ends=True, segments=16, radius1=0.036, radius2=0.036, depth=0.008)
mesh_tsuba = bpy.data.meshes.new("WP_Katana_Tsuba_Mesh")
bm_tsuba.to_mesh(mesh_tsuba)
bm_tsuba.free()
obj_tsuba = bpy.data.objects.new("WP_Katana_Tsuba", mesh_tsuba)
obj_tsuba.location = (-0.155, -0.015, 1.20)
obj_tsuba.rotation_euler = (math.radians(65), math.radians(15), math.radians(-75))
obj_tsuba.data.materials.append(m_armor)
mesh_tsuba.shade_smooth()
col.objects.link(obj_tsuba)

# Empuñadura (Tsuka) y Pomo (Kashira)
bm_tsuka = bmesh.new()
bmesh.ops.create_cone(bm_tsuka, cap_ends=True, segments=10, radius1=0.013, radius2=0.011, depth=0.20)
for v in bm_tsuka.verts:
    v.co.x *= 0.55
mesh_tsuka = bpy.data.meshes.new("WP_Katana_Tsuka_Mesh")
bm_tsuka.to_mesh(mesh_tsuka)
bm_tsuka.free()
obj_tsuka = bpy.data.objects.new("WP_Katana_Tsuka", mesh_tsuka)
obj_tsuka.location = (-0.175, -0.065, 1.29)
obj_tsuka.rotation_euler = (math.radians(25), math.radians(-15), math.radians(15))
obj_tsuka.data.materials.append(m_armor)
mesh_tsuka.shade_smooth()
col.objects.link(obj_tsuka)
'''
        return code
