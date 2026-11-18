"""
================================================================================
PROCESADOR CINEMATOGRÁFICO DE MAPAS PBR (2048x2048) - UNREAL ENGINE 5
Proyecto: Game (F:/Dev/Game)
Módulo: Art/Textures/Modular/procesar_mapas_pbr_cinematograficos.py
================================================================================
Convierte los 10 masters generados en suites completas de texturas PBR (40 mapas):
- BaseColor (sRGB 2048x2048)
- Normal (Tangent Space DirectX para UE5: R=X, G=-Y, B=Z)
- ORM (R=AO, G=Roughness, B=Metallic)
- Emissive (HDR sRGB)
"""

import os
import shutil
import numpy as np
import cv2
from PIL import Image

TARGET_DIR = r"F:\Dev\Game\Art\Textures\Modular"
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
RES = 2048

PACK_SOURCES = {
    # 5 Packs Oxidados / Percutidos
    "T_Derelict_Rust_Plates": os.path.join(ARTIFACT_DIR, "test_rust_plates_1791317706227.jpg"),
    "T_Battered_Armor_Impacts": os.path.join(ARTIFACT_DIR, "tex_armor_impacts_1791317799235.jpg"),
    "T_Corroded_Acid_Pipes": os.path.join(ARTIFACT_DIR, "tex_acid_pipes_1791317877123.jpg"),
    "T_Decayed_Rusted_Grating": os.path.join(ARTIFACT_DIR, "tex_decayed_grating_1791318002850.jpg"),
    "T_Scorched_Plasma_Slag": os.path.join(ARTIFACT_DIR, "tex_plasma_slag_1791318083011.jpg"),
    
    # 5 Packs Mapas de Lujo (Tier 2 Crucero 'Celestia' / Art Déco)
    "T_Luxury_Marble_Gold_Inlay": os.path.join(ARTIFACT_DIR, "tex_marble_gold_1791318168899.jpg"),
    "T_Luxury_Walnut_Wood_Panels": os.path.join(ARTIFACT_DIR, "tex_walnut_panels_1791318309176.jpg"),
    "T_Luxury_ArtDeco_Gilded_Brass": os.path.join(ARTIFACT_DIR, "tex_gilded_brass_1791318404714.jpg"),
    "T_Luxury_Quilted_Velvet_Leather": os.path.join(ARTIFACT_DIR, "tex_quilted_leather_1791318496728.jpg"),
    "T_Luxury_Smoked_Glass_Lattice": os.path.join(ARTIFACT_DIR, "tex_smoked_glass_1791318649622.jpg"),
}

