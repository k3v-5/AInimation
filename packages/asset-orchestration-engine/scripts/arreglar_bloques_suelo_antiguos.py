"""arreglar_bloques_suelo_antiguos.py — Erradica coplanaridad en SM_Bloque_Biotech_Drenaje y SM_Bloque_Robotica_Rejilla."""

import bpy
import bmesh
import math
import os
import sys

RAIZ_BLENDER = r"E:/Darx_Proyect/Art/Blender"
if RAIZ_BLENDER not in sys.path:
    sys.path.append(RAIZ_BLENDER)

import darx_lib as dl

FBX_DIR = r"E:/Darx_Proyect/Art/FBX/Biomas"
COL_BIOMAS = "DARX_Biomas_Estructuras"

def crear_materiales():
    m = {}
    m["M_Robo_Obsidian"] = dl.mat("M_Robo_Obsidian", (0.02, 0.02, 0.02), rough=0.35, metal=0.90)
    m["M_Robo_Chrome"] = dl.mat("M_Robo_Chrome", (0.95, 0.95, 0.98), rough=0.04, metal=0.98)
    m["M_Robo_Copper"] = dl.mat("M_Robo_Copper", (0.80, 0.45, 0.18), rough=0.25, metal=0.95)
    m["M_Robo_Glass"] = dl.mat("M_Robo_Glass", (0.10, 0.12, 0.15), rough=0.05, metal=0.10)
    m["M_Robo_Core"] = dl.mat("M_Robo_Core", (1.0, 0.60, 0.05), rough=0.10, emis=(1.0, 0.60, 0.05), emis_str=4.0)
    m["M_Robo_Hazard"] = dl.mat("M_Robo_Hazard", (0.95, 0.65, 0.02), rough=0.30, metal=0.10)
    
    m["M_Lab_Dark"] = dl.mat("M_Lab_Dark", (0.03, 0.03, 0.035), rough=0.50, metal=0.90)
    m["M_Bio_Chitin"] = dl.mat("M_Bio_Chitin", (0.08, 0.03, 0.03), rough=0.70, metal=0.05)
    m["M_Bio_Acid"] = dl.mat("M_Bio_Acid", (0.05, 0.96, 0.12), rough=0.15, emis=(0.05, 0.96, 0.12), emis_str=3.5)
    return m

def arreglar_bloque_biotech_drenaje(mats):
    """SM_Bloque_Biotech_Drenaje con foso profundo y rejilla sin coplanaridad."""
    b = dl.MB("SM_Bloque_Biotech_Drenaje")
    DARK, CHITIN = mats["M_Lab_Dark"], mats["M_Bio_Chitin"]
    
    # 1. Base estructural
    b.box((1.0, 1.0, 0.85), (0, 0, 0.425), m=DARK)
    # 2. Marco superior rebajado
    b.box((0.98, 0.98, 0.12), (0, 0, 0.91), m=DARK)
    # 3. Foso profundo interior (Z_top = 0.86, separado 14 cm de la superficie)
    b.box((0.80, 0.80, 0.04), (0, 0, 0.84), m=DARK)
    # 4. Rejilla protectora elevada (Z_top = 0.99, separada 13 cm del foso y 1 cm bajo el marco)
    for dx in [-0.3, -0.1, 0.1, 0.3]:
        b.box((0.04, 0.84, 0.03), (dx, 0, 0.975), m=CHITIN)
    return b.build(COL_BIOMAS)

def arreglar_bloque_robotica_rejilla(mats):
    """SM_Bloque_Robotica_Rejilla sin caras coplanares entre cristal y marco."""
    b = dl.MB("SM_Bloque_Robotica_Rejilla")
    OBSIDIAN, CHROME, COPPER, GLASS, CORE = (
        mats["M_Robo_Obsidian"], mats["M_Robo_Chrome"], mats["M_Robo_Copper"],
        mats["M_Robo_Glass"], mats["M_Robo_Core"]
    )
    
    # 1. Marco exterior
    b.box((1.0, 1.0, 0.96), (0, 0, 0.48), m=OBSIDIAN)
    # 2. Ventanas de cristal
    b.cyl(0.40, 0.05, (0, -0.46, 0.5), rot=(math.pi/2, 0, 0), seg=20, m=GLASS)
    b.cyl(0.40, 0.05, (0, 0.46, 0.5), rot=(math.pi/2, 0, 0), seg=20, m=GLASS)
    # 3. Turbinas interiores
    b.cyl(0.12, 0.06, (0, -0.42, 0.5), rot=(math.pi/2, 0, 0), seg=16, m=COPPER)
    b.cyl(0.12, 0.06, (0, 0.42, 0.5), rot=(math.pi/2, 0, 0), seg=16, m=COPPER)
    # 4. Tubos laterales
    for dx in [-0.38, 0.38]:
        b.cyl(0.028, 0.78, (dx, -0.45, 0.5), seg=10, m=GLASS)
        b.cyl(0.012, 0.68, (dx, -0.45, 0.5), seg=8, m=CORE)
    return b.build(COL_BIOMAS)

def ejecutar():
    print("=== ARREGLANDO BLOQUES ANTIGUOS COPLANARES ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    c = dl.coll(COL_BIOMAS)
    mats = crear_materiales()
    
    objs = [
        arreglar_bloque_biotech_drenaje(mats),
        arreglar_bloque_robotica_rejilla(mats)
    ]
    
    for obj in objs:
        ruta_fbx = os.path.join(FBX_DIR, f"{obj.name}.fbx")
        dl.export_fbx(obj, ruta_fbx)
        print(f"Exportado: {ruta_fbx}")

if __name__ == "__main__":
    ejecutar()
