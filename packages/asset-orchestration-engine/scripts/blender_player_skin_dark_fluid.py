import bpy
import bmesh
import math
from mathutils import Matrix, Vector, Quaternion
import os
import sys
import argparse

def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-file", type=str, default="")
    parser.add_argument("--preview-output", type=str, default="")
    return parser.parse_args(argv)

def clean_collection(col_name="AOE_Player_DarkFluid"):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return col
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)
    return col

# -------------------------------------------------------------
# SHADER: GLOSSY LIQUID OBSIDIAN WITH ELECTRIC PURPLE VEINS (APPROVED)
# -------------------------------------------------------------

def create_liquid_obsidian_purple_shader(name="M_DarX_DarkFluid_ElectricVeins"):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    # 1. Output & Principled BSDF
    output_node = nt.nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (1100, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (750, 0)
    nt.links.new(bsdf.outputs["BSDF"], output_node.inputs["Surface"])

    # High Gloss Mirror Liquid Obsidian Ferrofluid
    bsdf.inputs["Metallic"].default_value = 0.94
    bsdf.inputs["Roughness"].default_value = 0.025
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.68
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.01
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 1.0
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.01

    # 2. Coordinates & Mapping
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Scale"].default_value = (1.6, 1.6, 1.2)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # 3. Dual Organic Fluid Noise Currents
    noise1 = nt.nodes.new(type="ShaderNodeTexNoise")
    noise1.location = (-600, 150)
    noise1.inputs["Scale"].default_value = 1.8
    noise1.inputs["Detail"].default_value = 4.0
    noise1.inputs["Roughness"].default_value = 0.45
    noise1.inputs["Distortion"].default_value = 4.0
    nt.links.new(mapping.outputs["Vector"], noise1.inputs["Vector"])

    noise2 = nt.nodes.new(type="ShaderNodeTexNoise")
    noise2.location = (-600, -150)
    noise2.inputs["Scale"].default_value = 3.6
    noise2.inputs["Detail"].default_value = 5.0
    noise2.inputs["Roughness"].default_value = 0.50
    noise2.inputs["Distortion"].default_value = 2.5
    nt.links.new(mapping.outputs["Vector"], noise2.inputs["Vector"])

    mix_noise = nt.nodes.new(type="ShaderNodeMix")
    mix_noise.data_type = 'FLOAT'
    mix_noise.location = (-400, 0)
    mix_noise.inputs["Factor"].default_value = 0.35
    nt.links.new(noise1.outputs["Fac"], mix_noise.inputs[2])
    nt.links.new(noise2.outputs["Fac"], mix_noise.inputs[3])

    # 4. ColorRamp: 75% Deep Obsidian Black + 25% Vibrant Neon Violet/Purple Streams
    color_ramp = nt.nodes.new(type="ShaderNodeValToRGB")
    color_ramp.location = (-150, 150)
    elements = color_ramp.color_ramp.elements
    elements.remove(elements[1])

    # Pos 0.52: Pure Glossy Liquid Obsidian Black Base (Dominant 75%)
    elements[0].position = 0.52
    elements[0].color = (0.003, 0.003, 0.005, 1.0)

    # Pos 0.60: Deep Midnight Violet Undertone
    e1 = elements.new(0.60)
    e1.color = (0.18, 0.01, 0.48, 1.0)

    # Pos 0.70: Electric Neon Violet / Purple Stream
    e2 = elements.new(0.70)
    e2.color = (0.65, 0.02, 0.98, 1.0)

    # Pos 0.82: Intense Neon Purple / Magenta Detail
    e3 = elements.new(0.82)
    e3.color = (0.92, 0.02, 1.0, 1.0)

    # Pos 0.94: Brilliant White-Hot Violet Plasma Core
    e4 = elements.new(0.94)
    e4.color = (1.0, 0.70, 1.0, 1.0)

    nt.links.new(mix_noise.outputs[0], color_ramp.inputs["Fac"])
    nt.links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # 5. Emission Mask
    emit_ramp = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_ramp.location = (-150, -150)
    emit_elements = emit_ramp.color_ramp.elements
    emit_elements[0].position = 0.58
    emit_elements[0].color = (0, 0, 0, 1)
    emit_elements[1].position = 0.86
    emit_elements[1].color = (1, 1, 1, 1)
    nt.links.new(mix_noise.outputs[0], emit_ramp.inputs["Fac"])

    math_strength = nt.nodes.new(type="ShaderNodeMath")
    math_strength.location = (200, -150)
    math_strength.operation = 'MULTIPLY'
    math_strength.inputs[1].default_value = 35.0
    nt.links.new(emit_ramp.outputs["Color"], math_strength.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(color_ramp.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(math_strength.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(color_ramp.outputs["Color"], bsdf.inputs["Emission"])

    # 6. Fluid Ripple Bump
    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (250, -320)
    bump.inputs["Strength"].default_value = 0.04
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(mix_noise.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

# -------------------------------------------------------------
# SOLID OVERLAPPING LIMB PRIMITIVES
# -------------------------------------------------------------

def add_solid_overlapping_limb(bm, p1, p2, r1, r2, segments=16, overlap=0.025):
    v1 = Vector(p1)
    v2 = Vector(p2)
    dir_vec = v2 - v1
    dist = dir_vec.length
    if dist < 0.001:
        return
    
    d_norm = dir_vec.normalized()
    p1_ext = v1 - d_norm * overlap
    p2_ext = v2 + d_norm * overlap
    dist_ext = (p2_ext - p1_ext).length
    mid = (p1_ext + p2_ext) * 0.5

    up = Vector((0, 0, 1))
    if abs(d_norm.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    rot = up.rotation_difference(d_norm)
    mat_rot = rot.to_matrix().to_4x4()
    mat_trans = Matrix.Translation(mid)

    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=segments,
        radius1=r1,
        radius2=r2,
        depth=dist_ext,
        matrix=mat_trans @ mat_rot
    )

# -------------------------------------------------------------
# MASTER-TIER ARTICULATED HAND & SLEEK WRIST
# -------------------------------------------------------------

def build_master_articulated_hand(bm, wrist_pos, forward_dir, up_dir, is_right=True, scale=1.0):
    """
    Constructs an anatomically refined, predatory superhero hand and wrist:
    - Elegant carpal joint with contoured radius & ulna styloid bone processes.
    - Metacarpal palm arch with independent thenar & hypothenar muscle eminences.
    - Full opposable thumb with 3 distinct articulated segments and predatory claw.
    - 4 independently articulated, splayed fingers with 3 distinct phalanges per finger.
    - Prominent dorsal extensor tendons connecting wrist to knuckles.
    - Zero webbing: deep separation between all digits.
    - Suspended micro ferrofluid droplets orbiting fingertips.
    """
    w_pos = Vector(wrist_pos)
    fwd = Vector(forward_dir).normalized()
    up = Vector(up_dir).normalized()
    side = fwd.cross(up).normalized()
    if not is_right:
        side = -side

    # 1. Carpal & Styloid Wrist Joint (Ulna & Radius bone definition)
    p_radius = w_pos + side * (0.018 * scale) + up * (0.002 * scale)
    p_ulna = w_pos - side * (0.017 * scale) + up * (0.004 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0085 * scale, matrix=Matrix.Translation(p_radius))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * scale, matrix=Matrix.Translation(p_ulna))

    # Wrist Core Block
    mat_wrist = Matrix.Translation(w_pos) @ Matrix.Diagonal((0.032 * scale, 0.026 * scale, 0.024 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_wrist)

    # 2. Metacarpal Palm (Tapered, athletic, cupped)
    palm_center = w_pos + fwd * (0.046 * scale)
    mat_palm = Matrix.Translation(palm_center) @ Matrix.Diagonal((0.034 * scale, 0.040 * scale, 0.018 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_palm)

    # Thenar Pad (Base of thumb muscle)
    thenar_pos = w_pos + fwd * (0.026 * scale) + side * (0.018 * scale) - up * (0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.013 * scale, matrix=Matrix.Translation(thenar_pos))

    # Hypothenar Pad (Pinky edge muscle)
    hypo_pos = w_pos + fwd * (0.028 * scale) - side * (0.016 * scale) - up * (0.005 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.011 * scale, matrix=Matrix.Translation(hypo_pos))

    # Connect wrist to palm
    add_solid_overlapping_limb(bm, w_pos, palm_center, 0.026 * scale, 0.024 * scale, segments=10, overlap=0.012 * scale)

    # 3. Dorsal Extensor Tendons (Prominent fluid cords on back of hand)
    knuckle_targets = [
        ("Index",   0.014 * scale),
        ("Middle",  0.004 * scale),
        ("Ring",   -0.005 * scale),
        ("Pinky",  -0.014 * scale)
    ]
    for name, s_off in knuckle_targets:
        p_knuckle = palm_center + fwd * (0.030 * scale) + side * s_off + up * (0.007 * scale)
        p_wrist_tendon = w_pos + side * (s_off * 0.45) + up * (0.008 * scale)
        add_solid_overlapping_limb(bm, p_wrist_tendon, p_knuckle, 0.0035 * scale, 0.0030 * scale, segments=6, overlap=0.005 * scale)

    # 4. OPPOSABLE THUMB (Metacarpal + Proximal + Distal Claw)
    # Metacarpal shaft from wrist to thumb MCP knuckle
    thumb_mcp = thenar_pos + fwd * (0.016 * scale) + side * (0.012 * scale) - up * (0.002 * scale)
    add_solid_overlapping_limb(bm, thenar_pos, thumb_mcp, 0.011 * scale, 0.009 * scale, segments=8, overlap=0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0085 * scale, matrix=Matrix.Translation(thumb_mcp))

    # Proximal phalanx (reaching forward and splaying outward)
    thumb_dir1 = (fwd * 0.65 + side * 0.70 + up * 0.15).normalized()
    thumb_ip = thumb_mcp + thumb_dir1 * (0.028 * scale)
    add_solid_overlapping_limb(bm, thumb_mcp, thumb_ip, 0.0085 * scale, 0.0070 * scale, segments=8, overlap=0.005 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * scale, matrix=Matrix.Translation(thumb_ip))

    # Distal phalanx (curving inward to predatory claw tip)
    thumb_dir2 = (fwd * 0.85 + side * 0.30 - up * 0.35).normalized()
    thumb_tip = thumb_ip + thumb_dir2 * (0.025 * scale)
    add_solid_overlapping_limb(bm, thumb_ip, thumb_tip, 0.0070 * scale, 0.0018 * scale, segments=8, overlap=0.005 * scale)

    # 5. FOUR INDEPENDENTLY ARTICULATED FINGERS
    # Generous lateral spacing to eliminate any webbing
    finger_configs = [
        # (name, side_offset, base_len, mid_len, tip_len, curl_angle, splay_angle)
        ("Index",   0.015,  0.036, 0.028, 0.024,  math.radians(18),  math.radians(16)),
        ("Middle",  0.004,  0.040, 0.032, 0.027,  math.radians(22),  math.radians(3)),
        ("Ring",   -0.007,  0.037, 0.028, 0.024,  math.radians(26), -math.radians(9)),
        ("Pinky",  -0.017,  0.030, 0.022, 0.019,  math.radians(32), -math.radians(22))
    ]

    for name, s_off, l1, l2, l3, curl_deg, splay_deg in finger_configs:
        knuckle_pos = palm_center + fwd * (0.030 * scale) + side * (s_off * scale) + up * (0.006 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0080 * scale, matrix=Matrix.Translation(knuckle_pos))

        # Phalanx 1 (Proximal)
        d1 = (fwd * math.cos(splay_deg) + side * math.sin(splay_deg) - up * math.sin(curl_deg * 0.40)).normalized()
        p_joint1 = knuckle_pos + d1 * (l1 * scale)
        add_solid_overlapping_limb(bm, knuckle_pos, p_joint1, 0.0080 * scale, 0.0065 * scale, segments=8, overlap=0.005 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0068 * scale, matrix=Matrix.Translation(p_joint1))

        # Phalanx 2 (Intermediate)
        d2 = (d1 - up * math.sin(curl_deg * 0.85)).normalized()
        p_joint2 = p_joint1 + d2 * (l2 * scale)
        add_solid_overlapping_limb(bm, p_joint1, p_joint2, 0.0065 * scale, 0.0050 * scale, segments=8, overlap=0.004 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0052 * scale, matrix=Matrix.Translation(p_joint2))

        # Phalanx 3 (Distal Razor Claw)
        d3 = (d2 - up * math.sin(curl_deg * 1.20)).normalized()
        p_tip = p_joint2 + d3 * (l3 * scale)
        add_solid_overlapping_limb(bm, p_joint2, p_tip, 0.0050 * scale, 0.0016 * scale, segments=6, overlap=0.004 * scale)

        # Micro-droplet suspended ahead of claw
        p_drop = p_tip + d3 * (0.016 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0030 * scale, matrix=Matrix.Translation(p_drop))

# -------------------------------------------------------------
# SCULPTED ORGANIC SUPERHERO HEAD (APPROVED)
# -------------------------------------------------------------

def build_organic_superhero_head(bm, center_pos=(0.0, 0.22, 1.76)):
    cx, cy, cz = center_pos

    # 1. Main Cranium (Lean athletic skull)
    mat_cranium = Matrix.Translation((cx, cy - 0.015, cz + 0.035)) @ Matrix.Diagonal((0.092, 0.112, 0.128, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0, matrix=mat_cranium)

    # 2. Forehead & Brow Ridge
    mat_brow = Matrix.Translation((cx, cy + 0.060, cz + 0.038)) @ Matrix.Rotation(math.radians(-15), 4, 'X') @ Matrix.Diagonal((0.082, 0.050, 0.032, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_brow)

    # 3. Visor Mask Face Shield
    mat_visor = Matrix.Translation((cx, cy + 0.060, cz + 0.010)) @ Matrix.Rotation(math.radians(18), 4, 'X') @ Matrix.Diagonal((0.075, 0.040, 0.038, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_visor)

    # 4. Cheekbones
    for side in [1.0, -1.0]:
        mat_cheek = Matrix.Translation((cx + side * 0.060, cy + 0.038, cz + 0.010)) @ Matrix.Diagonal((0.030, 0.045, 0.032, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cheek)

    # 5. Heroic V-Line Jaw & Temples
    for side in [1.0, -1.0]:
        p_temple = (cx + side * 0.070, cy - 0.01, cz + 0.01)
        p_chin = (cx + side * 0.016, cy + 0.052, cz - 0.062)
        add_solid_overlapping_limb(bm, p_temple, p_chin, 0.024, 0.018, segments=8, overlap=0.015)

    # 6. Crisp Athletic Chin
    mat_chin = Matrix.Translation((cx, cy + 0.055, cz - 0.062)) @ Matrix.Diagonal((0.036, 0.040, 0.032, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_chin)

    # 7. Aerodynamic Crown Crest
    mat_crest = Matrix.Translation((cx, cy - 0.068, cz + 0.052)) @ Matrix.Rotation(math.radians(-35), 4, 'X') @ Matrix.Diagonal((0.026, 0.105, 0.046, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_crest)

# -------------------------------------------------------------
# LEAN ATHLETIC HUMANOID SUPERHERO BODY
# -------------------------------------------------------------

def build_sleek_humanoid_superhero(col):
    mesh = bpy.data.meshes.new("SK_Player_SuperheroSleek_Mesh")
    obj = bpy.data.objects.new("SK_Player_SuperheroSleek", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    # 1. TORSO & SPINE (Slender athletic runner proportions)
    torso_segments = [
        ((0.0, 0.00, 0.90), (0.0, 0.04, 1.04), 0.150, 0.132), # Pelvis -> Lower Abs
        ((0.0, 0.04, 1.04), (0.0, 0.10, 1.20), 0.132, 0.124), # Lower Abs -> Narrow Waist
        ((0.0, 0.10, 1.20), (0.0, 0.18, 1.38), 0.124, 0.195), # Narrow Waist -> Ribcage/Lats
        ((0.0, 0.18, 1.38), (0.0, 0.24, 1.52), 0.195, 0.215), # Ribcage -> Broad Chest & Pectorals
        ((0.0, 0.24, 1.52), (0.0, 0.20, 1.62), 0.215, 0.095), # Chest -> Trapezius Slope
        ((0.0, 0.20, 1.62), (0.0, 0.22, 1.70), 0.065, 0.052)  # Trapezius -> Slender Athletic Neck
    ]
    for p1, p2, r1, r2 in torso_segments:
        add_solid_overlapping_limb(bm, p1, p2, r1, r2, segments=16, overlap=0.03)

    # 2. SCULPTED ORGANIC SUPERHERO HEAD (APPROVED)
    build_organic_superhero_head(bm, center_pos=(0.0, 0.22, 1.76))

    # 3. PECTORAL PLATES (Muscular contours)
    mat_pec_r = Matrix.Translation((0.10, 0.25, 1.44)) @ Matrix.Diagonal((0.12, 0.07, 0.10, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_r)
    mat_pec_l = Matrix.Translation((-0.10, 0.25, 1.44)) @ Matrix.Diagonal((0.12, 0.07, 0.10, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_l)

    # 4. RIGHT ARM (Lean forward sprint lead with MASTER ARTICULATED HAND)
    sh_r = (0.22, 0.22, 1.50)
    elbow_r = (0.34, 0.54, 1.44)
    wrist_r = (0.28, 0.88, 1.55)

    add_solid_overlapping_limb(bm, (0.12, 0.24, 1.52), sh_r, 0.098, 0.105, segments=12, overlap=0.02)
    add_solid_overlapping_limb(bm, sh_r, elbow_r, 0.105, 0.075, segments=12, overlap=0.025)
    add_solid_overlapping_limb(bm, elbow_r, wrist_r, 0.075, 0.034, segments=12, overlap=0.025) # Elegant carpal taper

    fwd_r = (Vector((0.24, 1.06, 1.64)) - Vector(wrist_r)).normalized()
    up_r = Vector((0.1, 0.2, 0.95)).normalized()
    build_master_articulated_hand(bm, wrist_r, fwd_r, up_r, is_right=True, scale=1.0)

    # 5. LEFT ARM (Lean backward swing with MASTER ARTICULATED HAND)
    sh_l = (-0.22, 0.20, 1.50)
    elbow_l = (-0.34, -0.10, 1.34)
    wrist_l = (-0.32, -0.40, 1.16)

    add_solid_overlapping_limb(bm, (-0.12, 0.24, 1.52), sh_l, 0.098, 0.105, segments=12, overlap=0.02)
    add_solid_overlapping_limb(bm, sh_l, elbow_l, 0.105, 0.075, segments=12, overlap=0.025)
    add_solid_overlapping_limb(bm, elbow_l, wrist_l, 0.075, 0.034, segments=12, overlap=0.025)

    fwd_l = (Vector((-0.30, -0.58, 1.02)) - Vector(wrist_l)).normalized()
    up_l = Vector((-0.1, -0.2, 0.95)).normalized()
    build_master_articulated_hand(bm, wrist_l, fwd_l, up_l, is_right=False, scale=0.96)

    # 6. RIGHT LEG (Lean sprint stride)
    hip_r = (0.115, 0.04, 0.88)
    knee_r = (0.155, 0.46, 0.90)
    ankle_r = (0.165, 0.78, 0.50)
    foot_r = (0.165, 0.96, 0.30)

    add_solid_overlapping_limb(bm, (0.055, 0.02, 0.90), hip_r, 0.135, 0.125, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, hip_r, knee_r, 0.125, 0.088, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, knee_r, ankle_r, 0.088, 0.052, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, ankle_r, foot_r, 0.052, 0.035, segments=10, overlap=0.02)

    # 7. LEFT LEG (Lean trailing sprint stride)
    hip_l = (-0.115, -0.04, 0.88)
    knee_l = (-0.155, -0.32, 0.68)
    ankle_l = (-0.165, -0.68, 0.34)
    foot_l = (-0.165, -0.86, 0.16)

    add_solid_overlapping_limb(bm, (-0.055, -0.02, 0.90), hip_l, 0.135, 0.125, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, hip_l, knee_l, 0.125, 0.088, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, knee_l, ankle_l, 0.088, 0.052, segments=12, overlap=0.03)
    add_solid_overlapping_limb(bm, ankle_l, foot_l, 0.052, 0.035, segments=10, overlap=0.02)

    # 8. Floating Ferrofluid Beads along body
    droplets = [
        (0.00, -0.15, 1.45, 0.018),
        (0.00, -0.28, 1.25, 0.016),
        (-0.14, -0.18, 1.35, 0.014),
        (0.14, -0.18, 1.35, 0.014),
        (0.20, 0.98, 0.22, 0.015),
        (-0.18, -0.92, 0.10, 0.014)
    ]
    for x, y, z, r in droplets:
        mat_drop = Matrix.Translation((x, y, z)) @ Matrix.Diagonal((r, r, r * 1.3, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_drop)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Fine voxel remesh at 0.0055 to preserve complete finger separation, knuckles & dorsal tendons
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.data.remesh_voxel_size = 0.0055
    bpy.ops.object.voxel_remesh()

    sm = obj.modifiers.new("Smooth", type='SMOOTH')
    sm.factor = 0.38
    sm.iterations = 2

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    for poly in obj.data.polygons:
        poly.use_smooth = True

    return obj

# -------------------------------------------------------------
# SLATE GREY SCI-FI STUDIO ENVIRONMENT & LIGHTING
# -------------------------------------------------------------

def build_scifi_studio_environment(col):
    mesh = bpy.data.meshes.new("ENV_SciFi_Studio_Dark_Mesh")
    obj = bpy.data.objects.new("ENV_SciFi_Studio_Dark", mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    mat_floor = Matrix.Translation((0, 0, -0.01)) @ Matrix.Diagonal((16.0, 16.0, 0.02, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_floor)

    for y_pos in [-3.0, -1.5, 0.0, 1.5, 3.0, 4.5]:
        mat_strip = Matrix.Translation((0, y_pos, 0.01)) @ Matrix.Diagonal((14.0, 0.12, 0.01, 1.0))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_strip)

    for x_pos in [-4.5, 4.5]:
        for y_pos in [-3.0, 0.5, 4.0]:
            mat_pillar = Matrix.Translation((x_pos, y_pos, 2.5)) @ Matrix.Diagonal((0.6, 0.6, 5.0, 1.0))
            bmesh.ops.create_cube(bm, size=1.0, matrix=mat_pillar)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mat_floor_dark = bpy.data.materials.get("M_DarX_DarkFloor_Graphite")
    if not mat_floor_dark:
        mat_floor_dark = bpy.data.materials.new("M_DarX_DarkFloor_Graphite")
        mat_floor_dark.use_nodes = True
        bsdf = mat_floor_dark.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.07, 0.08, 0.11, 1.0)
            bsdf.inputs["Metallic"].default_value = 0.30
            bsdf.inputs["Roughness"].default_value = 0.25
    obj.data.materials.clear()
    obj.data.materials.append(mat_floor_dark)
    return obj

def setup_lights():
    scene = bpy.context.scene
    # Key light: Neutral studio light
    key_name = "AOE_Player_Light_Key"
    if key_name in bpy.data.objects:
        key_obj = bpy.data.objects[key_name]
    else:
        k_data = bpy.data.lights.new(key_name, type='SUN')
        key_obj = bpy.data.objects.new(key_name, k_data)
        scene.collection.objects.link(key_obj)
    key_obj.data.energy = 4.0
    key_obj.data.color = (1.0, 0.98, 0.96)
    key_obj.location = (4.0, 4.0, 4.2)
    key_obj.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-45))

    # Front Key Light (Illuminates head, chest, hands)
    front_name = "AOE_Player_Light_FrontFace"
    if front_name in bpy.data.objects:
        front_obj = bpy.data.objects[front_name]
    else:
        ff_data = bpy.data.lights.new(front_name, type='SUN')
        front_obj = bpy.data.objects.new(front_name, ff_data)
        scene.collection.objects.link(front_obj)
    front_obj.data.energy = 3.5
    front_obj.data.color = (0.95, 0.95, 1.0)
    front_obj.location = (0.5, 3.5, 2.2)
    front_obj.rotation_euler = (math.radians(25), math.radians(10), math.radians(-150))

    # Electric Violet Rim Light
    rim_name = "AOE_Player_Light_Rim"
    if rim_name in bpy.data.objects:
        rim_obj = bpy.data.objects[rim_name]
    else:
        r_data = bpy.data.lights.new(rim_name, type='SUN')
        rim_obj = bpy.data.objects.new(rim_name, r_data)
        scene.collection.objects.link(rim_obj)
    rim_obj.data.energy = 8.0
    rim_obj.data.color = (0.85, 0.02, 1.0)
    rim_obj.location = (-4.0, -4.0, 2.8)
    rim_obj.rotation_euler = (math.radians(-50), math.radians(20), math.radians(135))

    # Soft ambient fill
    fill_name = "AOE_Player_Light_Fill"
    if fill_name in bpy.data.objects:
        fill_obj = bpy.data.objects[fill_name]
    else:
        f_data = bpy.data.lights.new(fill_name, type='SUN')
        fill_obj = bpy.data.objects.new(fill_name, f_data)
        scene.collection.objects.link(fill_obj)
    fill_obj.data.energy = 2.0
    fill_obj.data.color = (0.50, 0.60, 0.75)
    fill_obj.location = (0.0, 2.5, 0.4)

def render_camera_view(cam_pos, target_pos, lens, output_file, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "AOE_Player_Cam_Dyn"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    empty_name = "AOE_Player_Cam_Dyn_Target"
    if empty_name in bpy.data.objects:
        target_empty = bpy.data.objects[empty_name]
    else:
        target_empty = bpy.data.objects.new(empty_name, None)
        scene.collection.objects.link(target_empty)
    target_empty.location = target_pos

    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = target_empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    scene.camera = cam_obj

    scene.render.filepath = output_file
    bpy.ops.render.render(write_still=True)

def render_all_views(output_base_dir):
    os.makedirs(output_base_dir, exist_ok=True)
    scene = bpy.context.scene
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.10, 0.11, 0.15, 1.0)
            bg.inputs["Strength"].default_value = 0.8

    setup_lights()

    # 1. Front-3/4 Action View
    v1_file = os.path.join(output_base_dir, "view_action_34.png")
    render_camera_view((2.7, 2.7, 1.45), (0.0, 0.12, 1.05), 40.0, v1_file, res=(1920, 1080))
    print(f"RENDERED: {v1_file}")

    # 2. Front View (Head, Pectorals, Hands, Legs)
    v2_file = os.path.join(output_base_dir, "view_front.png")
    render_camera_view((0.0, 3.6, 1.25), (0.0, 0.12, 1.05), 45.0, v2_file, res=(960, 540))
    print(f"RENDERED: {v2_file}")

    # 3. Back View (Spine, Glutes, Deltoids, Crest)
    v3_file = os.path.join(output_base_dir, "view_back.png")
    render_camera_view((0.0, -3.6, 1.25), (0.0, 0.0, 1.05), 45.0, v3_file, res=(960, 540))
    print(f"RENDERED: {v3_file}")

    # 4. First-Person View (Forearm, Articulated Wrist & 5-finger Claw Hand)
    v4_file = os.path.join(output_base_dir, "view_fps.png")
    render_camera_view((0.10, 0.62, 1.72), (0.26, 1.02, 1.60), 28.0, v4_file, res=(960, 540))
    print(f"RENDERED: {v4_file}")

    # 5. Hand Close-Up Detail View (Splayed Fingers, Articulated Phalanges, Thumb Metacarpal)
    v5_file = os.path.join(output_base_dir, "view_hand_closeup.png")
    render_camera_view((0.44, 1.15, 1.76), (0.25, 0.98, 1.60), 58.0, v5_file, res=(1080, 1080))
    print(f"RENDERED: {v5_file}")

def main():
    args = parse_args()
    col = clean_collection("AOE_Player_DarkFluid")

    # 1. Build sleek humanoid superhero body with master articulated hands & wrists
    body = build_sleek_humanoid_superhero(col)
    env = build_scifi_studio_environment(col)

    # 2. Apply approved texture: Glossy Liquid Obsidian + Electric Purple Veins
    vein_mat = create_liquid_obsidian_purple_shader("M_DarX_DarkFluid_ElectricVeins")

    body.data.materials.clear()
    body.data.materials.append(vein_mat)

    for obj in bpy.data.objects:
        if obj.name not in ["SK_Player_SuperheroSleek", "ENV_SciFi_Studio_Dark"] and not obj.name.startswith("AOE_Player_"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    if args.preview_output:
        out_dir = os.path.dirname(os.path.abspath(args.preview_output))
        render_all_views(out_dir)

    if args.blend_file:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend_file)
        print(f"FILE_SAVED: {args.blend_file}")

if __name__ == "__main__":
    main()
