"""generate_boss_angel_cthulhu.py — Modelado 3D, Armadura, Renders 4 Vistas y Exportación FBX de Azra'Koth.

Jefe: Azra'Koth, El Heraldo Primordial — ABERRACIÓN DE PIEL HUMANA Y SANGRE (Eldritch Flesh Aberration v4).
Dimensiones: Altura 4.20 m, Envergadura de alas 5.60 m.
Pivote en el suelo (Z=0), Frente = -Y, Arriba = +Z (Regla 13).

DISEÑO: ABERRACIÓN DE PESADILLA BIOLÓGICA (BODY HORROR Y MUTACIÓN)
----------------------------------------------------------------------
1. PIEL HUMANA Y SANGRE REALISTA:
   - Dermis humana viva con Subsurface Scattering (SSS).
   - Sangre fresca líquida brillante (M_Monster_BloodWet) con bajísima rugosidad y alto clearcoat que chorrea por todo el cuerpo.
   - Carne viva lacerada y coágulos oscuros (M_Monster_FleshRaw) en heridas, bocas aberrantes y muñones.
   - Pústulas y tumores carnosos (M_Monster_Tumor) que deforman la silueta.

2. MUCHAS EXTREMIDADES POR TODO SU CUERPO:
   - 8 Brazos humanos en total:
     * Par principal depredador colosal.
     * Par de brazos torácicos secundarios que brotan bajo los pectorales intentando desgarrar al frente.
     * Par de brazos dorsales arácnidos que brotan de la espalda alta por encima de los hombros.
     * Par de brazos pélvicos cadavéricos que brotan de las caderas.
   - Racimos de dedos y manos parásitas que emergen de la carne y costillas rotas.
   - Piernas vestigiales atrofiadas detrás de los muslos.
   - Múltiples tentáculos y dedos prensiles faciales y cervicales.

3. DEFORMIDADES GROTESCAS:
   - Asimetría corporal severa: hombro deformado por hipertrofia tumoral.
   - Costillas quebradas que atraviesan la piel como espolones óseos ensangrentados.
   - Segunda boca aberrante vertical en el abdomen con dientes desalineados y sangre manante.
   - Ojos humanos múltiples dispersos por hombros, pecho y espalda.
   - Cresta de espinas vertebrales ensangrentadas desgarrando el dorso.
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Matrix, Vector, Euler

RAIZ_BLENDER = r"E:/Darx_Proyect/Art/Blender"
if RAIZ_BLENDER not in sys.path:
    sys.path.append(RAIZ_BLENDER)

import darx_lib as dl

COL_BOSS = "DARX_Boss_AngelCthulhu"
ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FBX_DIR = r"E:/Darx_Proyect/Art/FBX"
R = math.radians


def mat_skin(name, rgb_base, rough=0.45, sss_weight=0.72, sss_radius=(1.0, 0.35, 0.15), coat=0.18):
    """Crea un material Principled PBR de piel humana viva con Subsurface Scattering."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        nt.links.new(bsdf.outputs[0], out.inputs[0])

    bsdf.inputs["Base Color"].default_value = (*rgb_base, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0

    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = sss_weight
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = sss_radius
        if "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = 0.06
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = sss_weight
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.95, 0.38, 0.25, 1.0)

    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.20

    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.50

    m.diffuse_color = (*rgb_base, 1.0)
    m.roughness = rough
    m.metallic = 0.0
    return m


