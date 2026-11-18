"""
Bezier Anime Hair Generator
===========================
Constructs luscious, flowing, professional anime hair using 3D Bézier curves
with custom cross-section bevel profiles and sharp tip tapers.
Eliminates disjointed icospheres and robotic blocky hair.
"""

from typing import List, Dict, Tuple, Any
from ..core.anime_schema import AnimeHairStrandSpec


class BezierHairGenerator:
    """Generates layered anime hair strands using parametric curves."""

    def __init__(self, hair_style: str = "high_ponytail_layered"):
        self.hair_style = hair_style

    def generate_hair_strands(self) -> List[AnimeHairStrandSpec]:
        """
        Calculates 3D control points for layered anime hair:
        1. Front Bangs (Flequillo dividido en 5 mechones orgánicos)
        2. Sideburns (Patillas laterales estilizadas que enmarcan la cara)
        3. High Ponytail (Coleta alta con volumen y doble curvatura aerodinámica)
        4. Back Volume (Casquete base que cubre el cráneo)
        """
        strands = []

        # --- 1. FRONT BANGS (FLEQUILLO) ---
        # Central Strand
        strands.append(AnimeHairStrandSpec(
            strand_id="Strand_Bang_Center",
            category="bangs",
            control_points=[
                (0.000, -0.065, 1.635),  # Root near hairline
                (0.000, -0.092, 1.585),  # Mid curve out
                (0.000, -0.095, 1.515),  # Tip above nose bridge
            ],
            bevel_radius_root=0.016,
            bevel_radius_tip=0.002
        ))

        # Left / Right Inner Bangs
        for side, sign in [("L", 1), ("R", -1)]:
            strands.append(AnimeHairStrandSpec(
                strand_id=f"Strand_Bang_Inner_{side}",
                category="bangs",
                control_points=[
                    (sign * 0.025, -0.060, 1.630),
                    (sign * 0.035, -0.090, 1.575),
                    (sign * 0.038, -0.092, 1.505),
                ],
                bevel_radius_root=0.015,
                bevel_radius_tip=0.002
            ))

        # Left / Right Outer Sweeping Bangs
        for side, sign in [("L", 1), ("R", -1)]:
            strands.append(AnimeHairStrandSpec(
                strand_id=f"Strand_Bang_Outer_{side}",
                category="bangs",
                control_points=[
                    (sign * 0.055, -0.050, 1.620),
                    (sign * 0.075, -0.082, 1.560),
                    (sign * 0.082, -0.078, 1.485),
                ],
                bevel_radius_root=0.018,
                bevel_radius_tip=0.002
            ))

        # --- 2. SIDEBURNS (PATILLAS LARGAS ESTILIZADAS) ---
        for side, sign in [("L", 1), ("R", -1)]:
            strands.append(AnimeHairStrandSpec(
                strand_id=f"Strand_Sideburn_{side}",
                category="sideburns",
                control_points=[
                    (sign * 0.085, -0.025, 1.600),
                    (sign * 0.092, -0.055, 1.520),
                    (sign * 0.085, -0.065, 1.430),
                    (sign * 0.075, -0.060, 1.370),  # Falls past the jawline
                ],
                bevel_radius_root=0.018,
                bevel_radius_tip=0.003
            ))

        # --- 3. HIGH PONYTAIL (COLETA ALTA DINÁMICA DE 3 CAPAS) ---
        # Main Central Ponytail Arc
        strands.append(AnimeHairStrandSpec(
            strand_id="Strand_Ponytail_Main",
            category="ponytail",
            control_points=[
                (0.000, 0.080, 1.640),   # Hair tie anchor point
                (0.010, 0.160, 1.690),   # Arches upward and back
                (0.020, 0.260, 1.620),   # Descends with gravity
                (0.035, 0.350, 1.490),   # Sweeps dynamically
                (0.045, 0.410, 1.340),   # Sharp tapered tail tip
            ],
            bevel_radius_root=0.038,
            bevel_radius_tip=0.004
        ))

        # Flanking Ponytail Tendrils (Left and Right)
        for side, sign in [("L", 1), ("R", -1)]:
            strands.append(AnimeHairStrandSpec(
                strand_id=f"Strand_Ponytail_Tendril_{side}",
                category="ponytail",
                control_points=[
                    (sign * 0.025, 0.085, 1.635),
                    (sign * 0.060, 0.170, 1.670),
                    (sign * 0.080, 0.280, 1.580),
                    (sign * 0.070, 0.360, 1.410),
                ],
                bevel_radius_root=0.024,
                bevel_radius_tip=0.003
            ))

        return strands

    def get_blender_bezier_code(self) -> str:
        """
        Returns Python code to build Bézier curves with taper in Blender.
        """
        code = '''
def create_bezier_hair_strand(name, points, r_root, r_tip, mat):
    curve_data = bpy.data.curves.new(name + "_Data", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_resolution = 4
    curve_data.bevel_depth = r_root
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        # Linear taper from root to tip
        t = i / max(1, len(points) - 1)
        bp.radius = (1.0 - t) + (r_tip / max(0.0001, r_root)) * t

    curve_obj = bpy.data.objects.new(name, curve_data)
    if mat:
        curve_obj.data.materials.append(mat)
    col.objects.link(curve_obj)
    return curve_obj
'''
        return code
