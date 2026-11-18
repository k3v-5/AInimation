import bpy
import bmesh
import os
import sys
from mathutils import Vector

def analizar_fbx_suelo():
    fbx_path = r"E:\Darx_Proyect\Art\FBX\Biomas\SM_Clean_Floor_Tile.fbx"
    if not os.path.exists(fbx_path):
        print(f"No existe: {fbx_path}")
        return

    # Limpiar escena
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if not obj:
        print("No se importo ningun objeto")
        return

    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    print(f"=== ANALISIS DE {obj.name} ===")
    print(f"Total Vertices: {len(bm.verts)}")
    print(f"Total Caras: {len(bm.faces)}")

    # Buscar caras con normales hacia +Z (caras del suelo mirando arriba)
    caras_up = [f for f in bm.faces if f.normal.z > 0.9]
    print(f"Caras mirando hacia arriba (+Z): {len(caras_up)}")

    # Agrupar por coordenada Z
    z_grupos = {}
    for f in caras_up:
        z_prom = round(sum(v.co.z for v in f.verts) / len(f.verts), 5)
        mat_idx = f.material_index
        mat_name = obj.data.materials[mat_idx].name if mat_idx < len(obj.data.materials) else "None"
        if z_prom not in z_grupos:
            z_grupos[z_prom] = []
        z_grupos[z_prom].append({
            "mat": mat_name,
            "area": round(f.calc_area(), 5),
            "centro": [round(c, 4) for c in f.calc_center_bounds()]
        })

    print("\n--- DISTRIBUCION DE CARAS SUPERIORES POR ALTURA Z ---")
    for z_val in sorted(z_grupos.keys()):
        caras = z_grupos[z_val]
        mats = set(c["mat"] for c in caras)
        print(f"Z = {z_val*100.0:.2f} cm | Caras: {len(caras)} | Materiales: {list(mats)}")
        for c in caras:
            print(f"   Mat: {c['mat']}, Area: {c['area']}, Centro: {c['centro']}")

    # Analizar si hay caras o volumenes que se solapan (z-fighting)
    # Por ejemplo, si dos caras de diferente material estan separadas por menos de 2 mm (0.002 m)
    claves_z = sorted(z_grupos.keys())
    print("\n--- ANALISIS DE RIESGO DE Z-FIGHTING ENTRE PLANOS ---")
    for i in range(len(claves_z)):
        for j in range(i + 1, len(claves_z)):
            diff_cm = (claves_z[j] - claves_z[i]) * 100.0
            if diff_cm <= 1.0: # menos de 1 cm
                mats_i = set(c["mat"] for c in z_grupos[claves_z[i]])
                mats_j = set(c["mat"] for c in z_grupos[claves_z[j]])
                print(f"ALERTA Z-FIGHTING: Z={claves_z[i]*100.0:.3f}cm ({mats_i}) vs Z={claves_z[j]*100.0:.3f}cm ({mats_j}) -> Separacion: {diff_cm*10.0:.2f} mm!")

if __name__ == "__main__":
    analizar_fbx_suelo()
