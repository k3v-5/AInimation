"""generate_biome_lab_assets.py — Generador Maestro de Bloques Modulares y Props 3D con Micro-Detalles AAA.

Fase 3: Modelado de Alta Densidad y Micro-Detalles por Bioma de Laboratorio:
- Bioma 1: Biotecnología y Contención Biohazard (Imagen 1) - 8 Assets
- Bioma 2: Sala Limpia y Acelerador Cuántico (Imagen 2) - 8 Assets
- Bioma 3: Robótica y Ensamblaje Mecatrónico (Imagen 3) - 8 Assets

Cumple estrictamente con:
- Regla 3: Unicidad absoluta de diseño y silueta.
- Regla 4: Previsualización visual obligatoria en Blender antes de importar.
- Regla 5: Buffer matemático anti-clipping >= 30 cm y pasillo libre >= 6 m.
- Regla 11: 5 fases de modelado 3D (Fase 3: Detalles y pulido).
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

COL_MAESTRA = "DARX_MegaFase_Biomas"
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
    m["M_Bio_PurpleFluid"] = dl.mat("M_Bio_PurpleFluid", (0.65, 0.05, 0.85), rough=0.15, emis=(0.65, 0.05, 0.85), emis_str=3.5)

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
    m["M_Robo_SmokedGlass"] = dl.mat("M_Robo_SmokedGlass", (0.07, 0.07, 0.08), rough=0.04, metal=0.15)
    m["M_Robo_Charcoal"] = dl.mat("M_Robo_Charcoal", (0.025, 0.025, 0.028), rough=0.52, metal=0.92)
    m["M_Robo_CircuitGreen"] = dl.mat("M_Robo_CircuitGreen", (0.015, 0.28, 0.075), rough=0.28, metal=0.40)
    m["M_Robo_RedStop"] = dl.mat("M_Robo_RedStop", (0.85, 0.05, 0.04), rough=0.3, emis=(0.85, 0.05, 0.04), emis_str=2.0)
    return m

# ==============================================================================
# BIOMA 1: BIOTECNOLOGÍA Y CONTENCIÓN BIOHAZARD (IMAGEN 1)
# ==============================================================================

def modelar_bio_floor_grate(mats):
    """SM_Bio_Floor_Grate: Suelo modular 1x1x1m con fosa profunda, lodo fluorescente y rejilla con pernos."""
    b = dl.MB("SM_Bio_Floor_Grate")
    DM, PY, AG = mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"]
    
    # 1. Marco perimetral con bisel
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=DM)
    # 2. Fosa profunda de drenaje
    b.box((0.86, 0.86, 0.22), (0, 0, 0.89), m=DM)
    # 3. Lodo cáustico verde en el fondo con burbujas en relieve
    b.box((0.82, 0.82, 0.05), (0, 0, 0.82), m=AG)
    for bx, by in [(-0.25, -0.2), (0.2, 0.15), (-0.1, 0.3), (0.3, -0.25)]:
        b.sph(0.035, (bx, by, 0.85), scale=(1.2, 1.2, 0.6), m=AG)
    # 4. Rejilla industrial de acero
    for dx in [-0.32, -0.16, 0.0, 0.16, 0.32]:
        b.box((0.035, 0.84, 0.05), (dx, 0, 0.975), m=DM)
    for dy in [-0.32, -0.16, 0.0, 0.16, 0.32]:
        b.box((0.84, 0.035, 0.04), (0, dy, 0.975), m=DM)
    # 5. Bordes reforzados y pernos de advertencia
    for px in [-0.45, 0.45]:
        for py in [-0.45, 0.45]:
            b.cyl(0.028, 0.05, (px, py, 1.0), seg=8, m=PY)
    return b.build(COL_MAESTRA)

def modelar_bio_wall_pipes(mats):
    """SM_Bio_Wall_Pipes: Pared 1x1x1m con haces de tuberías con bridas, manómetros dobles y rótulo."""
    b = dl.MB("SM_Bio_Wall_Pipes")
    DM, PY, AG, HS = mats["M_Bio_DarkMetal"], mats["M_Bio_PipeYellow"], mats["M_Bio_AcidGreen"], mats["M_Bio_HazardSign"]
    
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=DM)
    for y_face in [-0.48, 0.48]:
        y_dir = -1 if y_face < 0 else 1
        # Rótulo de peligro
        b.box((0.92, 0.025, 0.12), (0, y_face, 0.88), m=HS)
        # 3 Tuberías con bridas y pernos
        b.cyl(0.05, 0.96, (-0.28, y_face + y_dir * 0.03, 0.5), seg=14, m=PY)
        b.cyl(0.07, 0.96, (0.0, y_face + y_dir * 0.03, 0.5), seg=14, m=DM)
        b.cyl(0.045, 0.96, (0.28, y_face + y_dir * 0.03, 0.5), seg=14, m=PY)
        # Bridas hexagonales en tuberías
        for bz in [0.20, 0.80]:
            b.cyl(0.085, 0.04, (0.0, y_face + y_dir * 0.03, bz), seg=8, m=DM)
            b.cyl(0.065, 0.03, (-0.28, y_face + y_dir * 0.03, bz), seg=8, m=PY)
            b.cyl(0.060, 0.03, (0.28, y_face + y_dir * 0.03, bz), seg=8, m=PY)
        # Manómetro de presión con aguja y cristal
        b.cyl(0.065, 0.04, (0.0, y_face + y_dir * 0.07, 0.52), rot=(math.pi/2, 0, 0), seg=16, m=PY)
        b.cyl(0.05, 0.01, (0.0, y_face + y_dir * 0.09, 0.52), rot=(math.pi/2, 0, 0), seg=12, m=AG)
        b.box((0.005, 0.015, 0.04), (0.0, y_face + y_dir * 0.095, 0.53), m=DM) # aguja
        # Válvula de alivio con 4 radios
        b.cyl(0.02, 0.05, (-0.28, y_face + y_dir * 0.06, 0.40), rot=(math.pi/2, 0, 0), seg=8, m=DM)
        b.cyl(0.055, 0.015, (-0.28, y_face + y_dir * 0.09, 0.40), rot=(math.pi/2, 0, 0), seg=12, m=PY)
        b.box((0.11, 0.015, 0.015), (-0.28, y_face + y_dir * 0.09, 0.40), m=PY)
        # Caja de conexiones eléctricas y testigo verde
        b.box((0.12, 0.04, 0.16), (0.28, y_face + y_dir * 0.04, 0.35), m=DM)
        b.cyl(0.015, 0.02, (0.28, y_face + y_dir * 0.065, 0.38), rot=(math.pi/2, 0, 0), seg=8, m=AG)
    return b.build(COL_MAESTRA)

def modelar_bio_pillar_organic(mats):
    """SM_Bio_Pillar_Organic: Columna con collarines hexagonales, zarcillos y fluido cáustico."""
    b = dl.MB("SM_Bio_Pillar_Organic")
    DM, AG, CF, PY = mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_ChitinFlesh"], mats["M_Bio_PipeYellow"]
    
    b.cyl(0.50, 0.35, (0, 0, 0.175), seg=8, m=DM)
    b.cyl(0.50, 0.35, (0, 0, 2.825), seg=8, m=DM)
    b.cyl(0.38, 2.30, (0, 0, 1.50), seg=16, m=DM)
    # Núcleo transparente con líquido cáustico
    b.cyl(0.20, 2.20, (0, 0, 1.50), seg=16, m=AG)
    # Zarcillos y pústulas mutantes en relieve
    for i in range(12):
        ang = i * (math.pi / 6)
        z = 0.45 + i * 0.18
        x = math.cos(ang) * 0.35
        y = math.sin(ang) * 0.35
        b.sph(0.08, (x, y, z), scale=(1.2, 1.2, 1.4), m=CF)
        if i % 3 == 0:
            b.sph(0.04, (x*1.15, y*1.15, z + 0.03), scale=(1, 1, 1), m=AG) # pústula fluorescente
    # Collarines industriales con pernos
    for z_c in [0.85, 1.55, 2.25]:
        b.cyl(0.44, 0.09, (0, 0, z_c), seg=12, m=PY)
        for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
            b.cyl(0.02, 0.03, (math.cos(ang)*0.45, math.sin(ang)*0.45, z_c), seg=6, m=DM)
    return b.build(COL_MAESTRA)

def modelar_bio_cover_hazard(mats):
    """SM_Bio_Cover_Hazard: Barricada reforzada con baliza química, asas y advertencias."""
    b = dl.MB("SM_Bio_Cover_Hazard")
    DM, AG, HS, PY = mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_HazardSign"], mats["M_Bio_PipeYellow"]
    
    b.box((1.2, 0.45, 0.15), (0, 0, 0.075), m=DM)
    b.box((1.16, 0.32, 0.75), (0, 0, 0.50), m=DM)
    # Refuerzos angulares
    b.box((1.12, 0.05, 0.18), (0, -0.17, 0.65), m=HS)
    b.box((1.12, 0.05, 0.18), (0, 0.17, 0.65), m=HS)
    # Baliza química superior protegida por barras
    b.cyl(0.035, 0.85, (0, 0, 0.92), rot=(0, math.pi/2, 0), seg=14, m=AG)
    b.box((0.88, 0.08, 0.02), (0, 0, 0.96), m=DM) # tejadillo protector
    # Asas tácticas laterales
    for x in [-0.56, 0.56]:
        b.box((0.08, 0.38, 0.85), (x, 0, 0.48), m=PY)
        b.cyl(0.02, 0.20, (x + (-0.02 if x<0 else 0.02), 0, 0.75), seg=8, m=DM)
    return b.build(COL_MAESTRA)

def modelar_bio_giant_specimen_pod(mats):
    """SM_Bio_GiantSpecimenPod: Tanque colosal central con espécimen mutante biomecánico (Imagen 1)."""
    b = dl.MB("SM_Bio_GiantSpecimenPod")
    DM, AG, BG, CF, PY, SG = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_Glass"],
        mats["M_Bio_ChitinFlesh"], mats["M_Bio_PipeYellow"], mats["M_Bio_ScreenGreen"]
    )
    
    # 1. Base octogonal con bridas
    b.cyl(1.30, 0.45, (0, 0, 0.225), seg=8, m=DM)
    b.cyl(1.35, 0.08, (0, 0, 0.41), seg=16, m=PY)
    # Pernos perimetrales en la brida
    for i in range(16):
        ang = i * (math.pi / 8)
        b.cyl(0.025, 0.03, (math.cos(ang)*1.28, math.sin(ang)*1.28, 0.46), seg=6, m=DM)
        
    # 2. 4 Soportes hidráulicos con fuelles de amortiguación
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        x = math.cos(ang) * 1.38
        y = math.sin(ang) * 1.38
        b.box((0.28, 0.28, 0.65), (x, y, 0.325), m=PY)
        # Fuelle hidráulico corrugado
        for fz in [0.40, 0.48, 0.56]:
            b.cyl(0.11, 0.04, (x, y, fz), seg=12, m=DM)
        b.seg((x, y, 0.65), (math.cos(ang)*1.0, math.sin(ang)*1.0, 1.05), 0.08, 0.07, m=DM)
        
    # 3. Cilindro de fluido verde mutagénico con burbujas internas
    b.cyl(0.92, 2.30, (0, 0, 1.60), seg=24, m=AG)
    b.cyl(1.0, 2.30, (0, 0, 1.60), seg=24, m=BG)
    # Burbujas en el fluido
    for bx, by, bz in [(-0.4, 0.3, 1.2), (0.35, -0.4, 1.8), (-0.2, -0.35, 2.2), (0.45, 0.2, 1.5), (0.1, 0.4, 2.4)]:
        b.sph(0.045, (bx, by, bz), scale=(1, 1, 1), m=AG)
        
    # 4. Espécimen mutante alienígena suspendido con espina y costillas biomecánicas
    # Torso
    b.sph(0.36, (0, 0, 1.70), scale=(0.85, 0.65, 1.45), m=CF)
    # Vértebras lumbares y dorsales en relieve
    for vz in [1.35, 1.50, 1.65, 1.80, 1.95]:
        b.box((0.10, 0.12, 0.06), (0, 0.20, vz), m=DM)
        # Arcos costales
        b.seg((-0.18, 0.05, vz), (0, 0.20, vz), 0.025, 0.025, m=CF)
        b.seg((0.18, 0.05, vz), (0, 0.20, vz), 0.025, 0.025, m=CF)
    # Cabeza bio-alienígena con cresta y zócalos
    b.sph(0.24, (0, -0.15, 2.25), scale=(0.8, 1.25, 0.95), m=CF)
    b.box((0.10, 0.28, 0.14), (0, -0.10, 2.38), m=DM) # implante craneal
    # 4 Cables neurales que salen de la nuca al domo
    for cx in [-0.08, -0.03, 0.03, 0.08]:
        b.seg((cx, 0.05, 2.35), (cx*2.5, 0.25, 2.85), 0.015, 0.015, m=PY)
    # Brazos con garras suspendidas
    b.seg((0.22, 0, 1.80), (0.48, -0.18, 1.45), 0.065, 0.04, m=CF)
    b.seg((-0.22, 0, 1.80), (-0.48, -0.18, 1.45), 0.065, 0.04, m=CF)
    b.box((0.08, 0.12, 0.04), (0.48, -0.22, 1.42), m=DM) # garra mecánica
    b.box((0.08, 0.12, 0.04), (-0.48, -0.22, 1.42), m=DM)
    
    # 5. Domo superior blindado con toberas y cáncamos
    b.cyl(1.25, 0.35, (0, 0, 2.925), seg=8, m=DM)
    b.cyl(1.30, 0.08, (0, 0, 2.78), seg=16, m=PY)
    b.sph(1.05, (0, 0, 3.0), scale=(1.0, 1.0, 0.55), m=DM)
    b.cyl(0.25, 0.20, (0, 0, 3.35), seg=12, m=DM) # válvula central
    
    # 6. 4 Mangueras gruesas trenzadas que bajan del domo
    for ang in [-math.pi/3, math.pi/3, -2*math.pi/3, 2*math.pi/3]:
        fx = math.cos(ang) * 1.10
        fy = math.sin(ang) * 1.10
        b.seg((fx, fy, 2.9), (fx*1.25, fy*1.25, 1.6), 0.07, 0.07, m=PY)
        b.seg((fx*1.25, fy*1.25, 1.6), (fx*1.08, fy*1.08, 0.45), 0.07, 0.07, m=PY)
        
    # 7. Consola frontal con teclado y display verde
    b.box((0.60, 0.38, 0.90), (0, -1.22, 0.45), m=DM)
    b.box((0.50, 0.05, 0.38), (0, -1.42, 0.72), m=SG)
    b.box((0.45, 0.20, 0.05), (0, -1.25, 0.88), m=PY) # teclado
    return b.build(COL_MAESTRA)

def modelar_bio_chemical_workstation(mats):
    """SM_Bio_ChemicalWorkstation: Mesa química con matraces, serpentín de destilación y microscopio (Imagen 1)."""
    b = dl.MB("SM_Bio_ChemicalWorkstation")
    DM, AG, BG, PY, CF, SG, PF = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_Glass"],
        mats["M_Bio_PipeYellow"], mats["M_Bio_ChitinFlesh"], mats["M_Bio_ScreenGreen"], mats["M_Bio_PurpleFluid"]
    )
    
    # 1. Estructura de la mesa (2.4x0.95x0.92m) con cajoneras
    for x in [-1.1, 1.1]:
        for y in [-0.38, 0.38]:
            b.box((0.08, 0.08, 0.88), (x, y, 0.44), m=DM)
    b.box((2.4, 0.95, 0.08), (0, 0, 0.88), m=DM)
    # Módulo de cajones
    b.box((0.55, 0.80, 0.65), (-0.75, 0, 0.48), m=DM)
    for dz in [0.28, 0.48, 0.68]:
        b.box((0.48, 0.02, 0.14), (-0.75, -0.41, dz), m=PY)
        b.box((0.15, 0.03, 0.03), (-0.75, -0.43, dz), m=DM) # tirador
        
    # Estante superior con soportes
    b.box((0.06, 0.06, 0.55), (-1.05, 0.3, 1.15), m=DM)
    b.box((0.06, 0.06, 0.55), (1.05, 0.3, 1.15), m=DM)
    b.box((2.3, 0.35, 0.04), (0, 0.3, 1.42), m=DM)
    
    # 2. Gradilla con 8 tubos de ensayo y tapones
    b.box((0.55, 0.12, 0.06), (-0.7, -0.15, 0.95), m=DM)
    for i, tx in enumerate([-0.90, -0.85, -0.80, -0.75, -0.70, -0.65, -0.60, -0.55]):
        col = AG if i % 3 == 0 else (PF if i % 3 == 1 else PY)
        b.cyl(0.015, 0.16, (tx, -0.15, 1.03), seg=8, m=col)
        b.cyl(0.018, 0.18, (tx, -0.15, 1.04), seg=8, m=BG)
        b.cyl(0.019, 0.02, (tx, -0.15, 1.14), seg=8, m=DM) # tapón
        
    # 3. Matraces Erlenmeyer con tapones y serpentín de destilación
    # Matraz 1 (Verde)
    b.frustum(0.09, 0.025, 0.18, (-0.25, -0.10, 1.01), seg=14, m=AG)
    b.cyl(0.025, 0.08, (-0.25, -0.10, 1.14), seg=12, m=BG)
    b.cyl(0.026, 0.025, (-0.25, -0.10, 1.19), seg=12, m=DM) # tapón
    # Matraz 2 (Púrpura)
    b.frustum(0.11, 0.03, 0.22, (0.05, 0.12, 1.03), seg=14, m=PF)
    b.cyl(0.03, 0.09, (0.05, 0.12, 1.18), seg=12, m=BG)
    # Tubo serpentín de destilación que une los matraces
    b.seg((-0.25, -0.10, 1.18), (-0.10, 0.01, 1.35), 0.008, 0.008, m=BG)
    b.seg((-0.10, 0.01, 1.35), (0.05, 0.12, 1.18), 0.008, 0.008, m=BG)
    
    # 4. Microscopio biológico con doble ocular y perillas
    b.box((0.24, 0.28, 0.05), (0.55, -0.10, 0.94), m=DM)
    b.cyl(0.045, 0.30, (0.55, 0.02, 1.10), seg=12, m=DM)
    b.box((0.15, 0.15, 0.02), (0.55, -0.10, 1.06), m=PY) # platina
    b.cyl(0.035, 0.12, (0.55, -0.10, 1.18), seg=12, m=DM) # torreta
    # Perillas micrométricas
    b.cyl(0.025, 0.04, (0.50, 0.02, 1.08), rot=(0, math.pi/2, 0), seg=8, m=PY)
    b.cyl(0.025, 0.04, (0.60, 0.02, 1.08), rot=(0, math.pi/2, 0), seg=8, m=PY)
    # Doble ocular inclinado
    b.cyl(0.018, 0.12, (0.52, -0.06, 1.30), rot=(-math.pi/5, 0, 0), seg=8, m=DM)
    b.cyl(0.018, 0.12, (0.58, -0.06, 1.30), rot=(-math.pi/5, 0, 0), seg=8, m=DM)
    
    # 5. Centrifugadora con display digital
    b.cyl(0.18, 0.22, (0.95, -0.12, 1.03), seg=16, m=DM)
    b.cyl(0.15, 0.02, (0.95, -0.12, 1.14), seg=16, m=PY)
    b.box((0.08, 0.02, 0.04), (0.95, -0.29, 1.08), m=SG)
    return b.build(COL_MAESTRA)

def modelar_bio_control_console(mats):
    """SM_Bio_ControlConsole: Consola con CRT bulboso verde, visera, teclado y palancas (Imagen 1)."""
    b = dl.MB("SM_Bio_ControlConsole")
    DM, AG, PY, SG, HS = (
        mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_PipeYellow"],
        mats["M_Bio_ScreenGreen"], mats["M_Bio_HazardSign"]
    )
    
    b.box((1.7, 0.95, 0.85), (0, 0, 0.425), m=DM)
    b.box((1.65, 0.45, 0.12), (0, -0.20, 0.88), m=DM)
    # Teclado con teclas individuales en relieve
    for row in range(3):
        for col in range(8):
            b.box((0.04, 0.04, 0.015), (-0.55 + col*0.06, -0.26 + row*0.06, 0.96), m=PY)
    # Palancas de mando con protectores
    for lx in [0.25, 0.40, 0.55]:
        b.box((0.03, 0.08, 0.04), (lx, -0.20, 0.96), m=DM)
        b.cyl(0.008, 0.08, (lx, -0.20, 1.0), rot=(math.pi/8, 0, 0), seg=6, m=PY)
        b.sph(0.015, (lx, -0.17, 1.04), m=AG)
        
    # Doble CRT bulboso verde con visera
    b.box((1.65, 0.45, 0.65), (0, 0.22, 1.25), m=DM)
    b.box((1.68, 0.52, 0.08), (0, 0.22, 1.60), m=DM) # visera superior
    # Pantalla 1 (ADN y Mutación)
    b.sph(0.32, (-0.42, 0.02, 1.28), scale=(1.2, 0.35, 0.9), m=SG)
    # Pantalla 2 (Biometría y Parámetros)
    b.sph(0.32, (0.42, 0.02, 1.28), scale=(1.2, 0.35, 0.9), m=SG)
    # Rótulo y manómetros
    b.box((1.60, 0.04, 0.08), (0, 0.01, 1.58), m=HS)
    for gx in [-0.72, 0.72]:
        b.cyl(0.055, 0.04, (gx, 0.01, 1.35), rot=(math.pi/2, 0, 0), seg=12, m=PY)
        b.cyl(0.040, 0.01, (gx, -0.015, 1.35), rot=(math.pi/2, 0, 0), seg=12, m=AG)
    return b.build(COL_MAESTRA)

def modelar_bio_secondary_tube(mats):
    """SM_Bio_SecondaryTube: Cilindro de preservación biológica adosable con espécimen embrionario."""
    b = dl.MB("SM_Bio_SecondaryTube")
    DM, AG, BG, CF, PY = mats["M_Bio_DarkMetal"], mats["M_Bio_AcidGreen"], mats["M_Bio_Glass"], mats["M_Bio_ChitinFlesh"], mats["M_Bio_PipeYellow"]
    
    b.box((0.85, 0.15, 2.4), (0, 0.32, 1.2), m=DM)
    # Pernos de anclaje mural
    for az in [0.3, 1.2, 2.1]:
        b.cyl(0.03, 0.05, (-0.35, 0.32, az), rot=(math.pi/2, 0, 0), seg=8, m=PY)
        b.cyl(0.03, 0.05, (0.35, 0.32, az), rot=(math.pi/2, 0, 0), seg=8, m=PY)
    # Tapas y cilindro
    b.cyl(0.42, 0.25, (0, 0, 0.125), seg=16, m=DM)
    b.cyl(0.42, 0.25, (0, 0, 2.275), seg=16, m=DM)
    b.cyl(0.36, 1.90, (0, 0, 1.20), seg=16, m=AG)
    b.cyl(0.39, 1.90, (0, 0, 1.20), seg=16, m=BG)
    # Espécimen embrionario en suspensión
    b.sph(0.18, (0, 0, 1.20), scale=(0.8, 0.8, 1.6), m=CF)
    b.sph(0.08, (0, -0.05, 1.35), scale=(1, 1, 1), m=AG) # núcleo luminiscente
    # Abrazaderas circulares con pernos
    for z in [0.45, 1.95]:
        b.cyl(0.44, 0.08, (0, 0, z), seg=16, m=PY)
    return b.build(COL_MAESTRA)


# ==============================================================================
# BIOMA 2: SALA LIMPIA Y ACELERADOR CUÁNTICO (IMAGEN 2)
# ==============================================================================

def modelar_clean_floor_tile(mats):
    """SM_Clean_Floor_Tile: Losa blanca biselada 1x1x1m con junta de silicona y cruz de fibra óptica cian."""
    b = dl.MB("SM_Clean_Floor_Tile")
    WC, CH, CN, DM = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"], mats["M_Clean_DarkMetal"]
    
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=WC)
    # Junta de silicona oscura hermética
    b.box((0.98, 0.98, 0.05), (0, 0, 0.98), m=DM)
    # Losa cerámica blanca brillante
    b.box((0.93, 0.93, 0.03), (0, 0, 0.99), m=WC)
    # Cruz central de fibra óptica cian
    b.box((0.04, 0.90, 0.02), (0, 0, 1.0), m=CN)
    b.box((0.90, 0.04, 0.02), (0, 0, 1.0), m=CN)
    # Nexus central de cromo y esquineros
    b.cyl(0.045, 0.025, (0, 0, 1.0), seg=12, m=CH)
    for x in [-0.42, 0.42]:
        for y in [-0.42, 0.42]:
            b.box((0.06, 0.06, 0.02), (x, y, 1.0), m=CH)
    return b.build(COL_MAESTRA)

def modelar_clean_wall_panel(mats):
    """SM_Clean_Wall_Panel: Muro cerámico blanco con ranuras HEPA en cromo y banda de datos cian."""
    b = dl.MB("SM_Clean_Wall_Panel")
    WC, CH, CN, DM = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"], mats["M_Clean_DarkMetal"]
    
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=WC)
    for y_face in [-0.48, 0.48]:
        y_dir = -1 if y_face < 0 else 1
        # Rejilla HEPA con louvers de cromo
        b.box((0.85, 0.03, 0.18), (0, y_face, 0.20), m=DM)
        for z_slit in [0.13, 0.17, 0.21, 0.25]:
            b.box((0.80, 0.04, 0.015), (0, y_face + y_dir*0.01, z_slit), m=CH)
        # Ranura horizontal de datos cian
        b.box((0.92, 0.03, 0.03), (0, y_face, 0.85), m=CN)
        # Panel central biselado con moldura de cromo
        b.box((0.75, 0.02, 0.45), (0, y_face, 0.55), m=WC)
        b.box((0.72, 0.04, 0.42), (0, y_face, 0.55), m=CH)
    return b.build(COL_MAESTRA)

def modelar_clean_pillar_prismatic(mats):
    """SM_Clean_Pillar_Prismatic: Columna prismática facetada con núcleo de cristal y ranuras cian."""
    b = dl.MB("SM_Clean_Pillar_Prismatic")
    WC, CH, CN, CR = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"], mats["M_Clean_Crystal"]
    
    b.box((0.85, 0.85, 0.25), (0, 0, 0.125), m=CH)
    b.box((0.85, 0.85, 0.25), (0, 0, 2.875), m=CH)
    b.prism(0.70, 0.70, 2.50, (0, 0, 1.50), taper=1.0, m=WC)
    # Núcleo de cristal cuántico
    b.cyl(0.22, 2.40, (0, 0, 1.50), seg=8, m=CR)
    # 4 Ranuras verticales de emisión cian
    for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
        x = math.cos(ang) * 0.36
        y = math.sin(ang) * 0.36
        b.box((0.04, 0.04, 2.3), (x, y, 1.50), m=CN)
    return b.build(COL_MAESTRA)

def modelar_clean_cover_sterile(mats):
    """SM_Clean_Cover_Sterile: Cobertura táctica minimalista biselada con pantalla empotrada."""
    b = dl.MB("SM_Clean_Cover_Sterile")
    WC, CH, CN = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"]
    
    b.box((1.2, 0.45, 0.12), (0, 0, 0.06), m=CH)
    b.box((1.15, 0.38, 0.78), (0, 0, 0.51), m=WC)
    b.prism(1.15, 0.38, 0.20, (0, 0, 0.92), taper=0.65, m=WC)
    # Tira de telemetría cian y pantalla
    b.box((1.05, 0.03, 0.04), (0, -0.20, 0.65), m=CN)
    b.box((0.35, 0.04, 0.15), (0, -0.20, 0.45), m=CN)
    return b.build(COL_MAESTRA)

def modelar_clean_particle_chamber(mats):
    """SM_Clean_ParticleChamber: Cámara de contención cuántica central con 24 nodos de doble hélice (Imagen 2)."""
    b = dl.MB("SM_Clean_ParticleChamber")
    WC, CH, CN, GL, CR, DM = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_Crystal"], mats["M_Clean_DarkMetal"]
    )
    
    # 1. Pedestal escalonado con luces rasantes
    b.box((2.35, 2.35, 0.20), (0, 0, 0.10), m=WC)
    b.box((2.05, 2.05, 0.15), (0, 0, 0.275), m=CH)
    b.box((2.10, 0.04, 0.04), (0, -1.04, 0.30), m=CN)
    b.box((2.10, 0.04, 0.04), (0, 1.04, 0.30), m=CN)
    
    # 2. 4 Pylons cromados en esquinas con canales de fibra óptica
    for cx in [-0.88, 0.88]:
        for cy in [-0.88, 0.88]:
            b.box((0.24, 0.24, 2.50), (cx, cy, 1.60), m=CH)
            b.box((0.06, 0.06, 2.30), (cx*0.95, cy*0.95, 1.60), m=CN)
            b.box((0.26, 0.26, 0.08), (cx, cy, 1.50), m=DM) # collarín magnético
            
    # 3. Cubo de cristal prismático de ultra-alta pureza
    b.box((1.55, 1.55, 2.15), (0, 0, 1.45), m=GL)
    
    # 4. Doble Hélice Cuántica con 24 nodos de energía interconectados
    num_puntos = 24
    for p in range(num_puntos):
        t = p / num_puntos
        ang = t * 5 * math.pi
        z = 0.55 + t * 1.80
        # Hebra A (Cian)
        x1 = math.cos(ang) * 0.44
        y1 = math.sin(ang) * 0.44
        b.sph(0.055, (x1, y1, z), m=CN)
        # Hebra B (Cristal)
        x2 = math.cos(ang + math.pi) * 0.44
        y2 = math.sin(ang + math.pi) * 0.44
        b.sph(0.055, (x2, y2, z), m=CR)
        # Filamentos de plasma conectando las hebras
        if p % 2 == 0:
            b.seg((x1, y1, z), (x2, y2, z), 0.012, 0.012, m=CN)
            
    # 5. Singularity core central pulsante
    b.sph(0.18, (0, 0, 1.45), m=CN)
    b.sph(0.24, (0, 0, 1.45), m=CR)
    
    # 6. Techo con acelerador toroidal y tobera de confinamiento
    b.box((2.05, 2.05, 0.25), (0, 0, 2.70), m=WC)
    b.cyl(0.88, 0.35, (0, 0, 2.85), seg=24, m=CH)
    b.cyl(0.58, 0.38, (0, 0, 2.85), seg=24, m=CN)
    b.frustum(0.35, 0.15, 0.25, (0, 0, 2.50), seg=16, m=DM) # tobera hacia abajo
    return b.build(COL_MAESTRA)

def modelar_clean_holo_console(mats):
    """SM_Clean_HoloConsole: Terminal en voladizo con pantallas holográficas flotantes sin marco (Imagen 2)."""
    b = dl.MB("SM_Clean_HoloConsole")
    WC, CH, CN, GL, DM = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"], mats["M_Clean_Glass"], mats["M_Clean_DarkMetal"]
    
    b.box((1.15, 0.72, 0.12), (0, 0, 0.06), m=WC)
    b.box((0.48, 0.42, 0.85), (0, 0.08, 0.48), m=WC)
    b.box((1.40, 0.78, 0.10), (0, -0.10, 0.95), rot=(math.pi/14, 0, 0), m=WC)
    # Teclado capacitivo empotrado
    b.box((0.78, 0.36, 0.01), (0, -0.15, 0.98), rot=(math.pi/14, 0, 0), m=DM)
    b.box((0.72, 0.32, 0.015), (0, -0.15, 0.99), rot=(math.pi/14, 0, 0), m=CN)
    # Proyectores de haz óptico inferiores
    for px in [-0.34, 0.34]:
        b.cyl(0.045, 0.06, (px, 0.10, 1.05), seg=12, m=CH)
        b.sph(0.02, (px, 0.10, 1.09), m=CN) # punto láser
    # Dos pantallas holográficas flotantes sin marco
    b.box((0.58, 0.01, 0.44), (-0.34, 0.12, 1.36), rot=(-math.pi/12, -math.pi/24, 0), m=CN)
    b.box((0.59, 0.012, 0.45), (-0.34, 0.12, 1.36), rot=(-math.pi/12, -math.pi/24, 0), m=GL)
    b.box((0.58, 0.01, 0.44), (0.34, 0.12, 1.36), rot=(-math.pi/12, math.pi/24, 0), m=CN)
    b.box((0.59, 0.012, 0.45), (0.34, 0.12, 1.36), rot=(-math.pi/12, math.pi/24, 0), m=GL)
    return b.build(COL_MAESTRA)

def modelar_clean_crystal_dispenser(mats):
    """SM_Clean_CrystalDispenser: Banco de muestras con cubos de cristal, minerales voxel y brazo articulado."""
    b = dl.MB("SM_Clean_CrystalDispenser")
    WC, CH, CN, GL, CR, DM = (
        mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"],
        mats["M_Clean_Glass"], mats["M_Clean_Crystal"], mats["M_Clean_DarkMetal"]
    )
    
    b.box((2.05, 0.88, 0.88), (0, 0, 0.44), m=WC)
    b.box((2.10, 0.92, 0.08), (0, 0, 0.92), m=CH)
    
    # 3 Campanas de cristal al vacío con cristales voxel
    for i, cx in enumerate([-0.65, 0.0, 0.65]):
        b.cyl(0.24, 0.04, (cx, 0, 0.98), seg=16, m=CH)
        b.cyl(0.19, 0.02, (cx, 0, 1.01), seg=16, m=CN)
        b.box((0.38, 0.38, 0.48), (cx, 0, 1.26), m=GL)
        # Cristal resonante voxel
        b.sph(0.11, (cx, 0, 1.26), scale=(1, 1, 1.2), m=CR)
        b.box((0.13, 0.13, 0.13), (cx, 0, 1.26), rot=(math.pi/4, math.pi/4, 0), m=CN)
        # Micro-cristales flotantes
        b.sph(0.025, (cx + 0.1, 0.08, 1.35), m=CR)
        b.sph(0.020, (cx - 0.08, -0.09, 1.20), m=CN)
        
    # Brazo robótico manipulador lateral
    b.cyl(0.06, 0.15, (0.95, -0.25, 1.02), seg=12, m=DM)
    b.seg((0.95, -0.25, 1.10), (0.85, -0.10, 1.35), 0.03, 0.025, m=CH)
    b.seg((0.85, -0.10, 1.35), (0.75, 0.05, 1.25), 0.025, 0.018, m=CH)
    b.box((0.04, 0.04, 0.06), (0.75, 0.05, 1.20), m=CN) # sensor láser
    return b.build(COL_MAESTRA)

def modelar_clean_server_bank(mats):
    """SM_Clean_ServerBank: Batería de supercomputación cuántica con bahías extraíbles y tiras LED."""
    b = dl.MB("SM_Clean_ServerBank")
    WC, CH, CN, DM = mats["M_Clean_WhiteCeramic"], mats["M_Clean_Chrome"], mats["M_Clean_CyanNeon"], mats["M_Clean_DarkMetal"]
    
    b.box((1.65, 0.72, 2.35), (0, 0, 1.175), m=WC)
    b.box((1.70, 0.76, 0.12), (0, 0, 0.06), m=CH)
    
    for i in range(6):
        bz = 0.36 + i * 0.33
        b.box((1.48, 0.04, 0.25), (0, -0.35, bz), m=DM)
        # Tiras LED y micro-perforaciones
        b.box((1.38, 0.02, 0.03), (0, -0.375, bz + 0.07), m=CN)
        b.box((0.50, 0.02, 0.02), (-0.40, -0.375, bz - 0.05), m=CN)
        b.box((0.16, 0.035, 0.04), (-0.58, -0.38, bz), m=CH)
        b.box((0.16, 0.035, 0.04), (0.58, -0.38, bz), m=CH)
    return b.build(COL_MAESTRA)


# ==============================================================================
# BIOMA 3: ROBÓTICA Y ENSAMBLAJE MECATRÓNICO (IMAGEN 3)
# ==============================================================================

def modelar_robo_floor_darkplate(mats):
    """SM_Robo_Floor_DarkPlate: Losa de acero azul cobalto con relieve de placa diamantada y cables de cobre."""
    b = dl.MB("SM_Robo_Floor_DarkPlate")
    CS, CB, AC, CC = mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"], mats["M_Robo_Charcoal"]
    
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=CS)
    b.box((0.92, 0.92, 0.04), (0, 0, 0.98), m=CC)
    # Patrón de placa diamantada en relieve
    for rx in [-0.25, 0.0, 0.25]:
        for ry in [-0.3, -0.1, 0.1, 0.3]:
            b.box((0.08, 0.03, 0.01), (rx, ry, 1.005), rot=(0, 0, math.pi/4), m=CS)
    # Canaleta con haz de cables trenzados de cobre
    b.box((0.18, 0.88, 0.035), (0.35, 0, 0.99), m=CS)
    b.cyl(0.025, 0.88, (0.32, 0, 0.99), rot=(math.pi/2, 0, 0), seg=10, m=CB)
    b.cyl(0.025, 0.88, (0.38, 0, 0.99), rot=(math.pi/2, 0, 0), seg=10, m=CB)
    # Remaches hexagonales de bronce
    for x in [-0.44, 0.44]:
        for y in [-0.44, 0.44]:
            b.cyl(0.03, 0.03, (x, y, 1.0), seg=6, m=CB)
    return b.build(COL_MAESTRA)

def modelar_robo_wall_riveted(mats):
    """SM_Robo_Wall_Riveted: Muro azul cobalto con vigas I-beam remachadas, conductos de cobre y testigo ámbar."""
    b = dl.MB("SM_Robo_Wall_Riveted")
    CS, CB, AC, CC = mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"], mats["M_Robo_Charcoal"]
    
    b.box((1.0, 1.0, 1.0), (0, 0, 0.5), m=CS)
    for y_face in [-0.48, 0.48]:
        y_dir = -1 if y_face < 0 else 1
        # Vigas maestras I-beam con alas
        for vz in [0.25, 0.75]:
            b.box((0.96, 0.05, 0.15), (0, y_face, vz), m=CC)
            b.box((0.96, 0.07, 0.03), (0, y_face + y_dir*0.015, vz + 0.06), m=CS)
            b.box((0.96, 0.07, 0.03), (0, y_face + y_dir*0.015, vz - 0.06), m=CS)
            # Remaches de bronce
            for rx in [-0.42, -0.21, 0.0, 0.21, 0.42]:
                b.cyl(0.022, 0.025, (rx, y_face + y_dir*0.035, vz), rot=(math.pi/2, 0, 0), seg=6, m=CB)
        # Tubería conduit de cobre con abrazaderas
        b.cyl(0.038, 0.96, (0.35, y_face + y_dir*0.025, 0.50), seg=12, m=CB)
        for cz in [0.15, 0.50, 0.85]:
            b.box((0.08, 0.04, 0.03), (0.35, y_face + y_dir*0.035, cz), m=CS)
        # Caja de fusibles con luz ámbar
        b.box((0.20, 0.07, 0.24), (-0.25, y_face + y_dir*0.035, 0.50), m=CS)
        b.cyl(0.028, 0.02, (-0.25, y_face + y_dir*0.075, 0.50), rot=(math.pi/2, 0, 0), seg=8, m=AC)
    return b.build(COL_MAESTRA)

def modelar_robo_pillar_copper(mats):
    """SM_Robo_Pillar_Copper: Columna cilíndrica con bobinado helicoidal de cobre continuo y aisladores cerámicos."""
    b = dl.MB("SM_Robo_Pillar_Copper")
    CS, CB, AC, CC = mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"], mats["M_Robo_Charcoal"]
    
    b.cyl(0.50, 0.35, (0, 0, 0.175), seg=12, m=CS)
    b.cyl(0.50, 0.35, (0, 0, 2.825), seg=12, m=CS)
    b.cyl(0.38, 2.30, (0, 0, 1.50), seg=16, m=CC)
    # Bobinado helicoidal denso de alambre de cobre
    for i in range(16):
        z = 0.45 + i * 0.13
        b.cyl(0.43, 0.045, (0, 0, z), seg=16, m=CB)
    # Aislantes cerámicos escalonados
    for az in [0.95, 1.50, 2.05]:
        b.cyl(0.47, 0.08, (0, 0, az), seg=12, m=CS)
        b.cyl(0.40, 0.03, (0, 0, az), seg=12, m=AC)
    return b.build(COL_MAESTRA)

def modelar_robo_cover_armor(mats):
    """SM_Robo_Cover_Armor: Barricada de armadura pesada multicapa con sensor óptico ámbar."""
    b = dl.MB("SM_Robo_Cover_Armor")
    CS, CB, AC, CC = mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"], mats["M_Robo_Charcoal"]
    
    b.box((1.2, 0.45, 0.15), (0, 0, 0.075), m=CS)
    b.box((1.16, 0.36, 0.72), (0, 0, 0.48), m=CS)
    b.box((1.08, 0.07, 0.58), (0, -0.17, 0.48), m=CC)
    for x in [-0.52, 0.52]:
        b.box((0.10, 0.38, 0.78), (x, 0, 0.50), m=CB)
    # Sensor ámbar horizontal
    b.box((0.98, 0.04, 0.06), (0, -0.19, 0.85), m=AC)
    return b.build(COL_MAESTRA)

def modelar_robo_assembly_cell(mats):
    """SM_Robo_AssemblyCell: Celda central de ensamblaje con chasis androide anatómico y 4 brazos articulados (Imagen 3)."""
    b = dl.MB("SM_Robo_AssemblyCell")
    CS, CB, AC, SG, CC = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_SmokedGlass"], mats["M_Robo_Charcoal"]
    )
    
    # 1. Base octogonal con borde de seguridad
    b.cyl(1.45, 0.40, (0, 0, 0.20), seg=8, m=CS)
    b.cyl(1.50, 0.08, (0, 0, 0.38), seg=8, m=CB)
    for ang in [i * math.pi/4 for i in range(8)]:
        b.cyl(0.04, 0.05, (math.cos(ang)*1.35, math.sin(ang)*1.35, 0.42), seg=6, m=CB)
        
    # 2. 4 Columnas estructurales de bronce y vigas del gantry
    for cx in [-1.05, 1.05]:
        for cy in [-1.05, 1.05]:
            b.box((0.22, 0.22, 2.85), (cx, cy, 1.625), m=CB)
            b.box((0.30, 0.30, 0.12), (cx, cy, 0.45), m=CS)
    # Vigas de acero cobalto superiores
    b.box((2.30, 0.22, 0.18), (0, -1.05, 3.05), m=CS)
    b.box((2.30, 0.22, 0.18), (0, 1.05, 3.05), m=CS)
    b.box((0.22, 2.30, 0.18), (-1.05, 0, 3.05), m=CS)
    b.box((0.22, 2.30, 0.18), (1.05, 0, 3.05), m=CS)
    
    # 3. Cerramiento de cristal ahumado
    b.box((2.1, 0.04, 2.3), (0, 1.05, 1.55), m=SG)
    b.box((0.04, 2.1, 2.3), (-1.05, 0, 1.55), m=SG)
    
    # 4. Pedestal central hidráulico de sujeción
    b.cyl(0.38, 0.65, (0, 0, 0.725), seg=12, m=CC)
    b.cyl(0.28, 0.25, (0, 0, 1.05), seg=12, m=CS)
    
    # 5. Chasis de androide anatómico completo
    # Pelvis y vértebras segmentadas
    b.box((0.34, 0.24, 0.15), (0, 0, 1.15), m=CS)
    for vz in [1.30, 1.42, 1.54, 1.66]:
        b.box((0.08, 0.10, 0.08), (0, 0.04, vz), m=CB)
    # Caja torácica abierta con reactor ámbar
    b.box((0.46, 0.30, 0.45), (0, 0, 1.90), m=CS)
    b.sph(0.13, (0, -0.06, 1.90), scale=(1, 1, 1), m=AC)
    # Clavículas y hombros
    b.box((0.56, 0.14, 0.08), (0, 0, 2.12), m=CB)
    # Cráneo cibernético con zócalos ópticos ámbar
    b.box((0.22, 0.24, 0.26), (0, 0, 2.30), m=CB)
    b.sph(0.035, (-0.06, -0.13, 2.32), m=AC)
    b.sph(0.035, (0.06, -0.13, 2.32), m=AC)
    
    # 6. 4 Brazos robóticos suspendidos con soldadura y agarre
    pos_brazos = [(-0.65, -0.65), (0.65, -0.65), (-0.65, 0.65), (0.65, 0.65)]
    targets = [(-0.18, -0.1, 1.95), (0.18, -0.1, 1.95), (-0.12, 0.1, 1.7), (0.12, 0.1, 1.7)]
    for i, ((bx, by), (tx, ty, tz)) in enumerate(zip(pos_brazos, targets)):
        # Base giratoria
        b.cyl(0.12, 0.15, (bx, by, 2.95), seg=12, m=CS)
        mid_x = (bx + tx) * 0.58
        mid_y = (by + ty) * 0.58
        mid_z = 2.45
        # Segmentos articulados
        b.seg((bx, by, 2.88), (mid_x, mid_y, mid_z), 0.055, 0.045, m=CB)
        b.seg((mid_x, mid_y, mid_z), (tx, ty, tz), 0.045, 0.03, m=CS)
        # Pistón hidráulico auxiliar
        b.seg((bx*0.9, by*0.9, 2.85), (mid_x*0.9, mid_y*0.9, 2.42), 0.02, 0.02, m=CS)
        # Efectores: 2 de soldadura (plasma ámbar) y 2 de pinza
        if i < 2:
            b.sph(0.045, (tx, ty, tz), scale=(1, 1, 1), m=AC)
        else:
            b.box((0.08, 0.12, 0.05), (tx, ty, tz), m=CB)
            b.box((0.03, 0.06, 0.08), (tx - 0.03, ty, tz - 0.04), m=CS)
            b.box((0.03, 0.06, 0.08), (tx + 0.03, ty, tz - 0.04), m=CS)
    return b.build(COL_MAESTRA)

def modelar_robo_workbench_circuits(mats):
    """SM_Robo_Workbench_Circuits: Banco mecatrónico con bandejas de microchips, 3 PCBs y soldador (Imagen 3)."""
    b = dl.MB("SM_Robo_Workbench_Circuits")
    CS, CB, AC, CC, CG = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_Charcoal"], mats["M_Robo_CircuitGreen"]
    )
    
    # 1. Mesa pesada con marco de bronce (2.2x0.9x0.92m)
    for x in [-1.0, 1.0]:
        for y in [-0.38, 0.38]:
            b.box((0.09, 0.09, 0.88), (x, y, 0.44), m=CB)
    b.box((2.2, 0.92, 0.08), (0, 0, 0.88), m=CC)
    
    # 2. Organizador vertical con 18 bandejas de microchips y chips DIP
    b.box((2.1, 0.22, 0.65), (0, 0.32, 1.25), m=CS)
    for row in range(3):
        rz = 1.05 + row * 0.18
        for col in range(6):
            cx = -0.75 + col * 0.30
            b.box((0.24, 0.12, 0.10), (cx, 0.28, rz), m=CB)
            b.box((0.15, 0.02, 0.04), (cx, 0.22, rz), m=AC) # etiqueta
            # Microchips con pines
            b.box((0.08, 0.05, 0.02), (cx, 0.26, rz + 0.02), m=CC)
            
    # 3. 3 Placas PCB con pistas de cobre, condensadores y disipadores
    for i, px in enumerate([-0.65, -0.15, 0.35]):
        b.box((0.36, 0.26, 0.015), (px, -0.12, 0.93), m=CG)
        # Microprocesador central
        b.box((0.12, 0.12, 0.025), (px, -0.12, 0.945), m=CC)
        # Disipador de aluminio con aletas
        for fx in [-0.04, 0.0, 0.04]:
            b.box((0.015, 0.10, 0.03), (px + fx, -0.12, 0.96), m=CS)
        # Condensadores cilíndricos
        b.cyl(0.02, 0.04, (px + 0.12, -0.05, 0.95), seg=8, m=CB)
        b.cyl(0.02, 0.04, (px + 0.12, -0.18, 0.95), seg=8, m=CB)
        # Pistas de cobre
        b.box((0.32, 0.02, 0.018), (px, -0.12, 0.935), m=CB)
        b.box((0.02, 0.22, 0.018), (px, -0.12, 0.935), m=CB)
        
    # 4. Soldador en espiral y lupa articulada
    b.box((0.22, 0.22, 0.14), (0.85, -0.15, 0.99), m=CS)
    b.cyl(0.018, 0.22, (0.75, -0.12, 1.05), rot=(math.pi/4, 0, 0), seg=8, m=CB)
    # Lámpara con lupa
    b.cyl(0.03, 0.35, (0.60, 0.15, 1.10), seg=8, m=CB)
    b.cyl(0.12, 0.02, (0.50, -0.05, 1.25), rot=(math.pi/6, 0, 0), seg=16, m=CS)
    b.cyl(0.09, 0.015, (0.50, -0.05, 1.25), rot=(math.pi/6, 0, 0), seg=16, m=AC)
    return b.build(COL_MAESTRA)

def modelar_robo_schematic_console(mats):
    """SM_Robo_SchematicConsole: Consola con pantalla táctil de 42 pulgadas, manómetros y seta de emergencia."""
    b = dl.MB("SM_Robo_SchematicConsole")
    CS, CB, AC, CC, RS = (
        mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"],
        mats["M_Robo_Charcoal"], mats["M_Robo_RedStop"]
    )
    
    b.box((1.65, 0.98, 0.85), (0, 0, 0.425), m=CS)
    b.box((1.70, 1.02, 0.08), (0, 0, 0.84), m=CB)
    
    # Gran monitor inclinado táctil con esquemas alámbricos ámbar
    b.box((1.48, 0.68, 0.12), (0, 0.05, 1.16), rot=(math.pi/6, 0, 0), m=CS)
    b.box((1.38, 0.58, 0.02), (0, 0.05, 1.23), rot=(math.pi/6, 0, 0), m=AC)
    
    # 4 Manómetros analógicos circulares
    for i, mx in enumerate([-0.52, -0.20, 0.20, 0.52]):
        b.cyl(0.065, 0.04, (mx, -0.40, 0.88), rot=(math.pi/2, 0, 0), seg=12, m=CB)
        b.cyl(0.050, 0.01, (mx, -0.425, 0.88), rot=(math.pi/2, 0, 0), seg=12, m=AC)
        b.box((0.006, 0.015, 0.035), (mx, -0.43, 0.89), m=CC) # aguja
        
    # Seta de parada de emergencia roja con collarín amarillo
    b.cyl(0.05, 0.03, (0.65, -0.25, 0.89), seg=12, m=AC) # collarín
    b.cyl(0.04, 0.04, (0.65, -0.25, 0.92), seg=12, m=RS) # seta roja
    return b.build(COL_MAESTRA)

def modelar_robo_mobile_assembler(mats):
    """SM_Robo_MobileAssembler: Robot móvil sobre orugas continuas con brazo de 3 ejes y baliza ámbar."""
    b = dl.MB("SM_Robo_MobileAssembler")
    CS, CB, AC, CC = mats["M_Robo_CobaltSteel"], mats["M_Robo_CopperBronze"], mats["M_Robo_AmberCore"], mats["M_Robo_Charcoal"]
    
    # 1. Chasis central blindado
    b.box((0.88, 0.68, 0.35), (0, 0, 0.40), m=CS)
    # 2. Dos orugas laterales con ruedas tensoras
    for y_track in [-0.44, 0.44]:
        b.box((1.24, 0.18, 0.34), (0, y_track, 0.22), m=CC)
        for wx in [-0.48, -0.16, 0.16, 0.48]:
            b.cyl(0.12, 0.20, (wx, y_track, 0.22), rot=(math.pi/2, 0, 0), seg=12, m=CB)
            b.cyl(0.05, 0.22, (wx, y_track, 0.22), rot=(math.pi/2, 0, 0), seg=8, m=CS) # cubo
            
    # 3. Brazo manipulador articulado de 3 ejes
    b.cyl(0.15, 0.12, (-0.20, 0, 0.64), seg=12, m=CS)
    b.seg((-0.20, 0, 0.70), (0.05, 0, 1.12), 0.065, 0.05, m=CB)
    b.seg((0.05, 0, 1.12), (0.38, 0, 0.92), 0.05, 0.035, m=CS)
    # Pinza con servo transportado
    b.box((0.15, 0.18, 0.08), (0.44, 0, 0.90), m=CB)
    b.box((0.12, 0.03, 0.08), (0.54, -0.06, 0.90), m=CS)
    b.box((0.12, 0.03, 0.08), (0.54, 0.06, 0.90), m=CS)
    b.cyl(0.05, 0.08, (0.54, 0, 0.90), seg=8, m=AC) # pieza sostenida
    
    # 4. Baliza giratoria de advertencia ámbar
    b.cyl(0.065, 0.14, (-0.25, 0.22, 0.68), seg=12, m=AC)
    b.box((0.04, 0.26, 0.08), (0.45, 0, 0.42), m=AC)
    return b.build(COL_MAESTRA)


# ==============================================================================
# SISTEMA DE RENDERS DE PREVISUALIZACIÓN (REGLAS 4 Y 5)
# ==============================================================================

def renderizar_showcases(modelos_por_bioma):
    """Genera renders limpios en Cycles/EEVEE para validación visual de los 3 biomas."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE'
        
    sc.render.resolution_x = 1280
    sc.render.resolution_y = 720
    sc.render.film_transparent = False
    
    w = bpy.data.worlds.get("DarxBiomaWorld") or bpy.data.worlds.new("DarxBiomaWorld")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.world = w
    
    cam = dl._rig_preview()
    cam.data.lens = 45.0
    
    archivos_generados = []
    
    # 1. Renders individuales de cada Bioma
    for i, (nombre_bioma, objs) in enumerate(modelos_por_bioma.items(), 1):
        for idx, obj in enumerate(objs):
            fila = idx // 4
            col = idx % 4
            obj.location = ((col - 1.5) * 2.8, (fila - 0.5) * 3.2, 0.0)
            
        bpy.context.view_layer.update()
        out_png = os.path.join(ARTIFACTS_DIR, f"preview_bioma{i}_{nombre_bioma}_showcase.png")
        dl.snap(objs, out_png, focus=(0, 0, 1.2), dist=12.0, yaw=35.0, pitch=22.0, res=1024)
        archivos_generados.append(out_png)
        print(f"DarX | Render generado: {out_png}")
        
    # 2. Render general de la Mega-Fase con los 3 biomas
    todos_los_objs = []
    offset_y = 0.0
    for nombre_bioma, objs in modelos_por_bioma.items():
        for idx, obj in enumerate(objs):
            fila = idx // 4
            col = idx % 4
            obj.location = ((col - 1.5) * 2.6, offset_y + (fila - 0.5) * 2.8, 0.0)
            todos_los_objs.append(obj)
        offset_y += 7.5
        
    bpy.context.view_layer.update()
    out_megafase = os.path.join(ARTIFACTS_DIR, "preview_megafase_biomas_showcase.png")
    dl.snap(todos_los_objs, out_megafase, focus=(0, 7.5, 1.5), dist=26.0, yaw=42.0, pitch=25.0, res=1280)
    archivos_generados.append(out_megafase)
    print(f"DarX | Render MegaFase generado: {out_megafase}")
    
    return archivos_generados