def crear_materiales_aberracion():
    m = {}
    # 1. Piel humana viva (dermis pálida con dispersión subdérmica cálida)
    m["M_Monster_HumanSkin"] = mat_skin("M_Monster_HumanSkin", (0.84, 0.66, 0.56), rough=0.45, sss_weight=0.72, coat=0.18)

    # 2. Piel humana estirada y tensa sobre costillas, articulaciones y pústulas
    m["M_Monster_SkinTense"] = mat_skin("M_Monster_SkinTense", (0.89, 0.75, 0.67), rough=0.34, sss_weight=0.45, coat=0.30)

    # 3. Sangre líquida brillante fresca (ultrahúmeda, viscosa y carmesí profunda)
    m["M_Monster_BloodWet"] = bpy.data.materials.get("M_Monster_BloodWet") or bpy.data.materials.new("M_Monster_BloodWet")
    m["M_Monster_BloodWet"].use_nodes = True
    nt_bl = m["M_Monster_BloodWet"].node_tree
    bsdf_bl = next((n for n in nt_bl.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf_bl is None:
        bsdf_bl = nt_bl.nodes.new("ShaderNodeBsdfPrincipled")
        out = next(n for n in nt_bl.nodes if n.type == 'OUTPUT_MATERIAL')
        nt_bl.links.new(bsdf_bl.outputs[0], out.inputs[0])
    bsdf_bl.inputs["Base Color"].default_value = (0.22, 0.012, 0.008, 1.0)
    bsdf_bl.inputs["Roughness"].default_value = 0.06
    bsdf_bl.inputs["Metallic"].default_value = 0.0
    if "Coat Weight" in bsdf_bl.inputs:
        bsdf_bl.inputs["Coat Weight"].default_value = 1.0
        if "Coat Roughness" in bsdf_bl.inputs:
            bsdf_bl.inputs["Coat Roughness"].default_value = 0.03
    if "Subsurface Weight" in bsdf_bl.inputs:
        bsdf_bl.inputs["Subsurface Weight"].default_value = 0.85
        if "Subsurface Radius" in bsdf_bl.inputs:
            bsdf_bl.inputs["Subsurface Radius"].default_value = (1.0, 0.15, 0.05)
    m["M_Monster_BloodWet"].diffuse_color = (0.35, 0.02, 0.01, 1.0)

    # 4. Carne viva lacerada y tejido muscular subcutáneo expuesto
    m["M_Monster_FleshRaw"] = mat_skin("M_Monster_FleshRaw", (0.44, 0.06, 0.05), rough=0.22, sss_weight=0.65, coat=0.50)

    # 5. Tumores y pústulas deformes
    m["M_Monster_Tumor"] = mat_skin("M_Monster_Tumor", (0.75, 0.54, 0.38), rough=0.32, sss_weight=0.55, coat=0.35)

    # 6. Hueso marfil y queratina de uñas / espolones / garras
    m["M_Monster_BoneNail"] = dl.mat("M_Monster_BoneNail", (0.91, 0.88, 0.82), rough=0.20, metal=0.06)

    # 7. Membrana de piel humana traslúcida estirada en las alas (con vetas venosas)
    m["M_Monster_WingSkin"] = mat_skin("M_Monster_WingSkin", (0.78, 0.48, 0.42), rough=0.36, sss_weight=0.88, coat=0.25)

    # 8. Oro celestial corrompido (aureola serafín ensangrentada)
    m["M_Angel_Gold"] = dl.mat("M_Angel_Gold", (0.94, 0.74, 0.18), rough=0.16, metal=0.95)

    # 9. Savia bio-celestial luminiscente (núcleo del corazón en el esternón)
    m["M_Bio_AcidGreen"] = dl.mat("M_Bio_AcidGreen", (0.06, 0.98, 0.22), rough=0.08,
                                  emis=(0.06, 0.98, 0.22), emis_str=5.5)

    # 10. Ojos humanos inyectados en sangre
    m["M_Bio_EyeCrimson"] = dl.mat("M_Bio_EyeCrimson", (0.96, 0.08, 0.06), rough=0.04,
                                   emis=(0.96, 0.08, 0.06), emis_str=4.0)
    return m


def build_boss_armature():
    """Crea la armadura ósea canónica para Azra'Koth (compatible 100% con UE5)."""
    arm_data = bpy.data.armatures.new("Armature_Boss_AngelCthulhu")
    arm_obj = bpy.data.objects.new("Armature_SK_Boss_AngelCthulhu", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    # 1. Root
    b_root = eb.new("root")
    b_root.head = (0, 0, 0)
    b_root.tail = (0, 0, 0.30)

    # 2. Pelvis (Z=1.40)
    b_pelvis = eb.new("pelvis")
    b_pelvis.head = (0, 0, 1.40)
    b_pelvis.tail = (0, 0, 1.70)
    b_pelvis.parent = b_root

    # 3. Columna vertebral (spine_01 y spine_02)
    b_spine1 = eb.new("spine_01")
    b_spine1.head = (0, 0, 1.70)
    b_spine1.tail = (0, -0.02, 2.20)
    b_spine1.parent = b_pelvis

    b_spine2 = eb.new("spine_02")
    b_spine2.head = (0, -0.02, 2.20)
    b_spine2.tail = (0, -0.04, 2.80)
    b_spine2.parent = b_spine1

    # 4. Cuello y Cabeza
    b_neck = eb.new("neck")
    b_neck.head = (0, -0.04, 2.80)
    b_neck.tail = (0, -0.08, 3.16)
    b_neck.parent = b_spine2

    b_head = eb.new("head")
    b_head.head = (0, -0.08, 3.16)
    b_head.tail = (0, -0.15, 3.75)
    b_head.parent = b_neck

    # 5. Aureola celestial flotante
    b_halo = eb.new("halo_root")
    b_halo.head = (0, -0.10, 4.05)
    b_halo.tail = (0, -0.10, 4.25)
    b_halo.parent = b_head

    # 6. 4 Extremidades / Dedos Quelíceros Faciales (Cthulhu)
    pos_queliceros = [
        ("mandible_l1", (-0.08, -0.34, 3.14), (-0.10, -0.46, 2.76), (-0.07, -0.50, 2.40), (-0.03, -0.44, 2.05)),
        ("mandible_l2", (-0.18, -0.30, 3.20), (-0.28, -0.42, 2.82), (-0.32, -0.46, 2.45), (-0.24, -0.40, 2.10)),
        ("mandible_r1", ( 0.08, -0.34, 3.14), ( 0.10, -0.46, 2.76), ( 0.07, -0.50, 2.40), ( 0.03, -0.44, 2.05)),
        ("mandible_r2", ( 0.18, -0.30, 3.20), ( 0.28, -0.42, 2.82), ( 0.32, -0.46, 2.45), ( 0.24, -0.40, 2.10)),
    ]
    for b_nom, p_h, p_j1, p_j2, p_tip in pos_queliceros:
        b_q1 = eb.new(f"{b_nom}_base")
        b_q1.head = p_h
        b_q1.tail = p_j1
        b_q1.parent = b_head

        b_q2 = eb.new(f"{b_nom}_mid")
        b_q2.head = p_j1
        b_q2.tail = p_j2
        b_q2.parent = b_q1

        b_q3 = eb.new(f"{b_nom}_claw")
        b_q3.head = p_j2
        b_q3.tail = p_tip
        b_q3.parent = b_q2

    # 7. 6 Alas Serafín
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        w_up1 = eb.new(f"wing_{lado}_upper_01")
        w_up1.head = (0.24 * sx, 0.15, 2.70)
        w_up1.tail = (1.15 * sx, 0.35, 3.55)
        w_up1.parent = b_spine2

        w_up2 = eb.new(f"wing_{lado}_upper_02")
        w_up2.head = (1.15 * sx, 0.35, 3.55)
        w_up2.tail = (2.35 * sx, 0.50, 4.15)
        w_up2.parent = w_up1

        w_md1 = eb.new(f"wing_{lado}_mid_01")
        w_md1.head = (0.22 * sx, 0.12, 2.40)
        w_md1.tail = (1.05 * sx, 0.30, 2.65)
        w_md1.parent = b_spine2

        w_md2 = eb.new(f"wing_{lado}_mid_02")
        w_md2.head = (1.05 * sx, 0.30, 2.65)
        w_md2.tail = (2.05 * sx, 0.40, 2.85)
        w_md2.parent = w_md1

        w_lw1 = eb.new(f"wing_{lado}_low_01")
        w_lw1.head = (0.20 * sx, 0.10, 1.85)
        w_lw1.tail = (0.85 * sx, 0.25, 1.70)
        w_lw1.parent = b_spine1

        w_lw2 = eb.new(f"wing_{lado}_low_02")
        w_lw2.head = (0.85 * sx, 0.25, 1.70)
        w_lw2.tail = (1.65 * sx, 0.35, 1.30)
        w_lw2.parent = w_lw1

    # 8. Brazos Primordiales
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        a_up = eb.new(f"arm_{lado}_upper")
        a_up.head = (0.46 * sx, -0.06, 2.62)
        a_up.tail = (0.72 * sx, -0.02, 2.05)
        a_up.parent = b_spine2

        a_fo = eb.new(f"arm_{lado}_forearm")
        a_fo.head = (0.72 * sx, -0.02, 2.05)
        a_fo.tail = (0.84 * sx, -0.22, 1.56)
        a_fo.parent = a_up

        a_hd = eb.new(f"hand_{lado}")
        a_hd.head = (0.84 * sx, -0.22, 1.56)
        a_hd.tail = (0.88 * sx, -0.34, 1.35)
        a_hd.parent = a_fo

    # 9. Piernas Levitantes
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        l_th = eb.new(f"leg_{lado}_thigh")
        l_th.head = (0.20 * sx, 0.02, 1.44)
        l_th.tail = (0.22 * sx, -0.06, 0.84)
        l_th.parent = b_pelvis

        l_sh = eb.new(f"leg_{lado}_shin")
        l_sh.head = (0.22 * sx, -0.06, 0.84)
        l_sh.tail = (0.20 * sx, -0.02, 0.26)
        l_sh.parent = l_th

        l_ft = eb.new(f"foot_{lado}")
        l_ft.head = (0.20 * sx, -0.02, 0.26)
        l_ft.tail = (0.18 * sx, -0.22, 0.02)
        l_ft.parent = l_sh

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj


def _crear_membrana_ala(bm, b_builder, p_base, ribs, mat, bone_name):
    """Crea una membrana poligonal de piel continua conectando las costillas del ala."""
    m_idx = b_builder.midx(mat)
    all_verts = []
    grid_verts = []

    for rib in ribs:
        row = []
        for pt in rib:
            v = bm.verts.new(pt)
            row.append(v)
            all_verts.append(v)
        grid_verts.append(row)

    for r in range(len(grid_verts) - 1):
        row_a = grid_verts[r]
        row_b = grid_verts[r + 1]
        n_pts = min(len(row_a), len(row_b))
        for i in range(n_pts - 1):
            try:
                f = bm.faces.new([row_a[i], row_a[i + 1], row_b[i + 1], row_b[i]])
                f.material_index = m_idx
                f.smooth = True
            except ValueError:
                pass

    if bone_name and b_builder._vb is not None:
        b_builder._vb.append((bone_name, all_verts))


def _crear_brazo_aberrante(b, p_sh, p_el, p_wr, p_palm, sx, mats, bone_name):
    """Genera un brazo humanoide adicional completo con piel, garras, inserción ensangrentada y orientación vectorial."""
    SK = mats["M_Monster_HumanSkin"]
    ST = mats["M_Monster_SkinTense"]
    FR = mats["M_Monster_FleshRaw"]
    BN = mats["M_Monster_BoneNail"]
    BL = mats["M_Monster_BloodWet"]

    b.bone(bone_name)
    # Muñón / inserción con carne viva lacerada y sangre manando
    b.sph(0.10, p_sh, scale=(1.1, 1.1, 1.1), u=10, v=6, m=FR)
    b.sph(0.08, (p_sh[0], p_sh[1] - 0.02, p_sh[2] - 0.03), scale=(1.0, 0.8, 1.2), u=8, v=6, m=BL)

    # Brazo superior
    b.seg(p_sh, p_el, 0.09, 0.07, m=SK, seg=12, smooth=True)
    b.sph(0.065, p_el, m=ST)

    # Antebrazo
    b.seg(p_el, p_wr, 0.07, 0.055, m=SK, seg=12, smooth=True)

    # Muñeca que une firmemente el antebrazo con la palma (sin brechas)
    b.seg(p_wr, p_palm, 0.055, 0.040, m=SK, seg=10, smooth=True)

    # Palma humana
    b.sph(0.045, p_palm, scale=(1.1, 0.7, 1.1), u=8, v=6, m=SK)

    # Vector direccional del brazo para proyectar los dedos hacia afuera
    v_wr = Vector(p_wr)
    v_palm = Vector(p_palm)
    d_arm = v_palm - v_wr
    if d_arm.length > 0.001:
        d_dir = d_arm.normalized()
    else:
        d_dir = Vector((0.0, -0.5, -0.85)).normalized()

    up_ref = Vector((0.0, 0.0, 1.0))
    side_vec = d_dir.cross(up_ref)
    if side_vec.length < 0.001:
        side_vec = Vector((1.0, 0.0, 0.0))
    else:
        side_vec = side_vec.normalized() * (1.0 if sx > 0 else -1.0)

    # 5 Dedos alargados con garras de marfil y sangre en las puntas
    for fx in [-0.032, -0.016, 0.0, 0.016, 0.032]:
        flen = 0.13 if abs(fx) < 0.01 else 0.10
        f_s = v_palm + side_vec * fx
        f_m = f_s + d_dir * (flen * 0.55)
        f_claw = f_m + d_dir * (flen * 0.45)
        b.seg(tuple(f_s), tuple(f_m), 0.014, 0.008, m=SK, seg=6, smooth=True)
        b.seg(tuple(f_m), tuple(f_claw), 0.008, 0.002, m=BN, seg=6)
        # Gota de sangre en la punta de la garra
        b.sph(0.006, tuple(f_claw), m=BL)


def build_boss_mesh(mats):
    """Construye la aberración viva de Azra'Koth: Piel humana, múltiples extremidades, deformidades y sangre."""
    b = dl.MB("SK_Boss_AngelCthulhu")

    SK = mats["M_Monster_HumanSkin"]    # Piel humana viva
    ST = mats["M_Monster_SkinTense"]    # Piel humana estirada/tensa
    FR = mats["M_Monster_FleshRaw"]     # Carne viva subcutánea expuesta
    BN = mats["M_Monster_BoneNail"]     # Queratina / hueso marfil
    WS = mats["M_Monster_WingSkin"]     # Membrana alar de piel humana
    AG = mats["M_Angel_Gold"]           # Aureola dorada
    SG = mats["M_Bio_AcidGreen"]        # Corazón bioluminiscente
    EC = mats["M_Bio_EyeCrimson"]       # Ojos inyectados en sangre
    BL = mats["M_Monster_BloodWet"]     # Sangre líquida fresca brillante
    TU = mats["M_Monster_Tumor"]        # Tumores y pústulas deformes

    # =========================================================================
    # 1. ROOT & PELVIS
    # =========================================================================
    b.bone("root")
    # Glifo sagrado circular profanado con charcos de sangre
    b.cyl(0.85, 0.04, (0, 0, 0.02), seg=24, m=SG)
    b.cyl(0.70, 0.06, (0, 0, 0.03), seg=20, m=AG)
    # Manchas de sangre sobre el glifo de invocación
    for bl_ang in [0.4, 1.6, 2.9, 4.2, 5.5]:
        bx = 0.55 * math.cos(bl_ang)
        by = 0.55 * math.sin(bl_ang)
        b.cyl(0.12, 0.015, (bx, by, 0.04), seg=10, m=BL)

    b.bone("pelvis")
    # Núcleo pélvico humanoide
    b.seg((0, 0.00, 1.40), (0, -0.02, 1.70), 0.24, 0.27, m=SK, seg=24, smooth=True)

    # Crestas ilíacas / caderas
    b.sph(0.14, (-0.24, 0.00, 1.56), scale=(0.8, 1.0, 1.0), u=14, v=8, m=ST)
    b.sph(0.14, ( 0.24, 0.00, 1.56), scale=(0.8, 1.0, 1.0), u=14, v=8, m=ST)

    # Vientre inferior con estrías de sangre manando desde el tórax
    b.sph(0.16, (0, -0.16, 1.52), scale=(1.2, 0.6, 0.9), u=14, v=8, m=SK)
    b.seg((0, -0.18, 1.65), (0, -0.17, 1.42), 0.025, 0.015, m=BL, seg=8, smooth=True) # Reguero de sangre

    # Glúteos estrictamente dorsales (+Y)
    b.sph(0.18, (-0.13, 0.16, 1.50), scale=(1.0, 0.85, 1.15), u=16, v=10, m=SK)
    b.sph(0.18, ( 0.13, 0.16, 1.50), scale=(1.0, 0.85, 1.15), u=16, v=10, m=SK)

    # =========================================================================
    # EXTREMIDADES ADICIONALES PÉLVICAS (Brazos que brotan de las caderas)
    # =========================================================================
    for sx in [-1.0, 1.0]:
        _crear_brazo_aberrante(
            b,
            p_sh=(0.28 * sx, 0.02, 1.55),
            p_el=(0.42 * sx, -0.08, 1.25),
            p_wr=(0.38 * sx, -0.18, 0.95),
            p_palm=(0.36 * sx, -0.22, 0.85),
            sx=sx,
            mats=mats,
            bone_name="pelvis"
        )

    # =========================================================================
    # 2. COLUMNA Y ABDOMEN ABERRANTE (spine_01: Z=1.70 -> 2.20)
    # =========================================================================
    b.bone("spine_01")
    # Tronco abdominal deformado
    b.seg((0, -0.02, 1.70), (0, -0.03, 2.20), 0.26, 0.30, m=SK, seg=24, smooth=True)

    # 6-Pack Rectus Abdominis desgarrado
    abs_coords = [
        (-0.075, -0.28, 1.84, 0.075, 0.05, 0.055), (0.075, -0.28, 1.84, 0.075, 0.05, 0.055),
        (-0.085, -0.30, 1.98, 0.085, 0.05, 0.055), (0.085, -0.30, 1.98, 0.085, 0.05, 0.055),
        (-0.090, -0.32, 2.12, 0.090, 0.05, 0.055), (0.090, -0.32, 2.12, 0.090, 0.05, 0.055),
    ]
    for ax, ay, az, sx, sy, sz in abs_coords:
        b.sph(sx, (ax, ay, az), scale=(1.0, sy / sx, sz / sx), u=10, v=6, m=SK)

    # BOCA ABERRANTE VERTICAL EN EL ABDOMEN (Segunda boca con carne viva y dientes)
    b.seg((-0.03, -0.29, 2.05), (-0.03, -0.29, 1.88), 0.045, 0.030, m=FR, seg=12, smooth=True)
    # Dientes humanos desalineados en el abdomen
    for dt_z in [2.02, 1.96, 1.91]:
        b.sph(0.009, (-0.045, -0.29, dt_z), m=BN)
        b.sph(0.009, (-0.015, -0.29, dt_z), m=BN)
    # Sangre viva brotando de la boca del abdomen
    b.seg((-0.03, -0.30, 1.90), (-0.03, -0.28, 1.70), 0.022, 0.012, m=BL, seg=8, smooth=True)

    # Costillas rotas que quiebran la piel hacia afuera (Deformidad esquelética)
    # Lado Izquierdo: Costilla astillada emergiendo de la carne
    b.seg((-0.20, -0.10, 2.05), (-0.38, -0.16, 2.15), 0.028, 0.012, m=BN, seg=8)
    b.sph(0.055, (-0.22, -0.11, 2.06), m=FR) # Carne rota alrededor de la costilla
    b.seg((-0.28, -0.13, 2.10), (-0.28, -0.13, 1.85), 0.018, 0.008, m=BL, seg=6) # Sangre que gotea de la fractura

    # Lado Derecho: Pústulas y tumores deformes
    b.sph(0.09, (0.24, -0.12, 1.95), scale=(1.1, 0.8, 1.3), u=10, v=6, m=TU)
    b.sph(0.05, (0.27, -0.18, 1.98), scale=(1.0, 1.2, 0.8), u=8, v=6, m=TU)
    b.sph(0.03, (0.28, -0.20, 1.94), m=BL) # Pústula reventada sangrante

    # Ojo humano abierto en el flanco abdominal derecho
    b.sph(0.030, (0.16, -0.28, 2.06), scale=(1.0, 0.8, 1.0), u=8, v=6, m=SK)
    b.sph(0.022, (0.16, -0.29, 2.06), u=8, v=6, m=BN)
    b.sph(0.013, (0.16, -0.30, 2.06), u=8, v=6, m=EC)

    # Vértebras lumbares dorsales con espinas afiladas
    for s_i in range(4):
        sz = 1.76 + s_i * 0.12
        b.sph(0.042, (0, 0.16, sz), scale=(0.8, 1.1, 0.8), u=8, v=6, m=ST)
        # Espina ósea dorsal
        b.seg((0, 0.16, sz), (0, 0.28, sz + 0.04), 0.018, 0.005, m=BN, seg=6)
        b.sph(0.008, (0, 0.28, sz + 0.04), m=BL)

    # =========================================================================
    # EXTREMIDADES ADICIONALES TORÁCICAS (Brazos que brotan bajo los pectorales)
    # =========================================================================
    for sx in [-1.0, 1.0]:
        _crear_brazo_aberrante(
            b,
            p_sh=(0.26 * sx, -0.18, 2.18),
            p_el=(0.42 * sx, -0.38, 2.00),
            p_wr=(0.32 * sx, -0.52, 1.82),
            p_palm=(0.26 * sx, -0.58, 1.75),
            sx=sx,
            mats=mats,
            bone_name="spine_01"
        )

    # =========================================================================
    # 3. TÓRAX, PECTORALES Y ESTERNÓN DESGARRADO (spine_02: Z=2.20 -> 2.80)
    # =========================================================================
    b.bone("spine_02")
    # Tronco torácico colosal
    b.seg((0, -0.03, 2.20), (0, -0.04, 2.80), 0.30, 0.35, m=SK, seg=24, smooth=True)

    # Pectorales desgarrados con laceraciones profundas
    # Pectoral Izquierdo
    b.box((0.24, 0.10, 0.24), (-0.17, -0.34, 2.52), rot=(R(10), R(-8), R(5)), m=SK, smooth=True)
    b.sph(0.18, (-0.17, -0.34, 2.52), scale=(1.20, 0.70, 0.95), u=14, v=10, m=SK)
    # Pectoral Derecho (Mutado, hinchado y deforme)
    b.box((0.26, 0.12, 0.26), ( 0.18, -0.35, 2.52), rot=(R(12), R(10), R(-7)), m=SK, smooth=True)
    b.sph(0.20, ( 0.18, -0.35, 2.52), scale=(1.30, 0.75, 1.05), u=14, v=10, m=SK)
    b.sph(0.08, ( 0.26, -0.38, 2.62), scale=(1.1, 0.9, 1.1), u=10, v=6, m=TU) # Tumor pectoral derecho

    # HENDIDURA DEL ESTERNÓN: Herida masiva abierta de carne viva y sangre manante
    b.seg((0, -0.34, 2.32), (0, -0.36, 2.66), 0.080, 0.105, m=FR, seg=16, smooth=True)
    # Núcleo bio-celestial palpitante
    b.sph(0.11, (0, -0.37, 2.48), scale=(0.8, 0.9, 1.2), u=16, v=10, m=SG)
    # Costillas óseas rotas clavadas hacia adentro
    for r_i, r_z in enumerate([2.40, 2.48, 2.56, 2.62]):
        b.seg((-0.12, -0.34, r_z), (-0.02, -0.40, r_z), 0.018, 0.010, m=BN, seg=8)
        b.seg(( 0.12, -0.34, r_z), ( 0.02, -0.40, r_z), 0.018, 0.010, m=BN, seg=8)
    
    # RÍO DE SANGRE VISCOSA que mana del esternón y cae en cascada por el abdomen
    b.seg((0, -0.38, 2.45), (0, -0.35, 2.15), 0.045, 0.030, m=BL, seg=12, smooth=True)
    b.seg((-0.04, -0.36, 2.35), (-0.06, -0.32, 1.95), 0.025, 0.015, m=BL, seg=10, smooth=True)
    b.seg(( 0.04, -0.36, 2.35), ( 0.06, -0.32, 1.95), 0.025, 0.015, m=BL, seg=10, smooth=True)

    # Racimo de dedos humanos parásitos que intentan SALIR del pecho desgarrado
    for f_idx, (fx, fz) in enumerate([(-0.06, 2.58), (-0.03, 2.62), (0.03, 2.60), (0.07, 2.55)]):
        b.seg((fx, -0.35, fz), (fx * 1.3, -0.44, fz + 0.04), 0.014, 0.008, m=SK, seg=6, smooth=True)
        b.seg((fx * 1.3, -0.44, fz + 0.04), (fx * 1.4, -0.48, fz + 0.02), 0.008, 0.002, m=BN, seg=6)
        b.sph(0.005, (fx * 1.4, -0.48, fz + 0.02), m=BL)

    # Espalda: Columna con espinas óseas colosales desgarrando la piel hacia atrás
    for s_i in range(5):
        sz = 2.26 + s_i * 0.11
        b.sph(0.048, (0, 0.18, sz), scale=(0.8, 1.2, 0.8), u=8, v=6, m=ST)
        # Espina ósea de marfil
        b.seg((0, 0.18, sz), (0, 0.36 + s_i * 0.02, sz + 0.05), 0.024, 0.006, m=BN, seg=8)
        # Sangre en la base y punta de la espina
        b.sph(0.020, (0, 0.20, sz), m=FR)
        b.sph(0.010, (0, 0.36 + s_i * 0.02, sz + 0.05), m=BL)

    # =========================================================================
    # EXTREMIDADES ADICIONALES DORSALES (Brazos arácnidos de la espalda alta)
    # =========================================================================
    for sx in [-1.0, 1.0]:
        _crear_brazo_aberrante(
            b,
            p_sh=(0.20 * sx, 0.16, 2.72),
            p_el=(0.48 * sx, 0.28, 3.12),
            p_wr=(0.54 * sx, 0.12, 3.46),
            p_palm=(0.46 * sx, -0.06, 3.68),
            sx=sx,
            mats=mats,
            bone_name="spine_02"
        )

    # =========================================================================
    # 4. CUELLO Y ROSTRO HUMANOIDE ELDRITCH MUTADO
    # =========================================================================
    b.bone("neck")
    # Columna muscular del cuello ensangrentada
    b.seg((0, -0.06, 2.80), (0, -0.10, 3.16), 0.18, 0.15, m=SK, seg=20, smooth=True)
    # Laceraciones en la garganta
    b.seg((-0.05, -0.22, 2.95), (0.05, -0.22, 2.92), 0.022, 0.018, m=FR, seg=8)
    b.seg((0, -0.23, 2.94), (0, -0.24, 2.78), 0.020, 0.010, m=BL, seg=8, smooth=True)

    b.bone("head")
    # Cráneo humanoide alargado hacia atrás con piel viva
    b.sph(0.30, (0, -0.05, 3.45), scale=(0.85, 1.15, 1.10), u=24, v=16, m=SK)

    # Frente humana y cejas cinceladas
    b.box((0.28, 0.10, 0.05), (0, -0.32, 3.54), rot=(R(14), 0, 0), m=SK, smooth=True)

    # Pómulos humanos estilizados
    b.sph(0.07, (-0.16, -0.26, 3.36), scale=(0.9, 0.5, 0.7), u=10, v=6, m=ST)
    b.sph(0.07, ( 0.16, -0.26, 3.36), scale=(0.9, 0.5, 0.7), u=10, v=6, m=ST)

    # Puente nasal demacrado
    b.seg((0, -0.30, 3.50), (0, -0.34, 3.34), 0.025, 0.016, m=SK, seg=8, smooth=True)

    # 6 Ojos humanos inyectados en sangre
    eyes_pos = [
        (-0.09, -0.30, 3.45), (-0.17, -0.27, 3.42), (-0.23, -0.21, 3.46),
        ( 0.09, -0.30, 3.45), ( 0.17, -0.27, 3.42), ( 0.23, -0.21, 3.46),
    ]
    for ex, ey, ez in eyes_pos:
        b.sph(0.032, (ex, ey, ez), scale=(1.0, 0.6, 0.7), u=8, v=6, m=SK)
        b.sph(0.026, (ex, ey - 0.012, ez), u=8, v=6, m=BN)
        b.sph(0.016, (ex, ey - 0.022, ez), u=8, v=6, m=EC)
        # Lágrima de sangre que baja de cada ojo
        b.seg((ex, ey - 0.022, ez), (ex * 0.95, ey - 0.020, ez - 0.12), 0.007, 0.002, m=BL, seg=6)

    # Ojo mutante adicional en la frente (tercer ojo aberrante)
    b.sph(0.032, (0, -0.33, 3.60), scale=(1.0, 0.7, 0.8), u=8, v=6, m=SK)
    b.sph(0.024, (0, -0.34, 3.60), u=8, v=6, m=BN)
    b.sph(0.015, (0, -0.35, 3.60), u=8, v=6, m=EC)
    b.seg((0, -0.35, 3.60), (0, -0.34, 3.48), 0.008, 0.003, m=BL, seg=6)

    # Cavidad interior de la garganta con carne viva
    b.seg((0, -0.20, 3.20), (0, -0.20, 3.04), 0.030, 0.020, m=FR, seg=12, smooth=True)

    # =========================================================================
    # 5. AUREOLA SERAFÍN CORROMPIDA Y ENSANGRENTADA
    # =========================================================================
    b.bone("halo_root")
    n_halo = 18
    r_halo = 0.50
    for h_i in range(n_halo):
        h_ang = h_i * (2.0 * math.pi / n_halo)
        hx = r_halo * math.cos(h_ang)
        hy = -0.10 + r_halo * math.sin(h_ang) * 0.70
        b.cyl(0.022, 0.10, (hx, hy, 4.05), rot=(0, math.pi/2, -h_ang), seg=8, m=AG)
        if h_i % 2 == 0:
            b.seg((hx, hy, 4.05), (hx * 1.25, hy * 1.15, 4.15), 0.016, 0.005, m=BN, seg=6)
            # Sangre en las puntas de la aureola
            b.sph(0.007, (hx * 1.25, hy * 1.15, 4.15), m=BL)

    # =========================================================================
    # 6. DEDOS QUELÍCEROS FACIALES (CTHULHU) ENSANGRENTADOS
    # =========================================================================
    pos_queliceros_pts = [
        ("mandible_l1", (-0.08, -0.34, 3.14), (-0.10, -0.46, 2.76), (-0.07, -0.50, 2.40), (-0.03, -0.44, 2.05)),
        ("mandible_r1", ( 0.08, -0.34, 3.14), ( 0.10, -0.46, 2.76), ( 0.07, -0.50, 2.40), ( 0.03, -0.44, 2.05)),
        ("mandible_l2", (-0.18, -0.30, 3.20), (-0.28, -0.42, 2.82), (-0.32, -0.46, 2.45), (-0.24, -0.40, 2.10)),
        ("mandible_r2", ( 0.18, -0.30, 3.20), ( 0.28, -0.42, 2.82), ( 0.32, -0.46, 2.45), ( 0.24, -0.40, 2.10)),
    ]
    for b_nom, p_base, p_j1, p_j2, p_tip in pos_queliceros_pts:
        b.bone(f"{b_nom}_base")
        b.seg(p_base, p_j1, 0.052, 0.044, m=SK, seg=12, smooth=True)
        b.sph(0.050, p_j1, m=ST)

        b.bone(f"{b_nom}_mid")
        b.seg(p_j1, p_j2, 0.044, 0.036, m=SK, seg=12, smooth=True)
        b.sph(0.042, p_j2, m=ST)

        b.bone(f"{b_nom}_claw")
        b.seg(p_j2, p_tip, 0.036, 0.022, m=SK, seg=10, smooth=True)
        p_nail_end = (p_tip[0] * 0.90, p_tip[1] + 0.06, p_tip[2] - 0.15)
        b.seg(p_tip, p_nail_end, 0.022, 0.004, m=BN, seg=8, smooth=True)
        # Sangre que gotea de cada tentáculo
        b.seg(p_nail_end, (p_nail_end[0], p_nail_end[1], p_nail_end[2] - 0.08), 0.006, 0.002, m=BL, seg=6)
        b.sph(0.008, (p_nail_end[0], p_nail_end[1], p_nail_end[2] - 0.08), m=BL)

    # 4 Tentáculos adicionales en el maxilar y cuello
    b.bone("head")
    for sx, xoff in [(-1.0, 0.24), (1.0, 0.24), (-1.0, 0.14), (1.0, 0.14)]:
        t_base = (xoff * sx, -0.24, 3.08)
        t_mid = (xoff * 1.3 * sx, -0.36, 2.70)
        t_tip = (xoff * 1.1 * sx, -0.40, 2.30)
        b.seg(t_base, t_mid, 0.028, 0.018, m=SK, seg=8, smooth=True)
        b.seg(t_mid, t_tip, 0.018, 0.005, m=BN, seg=8, smooth=True)
        b.sph(0.007, t_tip, m=BL)

    # =========================================================================
    # 7. 6 ALAS SERAFÍN CON PIEL ENSANGRENTADA Y LACERACIONES
    # =========================================================================
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        # --- PAR SUPERIOR ---
        b.bone(f"wing_{lado}_upper_01")
        p_w0 = (0.24 * sx, 0.15, 2.70)
        p_w1 = (1.15 * sx, 0.35, 3.55)
        b.seg(p_w0, p_w1, 0.085, 0.065, m=SK, seg=12, smooth=True)
        b.sph(0.090, p_w1, m=ST)

        b.bone(f"wing_{lado}_upper_02")
        p_w2 = (2.35 * sx, 0.50, 4.15)
        b.seg(p_w1, p_w2, 0.065, 0.045, m=ST, seg=10, smooth=True)

        struts_up = [
            [p_w2, (2.65 * sx, 0.45, 3.75), (2.85 * sx, 0.40, 3.30)],
            [p_w1, (2.15 * sx, 0.40, 3.20), (2.45 * sx, 0.35, 2.70)],
            [p_w1, (1.65 * sx, 0.32, 2.75), (1.95 * sx, 0.28, 2.20)],
            [p_w0, (1.15 * sx, 0.24, 2.30), (1.45 * sx, 0.20, 1.80)],
        ]
        for st in struts_up:
            for s_idx in range(len(st) - 1):
                b.seg(st[s_idx], st[s_idx + 1], 0.022, 0.010, m=BN, seg=8)
                # Salpicaduras de sangre en las falanges alares
                if s_idx == 1:
                    b.sph(0.018, st[s_idx], m=BL)

        _crear_membrana_ala(b.bm, b, p_w0, struts_up, WS, f"wing_{lado}_upper_02")

        # --- PAR MEDIO ---
        b.bone(f"wing_{lado}_mid_01")
        p_m0 = (0.22 * sx, 0.12, 2.40)
        p_m1 = (1.05 * sx, 0.30, 2.65)
        b.seg(p_m0, p_m1, 0.070, 0.055, m=SK, seg=10, smooth=True)

        b.bone(f"wing_{lado}_mid_02")
        p_m2 = (2.05 * sx, 0.40, 2.85)
        b.seg(p_m1, p_m2, 0.055, 0.040, m=ST, seg=8, smooth=True)

        struts_mid = [
            [p_m2, (2.25 * sx, 0.36, 2.50), (2.35 * sx, 0.32, 2.10)],
            [p_m1, (1.75 * sx, 0.30, 2.20), (1.85 * sx, 0.26, 1.75)],
            [p_m0, (1.20 * sx, 0.22, 1.85), (1.30 * sx, 0.18, 1.45)],
        ]
        for st in struts_mid:
            for s_idx in range(len(st) - 1):
                b.seg(st[s_idx], st[s_idx + 1], 0.018, 0.008, m=BN, seg=6)

        _crear_membrana_ala(b.bm, b, p_m0, struts_mid, WS, f"wing_{lado}_mid_02")

        # --- PAR INFERIOR ---
        b.bone(f"wing_{lado}_low_01")
        p_l0 = (0.20 * sx, 0.10, 1.85)
        p_l1 = (0.85 * sx, 0.25, 1.70)
        b.seg(p_l0, p_l1, 0.060, 0.045, m=SK, seg=8, smooth=True)

        b.bone(f"wing_{lado}_low_02")
        p_l2 = (1.65 * sx, 0.35, 1.30)
        b.seg(p_l1, p_l2, 0.045, 0.035, m=ST, seg=8, smooth=True)

        struts_low = [
            [p_l2, (1.75 * sx, 0.30, 1.00), (1.80 * sx, 0.26, 0.70)],
            [p_l1, (1.30 * sx, 0.24, 0.95), (1.35 * sx, 0.20, 0.65)],
            [p_l0, (0.75 * sx, 0.18, 0.90), (0.80 * sx, 0.14, 0.60)],
        ]
        for st in struts_low:
            for s_idx in range(len(st) - 1):
                b.seg(st[s_idx], st[s_idx + 1], 0.016, 0.007, m=BN, seg=6)

        _crear_membrana_ala(b.bm, b, p_l0, struts_low, WS, f"wing_{lado}_low_02")

    # =========================================================================
    # 8. BRAZOS PRINCIPALES DEPREDADORES ENSANGRENTADOS
    # =========================================================================
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        b.bone(f"arm_{lado}_upper")
        p_sh = (0.46 * sx, -0.06, 2.62)
        b.sph(0.18, p_sh, scale=(1.2, 1.0, 1.1), u=14, v=10, m=SK)
        p_el = (0.72 * sx, -0.02, 2.05)
        b.seg(p_sh, p_el, 0.14, 0.11, m=SK, seg=16, smooth=True)
        b.sph(0.075, (0.72 * sx, 0.05, 2.05), m=ST)

        b.bone(f"arm_{lado}_forearm")
        p_wr = (0.84 * sx, -0.22, 1.56)
        b.seg(p_el, p_wr, 0.11, 0.085, m=SK, seg=16, smooth=True)
        # Regueros de sangre bajando por el antebrazo
        b.seg((0.80 * sx, -0.12, 1.95), (0.83 * sx, -0.20, 1.60), 0.015, 0.008, m=BL, seg=8, smooth=True)

        b.bone(f"hand_{lado}")
        p_palm = (0.86 * sx, -0.26, 1.48)
        b.box((0.12, 0.09, 0.05), p_palm, rot=(R(25), R(sx * 15), 0), m=SK, smooth=True)
        # 5 Dedos alargados empapados en sangre
        fingers = [
            ( 0.04 * sx, -0.06,  0.01, 0.10),
            ( 0.02 * sx, -0.10, -0.04, 0.16),
            (-0.01 * sx, -0.11, -0.06, 0.18),
            (-0.04 * sx, -0.10, -0.04, 0.16),
            (-0.07 * sx, -0.08, -0.02, 0.12),
        ]
        for fx, fy, fz, flen in fingers:
            f_start = (p_palm[0] + fx, p_palm[1] + fy, p_palm[2] + fz)
            f_end = (f_start[0] + fx * 0.3, f_start[1] - flen * 0.6, f_start[2] - flen * 0.8)
            b.seg(f_start, f_end, 0.020, 0.012, m=SK, seg=8, smooth=True)
            f_claw = (f_end[0], f_end[1] - 0.05, f_end[2] - 0.06)
            b.seg(f_end, f_claw, 0.012, 0.003, m=BN, seg=6)
            # Sangre que gotea de cada uña
            b.sph(0.008, f_claw, m=BL)

    # =========================================================================
    # 9. PIERNAS HUMANAS CON EXTREMIDADES VESTIGIALES Y SANGRE
    # =========================================================================
    for lado, sx in [("l", -1.0), ("r", 1.0)]:
        b.bone(f"leg_{lado}_thigh")
        p_hip = (0.20 * sx, 0.02, 1.44)
        p_knee = (0.22 * sx, -0.06, 0.84)
        b.seg(p_hip, p_knee, 0.16, 0.12, m=SK, seg=20, smooth=True)
        b.sph(0.085, (0.22 * sx, -0.14, 0.84), scale=(0.9, 0.6, 1.1), u=10, v=6, m=ST)

        # Pierna vestigial atrofiada secundaria que cuelga detrás del muslo
        p_vest_hip = (0.16 * sx, 0.12, 1.38)
        p_vest_knee = (0.18 * sx, 0.18, 0.95)
        p_vest_foot = (0.16 * sx, 0.15, 0.60)
        b.seg(p_vest_hip, p_vest_knee, 0.060, 0.040, m=SK, seg=10, smooth=True)
        b.seg(p_vest_knee, p_vest_foot, 0.040, 0.020, m=SK, seg=10, smooth=True)
        b.seg(p_vest_foot, (p_vest_foot[0], p_vest_foot[1] - 0.06, p_vest_foot[2] - 0.05), 0.015, 0.003, m=BN, seg=6)
        b.sph(0.008, (p_vest_foot[0], p_vest_foot[1] - 0.06, p_vest_foot[2] - 0.05), m=BL)

        b.bone(f"leg_{lado}_shin")
        p_ank = (0.20 * sx, -0.02, 0.26)
        b.seg(p_knee, p_ank, 0.12, 0.08, m=SK, seg=18, smooth=True)
        b.sph(0.095, (0.21 * sx, 0.06, 0.68), scale=(0.9, 1.1, 1.3), u=10, v=6, m=SK)
        # Sangre bajando por la espinilla
        b.seg((0.21 * sx, -0.08, 0.78), (0.20 * sx, -0.04, 0.32), 0.014, 0.006, m=BL, seg=8, smooth=True)

        b.sph(0.040, (0.15 * sx, -0.02, 0.26), m=ST)
        b.sph(0.040, (0.25 * sx, -0.02, 0.26), m=ST)

        b.bone(f"foot_{lado}")
        p_toe = (0.18 * sx, -0.18, 0.05)
        b.seg(p_ank, p_toe, 0.075, 0.055, m=SK, seg=12, smooth=True)
        for tx, ty in [(-0.035, -0.05), (0.00, -0.07), (0.035, -0.05)]:
            t_claw = (p_toe[0] + tx * sx, p_toe[1] + ty - 0.08, 0.01)
            b.seg((p_toe[0] + tx * sx, p_toe[1] + ty, 0.05), t_claw, 0.018, 0.004, m=BN, seg=6)
            b.sph(0.007, t_claw, m=BL)

    mesh_obj = b.build(COL_BOSS)
    return mesh_obj


def renderizar_cuatro_vistas(mesh_obj, arm_obj):
    """Renderiza las 4 perspectivas canónicas de validación visual con EEVEE en alta calidad."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    sc = bpy.context.scene

    motores = [item.identifier for item in bpy.types.Scene.bl_rna.properties['render'].fixed_type.properties['engine'].enum_items]
    if 'BLENDER_EEVEE_NEXT' in motores:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    else:
        sc.render.engine = 'BLENDER_EEVEE'

    sc.render.resolution_x = 1024
    sc.render.resolution_y = 1024
    sc.render.film_transparent = False

    w = bpy.data.worlds.get("DarxBossWorldAngel") or bpy.data.worlds.new("DarxBossWorldAngel")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.025, 0.028, 0.035, 1.0)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.world = w

    objs = [mesh_obj, arm_obj]
    center_focus = (0, -0.10, 2.45)

    # 1. Vista Frontal
    out_front = os.path.join(ARTIFACTS_DIR, "preview_boss_angel_cthulhu_frontal.png")
    dl.snap(objs, out_front, focus=center_focus, dist=8.2, yaw=0.0, pitch=6.0, res=1024, engine=sc.render.engine)

    # 2. Vista Trasera
    out_back = os.path.join(ARTIFACTS_DIR, "preview_boss_angel_cthulhu_trasera.png")
    dl.snap(objs, out_back, focus=center_focus, dist=8.2, yaw=180.0, pitch=6.0, res=1024, engine=sc.render.engine)

    # 3. Vista de Acción / Ataque
    out_action = os.path.join(ARTIFACTS_DIR, "preview_boss_angel_cthulhu_ataque.png")
    dl.snap(objs, out_action, focus=center_focus, dist=7.8, yaw=32.0, pitch=12.0, res=1024, engine=sc.render.engine)

    # 4. Vista Primera Persona (FPS)
    out_fps = os.path.join(ARTIFACTS_DIR, "preview_boss_angel_cthulhu_fps.png")
    dl.snap(objs, out_fps, focus=(0, -0.16, 2.70), dist=4.8, yaw=0.0, pitch=-8.0, res=1024, engine=sc.render.engine)

    print("DarX | Renders de 4 vistas generados con éxito:")
    print(f"  - Frontal: {out_front}")
    print(f"  - Trasera: {out_back}")
    print(f"  - Ataque: {out_action}")
    print(f"  - FPS: {out_fps}")


def main():
    print("DarX | Generando Jefe: Azra'Koth — ABERRACIÓN DE PIEL HUMANA Y SANGRE (v4)...")
    dl.wipe(COL_BOSS)

    mats = crear_materiales_aberracion()
    arm_obj = build_boss_armature()
    mesh_obj = build_boss_mesh(mats)

    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj

    renderizar_cuatro_vistas(mesh_obj, arm_obj)

    fbx_out = os.path.join(FBX_DIR, "SK_Boss_AngelCthulhu.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        bake_anim=False
    )
    print(f"DarX | Exportado FBX exitosamente: {fbx_out}")
    print("=== MODELADO DE AZRA'KOTH (ABERRACIÓN PIEL Y SANGRE) COMPLETADO ===")


if __name__ == "__main__":
    main()
