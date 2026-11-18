"""generate_biome_lab_phase3_assets.py — Fase 3: 12 Nuevos Objetos de Laboratorio por Bioma.

Modelado 3D de alta densidad, micro-detalles AAA, renders Cycles/EEVEE y exportación canónica FBX:
- Bioma 1 (Biohazard):
  1. SM_Bio_Centrifuge_Extractor (Centrífuga extractora acorazada con rotor basculante y viales biológicos)
  2. SM_Bio_Decontamination_Shower (Ducha de descontaminación de alta presión con marco octogonal y toberas)
  3. SM_Bio_Spore_Cryo_Storage (Banco criogénico horizontal de esporas con 4 esclusas herméticas y nitrógeno)
  4. SM_Bio_Specimen_Dissection_Slab (Mesa quirúrgica de acero quirúrgico oscuro con canales de fluidos y lámpara articulada)
- Bioma 2 (Clean Room / Acelerador Cuántico):
  5. SM_Clean_Toroidal_Superconductor (Superconductor toroidal masivo con 12 bobinas magnéticas en cromo y base cerámica)
  6. SM_Clean_Vacuum_Chamber_Node (Nodo de cámara de ultra-alto vacío UHV esférico con 6 bridas ConFlat y bomba turbomolecular)
  7. SM_Clean_Air_Shower_Portal (Portal monolítico de paso estéril con micro-toberas laminares e iluminación cian)
  8. SM_Clean_Collimator_Station (Banco óptico de colimación con riel micrométrico, diafragma iris y sensor cuántico)
- Bioma 3 (Robótica / Ensamblaje Mecatrónico):
  9. SM_Robo_Gantry_Welding_Arm (Brazo robótico de soldadura suspendido en gantry de 4 DOF con umbilical y tobera de arco)
  10. SM_Robo_Induction_Furnace (Horno de fundición por inducción electromagnética con bobinas de cobre y núcleo ardiente)
  11. SM_Robo_Pneumatic_Manifold (Manifold mural vertical de distribución neumática con 8 electroválvulas y manómetros)
  12. SM_Robo_Exoskeleton_Dock (Estación de recarga y soporte vertical de exoesqueleto con abrazaderas biomecánicas)

Cumple con:
- Regla 3: Diseños 100% únicos y no clonados.
- Regla 4 y 5: Renders en 4 cuadrantes y showcases antes de importar.
- Regla 11: Estructura de 5 fases de modelado 3D.
- Regla 13: Eje canónico -Y en Blender -> +X en Unreal Engine.
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

COL_MAESTRA = "DARX_MegaFase_Biomas_Phase3"
ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FBX_SUBDIR = "Biomas"

# ==============================================================================
# DEFINICIÓN DE MATERIALES PBR CALIBRADOS
# ==============================================================================
def crear_materiales():
    m = {}
    # --- BIOMA 1: BIOHAZARD ---
    m["M_Bio_DarkMetal"] = dl.mat("M_Bio_DarkMetal", (0.035, 0.045, 0.040), rough=0.48, metal=0.90)
    m["M_Bio_PipeYellow"] = dl.mat("M_Bio_PipeYellow", (0.88, 0.65, 0.06), rough=0.35, metal=0.35)
    m["M_Bio_AcidGreen"] = dl.mat("M_Bio_AcidGreen", (0.05, 0.96, 0.12), rough=0.12, emis=(0.05, 0.98, 0.12), emis_str=4.8)
    m["M_Bio_Glass"] = dl.mat("M_Bio_Glass", (0.05, 0.22, 0.09), rough=0.03, metal=0.12, emis=(0.02, 0.38, 0.08), emis_str=1.4)
    m["M_Bio_ChitinFlesh"] = dl.mat("M_Bio_ChitinFlesh", (0.10, 0.032, 0.032), rough=0.78, metal=0.05)
    m["M_Bio_HazardSign"] = dl.mat("M_Bio_HazardSign", (0.94, 0.60, 0.02), rough=0.28, metal=0.10)
    m["M_Bio_ScreenGreen"] = dl.mat("M_Bio_ScreenGreen", (0.02, 0.88, 0.14), rough=0.08, emis=(0.02, 0.92, 0.14), emis_str=4.2)
    m["M_Bio_BrassValve"] = dl.mat("M_Bio_BrassValve", (0.82, 0.62, 0.18), rough=0.25, metal=0.95)

    # --- BIOMA 2: SALA LIMPIA / CUÁNTICO ---
    m["M_Clean_WhiteCeramic"] = dl.mat("M_Clean_WhiteCeramic", (0.93, 0.94, 0.96), rough=0.14, metal=0.04)
    m["M_Clean_Chrome"] = dl.mat("M_Clean_Chrome", (0.96, 0.96, 0.98), rough=0.02, metal=0.99)
    m["M_Clean_CyanNeon"] = dl.mat("M_Clean_CyanNeon", (0.0, 0.88, 1.0), rough=0.06, emis=(0.0, 0.88, 1.0), emis_str=5.0)
    m["M_Clean_Glass"] = dl.mat("M_Clean_Glass", (0.84, 0.94, 0.99), rough=0.015, metal=0.06)
    m["M_Clean_DarkMetal"] = dl.mat("M_Clean_DarkMetal", (0.025, 0.025, 0.035), rough=0.32, metal=0.94)
    m["M_Clean_Crystal"] = dl.mat("M_Clean_Crystal", (0.18, 0.72, 0.95), rough=0.05, metal=0.10, emis=(0.12, 0.58, 0.88), emis_str=3.0)

    # --- BIOMA 3: ROBÓTICA ---
    m["M_Robo_CobaltSteel"] = dl.mat("M_Robo_CobaltSteel", (0.038, 0.075, 0.175), rough=0.30, metal=0.89)
    m["M_Robo_CopperBronze"] = dl.mat("M_Robo_CopperBronze", (0.78, 0.42, 0.14), rough=0.20, metal=0.96)
    m["M_Robo_AmberCore"] = dl.mat("M_Robo_AmberCore", (1.0, 0.58, 0.03), rough=0.04, emis=(1.0, 0.58, 0.03), emis_str=4.6)
    m["M_Robo_HazardStripe"] = dl.mat("M_Robo_HazardStripe", (0.92, 0.65, 0.05), rough=0.35, metal=0.15)
    m["M_Robo_ScreenAmber"] = dl.mat("M_Robo_ScreenAmber", (0.98, 0.55, 0.04), rough=0.08, emis=(0.98, 0.55, 0.04), emis_str=4.4)
    m["M_Robo_Porcelain"] = dl.mat("M_Robo_Porcelain", (0.45, 0.22, 0.12), rough=0.18, metal=0.02)
    return m

# ==============================================================================
# 1. BIOMA 1: BIOHAZARD (4 PROPS NUEVOS)
# ==============================================================================

def modelar_bio_centrifuge_extractor(mats):
    """SM_Bio_Centrifuge_Extractor: Centrífuga de extracción rotacional con tambor de 8 viales biológicos."""
    b = dl.MB("SM_Bio_Centrifuge_Extractor")
    DM, PY, AG, GL, CF, BV, SG, HZ = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"],
        mats["M_Bio_Glass"], mats["M_Bio_ChitinFlesh"], mats["M_Bio_BrassValve"],
        mats["M_Bio_ScreenGreen"], mats["M_Bio_HazardSign"]
    )
    # Pedestal y carcasa principal angulada
    b.box((1.80, 1.10, 0.22), (0, 0, 0.11), m=DM)
    b.box((1.65, 0.95, 0.65), (0, 0, 0.54), m=DM)
    # Franjas de advertencia en zócalo
    b.box((1.82, 0.04, 0.10), (0, -0.56, 0.10), m=HZ)
    b.box((1.82, 0.04, 0.10), (0, 0.56, 0.10), m=HZ)

    # Tambor cilíndrico superior empotrado
    b.cyl(0.48, 0.35, (-0.25, 0, 0.98), seg=24, m=DM)
    b.cyl(0.42, 0.18, (-0.25, 0, 1.05), seg=20, m=PY)

    # 8 Rotores basculantes con viales de fluido ácido
    for ang_i in range(8):
        theta = ang_i * (2.0 * math.pi / 8.0)
        rx = -0.25 + 0.28 * math.cos(theta)
        ry = 0.28 * math.sin(theta)
        # Portavial
        b.cyl(0.045, 0.18, (rx, ry, 1.06), rot=(0.25 * math.sin(theta), -0.25 * math.cos(theta), theta), seg=10, m=BV)
        # Vial con líquido fluorescente
        b.cyl(0.035, 0.14, (rx, ry, 1.06), rot=(0.25 * math.sin(theta), -0.25 * math.cos(theta), theta), seg=8, m=AG)

    # Tapa basculante semi-abierta con bisagra masiva
    b.cyl(0.49, 0.06, (-0.25, 0.08, 1.25), rot=(0.32, 0, 0), seg=24, m=DM)
    b.cyl(0.24, 0.03, (-0.25, 0.08, 1.26), rot=(0.32, 0, 0), seg=16, m=GL)
    b.cyl(0.06, 0.35, (-0.25, 0.52, 1.15), rot=(0, math.pi/2, 0), seg=12, m=BV)

    # Consola de control y tacómetro a la derecha
    b.box((0.55, 0.80, 0.40), (0.50, 0, 0.95), m=DM)
    b.box((0.45, 0.30, 0.20), (0.50, -0.15, 1.18), rot=(0.35, 0, 0), m=SG)
    # Perillas de calibración RPM
    for px in [0.38, 0.50, 0.62]:
        b.cyl(0.035, 0.05, (px, 0.15, 1.16), seg=10, m=BV)

    # Tuberías de drenaje lateral
    b.cyl(0.04, 0.85, (0.85, -0.20, 0.45), seg=10, m=PY)
    b.cyl(0.04, 0.45, (0.85, 0.02, 0.85), rot=(math.pi/2, 0, 0), seg=10, m=PY)

    return b.build(COL_MAESTRA)

def modelar_bio_decontamination_shower(mats):
    """SM_Bio_Decontamination_Shower: Ducha octogonal de descontaminación cáustica con toberas y válvula de pánico."""
    b = dl.MB("SM_Bio_Decontamination_Shower")
    DM, PY, AG, GL, BV, HZ, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"],
        mats["M_Bio_Glass"], mats["M_Bio_BrassValve"], mats["M_Bio_HazardSign"],
        mats["M_Bio_ScreenGreen"]
    )
    # Plataforma de drenaje con rejilla
    b.box((1.40, 1.40, 0.16), (0, 0, 0.08), m=DM)
    b.box((1.15, 1.15, 0.03), (0, 0, 0.17), m=DM)
    # Drenaje central con sifón
    b.cyl(0.20, 0.04, (0, 0, 0.18), seg=16, m=PY)

    # 4 Columnas estructurales cuadradas
    for cx in [-0.60, 0.60]:
        for cy in [-0.60, 0.60]:
            b.box((0.12, 0.12, 2.45), (cx, cy, 1.28), m=DM)
            b.box((0.16, 0.16, 0.10), (cx, cy, 0.20), m=PY)

    # Marco superior de soporte
    b.box((1.40, 0.12, 0.14), (0, -0.60, 2.50), m=DM)
    b.box((1.40, 0.12, 0.14), (0, 0.60, 2.50), m=DM)
    b.box((0.12, 1.20, 0.14), (-0.60, 0, 2.50), m=DM)
    b.box((0.12, 1.20, 0.14), (0.60, 0, 2.50), m=DM)

    # Colector circular superior de aspersión
    b.cyl(0.45, 0.08, (0, 0, 2.42), seg=20, m=PY)
    # 6 Toberas cónicas orientadas hacia el centro
    for ang in range(6):
        a = ang * (2.0 * math.pi / 6.0)
        nx = 0.32 * math.cos(a)
        ny = 0.32 * math.sin(a)
        b.cyl(0.04, 0.10, (nx, ny, 2.35), rot=(0.20 * math.sin(a), -0.20 * math.cos(a), a), seg=10, m=BV)

    # Depósito de biocida superior translúcido
    b.cyl(0.28, 0.50, (0, 0, 2.75), seg=18, m=GL)
    b.cyl(0.24, 0.44, (0, 0, 2.75), seg=14, m=AG)
    b.cyl(0.30, 0.08, (0, 0, 3.02), seg=18, m=DM)

    # Tubería lateral descendente de alimentación con manómetro
    b.cyl(0.04, 2.20, (0.62, 0.35, 1.35), seg=12, m=PY)
    b.cyl(0.08, 0.05, (0.62, 0.35, 1.80), rot=(0, math.pi/2, 0), seg=12, m=SG)

    # Palanca de emergencia de tirón triangular
    b.box((0.08, 0.08, 0.15), (0.62, -0.35, 1.50), m=HZ)
    b.cyl(0.015, 0.45, (0.50, -0.35, 1.30), seg=8, m=BV)
    b.box((0.12, 0.04, 0.08), (0.50, -0.35, 1.05), m=PY)

    return b.build(COL_MAESTRA)

def modelar_bio_spore_cryo_storage(mats):
    """SM_Bio_Spore_Cryo_Storage: Banco criogénico horizontal de esporas con 4 esclusas herméticas."""
    b = dl.MB("SM_Bio_Spore_Cryo_Storage")
    DM, PY, AG, GL, BV, HZ, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"],
        mats["M_Bio_Glass"], mats["M_Bio_BrassValve"], mats["M_Bio_HazardSign"],
        mats["M_Bio_ScreenGreen"]
    )
    # Chasis principal horizontal acorazado
    b.box((2.40, 0.90, 0.85), (0, 0, 0.42), m=DM)
    # Patas de soporte antivibración
    for px in [-1.05, -0.35, 0.35, 1.05]:
        for py in [-0.38, 0.38]:
            b.box((0.14, 0.12, 0.16), (px, py, 0.08), m=PY)

    # 4 Compuertas herméticas cuadradas con cierres perimétricos
    pos_esc = [-0.85, -0.28, 0.28, 0.85]
    for ex in pos_esc:
        # Marco de sellado térmico
        b.box((0.44, 0.65, 0.08), (ex, 0, 0.88), m=DM)
        b.box((0.36, 0.55, 0.06), (ex, 0, 0.92), m=PY)
        # Mirilla circular con escarcha
        b.cyl(0.10, 0.08, (ex, 0, 0.94), seg=16, m=GL)
        b.cyl(0.08, 0.04, (ex, 0, 0.92), seg=12, m=AG)
        # Pasador de bloqueo manual
        b.cyl(0.025, 0.22, (ex, 0.30, 0.96), rot=(0, math.pi/2, 0), seg=8, m=BV)

    # Chaqueta lateral de nitrógeno líquido con tubería colectora
    b.cyl(0.045, 2.30, (0, -0.42, 0.65), rot=(0, math.pi/2, 0), seg=12, m=PY)
    for ex in pos_esc:
        b.cyl(0.03, 0.15, (ex, -0.42, 0.75), seg=8, m=BV)
        # Manómetro individual
        b.cyl(0.05, 0.03, (ex, -0.45, 0.82), rot=(math.pi/2, 0, 0), seg=12, m=SG)

    # Consola central de control criogénico
    b.box((0.45, 0.25, 0.30), (0, 0.32, 1.02), m=DM)
    b.box((0.38, 0.03, 0.22), (0, 0.44, 1.04), rot=(-0.25, 0, 0), m=SG)
    b.box((0.25, 0.04, 0.10), (0, -0.44, 0.35), m=HZ)

    return b.build(COL_MAESTRA)

def modelar_bio_specimen_dissection_slab(mats):
    """SM_Bio_Specimen_Dissection_Slab: Mesa quirúrgica de autopsia biológica con canales y brazo de lámpara."""
    b = dl.MB("SM_Bio_Specimen_Dissection_Slab")
    DM, PY, AG, GL, BV, CF, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"],
        mats["M_Bio_Glass"], mats["M_Bio_BrassValve"], mats["M_Bio_ChitinFlesh"],
        mats["M_Bio_ScreenGreen"]
    )
    # Columna telescópica central masiva
    b.box((0.70, 0.50, 0.20), (0, 0, 0.10), m=DM)
    b.cyl(0.18, 0.55, (0, 0, 0.40), seg=18, m=DM)
    b.cyl(0.15, 0.50, (0, 0, 0.42), seg=16, m=PY)

    # Placa quirúrgica cóncava de acero
    b.box((2.30, 0.85, 0.14), (0, 0, 0.75), m=DM)
    # Reborde perimetral y canal colector
    b.box((2.32, 0.06, 0.22), (0, -0.42, 0.79), m=DM)
    b.box((2.32, 0.06, 0.22), (0, 0.42, 0.79), m=DM)
    b.box((0.06, 0.85, 0.22), (-1.13, 0, 0.79), m=DM)
    b.box((0.06, 0.85, 0.22), (1.13, 0, 0.79), m=DM)

    # Sifón y cubeta inferior de drenaje
    b.cyl(0.08, 0.15, (-0.95, 0, 0.65), seg=12, m=PY)
    b.cyl(0.12, 0.25, (-0.95, 0, 0.45), seg=14, m=AG)

    # Brazo articulado superior con lámpara médica multiradial
    b.cyl(0.05, 1.20, (1.05, 0.35, 1.30), seg=10, m=DM)
    b.cyl(0.04, 0.85, (0.65, 0.20, 1.90), rot=(0, -0.75, 0), seg=10, m=PY)
    # Cúpula de lámpara
    b.cyl(0.24, 0.08, (0.20, 0.05, 1.85), rot=(0.3, -0.3, 0), seg=18, m=DM)
    b.cyl(0.20, 0.04, (0.20, 0.05, 1.83), rot=(0.3, -0.3, 0), seg=16, m=AG)

    # Bandeja lateral con instrumental
    b.box((0.35, 0.50, 0.04), (0, -0.55, 0.75), m=DM)
    b.box((0.04, 0.25, 0.02), (-0.08, -0.55, 0.78), m=BV)
    b.box((0.04, 0.20, 0.02), (0.05, -0.55, 0.78), m=BV)

    return b.build(COL_MAESTRA)

# ==============================================================================
# 2. BIOMA 2: SALA LIMPIA / ACELERADOR CUÁNTICO (4 PROPS NUEVOS)
# ==============================================================================

def modelar_clean_toroidal_superconductor(mats):
    """SM_Clean_Toroidal_Superconductor: Superconductor toroidal cuántico con 12 bobinas en cromo y base cerámica."""
    b = dl.MB("SM_Clean_Toroidal_Superconductor")
    WC, CH, CN, GL, DM, CR = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_DarkMetal"], mats["M_Clean_Crystal"]
    )
    # Base circular de cerámica técnica blanca
    b.cyl(1.10, 0.24, (0, 0, 0.12), seg=32, m=WC)
    b.cyl(0.95, 0.08, (0, 0, 0.28), seg=28, m=DM)

    # Toroide principal de contención de plasma
    r_major = 0.75
    r_minor = 0.22
    # Generar aproximación por 24 segmentos de anillo
    n_seg = 24
    for k in range(n_seg):
        ang1 = k * (2.0 * math.pi / n_seg)
        px = r_major * math.cos(ang1)
        py = r_major * math.sin(ang1)
        b.cyl(r_minor, 0.22, (px, py, 0.65), rot=(math.pi/2, 0, -ang1), seg=14, m=CH)

    # Núcleo de plasma cian interno visible
    b.cyl(0.60, 0.12, (0, 0, 0.65), seg=24, m=CN)

    # 12 Bobinas superconductoras radiales con blindaje
    for i in range(12):
        theta = i * (2.0 * math.pi / 12.0)
        bx = r_major * math.cos(theta)
        by = r_major * math.sin(theta)
        b.box((0.14, 0.26, 0.55), (bx, by, 0.65), rot=(0, 0, theta), m=DM)
        # Línea de alimentación criogénica cian
        b.box((0.05, 0.28, 0.10), (bx, by, 0.95), rot=(0, 0, theta), m=CN)

    # Terminal superior de busbar de corriente
    b.cyl(0.35, 0.25, (0, 0, 0.90), seg=20, m=WC)
    b.cyl(0.25, 0.15, (0, 0, 1.05), seg=18, m=CR)

    # Conductores de vacío exteriores
    for qx, qy in [(-0.95, -0.40), (0.95, 0.40)]:
        b.cyl(0.06, 0.60, (qx, qy, 0.45), seg=12, m=CH)
        b.cyl(0.10, 0.06, (qx, qy, 0.72), seg=14, m=DM)

    return b.build(COL_MAESTRA)

def modelar_clean_vacuum_chamber_node(mats):
    """SM_Clean_Vacuum_Chamber_Node: Nodo UHV esférico de ultra-alto vacío con bridas ConFlat y bomba turbo."""
    b = dl.MB("SM_Clean_Vacuum_Chamber_Node")
    WC, CH, CN, GL, DM, CR = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_DarkMetal"], mats["M_Clean_Crystal"]
    )
    # Soporte trípode antivibración
    b.cyl(0.70, 0.15, (0, 0, 0.08), seg=20, m=WC)
    for a_i in range(3):
        ang = a_i * (2.0 * math.pi / 3.0)
        lx = 0.55 * math.cos(ang)
        ly = 0.55 * math.sin(ang)
        b.box((0.12, 0.12, 0.75), (lx, ly, 0.45), rot=(0, 0.12, ang), m=DM)

    # Bomba turbomolecular cilíndrica inferior con aletas disipadoras
    b.cyl(0.32, 0.55, (0, 0, 0.60), seg=24, m=DM)
    for fi in range(6):
        b.cyl(0.36, 0.02, (0, 0, 0.40 + fi*0.07), seg=20, m=CH)

    # Esfera central de vacío multipuerto UHV
    b.sph(0.55, (0, 0, 1.35), u=24, v=12, m=CH)

    # 4 Bridas ortogonales horizontales ConFlat (CF)
    for bx, by, rz in [(0.58, 0, 0), (-0.58, 0, 0), (0, 0.58, math.pi/2), (0, -0.58, math.pi/2)]:
        b.cyl(0.24, 0.15, (bx, by, 1.35), rot=(0, math.pi/2 if bx!=0 else 0, rz), seg=18, m=DM)
        b.cyl(0.28, 0.04, (bx*1.12, by*1.12, 1.35), rot=(0, math.pi/2 if bx!=0 else 0, rz), seg=18, m=CH)

    # Ventana óptica frontal de cuarzo con retícula de interferencia
    b.cyl(0.22, 0.08, (0, -0.62, 1.35), rot=(math.pi/2, 0, 0), seg=18, m=GL)
    b.cyl(0.18, 0.03, (0, -0.64, 1.35), rot=(math.pi/2, 0, 0), seg=16, m=CR)

    # Puerto vertical superior para analizador espectral
    b.cyl(0.20, 0.45, (0, 0, 1.95), seg=18, m=DM)
    b.cyl(0.25, 0.05, (0, 0, 2.18), seg=18, m=CH)
    b.cyl(0.12, 0.04, (0, 0, 2.22), seg=14, m=CN)

    # Pantalla táctil de control de vacío
    b.box((0.35, 0.04, 0.25), (0.45, -0.40, 1.05), rot=(0, 0, -0.45), m=DM)
    b.box((0.30, 0.02, 0.20), (0.46, -0.42, 1.05), rot=(0, 0, -0.45), m=CN)

    return b.build(COL_MAESTRA)

def modelar_clean_air_shower_portal(mats):
    """SM_Clean_Air_Shower_Portal: Portal monolítico de paso estéril con microtoberas ionizantes e iluminación cian."""
    b = dl.MB("SM_Clean_Air_Shower_Portal")
    WC, CH, CN, GL, DM = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_DarkMetal"]
    )
    # Rampa de entrada y suelo de rejilla perforada
    b.box((1.80, 0.60, 0.12), (0, 0, 0.06), m=DM)
    b.box((1.10, 0.55, 0.04), (0, 0, 0.13), m=CH)

    # Columnas laterales monolíticas en cerámica blanca
    b.box((0.32, 0.60, 2.40), (-0.74, 0, 1.32), m=WC)
    b.box((0.32, 0.60, 2.40), (0.74, 0, 1.32), m=WC)

    # Dintel superior de flujo laminar
    b.box((1.80, 0.60, 0.32), (0, 0, 2.58), m=WC)
    b.box((1.10, 0.48, 0.06), (0, 0, 2.40), m=DM)

    # Bandas perimetrales de neón cian
    b.box((0.03, 0.58, 2.20), (-0.57, 0, 1.25), m=CN)
    b.box((0.03, 0.58, 2.20), (0.57, 0, 1.25), m=CN)
    b.box((1.10, 0.58, 0.03), (0, 0, 2.38), m=CN)

    # 16 Toberas cilíndricas de eyección de aire ionizado
    for col_x in [-0.58, 0.58]:
        for z_i in range(8):
            tz = 0.50 + z_i * 0.24
            for fy in [-0.15, 0.15]:
                b.cyl(0.025, 0.04, (col_x + (-0.02 if col_x>0 else 0.02), fy, tz), rot=(0, math.pi/2, 0), seg=8, m=CH)

    # Escáner biométrico y panel táctil lateral
    b.box((0.04, 0.20, 0.35), (0.91, 0, 1.30), m=DM)
    b.box((0.02, 0.16, 0.25), (0.93, 0, 1.30), m=CN)

    return b.build(COL_MAESTRA)

def modelar_clean_collimator_station(mats):
    """SM_Clean_Collimator_Station: Banco óptico de colimación con riel micrométrico, iris y sensor cuántico."""
    b = dl.MB("SM_Clean_Collimator_Station")
    WC, CH, CN, GL, DM, CR = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_DarkMetal"], mats["M_Clean_Crystal"]
    )
    # Banco de granito cerámico con patas de desacoplo
    b.box((2.00, 0.80, 0.18), (0, 0, 0.70), m=WC)
    for px in [-0.85, 0.85]:
        for py in [-0.30, 0.30]:
            b.cyl(0.08, 0.60, (px, py, 0.31), seg=16, m=DM)
            b.cyl(0.12, 0.08, (px, py, 0.05), seg=16, m=CH)

    # Riel lineal de deslizamiento óptico de precisión
    b.box((1.85, 0.18, 0.06), (0, 0, 0.82), m=CH)
    b.box((1.85, 0.04, 0.03), (0, 0, 0.86), m=DM)

    # Carretilla 1: Fuente emisora colimada
    b.box((0.26, 0.30, 0.12), (-0.65, 0, 0.88), m=DM)
    b.cyl(0.10, 0.30, (-0.65, 0, 1.05), rot=(0, math.pi/2, 0), seg=18, m=CH)
    b.cyl(0.05, 0.04, (-0.48, 0, 1.05), rot=(0, math.pi/2, 0), seg=14, m=CN)

    # Carretilla 2: Diafragma Iris micrométrico central
    b.box((0.24, 0.28, 0.12), (0.0, 0, 0.88), m=DM)
    b.cyl(0.22, 0.06, (0.0, 0, 1.05), rot=(0, math.pi/2, 0), seg=24, m=CH)
    b.cyl(0.09, 0.08, (0.0, 0, 1.05), rot=(0, math.pi/2, 0), seg=18, m=DM)
    # Tornillo micrométrico moleteado
    b.cyl(0.03, 0.14, (0.0, 0.22, 1.15), rot=(math.pi/2, 0, 0), seg=12, m=CH)

    # Carretilla 3: Sensor y espectrómetro cuántico
    b.box((0.30, 0.32, 0.14), (0.65, 0, 0.88), m=DM)
    b.box((0.26, 0.26, 0.35), (0.65, 0, 1.12), m=WC)
    b.cyl(0.08, 0.12, (0.50, 0, 1.05), rot=(0, math.pi/2, 0), seg=16, m=CR)
    # Pantalla de lectura digital
    b.box((0.02, 0.18, 0.15), (0.79, 0, 1.15), m=CN)

    return b.build(COL_MAESTRA)

# ==============================================================================
# 3. BIOMA 3: ROBÓTICA / MECATRÓNICA (4 PROPS NUEVOS)
# ==============================================================================

def modelar_robo_gantry_welding_arm(mats):
    """SM_Robo_Gantry_Welding_Arm: Brazo robótico suspendido en pórtico de 4 DOF con tobera de arco y antorcha."""
    b = dl.MB("SM_Robo_Gantry_Welding_Arm")
    CS, CB, AC, HZ, SA, PO = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_HazardStripe"], mats["M_Robo_ScreenAmber"], mats["M_Robo_Porcelain"]
    )
    # Marco pórtico masivo
    b.box((1.60, 0.20, 0.24), (0, -0.35, 2.70), m=CS)
    b.box((1.60, 0.20, 0.24), (0, 0.35, 2.70), m=CS)
    b.box((0.24, 0.90, 0.24), (-0.75, 0, 2.70), m=CS)
    b.box((0.24, 0.90, 0.24), (0.75, 0, 2.70), m=CS)
    # Columnas verticales de apoyo
    b.box((0.18, 0.18, 2.65), (-0.75, -0.35, 1.35), m=CS)
    b.box((0.18, 0.18, 2.65), (-0.75, 0.35, 1.35), m=CS)
    b.box((0.18, 0.18, 2.65), (0.75, -0.35, 1.35), m=CS)
    b.box((0.18, 0.18, 2.65), (0.75, 0.35, 1.35), m=CS)

    # Carro de deslizamiento en el riel superior
    b.box((0.45, 0.60, 0.20), (0, 0, 2.52), m=CS)
    b.cyl(0.18, 0.12, (0, 0, 2.38), seg=18, m=CB)

    # Articulación 1 y brazo superior
    b.cyl(0.12, 0.28, (0, 0, 2.18), rot=(math.pi/2, 0, 0), seg=16, m=CS)
    b.box((0.16, 0.18, 0.70), (0.12, 0, 1.80), rot=(0, -0.35, 0), m=CS)

    # Articulación 2 (Codo robótico)
    b.cyl(0.10, 0.24, (0.28, 0, 1.45), rot=(math.pi/2, 0, 0), seg=16, m=CB)
    b.box((0.14, 0.14, 0.65), (0.10, 0, 1.15), rot=(0, 0.40, 0), m=CS)

    # Cabezal de soldadura y antorcha de arco
    b.cyl(0.08, 0.18, (-0.05, 0, 0.82), rot=(0, 0.20, 0), seg=14, m=CB)
    b.cyl(0.04, 0.16, (-0.08, 0, 0.66), rot=(0, 0.20, 0), seg=12, m=CS)
    # Chispero y electrodo
    b.cyl(0.015, 0.08, (-0.10, 0, 0.54), rot=(0, 0.20, 0), seg=8, m=AC)

    # Umbilical corrugado de potencia
    for seg_i in range(8):
        uz = 2.40 - seg_i * 0.18
        ux = -0.15 + 0.08 * math.sin(seg_i * 0.8)
        b.sph(0.05, (ux, 0.18, uz), u=10, v=6, m=CB)

    return b.build(COL_MAESTRA)

def modelar_robo_induction_furnace(mats):
    """SM_Robo_Induction_Furnace: Horno electromagnético de fundición con crisol, bobinas de cobre y núcleo ardiente."""
    b = dl.MB("SM_Robo_Induction_Furnace")
    CS, CB, AC, HZ, SA, PO = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_HazardStripe"], mats["M_Robo_ScreenAmber"], mats["M_Robo_Porcelain"]
    )
    # Bancada robusta de fundición acorazada
    b.box((1.90, 1.30, 0.35), (0, 0, 0.18), m=CS)
    b.box((1.92, 0.06, 0.12), (0, -0.62, 0.18), m=HZ)
    b.box((1.92, 0.06, 0.12), (0, 0.62, 0.18), m=HZ)

    # Soportes laterales de basculamiento (munones)
    b.box((0.25, 0.35, 1.05), (-0.75, 0, 0.85), m=CS)
    b.box((0.25, 0.35, 1.05), (0.75, 0, 0.85), m=CS)
    b.cyl(0.14, 0.40, (-0.75, 0, 1.15), rot=(0, math.pi/2, 0), seg=18, m=CB)
    b.cyl(0.14, 0.40, (0.75, 0, 1.15), rot=(0, math.pi/2, 0), seg=18, m=CB)

    # Crisol cilíndrico central
    b.cyl(0.55, 1.10, (0, 0, 1.05), seg=24, m=CS)
    # Núcleo interior refractario con metal ardiente
    b.cyl(0.42, 0.20, (0, 0, 1.45), seg=20, m=AC)
    b.cyl(0.48, 0.08, (0, 0, 1.62), seg=24, m=CS)

    # 5 Espiras de bobinado macizo de cobre refrigerado
    for coil_i in range(5):
        cz = 0.70 + coil_i * 0.18
        b.cyl(0.62, 0.08, (0, 0, cz), seg=24, m=CB)

    # Cilindro hidráulico basculante
    b.cyl(0.08, 0.75, (-0.55, -0.42, 0.75), rot=(0.4, 0, 0), seg=14, m=CS)
    b.cyl(0.05, 0.65, (-0.55, -0.42, 0.78), rot=(0.4, 0, 0), seg=10, m=CB)

    # Consola de potencia MW
    b.box((0.35, 0.50, 0.90), (0.95, -0.25, 0.75), m=CS)
    b.box((0.02, 0.38, 0.35), (1.13, -0.25, 0.95), m=SA)

    return b.build(COL_MAESTRA)

def modelar_robo_pneumatic_manifold(mats):
    """SM_Robo_Pneumatic_Manifold: Manifold mural vertical con batería de 8 electroválvulas y manómetros."""
    b = dl.MB("SM_Robo_Pneumatic_Manifold")
    CS, CB, AC, HZ, SA, PO = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_HazardStripe"], mats["M_Robo_ScreenAmber"], mats["M_Robo_Porcelain"]
    )
    # Panel posterior de fijación a muro
    b.box((1.80, 0.14, 2.10), (0, 0, 1.05), m=CS)
    b.box((1.70, 0.04, 0.10), (0, -0.09, 2.00), m=HZ)

    # Colector cilíndrico maestro horizontal superior e inferior
    b.cyl(0.08, 1.60, (0, -0.15, 1.80), rot=(0, math.pi/2, 0), seg=18, m=CS)
    b.cyl(0.08, 1.60, (0, -0.15, 0.35), rot=(0, math.pi/2, 0), seg=18, m=CS)

    # 8 Válvulas solenoides en línea
    for v_i in range(8):
        vx = -0.70 + v_i * 0.20
        # Bloque de válvula
        b.box((0.14, 0.18, 0.40), (vx, -0.18, 1.10), m=CB)
        # Solenoide electromagnético superior
        b.cyl(0.045, 0.18, (vx, -0.18, 1.38), seg=12, m=CS)
        # Indicador LED ámbar
        b.sph(0.025, (vx, -0.28, 1.38), u=8, v=6, m=AC)
        # Conexión vertical de tubería de presión
        b.cyl(0.025, 0.35, (vx, -0.18, 1.60), seg=8, m=PO)
        b.cyl(0.025, 0.40, (vx, -0.18, 0.65), seg=8, m=PO)
        # Manómetro individual
        b.cyl(0.045, 0.04, (vx, -0.26, 0.92), rot=(math.pi/2, 0, 0), seg=12, m=SA)

    # Tanque secador desecante lateral
    b.cyl(0.14, 1.20, (0.75, -0.22, 1.05), seg=18, m=CS)
    b.cyl(0.16, 0.08, (0.75, -0.22, 1.68), seg=18, m=CB)
    b.cyl(0.16, 0.08, (0.75, -0.22, 0.42), seg=18, m=CB)

    return b.build(COL_MAESTRA)

def modelar_robo_exoskeleton_dock(mats):
    """SM_Robo_Exoskeleton_Dock: Estación vertical de acople mecatrónico y recarga de exoesqueletos."""
    b = dl.MB("SM_Robo_Exoskeleton_Dock")
    CS, CB, AC, HZ, SA, PO = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_HazardStripe"], mats["M_Robo_ScreenAmber"], mats["M_Robo_Porcelain"]
    )
    # Plataforma de pisada con huellas
    b.box((1.70, 1.40, 0.16), (0, 0, 0.08), m=CS)
    b.box((1.60, 0.08, 0.08), (0, -0.62, 0.12), m=HZ)
    # Placas de alineación de pies
    b.box((0.28, 0.50, 0.04), (-0.35, 0, 0.18), m=CB)
    b.box((0.28, 0.50, 0.04), (0.35, 0, 0.18), m=CB)

    # Columna vertebral de recarga posterior
    b.box((0.55, 0.45, 2.30), (0, 0.45, 1.25), m=CS)
    b.box((0.40, 0.15, 2.10), (0, 0.22, 1.30), m=CB)

    # Abrazaderas neumáticas para piernas (inferiores)
    for z_arm, r_arm in [(0.60, 0.38), (1.30, 0.44)]:
        # Soportes telescópicos
        b.box((0.20, 0.35, 0.10), (-0.42, 0.15, z_arm), m=CS)
        b.box((0.20, 0.35, 0.10), (0.42, 0.15, z_arm), m=CS)
        # Garras semicirculares
        b.cyl(0.12, 0.08, (-0.42, -0.05, z_arm), rot=(math.pi/2, 0, 0), seg=12, m=CB)
        b.cyl(0.12, 0.08, (0.42, -0.05, z_arm), rot=(math.pi/2, 0, 0), seg=12, m=CB)

    # Arreglo de acople dorsal con conectores de inducción ámbar
    for d_i in range(4):
        dz = 1.0 + d_i * 0.25
        b.cyl(0.06, 0.12, (0, 0.15, dz), rot=(math.pi/2, 0, 0), seg=12, m=AC)

    # Brazo articulado superior para yelmo/arnés
    b.box((0.16, 0.65, 0.14), (0, 0.10, 2.25), m=CS)
    b.cyl(0.14, 0.12, (0, -0.22, 2.18), seg=16, m=CB)
    b.sph(0.08, (0, -0.22, 2.12), u=12, v=8, m=AC)

    # Pantalla lateral interactiva de estado
    b.box((0.08, 0.35, 0.60), (0.65, 0.40, 1.55), rot=(0, 0, -0.25), m=CS)
    b.box((0.02, 0.30, 0.50), (0.69, 0.40, 1.55), rot=(0, 0, -0.25), m=SA)

    return b.build(COL_MAESTRA)

# ==============================================================================
# RENDERIZADO MULTIVISTA Y SHOWCASE FASE 3
# ==============================================================================

def renderizar_showcases(modelos_por_bioma):
    """Genera renders individuales por bioma y showcase consolidado en artifacts."""
    sc = bpy.context.scene
    motores = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    if 'CYCLES' in motores:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 64
        sc.cycles.use_denoising = True
    elif 'BLENDER_EEVEE_NEXT' in motores:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    else:
        sc.render.engine = 'BLENDER_EEVEE'
        
    sc.render.resolution_x = 1280
    sc.render.resolution_y = 720
    sc.render.film_transparent = False
    
    w = bpy.data.worlds.get("DarxBiomaWorldPhase3") or bpy.data.worlds.new("DarxBiomaWorldPhase3")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.world = w
    
    archivos_generados = []
    
    # Renderizar cada bioma por separado en cuadrícula 2x2
    posiciones_2x2 = [
        (-1.6, 1.5, 0.0),
        (1.6, 1.5, 0.0),
        (-1.6, -1.5, 0.0),
        (1.6, -1.5, 0.0)
    ]
    for i, (nombre_bioma, objs) in enumerate(modelos_por_bioma.items(), 1):
        for idx, obj in enumerate(objs):
            obj.location = posiciones_2x2[idx]
            
        bpy.context.view_layer.update()
        out_png = os.path.join(ARTIFACTS_DIR, f"preview_fase3_bioma{i}_{nombre_bioma}.png")
        dl.snap(objs, out_png, focus=(0, 0, 0.9), dist=10.0, yaw=38.0, pitch=26.0, res=1024)
        archivos_generados.append(out_png)
        print(f"DarX | Render Fase 3 generado: {out_png}")

    # Render showcase conjunto (3 filas de biomas x 4 columnas de props)
    todos_los_objs = []
    for bioma_idx, (nombre_bioma, objs) in enumerate(modelos_por_bioma.items()):
        offset_y = (bioma_idx - 1.0) * 2.4
        for idx, obj in enumerate(objs):
            offset_x = (idx - 1.5) * 2.0
            obj.location = (offset_x, offset_y, 0.0)
            todos_los_objs.append(obj)

    bpy.context.view_layer.update()
    out_megafase = os.path.join(ARTIFACTS_DIR, "preview_fase3_todos_los_biomas_showcase.png")
    dl.snap(todos_los_objs, out_megafase, focus=(0, 0, 0.9), dist=16.5, yaw=35.0, pitch=28.0, res=1280)
    archivos_generados.append(out_megafase)
    print(f"DarX | Render Showcase Total Fase 3 generado: {out_megafase}")
    return archivos_generados

def main():
    print("=" * 80)
    print("DarX | Iniciando Pipeline Fase 3: 12 Nuevos Objetos de Laboratorio...")
    print("=" * 80)
    
    dl.wipe(COL_MAESTRA)
    dl.coll(COL_MAESTRA)
    mats = crear_materiales()

    bio1_objs = [
        modelar_bio_centrifuge_extractor(mats),
        modelar_bio_decontamination_shower(mats),
        modelar_bio_spore_cryo_storage(mats),
        modelar_bio_specimen_dissection_slab(mats)
    ]

    bio2_objs = [
        modelar_clean_toroidal_superconductor(mats),
        modelar_clean_vacuum_chamber_node(mats),
        modelar_clean_air_shower_portal(mats),
        modelar_clean_collimator_station(mats)
    ]

    bio3_objs = [
        modelar_robo_gantry_welding_arm(mats),
        modelar_robo_induction_furnace(mats),
        modelar_robo_pneumatic_manifold(mats),
        modelar_robo_exoskeleton_dock(mats)
    ]

    modelos_por_bioma = {
        "biohazard": bio1_objs,
        "cleanroom": bio2_objs,
        "robotics": bio3_objs
    }

    print("DarX | Generando renders de previsualización en Blender 5.2...")
    renders = renderizar_showcases(modelos_por_bioma)

    print("DarX | Exportando 12 StaticMeshes canónicas a Art/FBX/Biomas/...")
    out_dir = r"E:/Darx_Proyect/Art/FBX/Biomas"
    os.makedirs(out_dir, exist_ok=True)
    todos = bio1_objs + bio2_objs + bio3_objs
    for obj in todos:
        obj.location = (0, 0, 0)
        bpy.context.view_layer.update()
        dl.export_fbx([obj], obj.name, armature=False, anim=False, subdir=FBX_SUBDIR)
        print(f"  -> Exportado FBX: {obj.name}.fbx")

    print("=" * 80)
    print(f"DarX | Fase 3 completada: 12 FBX exportados y {len(renders)} renders generados.")
    print("=" * 80)

if __name__ == "__main__":
    main()
