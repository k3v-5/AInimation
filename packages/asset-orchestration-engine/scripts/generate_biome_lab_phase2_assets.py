"""generate_biome_lab_phase2_assets.py — Fase 2: 12 Nuevos Objetos de Laboratorio por Bioma.

Modelado 3D de alta densidad, micro-detalles AAA, renders Cycles/EEVEE y exportación canónica FBX:
- Bioma 1 (Biohazard):
  1. SM_Bio_Incubator_Vats (Batería de 3 incubadoras embrionarias con líquido verde y soporte vital)
  2. SM_Bio_Autoclave_Sterilizer (Esterilizador autoclave masivo con compuerta circular estanca y manómetros)
  3. SM_Bio_Overhead_Gantry (Estructura de grúa aérea y riel de techo con garra y cilindro de riesgo)
  4. SM_Bio_Hazard_Waste_Bin (Contenedor hermético de residuos cáusticos con pedal y filtro HEPA)
- Bioma 2 (Clean Room / Acelerador Cuántico):
  5. SM_Clean_Laser_Interferometer (Banco óptico de interferometría láser con divisores y prismas reflectores)
  6. SM_Clean_Cryo_Cooling_Tower (Torre criogénica de helio líquido con anillos de escarcha y chaqueta cromada)
  7. SM_Clean_Optical_Diagnostic_Pod (Cápsula vertical de diagnóstico con anillo fotónico levitante y retícula)
  8. SM_Clean_Ceiling_HEPA_Grid (Panel de techo con filtro laminar HEPA y luz perimetral cian/blanca)
- Bioma 3 (Robótica / Ensamblaje Mecatrónico):
  9. SM_Robo_Conveyor_Feeder (Cinta transportadora de rodillos con chasis, motor y sensor infrarrojo)
  10. SM_Robo_Heavy_Transformer (Transformador de alta tensión con radiadores de aceite y aisladores de porcelana)
  11. SM_Robo_Tool_Rack_Armory (Panel mural organizador con herramientas pesadas de plasma y arco)
  12. SM_Robo_Charging_Station (Estación de recarga por inducción magnética con tótem y display ámbar)

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

COL_MAESTRA = "DARX_MegaFase_Biomas_Phase2"
ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FBX_SUBDIR = "Biomas"

# ==============================================================================
# DEFINICIÓN DE MATERIALES PBR CALIBRADOS
# ==============================================================================
def crear_materiales():
    m = {}
    # --- BIOMA 1: BIOHAZARD (IMAGEN 1) ---
    m["M_Bio_DarkMetal"] = dl.mat("M_Bio_DarkMetal", (0.035, 0.045, 0.040), rough=0.48, metal=0.90)
    m["M_Bio_PipeYellow"] = dl.mat("M_Bio_PipeYellow", (0.88, 0.65, 0.06), rough=0.35, metal=0.35)
    m["M_Bio_AcidGreen"] = dl.mat("M_Bio_AcidGreen", (0.05, 0.96, 0.12), rough=0.12, emis=(0.05, 0.98, 0.12), emis_str=4.8)
    m["M_Bio_Glass"] = dl.mat("M_Bio_Glass", (0.05, 0.22, 0.09), rough=0.03, metal=0.12, emis=(0.02, 0.38, 0.08), emis_str=1.4)
    m["M_Bio_ChitinFlesh"] = dl.mat("M_Bio_ChitinFlesh", (0.10, 0.032, 0.032), rough=0.78, metal=0.05)
    m["M_Bio_HazardSign"] = dl.mat("M_Bio_HazardSign", (0.94, 0.60, 0.02), rough=0.28, metal=0.10)
    m["M_Bio_ScreenGreen"] = dl.mat("M_Bio_ScreenGreen", (0.02, 0.88, 0.14), rough=0.08, emis=(0.02, 0.92, 0.14), emis_str=4.2)
    m["M_Bio_BrassValve"] = dl.mat("M_Bio_BrassValve", (0.82, 0.62, 0.18), rough=0.25, metal=0.95)

    # --- BIOMA 2: SALA LIMPIA / CUÁNTICO (IMAGEN 2) ---
    m["M_Clean_WhiteCeramic"] = dl.mat("M_Clean_WhiteCeramic", (0.93, 0.94, 0.96), rough=0.14, metal=0.04)
    m["M_Clean_Chrome"] = dl.mat("M_Clean_Chrome", (0.96, 0.96, 0.98), rough=0.02, metal=0.99)
    m["M_Clean_CyanNeon"] = dl.mat("M_Clean_CyanNeon", (0.0, 0.88, 1.0), rough=0.06, emis=(0.0, 0.88, 1.0), emis_str=5.0)
    m["M_Clean_Glass"] = dl.mat("M_Clean_Glass", (0.84, 0.94, 0.99), rough=0.015, metal=0.06)
    m["M_Clean_DarkMetal"] = dl.mat("M_Clean_DarkMetal", (0.025, 0.025, 0.035), rough=0.32, metal=0.94)
    m["M_Clean_Crystal"] = dl.mat("M_Clean_Crystal", (0.18, 0.72, 0.95), rough=0.05, metal=0.10, emis=(0.12, 0.58, 0.88), emis_str=3.0)

    # --- BIOMA 3: ROBÓTICA (IMAGEN 3) ---
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

def modelar_bio_incubator_vats(mats):
    """SM_Bio_Incubator_Vats: Batería de 3 cilindros de incubación embrionaria con cúpulas y soporte vital."""
    b = dl.MB("SM_Bio_Incubator_Vats")
    DM, PY, AG, GL, CF, BV, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"],
        mats["M_Bio_Glass"], mats["M_Bio_ChitinFlesh"], mats["M_Bio_BrassValve"],
        mats["M_Bio_ScreenGreen"]
    )
    # Base pesada con zócalo
    b.box((2.20, 0.90, 0.26), (0, 0, 0.13), m=DM)
    for dx in [-0.95, 0.95]:
        for dy in [-0.35, 0.35]:
            b.cyl(0.06, 0.12, (dx, dy, 0.06), seg=10, m=PY)

    # 3 Tanques cilíndricos
    for i, cx in enumerate([-0.65, 0.0, 0.65]):
        # Anillo inferior
        b.cyl(0.26, 0.08, (cx, 0, 0.30), seg=16, m=DM)
        # Cilindro de cristal
        b.cyl(0.22, 0.90, (cx, 0, 0.79), seg=16, m=GL)
        # Fluido interno verde
        b.cyl(0.19, 0.82, (cx, 0, 0.75), seg=14, m=AG)
        # Embrión en suspensión
        b.sph(0.07, (cx, 0, 0.88), scale=(1, 1, 1.2), m=CF)
        for k in range(5):
            b.sph(0.045 - k*0.005, (cx + 0.02*math.sin(k), 0.02*math.cos(k), 0.80 - k*0.07), m=CF)
        # Anillo superior y cúpula
        b.cyl(0.25, 0.08, (cx, 0, 1.28), seg=16, m=DM)
        b.sph(0.22, (cx, 0, 1.32), scale=(1.0, 1.0, 0.6), m=PY)

    # Colector superior de tuberías
    b.cyl(0.04, 1.60, (0, 0, 1.55), rot=(0, math.pi/2, 0), seg=12, m=PY)
    for cx in [-0.65, 0.0, 0.65]:
        b.cyl(0.035, 0.18, (cx, 0, 1.45), seg=10, m=BV)

    # Manómetro central
    b.cyl(0.08, 0.04, (0, -0.06, 1.55), rot=(math.pi/2, 0, 0), seg=14, m=SG)

    # Consola lateral de monitoreo
    b.box((0.22, 0.35, 0.45), (1.05, 0, 0.50), m=DM)
    b.box((0.02, 0.24, 0.28), (1.17, 0, 0.55), m=SG)
    return b.build(COL_MAESTRA)

def modelar_bio_autoclave_sterilizer(mats):
    """SM_Bio_Autoclave_Sterilizer: Esterilizador autoclave masivo horizontal con compuerta circular."""
    b = dl.MB("SM_Bio_Autoclave_Sterilizer")
    DM, PY, BV, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_BrassValve"],
        mats["M_Bio_ScreenGreen"]
    )
    # Pedestales de soporte dobles
    for dx in [-0.50, 0.50]:
        b.box((0.16, 0.60, 0.30), (dx, 0, 0.15), m=DM)
        for dy in [-0.35, 0.35]:
            b.cyl(0.035, 0.08, (dx, dy, 0.32), seg=8, m=PY)

    # Cámara cilíndrica horizontal (longitud 1.2m, radio 0.42m)
    b.cyl(0.42, 1.20, (0, 0, 0.72), rot=(0, math.pi/2, 0), seg=18, m=DM)
    b.sph(0.42, (0.60, 0, 0.72), scale=(0.35, 1.0, 1.0), m=DM)

    # Brida frontal
    b.cyl(0.46, 0.08, (-0.60, 0, 0.72), rot=(0, math.pi/2, 0), seg=18, m=PY)

    # Compuerta masiva circular
    b.cyl(0.44, 0.09, (-0.68, 0, 0.72), rot=(0, math.pi/2, 0), seg=18, m=DM)
    # Bisagra pesada lateral
    b.cyl(0.07, 0.38, (-0.65, -0.44, 0.72), seg=12, m=PY)

    # Volante de cierre estanco central (6 radios)
    b.cyl(0.08, 0.08, (-0.76, 0, 0.72), rot=(0, math.pi/2, 0), seg=12, m=PY)
    for a in range(6):
        ang = math.radians(a * 60)
        b.cyl(0.02, 0.22, (-0.78, 0.11*math.sin(ang), 0.72 + 0.11*math.cos(ang)), rot=(ang, 0, 0), seg=8, m=PY)
    # Aro del volante con toroide aproximado
    for a in range(16):
        ang = math.radians(a * 22.5)
        b.sph(0.025, (-0.78, 0.24*math.cos(ang), 0.72 + 0.24*math.sin(ang)), m=PY)

    # Tubería superior de vapor con válvula de alivio
    b.cyl(0.045, 0.30, (0.10, 0, 1.26), seg=10, m=PY)
    b.cyl(0.075, 0.14, (0.10, 0, 1.44), seg=12, m=BV)
    b.cyl(0.035, 0.20, (0.10, 0.08, 1.54), seg=8, m=DM)

    # Manómetro analógico lateral
    b.cyl(0.09, 0.04, (-0.30, -0.44, 0.95), rot=(math.pi/2, 0, 0), seg=14, m=SG)
    return b.build(COL_MAESTRA)

def modelar_bio_overhead_gantry(mats):
    """SM_Bio_Overhead_Gantry: Estructura de grúa aérea de techo con carro motorizado y contenedor de riesgo."""
    b = dl.MB("SM_Bio_Overhead_Gantry")
    DM, PY, AG = mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"]

    # Dos rieles de techo en I (longitud 2.8m)
    for dy in [-0.45, 0.45]:
        b.box((2.80, 0.08, 0.10), (0, dy, 1.35), m=DM)
        b.box((2.80, 0.14, 0.025), (0, dy, 1.40), m=PY)
        b.box((2.80, 0.14, 0.025), (0, dy, 1.30), m=PY)
        for dx in [-1.10, 0.0, 1.10]:
            b.box((0.08, 0.08, 0.10), (dx, dy, 1.45), m=DM)

    # Carro puente motorizado transversal
    b.box((0.36, 0.70, 0.12), (0.20, 0, 1.24), m=DM)
    b.cyl(0.09, 0.24, (0.20, 0.38, 1.24), rot=(math.pi/2, 0, 0), seg=12, m=PY)

    # Polipasto / Tambor de cable
    b.cyl(0.11, 0.24, (0.20, 0, 1.14), rot=(0, math.pi/2, 0), seg=12, m=DM)
    b.cyl(0.022, 0.48, (0.20, 0, 0.86), seg=8, m=DM)

    # Garra de 4 dedos hidráulicos
    b.box((0.20, 0.20, 0.09), (0.20, 0, 0.60), m=PY)
    for a in range(4):
        ang = math.radians(a * 90)
        gx = 0.20 + 0.13 * math.cos(ang)
        gy = 0.13 * math.sin(ang)
        b.box((0.04, 0.04, 0.16), (gx, gy, 0.48), rot=(0.15*math.sin(ang), 0.15*math.cos(ang), ang), m=DM)

    # Contenedor presurizado cilíndrico de biohazard
    b.cyl(0.16, 0.46, (0.20, 0, 0.32), seg=14, m=PY)
    b.cyl(0.19, 0.05, (0.20, 0, 0.46), seg=14, m=DM)
    b.cyl(0.19, 0.05, (0.20, 0, 0.18), seg=14, m=DM)
    b.cyl(0.065, 0.12, (0.20, -0.13, 0.32), rot=(math.pi/2, 0, 0), seg=10, m=AG)
    return b.build(COL_MAESTRA)

def modelar_bio_hazard_waste_bin(mats):
    """SM_Bio_Hazard_Waste_Bin: Contenedor hermético para desecho de material biocontaminado con pedal."""
    b = dl.MB("SM_Bio_Hazard_Waste_Bin")
    DM, PY, AG, HS = mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"], mats["M_Bio_HazardSign"]

    # Cuerpo principal prismático octogonal
    b.cyl(0.34, 0.70, (0, 0, 0.40), seg=8, m=DM)
    b.cyl(0.35, 0.16, (0, 0, 0.48), seg=8, m=HS)

    # Tapa superior hermética con bisel
    b.cyl(0.37, 0.07, (0, 0, 0.78), seg=8, m=PY)
    b.box((0.14, 0.04, 0.03), (0, -0.26, 0.81), m=DM)

    # Bisagra trasera
    b.cyl(0.038, 0.20, (0, 0.35, 0.77), rot=(0, math.pi/2, 0), seg=10, m=DM)

    # Mecanismo de pedal inferior
    b.box((0.14, 0.16, 0.03), (0, -0.38, 0.04), m=PY)
    b.cyl(0.022, 0.20, (0, -0.30, 0.04), rot=(0, math.pi/2, 0), seg=8, m=DM)
    b.cyl(0.014, 0.74, (0.28, 0.20, 0.40), seg=6, m=DM)

    # Cartucho de filtro HEPA lateral
    b.cyl(0.09, 0.22, (0.34, 0, 0.46), rot=(0, math.pi/2, 0), seg=12, m=PY)
    b.cyl(0.10, 0.04, (0.45, 0, 0.46), rot=(0, math.pi/2, 0), seg=12, m=DM)

    # Baliza química superior
    b.sph(0.04, (0, 0, 0.84), scale=(1, 1, 0.7), m=AG)
    return b.build(COL_MAESTRA)

# ==============================================================================
# 2. BIOMA 2: SALA LIMPIA / CUÁNTICO (4 PROPS NUEVOS)
# ==============================================================================

def modelar_clean_laser_interferometer(mats):
    """SM_Clean_Laser_Interferometer: Banco óptico de precisión con láser colimado, prismas y detectores."""
    b = dl.MB("SM_Clean_Laser_Interferometer")
    WC, CH, CN, DM, CR = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_DarkMetal"], mats["M_Clean_Crystal"]
    )
    # Base masiva de granito sintético blanco
    b.box((2.40, 0.80, 0.12), (0, 0, 0.76), m=WC)
    # Patas neumáticas antivibración cromadas
    for dx in [-1.05, 1.05]:
        for dy in [-0.30, 0.30]:
            b.cyl(0.065, 0.70, (dx, dy, 0.35), seg=12, m=CH)
            b.cyl(0.08, 0.05, (dx, dy, 0.65), seg=12, m=DM)

    # Emisor láser colimado cilíndrico en el extremo izquierdo
    b.cyl(0.065, 0.42, (-0.90, 0, 0.90), rot=(0, math.pi/2, 0), seg=14, m=CH)
    b.cyl(0.08, 0.04, (-0.70, 0, 0.90), rot=(0, math.pi/2, 0), seg=14, m=CN)

    # Haces láser cian brillantes
    b.cyl(0.01, 0.60, (-0.40, 0, 0.90), rot=(0, math.pi/2, 0), seg=8, m=CN)

    # Divisor de haz cúbico central (Beam Splitter Cube)
    b.cyl(0.045, 0.08, (-0.10, 0, 0.84), seg=10, m=CH)
    b.box((0.08, 0.08, 0.08), (-0.10, 0, 0.90), m=CR)

    # Haz reflejado a 90° hacia adelante
    b.cyl(0.01, 0.30, (-0.10, -0.15, 0.90), rot=(math.pi/2, 0, 0), seg=8, m=CN)

    # Prisma reflector 1 (a 90°)
    b.cyl(0.045, 0.08, (-0.10, -0.30, 0.84), seg=10, m=CH)
    b.box((0.06, 0.03, 0.06), (-0.10, -0.30, 0.90), rot=(0, 0, math.radians(45)), m=CH)

    # Haz transmitido hacia detector 2
    b.cyl(0.01, 0.85, (0.35, 0, 0.90), rot=(0, math.pi/2, 0), seg=8, m=CN)

    # Prisma reflector 2 final
    b.cyl(0.045, 0.08, (0.75, 0, 0.84), seg=10, m=CH)
    b.box((0.03, 0.06, 0.06), (0.75, 0, 0.90), m=CH)

    # Fotodetector con pantalla digital
    b.box((0.18, 0.16, 0.14), (0.95, 0, 0.90), m=DM)
    b.box((0.01, 0.11, 0.09), (1.05, 0, 0.90), m=CN)
    return b.build(COL_MAESTRA)

def modelar_clean_cryo_cooling_tower(mats):
    """SM_Clean_Cryo_Cooling_Tower: Torre criogénica cilíndrica de helio líquido con anillos de escarcha."""
    b = dl.MB("SM_Clean_Cryo_Cooling_Tower")
    WC, CH, CN, DM = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_DarkMetal"]
    )
    # Base circular escalonada
    b.cyl(0.70, 0.14, (0, 0, 0.07), seg=20, m=WC)
    b.cyl(0.62, 0.12, (0, 0, 0.20), seg=18, m=DM)

    # Columna criogénica cromada principal
    b.cyl(0.52, 2.20, (0, 0, 1.34), seg=20, m=CH)

    # 4 Anillos perimetrales criogénicos con ranura emisiva cian
    for hz in [0.65, 1.15, 1.65, 2.15]:
        b.cyl(0.56, 0.06, (0, 0, hz), seg=20, m=WC)
        b.cyl(0.575, 0.025, (0, 0, hz), seg=20, m=CN)

    # Domo superior hemisférico
    b.sph(0.52, (0, 0, 2.44), scale=(1.0, 1.0, 0.75), m=CH)

    # Válvula de alivio de helio y chimenea
    b.cyl(0.09, 0.24, (0, 0, 2.82), seg=12, m=DM)
    b.cyl(0.12, 0.04, (0, 0, 2.94), seg=12, m=CN)

    # Bridas de acople rápido en la base
    for a in range(3):
        ang = math.radians(a * 120 + 30)
        bx = 0.58 * math.cos(ang)
        by = 0.58 * math.sin(ang)
        b.cyl(0.08, 0.20, (bx, by, 0.38), rot=(0, math.pi/2, ang), seg=12, m=DM)
        b.cyl(0.10, 0.03, (bx*1.12, by*1.12, 0.38), rot=(0, math.pi/2, ang), seg=12, m=CH)
    return b.build(COL_MAESTRA)

def modelar_clean_optical_diagnostic_pod(mats):
    """SM_Clean_Optical_Diagnostic_Pod: Cápsula vertical con anillo fotónico levitante y retícula cian."""
    b = dl.MB("SM_Clean_Optical_Diagnostic_Pod")
    WC, CH, CN, GL = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"]
    )
    # Pedestal circular cerámico
    b.cyl(0.55, 0.16, (0, 0, 0.08), seg=20, m=WC)
    b.cyl(0.57, 0.04, (0, 0, 0.16), seg=20, m=CH)

    # Columna cilíndrica de cristal puro
    b.cyl(0.42, 1.80, (0, 0, 1.08), seg=20, m=GL)

    # Núcleo de retícula holográfica interna
    b.cyl(0.20, 1.65, (0, 0, 1.08), seg=16, m=CN)

    # Anillo de escaneo fotónico levitante a media altura
    b.cyl(0.52, 0.08, (0, 0, 1.15), seg=20, m=CH)
    b.cyl(0.44, 0.09, (0, 0, 1.15), seg=20, m=CN)
    for a in range(8):
        ang = math.radians(a * 45)
        ex = 0.52 * math.cos(ang)
        ey = 0.52 * math.sin(ang)
        b.sph(0.03, (ex, ey, 1.15), m=CN)

    # Tapa superior toroidal y cúpula de sellado
    b.cyl(0.48, 0.08, (0, 0, 2.00), seg=20, m=CH)
    b.cyl(0.46, 0.12, (0, 0, 2.08), seg=20, m=WC)
    return b.build(COL_MAESTRA)

def modelar_clean_ceiling_hepa_grid(mats):
    """SM_Clean_Ceiling_HEPA_Grid: Panel de techo con filtro laminar estéril HEPA y luz perimetral."""
    b = dl.MB("SM_Clean_Ceiling_HEPA_Grid")
    WC, CH, CN, DM = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_DarkMetal"]
    )
    # 1. Chasis base posterior oscuro
    b.box((1.96, 1.96, 0.04), (0, 0, 0.02), m=DM)

    # 2. Marco cerámico perimetral elevado con bisel
    # Bordes Norte/Sur
    b.box((2.0, 0.16, 0.12), (0, -0.92, 0.07), m=WC)
    b.box((2.0, 0.16, 0.12), (0, 0.92, 0.07), m=WC)
    # Bordes Este/Oeste
    b.box((0.16, 1.68, 0.12), (-0.92, 0, 0.07), m=WC)
    b.box((0.16, 1.68, 0.12), (0.92, 0, 0.07), m=WC)

    # 3. Tiras perimetrales de LED cian brillante empotradas en el marco interior
    b.box((1.66, 0.025, 0.04), (0, -0.83, 0.07), m=CN)
    b.box((1.66, 0.025, 0.04), (0, 0.83, 0.07), m=CN)
    b.box((0.025, 1.64, 0.04), (-0.83, 0, 0.07), m=CN)
    b.box((0.025, 1.64, 0.04), (0.83, 0, 0.07), m=CN)

    # 4. Matriz de 16 celdas filtrantes HEPA cuadradas en relieve cromadas
    for gx in [-0.55, -0.18, 0.18, 0.55]:
        for gy in [-0.55, -0.18, 0.18, 0.55]:
            b.box((0.32, 0.32, 0.035), (gx, gy, 0.05), m=CH)
            # Micro-retícula interna
            b.box((0.28, 0.02, 0.04), (gx, gy, 0.055), m=CN)
            b.box((0.02, 0.28, 0.04), (gx, gy, 0.055), m=CN)

    # 5. Difusor laminar central circular de flujo aséptico
    b.cyl(0.18, 0.05, (0, 0, 0.065), seg=16, m=CH)
    b.sph(0.06, (0, 0, 0.08), m=CN)

    # 6. 4 Soportes de suspensión superior cromados con tensores
    for dx in [-0.85, 0.85]:
        for dy in [-0.85, 0.85]:
            b.cyl(0.035, 0.35, (dx, dy, 0.22), seg=10, m=CH)
            b.sph(0.05, (dx, dy, 0.40), m=DM)
            b.cyl(0.06, 0.04, (dx, dy, 0.10), seg=10, m=WC)
    return b.build(COL_MAESTRA)

# ==============================================================================
# 3. BIOMA 3: ROBÓTICA (4 PROPS NUEVOS)
# ==============================================================================

def modelar_robo_conveyor_feeder(mats):
    """SM_Robo_Conveyor_Feeder: Cinta transportadora de rodillos metálicos con motor y chasis."""
    b = dl.MB("SM_Robo_Conveyor_Feeder")
    CS, CB, AC, HS = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_HazardStripe"]
    )
    # Bastidor estructural de vigas longitudinales
    for dy in [-0.40, 0.40]:
        b.box((2.60, 0.08, 0.12), (0, dy, 0.70), m=CS)
        for dx in [-1.10, 0.0, 1.10]:
            b.box((0.09, 0.09, 0.65), (dx, dy, 0.35), m=CS)
            b.box((0.16, 0.16, 0.03), (dx, dy, 0.02), m=CB)

    # Cama de 14 rodillos metálicos estriados
    for i in range(14):
        rx = -1.15 + i * 0.175
        b.cyl(0.048, 0.76, (rx, 0, 0.74), rot=(math.pi/2, 0, 0), seg=12, m=CB)

    # Carcasa de cadena lateral de transmisión
    b.box((2.50, 0.04, 0.10), (0, 0.45, 0.74), m=HS)

    # Motor reductor eléctrico en el extremo
    b.cyl(0.15, 0.30, (1.20, 0.42, 0.65), rot=(0, math.pi/2, 0), seg=14, m=CS)
    b.box((0.14, 0.14, 0.18), (1.05, 0.42, 0.65), m=CB)

    # Pieza de chasis androide en tránsito
    b.box((0.30, 0.22, 0.14), (-0.20, 0, 0.85), m=CS)
    b.cyl(0.07, 0.04, (-0.20, 0, 0.93), seg=12, m=AC)

    # Pórtico con sensor infrarrojo de paso
    b.box((0.06, 0.06, 0.45), (0.50, -0.42, 0.96), m=CS)
    b.box((0.06, 0.06, 0.45), (0.50, 0.42, 0.96), m=CS)
    b.box((0.06, 0.90, 0.06), (0.50, 0, 1.18), m=CS)
    b.sph(0.04, (0.50, 0, 1.14), m=AC)
    return b.build(COL_MAESTRA)

def modelar_robo_heavy_transformer(mats):
    """SM_Robo_Heavy_Transformer: Transformador de alta tensión con radiadores y aisladores de porcelana."""
    b = dl.MB("SM_Robo_Heavy_Transformer")
    CS, CB, AC, SA, PC = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_ScreenAmber"], mats["M_Robo_Porcelain"]
    )
    # Base con rieles de rodadura
    for dy in [-0.50, 0.50]:
        b.box((1.80, 0.12, 0.08), (0, dy, 0.04), m=CS)

    # Cuba/cuerpo principal masivo
    b.box((1.60, 1.00, 1.30), (0, 0, 0.72), m=CS)

    # Aletas radiadoras de enfriamiento en ambos laterales
    for sgn in [-1, 1]:
        dy_b = sgn * 0.58
        for k in range(9):
            dx_a = -0.65 + k * 0.16
            b.box((0.02, 0.16, 1.10), (dx_a, dy_b, 0.72), m=CS)
        b.cyl(0.05, 1.50, (0, dy_b, 1.25), rot=(0, math.pi/2, 0), seg=12, m=CB)

    # 3 Aisladores de porcelana escalonada de alta tensión en el techo
    for i, ax in enumerate([-0.45, 0.0, 0.45]):
        for disc in range(4):
            d_rad = 0.14 - disc * 0.02
            b.cyl(d_rad, 0.06, (ax, 0, 1.42 + disc*0.10), seg=12, m=PC)
        b.cyl(0.025, 0.20, (ax, 0, 1.88), seg=8, m=CB)
        b.sph(0.05, (ax, 0, 1.98), m=CB)

    # Bobina toroidal frontal
    b.cyl(0.24, 0.12, (-0.35, -0.58, 0.72), rot=(math.pi/2, 0, 0), seg=16, m=CB)

    # Cuadro de mando / voltímetro
    b.box((0.24, 0.06, 0.30), (0.35, -0.55, 0.72), m=CS)
    b.cyl(0.08, 0.03, (0.35, -0.58, 0.76), rot=(math.pi/2, 0, 0), seg=12, m=SA)
    return b.build(COL_MAESTRA)

def modelar_robo_tool_rack_armory(mats):
    """SM_Robo_Tool_Rack_Armory: Panel mural organizador con herramientas pesadas de plasma y arco."""
    b = dl.MB("SM_Robo_Tool_Rack_Armory")
    CS, CB, AC, SA = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_ScreenAmber"]
    )
    # Bastidor mural de acero cobalto (1.80 x 0.14 x 2.05 m)
    b.box((1.80, 0.10, 2.00), (0, 0, 1.05), m=CS)
    b.box((1.68, 0.03, 1.84), (0, -0.05, 1.05), m=CS)

    # Luz superior de trabajo en visera
    b.box((1.72, 0.22, 0.08), (0, -0.10, 2.05), m=CS)
    b.box((1.64, 0.12, 0.02), (0, -0.12, 2.01), m=SA)

    # Herramienta 1: Antorcha de plasma industrial
    b.box((0.12, 0.08, 0.06), (-0.55, -0.10, 1.50), m=CB)
    b.cyl(0.045, 0.55, (-0.55, -0.16, 1.30), seg=10, m=CS)
    b.cyl(0.03, 0.14, (-0.55, -0.16, 0.98), seg=8, m=CB)
    b.sph(0.025, (-0.55, -0.16, 0.90), m=AC)

    # Herramienta 2: Cortador de arco con disco
    b.box((0.12, 0.08, 0.06), (-0.10, -0.10, 1.50), m=CB)
    b.cyl(0.18, 0.03, (-0.10, -0.18, 1.25), rot=(0, math.pi/2, 0), seg=16, m=CB)
    b.cyl(0.04, 0.40, (-0.10, -0.18, 1.55), seg=10, m=CS)

    # Herramienta 3: Brazo articulado de repuesto
    b.box((0.14, 0.08, 0.06), (0.45, -0.10, 1.55), m=CB)
    b.cyl(0.04, 0.35, (0.45, -0.16, 1.40), rot=(math.radians(20), 0, 0), seg=10, m=CS)
    b.sph(0.06, (0.45, -0.18, 1.20), m=CB)
    b.cyl(0.035, 0.30, (0.45, -0.15, 1.05), rot=(-math.radians(15), 0, 0), seg=8, m=CS)
    b.box((0.08, 0.10, 0.10), (0.45, -0.13, 0.88), m=CB)

    # Bandeja inferior con bobinas
    b.box((1.68, 0.25, 0.08), (0, -0.15, 0.35), m=CS)
    b.cyl(0.07, 0.12, (-0.40, -0.15, 0.45), seg=12, m=CB)
    b.cyl(0.07, 0.12, (-0.20, -0.15, 0.45), seg=12, m=CB)
    return b.build(COL_MAESTRA)

def modelar_robo_charging_station(mats):
    """SM_Robo_Charging_Station: Bahía de recarga por inducción magnética con tótem y display ámbar."""
    b = dl.MB("SM_Robo_Charging_Station")
    CS, CB, AC, SA = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_ScreenAmber"]
    )
    # Plataforma hexagonal de inducción en el suelo
    b.cyl(0.65, 0.14, (0, 0, 0.07), seg=6, m=CS)
    b.cyl(0.48, 0.04, (0, 0, 0.15), seg=18, m=CB)
    b.cyl(0.30, 0.03, (0, 0, 0.16), seg=14, m=CB)
    b.cyl(0.14, 0.04, (0, 0, 0.17), seg=12, m=AC)

    # Tótem vertical trasero
    b.box((0.36, 0.22, 1.30), (0, 0.48, 0.75), m=CS)

    # Brazos guía neumáticos de acople para drones
    for sgn in [-1, 1]:
        dx_g = sgn * 0.28
        b.cyl(0.035, 0.14, (dx_g, 0.40, 0.70), rot=(0, math.pi/2, 0), seg=8, m=CB)
        b.box((0.05, 0.30, 0.05), (dx_g + sgn*0.06, 0.25, 0.70), m=CS)
        b.box((0.03, 0.10, 0.10), (dx_g + sgn*0.08, 0.15, 0.70), m=CB)

    # Display táctil vertical ámbar
    b.box((0.26, 0.025, 0.42), (0, 0.36, 1.15), m=SA)

    # Baliza estroboscópica ámbar superior
    b.cyl(0.08, 0.08, (0, 0.48, 1.44), seg=12, m=CS)
    b.cyl(0.06, 0.12, (0, 0.48, 1.54), seg=12, m=AC)
    return b.build(COL_MAESTRA)

# ==============================================================================
# PIPELINE Y RENDERS DE PREVISUALIZACIÓN (REGLAS 4 Y 5)
# ==============================================================================
def renderizar_showcases(modelos_por_bioma):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE'
        
    sc.render.resolution_x = 1280
    sc.render.resolution_y = 720
    sc.render.film_transparent = False
    
    w = bpy.data.worlds.get("DarxBiomaWorldPhase2") or bpy.data.worlds.new("DarxBiomaWorldPhase2")
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
        out_png = os.path.join(ARTIFACTS_DIR, f"preview_fase2_bioma{i}_{nombre_bioma}.png")
        dl.snap(objs, out_png, focus=(0, 0, 0.9), dist=10.0, yaw=38.0, pitch=26.0, res=1024)
        archivos_generados.append(out_png)
        print(f"DarX | Render Fase 2 generado: {out_png}")

    # Render showcase conjunto (3 filas de biomas x 4 columnas de props)
    todos_los_objs = []
    for bioma_idx, (nombre_bioma, objs) in enumerate(modelos_por_bioma.items()):
        offset_y = (bioma_idx - 1.0) * 2.4
        for idx, obj in enumerate(objs):
            offset_x = (idx - 1.5) * 2.0
            obj.location = (offset_x, offset_y, 0.0)
            todos_los_objs.append(obj)

    bpy.context.view_layer.update()
    out_megafase = os.path.join(ARTIFACTS_DIR, "preview_fase2_todos_los_biomas_showcase.png")
    dl.snap(todos_los_objs, out_megafase, focus=(0, 0, 0.9), dist=16.5, yaw=35.0, pitch=28.0, res=1280)
    archivos_generados.append(out_megafase)
    print(f"DarX | Render Showcase Total Fase 2 generado: {out_megafase}")
    return archivos_generados

def main():
    print("=" * 80)
    print("DarX | Iniciando Pipeline Fase 2: 12 Nuevos Objetos de Laboratorio...")
    print("=" * 80)
    
    dl.wipe(COL_MAESTRA)
    dl.coll(COL_MAESTRA)
    mats = crear_materiales()

    bio1_objs = [
        modelar_bio_incubator_vats(mats),
        modelar_bio_autoclave_sterilizer(mats),
        modelar_bio_overhead_gantry(mats),
        modelar_bio_hazard_waste_bin(mats)
    ]

    bio2_objs = [
        modelar_clean_laser_interferometer(mats),
        modelar_clean_cryo_cooling_tower(mats),
        modelar_clean_optical_diagnostic_pod(mats),
        modelar_clean_ceiling_hepa_grid(mats)
    ]

    bio3_objs = [
        modelar_robo_conveyor_feeder(mats),
        modelar_robo_heavy_transformer(mats),
        modelar_robo_tool_rack_armory(mats),
        modelar_robo_charging_station(mats)
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
    print(f"DarX | Fase 2 completada: 12 FBX exportados y {len(renders)} renders generados.")
    print("=" * 80)

if __name__ == "__main__":
    main()