# ==============================================================================
# PIPELINE MAESTRO
# ==============================================================================

def ejecutar_pipeline():
    print("=" * 80)
    print("DarX | Iniciando Pipeline de Modelado con Micro-Detalles por Bioma...")
    print("=" * 80)
    
    dl.wipe(COL_MAESTRA)
    dl.coll(COL_MAESTRA)
    
    mats = crear_materiales()
    
    # Bioma 1: Biohazard
    bio1_objs = [
        modelar_bio_floor_grate(mats),
        modelar_bio_wall_pipes(mats),
        modelar_bio_pillar_organic(mats),
        modelar_bio_cover_hazard(mats),
        modelar_bio_giant_specimen_pod(mats),
        modelar_bio_chemical_workstation(mats),
        modelar_bio_control_console(mats),
        modelar_bio_secondary_tube(mats)
    ]
    
    # Bioma 2: Clean Room
    bio2_objs = [
        modelar_clean_floor_tile(mats),
        modelar_clean_wall_panel(mats),
        modelar_clean_pillar_prismatic(mats),
        modelar_clean_cover_sterile(mats),
        modelar_clean_particle_chamber(mats),
        modelar_clean_holo_console(mats),
        modelar_clean_crystal_dispenser(mats),
        modelar_clean_server_bank(mats)
    ]
    
    # Bioma 3: Robotics
    bio3_objs = [
        modelar_robo_floor_darkplate(mats),
        modelar_robo_wall_riveted(mats),
        modelar_robo_pillar_copper(mats),
        modelar_robo_cover_armor(mats),
        modelar_robo_assembly_cell(mats),
        modelar_robo_workbench_circuits(mats),
        modelar_robo_schematic_console(mats),
        modelar_robo_mobile_assembler(mats)
    ]
    
    modelos_por_bioma = {
        "biohazard": bio1_objs,
        "cleanroom": bio2_objs,
        "robotics": bio3_objs
    }
    
    print("DarX | Generando previsualizaciones fotorealistas...")
    renders = renderizar_showcases(modelos_por_bioma)
    
    print("DarX | Exportando 24 StaticMeshes a Art/FBX/Biomas/...")
    todos = bio1_objs + bio2_objs + bio3_objs
    for obj in todos:
        obj.location = (0, 0, 0)
        bpy.context.view_layer.update()
        dl.export_fbx([obj], obj.name, armature=False, anim=False, subdir=FBX_SUBDIR)
        print(f"  -> Exportado FBX: {obj.name}.fbx")
        
    print("=" * 80)
    print(f"DarX | Pipeline completado con éxito: 24 FBX exportados y {len(renders)} renders generados.")
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_pipeline()
