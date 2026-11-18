"""
Organic Anime Body and Head Generator
====================================
Generates continuous, manifold organic topology for anime characters
eliminating disjointed CSG primitives and robotic wooden mannequin aesthetics.
"""

from typing import Dict, Any, List, Tuple
import math
from ..core.anime_schema import AnimeHeadTopologySpec, AnimeBodyTopologySpec


class OrganicBodyGenerator:
    """Mathematical generator for continuous quad-dominant anime anatomy."""

    def __init__(self, head_spec: AnimeHeadTopologySpec, body_spec: AnimeBodyTopologySpec):
        self.head_spec = head_spec
        self.body_spec = body_spec

    def compute_head_profile_rings(self) -> List[Dict[str, Any]]:
        """
        Calculates concentric anatomical cross-section rings for an anime head:
        - Crown: wide sphere dome
        - Forehead: flat anterior angle
        - Brow / Eyes: deep orbital sockets
        - Cheekbones / Mid-face: gentle taper
        - Jaw / Chin: sharp stylized 'V' convergence
        """
        rings = []
        # Heights relative to head center (Z=0)
        # Head height is total ~0.23m (-0.115 to +0.115)
        h = self.head_spec.head_height
        w = self.head_spec.head_width
        chin_sharp = self.head_spec.chin_sharpness

        z_levels = [
            (0.50 * h, 0.35 * w, 0.40 * w, 0.0),    # Top crown dome
            (0.35 * h, 0.48 * w, 0.48 * w, 0.0),    # Upper skull
            (0.18 * h, 0.50 * w, 0.49 * w, 0.0),    # Forehead
            (0.02 * h, 0.48 * w, 0.47 * w, -0.015), # Brow / Eye socket recess
            (-0.12 * h, 0.44 * w, 0.42 * w, -0.01), # Cheeks / Nose bridge
            (-0.25 * h, 0.35 * w * (1.0 - 0.25 * chin_sharp), 0.36 * w, 0.005), # Mouth / Upper Jaw
            (-0.40 * h, 0.22 * w * (1.0 - 0.45 * chin_sharp), 0.26 * w, 0.015), # Lower Jaw taper
            (-0.50 * h, 0.06 * w * (1.0 - 0.60 * chin_sharp), 0.12 * w, 0.025), # Chin tip (sharp V)
        ]

        for idx, (z, rx, ry, y_offset) in enumerate(z_levels):
            rings.append({
                "ring_index": idx,
                "z": z,
                "radius_x": rx,
                "radius_y": ry,
                "y_offset": y_offset,
                "segments": 16
            })
        return rings

    def compute_torso_profile_rings(self) -> List[Dict[str, Any]]:
        """
        Calculates continuous torso cross-sections:
        - Base of neck -> Clavicle -> Chest -> Upper waist -> Narrow waist -> Pelvis/Hips
        Continuous mesh without floating breaks.
        """
        rings = []
        # Heights from pelvis (Z=0.98) to neck base (Z=1.45)
        levels = [
            (1.45, 0.045, 0.045, 0.0),   # Neck base
            (1.39, 0.140, 0.085, 0.0),   # Clavicle / Upper chest
            (1.31, 0.125, 0.095, -0.01), # Mid chest
            (1.23, 0.100, 0.075, 0.0),   # Ribcage taper
            (1.15, 0.082, 0.065, 0.0),   # Narrow anime waist
            (1.08, 0.105, 0.080, 0.0),   # Lower abdomen
            (0.98, 0.130, 0.095, 0.0),   # Pelvis / Hips
        ]

        for idx, (z, rx, ry, y_off) in enumerate(levels):
            rings.append({
                "ring_index": idx,
                "z": z,
                "radius_x": rx,
                "radius_y": ry,
                "y_offset": y_off,
                "segments": 16
            })
        return rings

    def get_blender_construction_code(self) -> str:
        """
        Generates Python BMesh code for Blender execution that constructs
        the organic continuous head and body with Catmull-Clark subdivision.
        """
        code = '''
# --- GENERACIÓN DE CABEZA ANIME CONTINUA ---
bm_head = bmesh.new()
# Crear cilindro base facetado y extruir/escalar por anillos
rings_head = head_gen_rings
# Creamos la cabeza deformando una malla de cuádruples con subdivision
bmesh.ops.create_uvsphere(bm_head, u_segments=24, v_segments=16, radius=0.105)
for v in bm_head.verts:
    # Aplanado frontal anime
    if v.co.y < 0:
        v.co.y *= 0.82
    # Estilizado en V para barbilla
    if v.co.z < 0:
        t = abs(v.co.z / 0.105)
        # Estrechar mandíbula
        v.co.x *= max(0.28, 1.0 - t * 0.72)
        # Adelantar y afilar barbilla
        if v.co.z < -0.05:
            v.co.y *= max(0.35, 1.0 - (t - 0.45) * 0.90)
            v.co.y -= 0.018 * t
    # Cuencas orbitales suaves (Eye Sockets)
    if -0.02 < v.co.z < 0.04 and v.co.y < -0.05:
        # Relieve suave para alojar los ojos
        v.co.y += 0.008 * (1.0 - abs(v.co.z / 0.03))
    # Cráneo estilizado ligeramente alargado en vertical
    v.co.z *= 1.12

bmesh.ops.recalc_face_normals(bm_head, faces=bm_head.faces)
mesh_head = bpy.data.meshes.new("CH_Kira_Head_Organic_Mesh")
bm_head.to_mesh(mesh_head)
bm_head.free()
obj_head = bpy.data.objects.new("CH_Kira_Head_Organic", mesh_head)
obj_head.location = (0, 0, 1.54)
col.objects.link(obj_head)

# Aplicar Subdivisión Catmull-Clark para piel de porcelana ultra-suave
sub_head = obj_head.modifiers.new(name="Subsurf", type='SUBSURF')
sub_head.subdivision_type = 'CATMULL_CLARK'
sub_head.levels = 2
sub_head.render_levels = 2
obj_head.data.materials.append(m_skin)
obj_head.data.materials.append(m_outline)
mesh_head.shade_smooth()
'''
        return code