def compute_normal_map(height_map: np.ndarray, strength: float = 3.5) -> np.ndarray:
    """Calcula el Normal Map en Tangent Space DirectX para UE5 (G invertido)."""
    sobel_x = cv2.Sobel(height_map, cv2.CV_32F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(height_map, cv2.CV_32F, 0, 1, ksize=5)
    
    dx = -sobel_x * strength
    dy = sobel_y * strength  # DirectX: invertido respecto a OpenGL
    dz = np.ones_like(height_map, dtype=np.float32)
    
    length = np.sqrt(dx**2 + dy**2 + dz**2) + 1e-6
    nx = dx / length
    ny = dy / length
    nz = dz / length
    
    r = ((nx * 0.5 + 0.5) * 255.0).astype(np.uint8)
    g = ((ny * 0.5 + 0.5) * 255.0).astype(np.uint8)
    b = ((nz * 0.5 + 0.5) * 255.0).astype(np.uint8)
    
    return np.stack([r, g, b], axis=-1)

def compute_ambient_occlusion(height_map: np.ndarray) -> np.ndarray:
    """Calcula mapa de oclusión ambiental física basado en valles y concavidades."""
    blur_large = cv2.GaussianBlur(height_map, (31, 31), 8)
    diff = height_map - blur_large
    ao = np.clip(0.75 + diff * 1.5, 0.2, 1.0)
    return (ao * 255.0).astype(np.uint8)

def process_pack(pack_name: str, src_path: str):
    print(f"\n---> Procesando pack PBR: {pack_name} desde {os.path.basename(src_path)}")
    assert os.path.exists(src_path), f"Error: no existe {src_path}"
    
    # Cargar y redimensionar imagen base a 2048x2048
    img = Image.open(src_path).convert("RGB")
    if img.size != (RES, RES):
        img = img.resize((RES, RES), Image.Resampling.LANCZOS)
    
    rgb_arr = np.array(img, dtype=np.float32) / 255.0
    gray = cv2.cvtColor((rgb_arr * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    hsv = cv2.cvtColor((rgb_arr * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    
    # Derivación específica de Height, Roughness, Metallic y Emissive
    emissive = np.zeros((RES, RES, 3), dtype=np.uint8)
    
    if pack_name == "T_Derelict_Rust_Plates":
        # Óxido vs chapa pintada
        # Pintura teal: tono verde-azul, saturación moderada. Óxido: tono naranja/marrón
        is_rust = (hsv[..., 0] < 30) & (hsv[..., 1] > 60) & (gray < 0.6)
        is_rivet_or_weld = (gray > 0.65) | (cv2.Laplacian(gray, cv2.CV_32F) > 0.15)
        
        height = gray * 0.6 + (1.0 - is_rust.astype(np.float32)) * 0.35
        height = cv2.GaussianBlur(height, (3, 3), 1.0)
        
        metallic = np.where(is_rust, 0.05, 0.85).astype(np.float32)
        roughness = np.where(is_rust, 0.88, 0.42).astype(np.float32)
        normal = compute_normal_map(height, strength=4.5)
        
    elif pack_name == "T_Battered_Armor_Impacts":
        # Acero de blindaje percutido, cráteres y fracturas
        is_crater_pit = (gray < 0.25)
        is_shrapnel_burr = (gray > 0.60)
        
        height = gray.copy()
        height[is_crater_pit] *= 0.3
        height[is_shrapnel_burr] += 0.2
        
        metallic = np.where(is_crater_pit, 0.2, 0.95).astype(np.float32)
        roughness = np.where(is_crater_pit, 0.78, np.where(is_shrapnel_burr, 0.18, 0.35)).astype(np.float32)
        normal = compute_normal_map(height, strength=5.2)
        
    elif pack_name == "T_Corroded_Acid_Pipes":
        # Tuberías de cuproníquel, pátina verdigris y ácido verde fosforescente
        is_green_acid = (hsv[..., 0] >= 35) & (hsv[..., 0] <= 85) & (hsv[..., 1] > 120) & (hsv[..., 2] > 100)
        is_pipe_metal = (hsv[..., 0] < 30) & (hsv[..., 1] > 70) & (~is_green_acid)
        is_verdigris = (hsv[..., 0] >= 85) & (hsv[..., 0] <= 115) & (hsv[..., 1] > 80)
        
        height = gray.copy()
        height[is_pipe_metal] += 0.25
        height[is_green_acid] -= 0.15
        
        metallic = np.where(is_pipe_metal, 0.90, 0.05).astype(np.float32)
        roughness = np.where(is_green_acid, 0.08, np.where(is_pipe_metal, 0.32, 0.82)).astype(np.float32)
        
        # Emissive ácido
        acid_glow = np.clip(is_green_acid.astype(np.float32) * (hsv[..., 2] / 255.0), 0.0, 1.0)
        emissive[..., 0] = (acid_glow * 40).astype(np.uint8)
        emissive[..., 1] = (acid_glow * 255).astype(np.uint8)
        emissive[..., 2] = (acid_glow * 30).astype(np.uint8)
        normal = compute_normal_map(height, strength=4.8)
        
    elif pack_name == "T_Decayed_Rusted_Grating":
        # Rejilla de acero con barras y huecos oscuros
        is_void = (gray < 0.18)
        is_polished_tread = (gray > 0.55) & (~is_void)
        
        height = np.where(is_void, 0.0, gray + 0.3).astype(np.float32)
        metallic = np.where(is_void, 0.0, np.where(is_polished_tread, 0.95, 0.65)).astype(np.float32)
        roughness = np.where(is_void, 1.0, np.where(is_polished_tread, 0.22, 0.80)).astype(np.float32)
        normal = compute_normal_map(height, strength=5.5)
        
    elif pack_name == "T_Scorched_Plasma_Slag":
        # Escoria de plasma incandescente
        is_molten_core = (rgb_arr[..., 0] > 0.7) & (rgb_arr[..., 1] > 0.4) & (rgb_arr[..., 2] < 0.4)
        is_cool_slag = (gray < 0.25) & (~is_molten_core)
        
        height = gray.copy()
        height[is_molten_core] -= 0.25
        height[is_cool_slag] += 0.30
        
        metallic = np.where(is_molten_core | is_cool_slag, 0.05, 0.92).astype(np.float32)
        roughness = np.where(is_molten_core, 0.12, np.where(is_cool_slag, 0.80, 0.35)).astype(np.float32)
        
        # Emissive núcleo de plasma incandescente
        core_intensity = np.clip(np.maximum(0.0, rgb_arr[..., 0] - 0.4) * 2.5 * is_molten_core, 0.0, 1.0)
        emissive[..., 0] = (core_intensity * 255).astype(np.uint8)
        emissive[..., 1] = (core_intensity * 140).astype(np.uint8)
        emissive[..., 2] = (core_intensity * 20).astype(np.uint8)
        normal = compute_normal_map(height, strength=4.5)
        
    elif pack_name == "T_Luxury_Marble_Gold_Inlay":
        # Mármol blanco Calacatta con incrustaciones de oro 24k
        is_gold = (rgb_arr[..., 0] > 0.6) & (rgb_arr[..., 1] > 0.45) & (rgb_arr[..., 2] < 0.35)
        
        height = np.where(is_gold, 0.62, 0.50 + gray * 0.08).astype(np.float32)
        metallic = np.where(is_gold, 0.98, 0.02).astype(np.float32)
        roughness = np.where(is_gold, 0.18, 0.08).astype(np.float32)
        normal = compute_normal_map(height, strength=3.0)
        
    elif pack_name == "T_Luxury_Walnut_Wood_Panels":
        # Boiserie de nogal con molduras de latón
        is_brass_strip = (rgb_arr[..., 0] > 0.7) & (rgb_arr[..., 1] > 0.6) & (rgb_arr[..., 2] < 0.4)
        
        height = gray.copy()
        height[is_brass_strip] += 0.18
        
        metallic = np.where(is_brass_strip, 0.96, 0.01).astype(np.float32)
        roughness = np.where(is_brass_strip, 0.16, 0.30).astype(np.float32)
        normal = compute_normal_map(height, strength=3.8)
        
    elif pack_name == "T_Luxury_ArtDeco_Gilded_Brass":
        # Relieve arquitectónico de latón dorado
        is_crevice = (gray < 0.35)
        height = gray.copy()
        
        metallic = np.where(is_crevice, 0.65, 0.98).astype(np.float32)
        roughness = np.where(is_crevice, 0.58, 0.20).astype(np.float32)
        normal = compute_normal_map(height, strength=4.2)
        
    elif pack_name == "T_Luxury_Quilted_Velvet_Leather":
        # Cuero acolchado Chesterfield azul noche con botones dorados
        is_button = (rgb_arr[..., 0] > 0.55) & (rgb_arr[..., 1] > 0.42) & (rgb_arr[..., 2] < 0.3) & (gray > 0.35)
        
        height = gray.copy()
        height[is_button] += 0.28
        
        metallic = np.where(is_button, 0.98, 0.0).astype(np.float32)
        roughness = np.where(is_button, 0.14, 0.40).astype(np.float32)
        normal = compute_normal_map(height, strength=3.6)
        
    elif pack_name == "T_Luxury_Smoked_Glass_Lattice":
        # Celosía de latón sobre vidrio ahumado con retroiluminación ámbar
        is_brass_grill = (rgb_arr[..., 0] > 0.45) & (rgb_arr[..., 1] > 0.35) & (gray > 0.35)
        is_amber_glow = (rgb_arr[..., 0] > 0.5) & (rgb_arr[..., 1] > 0.3) & (~is_brass_grill)
        
        height = np.where(is_brass_grill, 0.75, 0.45).astype(np.float32)
        height = cv2.GaussianBlur(height, (3, 3), 1.0)
        
        metallic = np.where(is_brass_grill, 0.95, 0.05).astype(np.float32)
        roughness = np.where(is_brass_grill, 0.22, 0.06).astype(np.float32)
        
        # Emissive backlight cálido
        glow_val = np.clip(is_amber_glow.astype(np.float32) * (rgb_arr[..., 0]), 0.0, 1.0)
        emissive[..., 0] = (glow_val * 240).astype(np.uint8)
        emissive[..., 1] = (glow_val * 160).astype(np.uint8)
        emissive[..., 2] = (glow_val * 45).astype(np.uint8)
        normal = compute_normal_map(height, strength=4.0)

    # Ambient Occlusion
    ao = compute_ambient_occlusion(height)
    
    # Empaquetado ORM (R=AO, G=Roughness, B=Metallic)
    orm = np.zeros((RES, RES, 3), dtype=np.uint8)
    orm[..., 0] = ao
    orm[..., 1] = (np.clip(roughness, 0.0, 1.0) * 255.0).astype(np.uint8)
    orm[..., 2] = (np.clip(metallic, 0.0, 1.0) * 255.0).astype(np.uint8)
    
    # Exportar mapas
    base_color_img = img
    normal_img = Image.fromarray(normal)
    orm_img = Image.fromarray(orm)
    emissive_img = Image.fromarray(emissive)
    
    files = {
        f"{pack_name}_BaseColor.png": base_color_img,
        f"{pack_name}_Normal.png": normal_img,
        f"{pack_name}_ORM.png": orm_img,
        f"{pack_name}_Emissive.png": emissive_img,
    }
    
    for filename, pimg in files.items():
        dst_path = os.path.join(TARGET_DIR, filename)
        pimg.save(dst_path, format="PNG")
        art_path = os.path.join(ARTIFACT_DIR, filename)
        pimg.save(art_path, format="PNG")
        print(f"  [GUARDADO] {filename}")

def main():
    print("=" * 80)
    print("PROCESADOR CINEMATOGRÁFICO DE MAPAS PBR (40 MAPAS A 2048x2048)")
    print("=" * 80)
    os.makedirs(TARGET_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    
    for pack_name, src_path in PACK_SOURCES.items():
        process_pack(pack_name, src_path)
        
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO EXITOSAMENTE PARA TODOS LOS 10 PACKS (40 MAPAS PBR)")
    print("=" * 80)

if __name__ == "__main__":
    main()
