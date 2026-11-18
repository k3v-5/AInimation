import bpy
import bmesh
import os
import glob

def auditar_todas_las_mallas_suelo():
    patrones = [
        r"E:\Darx_Proyect\Art\FBX\Biomas\*Floor*.fbx",
        r"E:\Darx_Proyect\Art\FBX\Biomas\*Rejilla*.fbx",
        r"E:\Darx_Proyect\Art\FBX\Biomas\*Drenaje*.fbx",
        r"E:\Darx_Proyect\Art\FBX\Biomas\*Resonador*.fbx"
    ]
    ficheros = []
    for p in patrones:
        ficheros.extend(glob.glob(p))

    print(f"=== AUDITANDO {len(ficheros)} MALLAS DE SUELO FBX ===")

    for fbx_path in ficheros:
        nom = os.path.basename(fbx_path)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        try:
            bpy.ops.import_scene.fbx(filepath=fbx_path)
        except Exception as e:
            print(f"Error cargando {nom}: {e}")
            continue

        obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
        if not obj:
            continue

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Caras normales +Z
        caras_up = [f for f in bm.faces if f.normal.z > 0.85]
        z_dict = {}
        for f in caras_up:
            z_val = round(sum(v.co.z for v in f.verts) / len(f.verts), 4)
            mat_idx = f.material_index
            mat_name = obj.data.materials[mat_idx].name if mat_idx < len(obj.data.materials) else "None"
            if z_val not in z_dict:
                z_dict[z_val] = []
            z_dict[z_val].append((mat_name, f.calc_area(), f.calc_center_bounds()))

        print(f"\n>> MALLA: {nom} ({len(caras_up)} caras hacia +Z)")
        coplanar_conflict = False
        for z_val, caras in sorted(z_dict.items()):
            mats = set(c[0] for c in caras)
            if len(mats) > 1:
                coplanar_conflict = True
                print(f"   [!] COPLANARIDAD EXACTA en Z={z_val*100:.2f}cm: {len(caras)} caras con materiales {list(mats)}")
            else:
                print(f"       Z={z_val*100:.2f}cm: {len(caras)} caras | Material: {list(mats)}")

        # Distancia entre niveles consecutivos
        z_levels = sorted(z_dict.keys())
        for i in range(len(z_levels)-1):
            dz = (z_levels[i+1] - z_levels[i]) * 100.0
            if dz < 0.8: # menos de 8 mm
                print(f"   [!] Z-FIGHTING PROBABLE: Distancia entre Z={z_levels[i]*100:.2f}cm y Z={z_levels[i+1]*100:.2f}cm es solo {dz*10:.2f} mm!")

if __name__ == "__main__":
    auditar_todas_las_mallas_suelo()
