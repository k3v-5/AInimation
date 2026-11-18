# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Sintetizador Procedural de Texturas PBR de Ultra-Alta Calidad (NumPy + SciPy)
# Astra Hazard - Pack Derelict/Oxidado (5) y Pack Luxury Art Déco (5)
# Generación de superficies físicas continuas, relieves tridimensionales auténticos,
# degradados térmicos reales, micro-grano orgánico y normales tangent-space para UE5.

import os
import shutil
import time
import numpy as np
import scipy.ndimage as ndi
from PIL import Image

PROJECT_ROOT = r"F:\Dev\Game"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

RES = 2048

# ==============================================================================
# UTILIDADES MATEMÁTICAS PROCEDURALES
# ==============================================================================

def fbm_fft(res, beta=2.2, seed=42):
    """Genera ruido fractal continuo (fBm) mediante síntesis espectral FFT."""
    rng = np.random.default_rng(seed)
    kx = np.fft.fftfreq(res)
    ky = np.fft.fftfreq(res)
    KX, KY = np.meshgrid(kx, ky)
    k_sq = KX**2 + KY**2
    k_sq[0, 0] = 1.0
    power = 1.0 / (k_sq ** (beta / 2.0))
    power[0, 0] = 0.0
    
    phases = rng.uniform(0, 2 * np.pi, (res, res))
    amplitudes = rng.rayleigh(1.0, (res, res)) * np.sqrt(power)
    noise_freq = amplitudes * (np.cos(phases) + 1j * np.sin(phases))
    noise = np.real(np.fft.ifft2(noise_freq))
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
    return noise.astype(np.float32)

def multi_octave_noise(res, seeds=(101, 202, 303), weights=(0.55, 0.35, 0.10), betas=(1.8, 2.4, 3.2)):
    total = np.zeros((res, res), dtype=np.float32)
    for s, w, b in zip(seeds, weights, betas):
        total += w * fbm_fft(res, beta=b, seed=s)
    total = (total - total.min()) / (total.max() - total.min() + 1e-8)
    return total

def height_to_normal(height_array, strength=4.8):
    """Convierte heightmap float32 a mapa de normales tangent-space (+X der, -Y abajo, +Z arr)."""
    gy, gx = np.gradient(height_array)
    gx = -gx * strength
    gy = gy * strength
    gz = np.ones_like(gx, dtype=np.float32)
    
    norm = np.sqrt(gx**2 + gy**2 + gz**2)
    norm = np.maximum(norm, 1e-6)
    nx = gx / norm
    ny = gy / norm
    nz = gz / norm
    
    r = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    g = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    b = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=-1), mode="RGB")

def compute_cavity_ao(height_array, radius=12.0):
    blurred = ndi.gaussian_filter(height_array, sigma=radius)
    diff = height_array - blurred
    ao = np.clip(1.0 + diff * 3.5, 0.0, 1.0)
    ao = ndi.gaussian_filter(ao, sigma=1.5)
    return ao.astype(np.float32)

def pack_orm(ao_array, roughness_array, metallic_array):
    r = np.clip(ao_array * 255.0, 0, 255).astype(np.uint8)
    g = np.clip(roughness_array * 255.0, 0, 255).astype(np.uint8)
    b = np.clip(metallic_array * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=-1), mode="RGB")

def save_and_export(prefix, base_rgb, height, roughness, metallic, emissive_rgb=None, norm_strength=4.8):
    normal_img = height_to_normal(height, strength=norm_strength)
    ao = compute_cavity_ao(height, radius=14.0)
    orm_img = pack_orm(ao, roughness, metallic)
    
    base_u8 = np.clip(base_rgb * 255.0, 0, 255).astype(np.uint8)
    base_img = Image.fromarray(base_u8, mode="RGB")
    
    if emissive_rgb is not None:
        emi_u8 = np.clip(emissive_rgb * 255.0, 0, 255).astype(np.uint8)
        emi_img = Image.fromarray(emi_u8, mode="RGB")
    else:
        emi_img = Image.new("RGB", (RES, RES), (0, 0, 0))
        
    for name, img in [("BaseColor", base_img), ("Normal", normal_img), ("ORM", orm_img), ("Emissive", emi_img)]:
        fpath = os.path.join(OUTPUT_DIR, f"{prefix}_{name}.png")
        img.save(fpath, optimize=True)
        shutil.copy(fpath, os.path.join(ARTIFACT_DIR, f"{prefix}_{name}.png"))
    print(f"  [OK] Exportados mapas para: {prefix}")

# ==============================================================================
# 1. T_Derelict_Rust_Plates
# ==============================================================================
def generate_derelict_rust_plates():
    print("[1/10] Sintetizando T_Derelict_Rust_Plates...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    seam_x = np.abs(x_idx - res / 2)
    seam_y = np.abs(y_idx - res / 2)
    seam_dist = np.minimum(seam_x, seam_y)
    
    height = np.ones((res, res), dtype=np.float32) * 0.70
    seam_depth = np.clip(seam_dist / 16.0, 0.0, 1.0)
    height *= (0.4 + 0.6 * seam_depth)
    
    rivet_mask = np.zeros((res, res), dtype=np.float32)
    rivet_spacing = 160
    rivet_r = 18.0
    for rx in range(80, res, rivet_spacing):
        for ry in [50, 970, 1070, 1990]:
            dist = np.sqrt((x_idx - rx)**2 + (y_idx - ry)**2)
            c = np.clip(1.0 - dist / rivet_r, 0.0, 1.0)
            rivet_mask = np.maximum(rivet_mask, c)
            
    rivet_profile = np.sin(rivet_mask * (np.pi / 2)) * 0.28
    height += rivet_profile
    
    rust_fbm = multi_octave_noise(res, seeds=(11, 22, 33), weights=(0.55, 0.35, 0.10), betas=(1.8, 2.3, 3.2))
    micro_pit = fbm_fft(res, beta=1.4, seed=44)
    
    peel_mask = np.clip((rust_fbm - 0.46) * 12.0, 0.0, 1.0)
    peel_edge = np.exp(-((rust_fbm - 0.46) / 0.04)**2)
    
    height -= peel_mask * 0.25
    height += peel_edge * 0.08
    height -= peel_mask * micro_pit * 0.10
    
    drip_noise = fbm_fft(res, beta=2.5, seed=55)
    drip_accum = np.zeros((res, res), dtype=np.float32)
    for ry in [50, 1070]:
        y_rel = y_idx - ry
        y_valid = (y_rel > 0) & (y_rel < 420)
        decay = np.exp(-y_rel / 160.0)
        streak = np.sin(x_idx * 0.08 + drip_noise * 6.0) ** 6
        drip_accum += (y_valid * decay * streak).astype(np.float32) * 0.7
    drip_accum = np.clip(drip_accum, 0.0, 1.0)
    
    c_paint = np.array([0.22, 0.28, 0.25], dtype=np.float32)
    c_paint_light = np.array([0.30, 0.36, 0.32], dtype=np.float32)
    paint_color = c_paint + (c_paint_light - c_paint) * rust_fbm[..., None] * 0.5
    
    c_rust_dark = np.array([0.24, 0.11, 0.05], dtype=np.float32)
    c_rust_mid = np.array([0.52, 0.22, 0.06], dtype=np.float32)
    c_rust_bright = np.array([0.76, 0.35, 0.08], dtype=np.float32)
    
    rust_blend = np.clip((rust_fbm - 0.46) / 0.35, 0.0, 1.0)[..., None]
    rust_color = c_rust_dark + (c_rust_mid - c_rust_dark) * rust_blend
    rust_color += (c_rust_bright - c_rust_mid) * (micro_pit[..., None] * rust_blend * 0.8)
    
    base_rgb = paint_color * (1.0 - peel_mask[..., None]) + rust_color * peel_mask[..., None]
    base_rgb = base_rgb * (1.0 - drip_accum[..., None] * 0.6) + c_rust_mid * (drip_accum[..., None] * 0.6)
    
    rivet_crest = np.clip((rivet_mask - 0.7) / 0.3, 0.0, 1.0)[..., None]
    c_bare_metal = np.array([0.65, 0.68, 0.70], dtype=np.float32)
    base_rgb = base_rgb * (1.0 - rivet_crest) + c_bare_metal * rivet_crest
    
    roughness = 0.55 * (1.0 - peel_mask) + 0.92 * peel_mask
    roughness = np.clip(roughness - rivet_crest.squeeze() * 0.35, 0.15, 0.95)
    metallic = 0.05 * (1.0 - peel_mask) + 0.02 * peel_mask + rivet_crest.squeeze() * 0.90
    metallic = np.clip(metallic, 0.0, 1.0)
    
    save_and_export("T_Derelict_Rust_Plates", base_rgb, height, roughness, metallic, norm_strength=4.8)

# ==============================================================================
# 2. T_Battered_Armor_Impacts (BLINDAJE DE COMBATE CON IMPACTOS ORGÁNICOS)
# ==============================================================================
def generate_battered_armor_impacts():
    print("[2/10] Sintetizando T_Battered_Armor_Impacts (Mamparo blindado con daño balístico real)...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    # Placa base con grano de forja y micro-abolladuras
    armor_noise = multi_octave_noise(res, seeds=(21, 22, 23), weights=(0.55, 0.30, 0.15), betas=(1.8, 2.4, 3.2))
    micro_dents = fbm_fft(res, beta=1.3, seed=25)
    
    # 2 Paneles de blindaje divididos por costura central biselada con placas de unión
    seam_v = np.abs(x_idx - res / 2.0)
    seam_h = np.abs(y_idx - res / 2.0)
    seam_dist = np.minimum(seam_v, seam_h)
    
    height = 0.68 + (armor_noise - 0.5) * 0.04
    # Ranura entre placas
    seam_groove = np.clip(seam_dist / 14.0, 0.0, 1.0)
    height *= (0.65 + 0.35 * seam_groove)
    
    # Filas de tornillos pesados de cabeza hexagonal en los marcos
    bolt_mask = np.zeros((res, res), dtype=np.float32)
    for bx in [80, 960, 1080, 1960]:
        for by in range(80, res, 160):
            d = np.sqrt((x_idx - bx)**2 + (y_idx - by)**2)
            bolt_mask = np.maximum(bolt_mask, np.clip(1.0 - d / 18.0, 0.0, 1.0))
    height += np.sin(bolt_mask * (np.pi / 2)) * 0.25
    
    # 7 Impactos Balísticos Orgánicos (deformación continua por ruido turbulento)
    crater_dep = np.zeros((res, res), dtype=np.float32)
    lip_raise = np.zeros((res, res), dtype=np.float32)
    soot_mask = np.zeros((res, res), dtype=np.float32)
    stress_cracks = np.zeros((res, res), dtype=np.float32)
    
    impacts = [
        (620, 580, 190.0, 1.1),
        (1450, 480, 220.0, 1.2),
        (950, 1180, 260.0, 1.3),
        (1580, 1420, 170.0, 1.0),
        (420, 1550, 210.0, 1.15),
        (1200, 1720, 150.0, 0.9),
        (820, 320, 130.0, 0.8),
    ]
    
    for cx, cy, r_imp, intens in impacts:
        dx = x_idx - cx
        dy = y_idx - cy
        dist = np.sqrt(dx**2 + dy**2)
        
        # Distorsión puramente orgánica usando ruido turbulento local
        turb = armor_noise * 80.0 + fbm_fft(res, beta=1.5, seed=int(cx + cy)) * 60.0
        eff_r = dist + turb
        
        # Hundimiento del cráter
        c_in = np.clip(1.0 - eff_r / r_imp, 0.0, 1.0) ** 1.7
        crater_dep = np.maximum(crater_dep, c_in * intens)
        
        # Rebabas alzadas de acero desplazado (pico irregular)
        rim_dist = np.abs(eff_r - r_imp)
        lip = np.exp(-(rim_dist / 32.0)**2) * (0.6 + 0.4 * micro_dents)
        lip_raise = np.maximum(lip_raise, lip * intens)
        
        # Dispersión de hollín y pólvora quemada
        soot = np.clip(1.0 - eff_r / (r_imp * 2.2), 0.0, 1.0) ** 1.3
        soot_mask = np.maximum(soot_mask, soot * intens)
        
        # Grietas de estrés radial fracturadas
        ang = np.arctan2(dy, dx)
        ray = np.abs(np.sin(ang * 5.0 + turb * 0.1))
        crack = (ray < 0.12) & (dist > r_imp * 0.5) & (dist < r_imp * 1.8)
        stress_cracks = np.maximum(stress_cracks, crack.astype(np.float32) * 0.15)
        
    # Arañazos de rebote y metralla (ricochets)
    ricochet_noise = np.abs(np.sin(x_idx * 0.06 + y_idx * 0.03 + armor_noise * 10.0)) ** 24
    ricochets = ricochet_noise * (armor_noise > 0.4).astype(np.float32) * 0.25
    
    height -= crater_dep * 0.52
    height += lip_raise * 0.35
    height -= stress_cracks * 0.12
    height -= ricochets * 0.08
    
    # BaseColor: Acero gris azulado pesado naval
    c_base_steel = np.array([0.22, 0.24, 0.27], dtype=np.float32)
    base_rgb = np.ones((res, res, 3), dtype=np.float32) * c_base_steel
    base_rgb += (armor_noise[..., None] - 0.5) * 0.04
    
    # Tizne negro y propelente quemado
    c_soot = np.array([0.07, 0.07, 0.08], dtype=np.float32)
    base_rgb = base_rgb * (1.0 - soot_mask[..., None] * 0.75) + c_soot * (soot_mask[..., None] * 0.75)
    
    # Tinte térmico continuo sutil en los bordes del cráter
    c_straw = np.array([0.65, 0.50, 0.26], dtype=np.float32)
    c_blue = np.array([0.20, 0.35, 0.60], dtype=np.float32)
    tint_w = np.clip((lip_raise - 0.1) / 0.5, 0.0, 1.0)[..., None]
    base_rgb += (c_straw * 0.5 + c_blue * 0.5) * (tint_w * 0.4)
    
    # Rebabas y arañazos de acero brillante
    c_bright_steel = np.array([0.78, 0.80, 0.84], dtype=np.float32)
    bright_w = np.clip((lip_raise - 0.3) / 0.45, 0.0, 1.0)[..., None]
    bright_w = np.maximum(bright_w, ricochets[..., None] * 3.0)
    base_rgb = base_rgb * (1.0 - bright_w) + c_bright_steel * bright_w
    
    # Roughness & Metallic
    metallic = 0.92 * (1.0 - crater_dep * 0.8)
    roughness = 0.38 + 0.10 * micro_dents
    roughness = roughness * (1.0 - bright_w.squeeze() * 0.65) # Rebabas pulidas
    roughness = np.clip(roughness + crater_dep * 0.50, 0.14, 0.92) # Fondo mate
    
    save_and_export("T_Battered_Armor_Impacts", base_rgb, height, roughness, metallic, norm_strength=5.2)

# ==============================================================================
# 3. T_Corroded_Acid_Pipes
# ==============================================================================
def generate_corroded_acid_pipes():
    print("[3/10] Sintetizando T_Corroded_Acid_Pipes...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    pipe_w = res / 4.0
    pipe_rel_x = (x_idx % pipe_w) - (pipe_w / 2.0)
    pipe_r = pipe_w * 0.44
    
    cyl_arg = np.maximum(0.0, pipe_r**2 - pipe_rel_x**2)
    pipe_cyl_height = np.sqrt(cyl_arg) / pipe_r
    pipe_mask = (np.abs(pipe_rel_x) < pipe_r).astype(np.float32)
    
    height = pipe_cyl_height * 0.70 * pipe_mask
    
    clamp_y1 = np.abs(y_idx - res * 0.30) < 32
    clamp_y2 = np.abs(y_idx - res * 0.70) < 32
    clamp_mask = (clamp_y1 | clamp_y2).astype(np.float32)
    height += clamp_mask * 0.18
    
    acid_fbm = multi_octave_noise(res, seeds=(31, 32, 33), weights=(0.5, 0.35, 0.15), betas=(1.6, 2.2, 3.0))
    crust_noise = fbm_fft(res, beta=1.3, seed=35)
    
    patina_mask = np.clip((acid_fbm - 0.42) * 8.0, 0.0, 1.0)
    height += patina_mask * crust_noise * 0.20
    
    fissure_noise = np.abs(np.sin(x_idx * 0.04 + acid_fbm * 12.0) + np.cos(y_idx * 0.04))
    leak_fissure = (fissure_noise < 0.08) & (patina_mask > 0.6) & (pipe_mask > 0.5)
    leak_mask = ndi.gaussian_filter(leak_fissure.astype(np.float32), sigma=2.5)
    
    c_bronze = np.array([0.38, 0.28, 0.18], dtype=np.float32)
    c_bronze_dark = np.array([0.22, 0.16, 0.10], dtype=np.float32)
    base_rgb = c_bronze_dark + (c_bronze - c_bronze_dark) * pipe_cyl_height[..., None]
    
    c_verdigris_base = np.array([0.14, 0.56, 0.46], dtype=np.float32)
    c_verdigris_bright = np.array([0.22, 0.74, 0.58], dtype=np.float32)
    verdigris_color = c_verdigris_base + (c_verdigris_bright - c_verdigris_base) * crust_noise[..., None]
    
    c_sulfur = np.array([0.76, 0.74, 0.22], dtype=np.float32)
    sulfur_mask = np.clip((acid_fbm - 0.62) * 10.0, 0.0, 1.0)[..., None]
    patina_color = verdigris_color * (1.0 - sulfur_mask) + c_sulfur * sulfur_mask
    
    base_rgb = base_rgb * (1.0 - patina_mask[..., None]) + patina_color * patina_mask[..., None]
    
    c_clamp = np.array([0.20, 0.22, 0.24], dtype=np.float32)
    base_rgb = base_rgb * (1.0 - clamp_mask[..., None]) + c_clamp * clamp_mask[..., None]
    
    c_acid_glow = np.array([0.15, 1.0, 0.35], dtype=np.float32)
    emissive_rgb = c_acid_glow * leak_mask[..., None] * 4.5
    base_rgb = base_rgb * (1.0 - leak_mask[..., None]) + c_acid_glow * leak_mask[..., None]
    
    roughness = 0.35 * (1.0 - patina_mask) + 0.88 * patina_mask
    metallic = 0.85 * (1.0 - patina_mask) * (1.0 - clamp_mask) + 0.65 * clamp_mask + 0.05 * patina_mask
    
    save_and_export("T_Corroded_Acid_Pipes", base_rgb, height, roughness, metallic, emissive_rgb, norm_strength=5.0)

# ==============================================================================
# 4. T_Decayed_Rusted_Grating
# ==============================================================================
def generate_decayed_rusted_grating():
    print("[4/10] Sintetizando T_Decayed_Rusted_Grating...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    u = (x_idx + y_idx) * 0.7071
    v = (x_idx - y_idx) * 0.7071
    
    pitch = 120.0
    u_rel = np.abs((u % pitch) - pitch / 2.0)
    v_rel = np.abs((v % pitch) - pitch / 2.0)
    
    bar_thick = 22.0
    bar_dist_max = np.maximum(
        np.maximum(0.0, bar_thick - u_rel),
        np.maximum(0.0, bar_thick - v_rel)
    )
    
    height = np.sin(np.clip(bar_dist_max / bar_thick, 0.0, 1.0) * (np.pi / 2)) * 0.75
    
    frame_dist = np.minimum(np.minimum(x_idx, res - x_idx), np.minimum(y_idx, res - y_idx))
    frame_mask = (frame_dist < 80).astype(np.float32)
    height = height * (1.0 - frame_mask) + (0.75 + 0.08 * np.clip((80 - frame_dist) / 80, 0, 1)) * frame_mask
    
    collapse_noise = fbm_fft(res, beta=2.0, seed=41)
    hole_dist = np.sqrt((x_idx - res * 0.52)**2 + (y_idx - res * 0.48)**2)
    hole_radius = 420.0 * (1.0 + 0.45 * np.sin(collapse_noise * 14.0))
    hole_mask = (hole_dist < hole_radius).astype(np.float32)
    hole_soft = np.clip((hole_dist - hole_radius + 40) / 60.0, 0.0, 1.0)
    height *= hole_soft
    
    rust_fbm = multi_octave_noise(res, seeds=(42, 43, 44), weights=(0.5, 0.35, 0.15), betas=(1.7, 2.3, 3.1))
    crest_wear = np.clip((height - 0.58) / 0.16, 0.0, 1.0) * (1.0 - hole_mask)
    
    c_abyss = np.array([0.04, 0.04, 0.05], dtype=np.float32)
    base_rgb = np.ones((res, res, 3), dtype=np.float32) * c_abyss
    
    c_rust_dark = np.array([0.22, 0.10, 0.05], dtype=np.float32)
    c_rust_bright = np.array([0.65, 0.28, 0.08], dtype=np.float32)
    bar_rust = c_rust_dark + (c_rust_bright - c_rust_dark) * rust_fbm[..., None]
    
    c_bright_tread = np.array([0.72, 0.74, 0.76], dtype=np.float32)
    bar_color = bar_rust * (1.0 - crest_wear[..., None]) + c_bright_tread * crest_wear[..., None]
    
    grate_presence = np.clip(height / 0.15, 0.0, 1.0)[..., None]
    base_rgb = base_rgb * (1.0 - grate_presence) + bar_color * grate_presence
    
    roughness = 0.90 * np.ones((res, res), dtype=np.float32)
    roughness = roughness * (1.0 - crest_wear * 0.72)
    
    metallic = 0.05 * np.ones((res, res), dtype=np.float32)
    metallic = metallic * (1.0 - crest_wear) + 0.95 * crest_wear
    
    save_and_export("T_Decayed_Rusted_Grating", base_rgb, height, roughness, metallic, norm_strength=5.2)

# ==============================================================================
# 5. T_Scorched_Plasma_Slag (BRECHA DE PLASMA MULTI-FOCAL ORGÁNICA)
# ==============================================================================
def generate_scorched_plasma_slag():
    print("[5/10] Sintetizando T_Scorched_Plasma_Slag (Brecha de plasma continua, flujo térmico)...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    # Mamparo de refuerzo con ranuras de panel y remaches
    rib_mask = (np.abs((x_idx % 512) - 256) < 20).astype(np.float32)
    height = 0.65 + rib_mask * 0.10
    
    plasma_noise = multi_octave_noise(res, seeds=(51, 52, 53), weights=(0.55, 0.30, 0.15), betas=(1.8, 2.4, 3.2))
    
    # Múltiples centros de plasma conectados orgánicamente (área amplia de quemado térmico)
    foci = [
        (750, 700, 480.0, 1.2),
        (1350, 950, 520.0, 1.1),
        (900, 1400, 440.0, 1.0),
        (1450, 1500, 380.0, 0.95),
    ]
    
    heat_field = np.zeros((res, res), dtype=np.float32)
    slag_core = np.zeros((res, res), dtype=np.float32)
    
    for fx, fy, r_p, intens in foci:
        dx = x_idx - fx
        dy = y_idx - fy
        dist = np.sqrt(dx**2 + dy**2)
        dist_turb = dist + (plasma_noise - 0.5) * 320.0
        
        h_val = np.clip(1.0 - dist_turb / r_p, 0.0, 1.0)
        heat_field = np.maximum(heat_field, h_val * intens)
        
        core_val = np.clip(1.0 - dist_turb / (r_p * 0.44), 0.0, 1.0) ** 1.8
        slag_core = np.maximum(slag_core, core_val * intens)
        
    # Gotas esféricas de escoria salpicada
    droplets_mask = np.zeros((res, res), dtype=np.float32)
    rng = np.random.default_rng(777)
    for _ in range(160):
        fx, fy, r_p, _ = foci[rng.integers(0, len(foci))]
        ang = rng.uniform(0, 2*np.pi)
        rad = rng.uniform(40, r_p * 1.1)
        bx = fx + rad * np.cos(ang)
        by = fy + rad * np.sin(ang)
        dr = rng.uniform(6.0, 26.0)
        d = np.sqrt((x_idx - bx)**2 + (y_idx - by)**2)
        droplets_mask = np.maximum(droplets_mask, np.clip(1.0 - d / dr, 0.0, 1.0))
        
    droplets_3d = np.sin(droplets_mask * (np.pi / 2)) * 0.22
    
    height -= slag_core * 0.45
    bubble_noise = fbm_fft(res, beta=1.2, seed=59)
    height += (slag_core * bubble_noise * 0.20) + droplets_3d
    
    # Paleta de temple continuo
    c_titanium = np.array([0.26, 0.28, 0.30], dtype=np.float32)
    c_straw = np.array([0.84, 0.70, 0.35], dtype=np.float32)
    c_copper = np.array([0.68, 0.30, 0.45], dtype=np.float32)
    c_purple = np.array([0.42, 0.14, 0.58], dtype=np.float32)
    c_cobalt = np.array([0.12, 0.32, 0.85], dtype=np.float32)
    c_iceblue = np.array([0.45, 0.72, 0.90], dtype=np.float32)
    c_charcoal = np.array([0.07, 0.07, 0.08], dtype=np.float32)
    
    base_rgb = np.ones((res, res, 3), dtype=np.float32) * c_titanium
    h = heat_field[..., None]
    
    z1 = np.clip((h - 0.05) / 0.18, 0.0, 1.0)
    col_z1 = c_titanium + (c_straw - c_titanium) * z1
    z2 = np.clip((h - 0.23) / 0.18, 0.0, 1.0)
    col_z2 = col_z1 + (c_purple - c_straw) * z2
    z3 = np.clip((h - 0.41) / 0.18, 0.0, 1.0)
    col_z3 = col_z2 + (c_cobalt - c_purple) * z3
    z4 = np.clip((h - 0.59) / 0.18, 0.0, 1.0)
    col_z4 = col_z3 + (c_iceblue - c_cobalt) * z4
    z5 = np.clip((h - 0.77) / 0.18, 0.0, 1.0)
    base_rgb = col_z4 + (c_charcoal - c_iceblue) * z5
    
    # Emissive: Fusión incandescente residual
    c_ember = np.array([1.0, 0.45, 0.08], dtype=np.float32)
    c_core_white = np.array([1.0, 0.92, 0.65], dtype=np.float32)
    
    ember_val = np.clip((slag_core - 0.45) / 0.50, 0.0, 1.0)
    emissive_rgb = (c_ember + (c_core_white - c_ember) * ember_val[..., None]) * (ember_val[..., None] * 5.5)
    base_rgb = base_rgb * (1.0 - ember_val[..., None] * 0.8) + c_ember * (ember_val[..., None] * 0.8)
    
    metallic = 0.90 * (1.0 - slag_core) + 0.10 * slag_core
    roughness = 0.32 + 0.15 * (heat_field > 0.1)
    roughness = np.clip(roughness * (1.0 - slag_core) + 0.88 * slag_core, 0.15, 0.95)
    
    save_and_export("T_Scorched_Plasma_Slag", base_rgb, height, roughness, metallic, emissive_rgb, norm_strength=5.0)

# ==============================================================================
# 6. T_Luxury_Marble_Gold_Inlay (BALDOSAS SÓLIDAS DE MÁRMOL Y MOSAICO DE ORO)
# ==============================================================================
def generate_luxury_marble_gold_inlay():
    print("[6/10] Sintetizando T_Luxury_Marble_Gold_Inlay (Mármol Carrara y mosaico dorado biselado)...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    warp_x = fbm_fft(res, beta=2.2, seed=61)
    warp_y = fbm_fft(res, beta=2.2, seed=62)
    
    u_warp = (x_idx / res) * 3.5 + (warp_x - 0.5) * 1.2
    v_warp = (y_idx / res) * 3.5 + (warp_y - 0.5) * 1.2
    
    vein_1 = np.abs(np.sin(u_warp * 3.0 + v_warp * 2.2 + fbm_fft(res, beta=1.8, seed=63) * 3.5))
    vein_2 = np.abs(np.sin(u_warp * 1.5 - v_warp * 3.2 + fbm_fft(res, beta=1.6, seed=65) * 2.5))
    vein_intensity = np.clip(1.0 - (vein_1 * vein_2) ** 0.25, 0.0, 1.0)
    
    # Mosaico Art Déco continuo: bandas doradas sólidas de 32px y medallones
    tile_w = res / 2.0
    u_tile = np.abs((x_idx % tile_w) - tile_w / 2.0)
    v_tile = np.abs((y_idx % tile_w) - tile_w / 2.0)
    
    gold_mask = np.zeros((res, res), dtype=np.float32)
    
    # Bandas perimetrales anchas sólidas
    border_dist = np.maximum(u_tile, v_tile)
    gold_mask = np.maximum(gold_mask, np.clip(1.0 - np.abs(border_dist - (tile_w / 2.0 - 45)) / 26.0, 0.0, 1.0))
    
    # Diamante central ancho
    diamond_dist = (u_tile + v_tile)
    gold_mask = np.maximum(gold_mask, np.clip(1.0 - np.abs(diamond_dist - 260) / 28.0, 0.0, 1.0))
    
    # Medallón de roseta central sólido
    c_dist = np.sqrt(u_tile**2 + v_tile**2)
    gold_mask = np.maximum(gold_mask, np.clip(1.0 - c_dist / 64.0, 0.0, 1.0))
    
    # Borde biselado del oro embutido
    gold_profile = np.sin(gold_mask * (np.pi / 2)) * 0.24
    gold_edge = np.exp(-((gold_mask - 0.5) / 0.18)**2) * 0.09
    
    height = 0.70 + gold_profile - gold_edge
    
    # BaseColor: Mármol Carrara blanco lechoso con vetas grises/oro
    c_marble_pure = np.array([0.94, 0.94, 0.93], dtype=np.float32)
    c_vein_grey = np.array([0.60, 0.62, 0.65], dtype=np.float32)
    c_vein_gold = np.array([0.80, 0.68, 0.40], dtype=np.float32)
    
    vein_color = c_vein_grey * 0.65 + c_vein_gold * 0.35
    marble_rgb = c_marble_pure * (1.0 - vein_intensity[..., None] * 0.58) + vein_color * (vein_intensity[..., None] * 0.58)
    
    # Oro pulido 24k
    c_gold_base = np.array([0.96, 0.82, 0.30], dtype=np.float32)
    c_gold_bright = np.array([1.0, 0.92, 0.56], dtype=np.float32)
    gold_rgb = c_gold_base + (c_gold_bright - c_gold_base) * (gold_profile[..., None] * 1.8)
    
    g_w = gold_mask[..., None]
    base_rgb = marble_rgb * (1.0 - g_w) + gold_rgb * g_w
    base_rgb *= (1.0 - gold_edge[..., None] * 2.2) # Grout shadow
    
    roughness = 0.08 * (1.0 - gold_mask) + 0.14 * gold_mask
    metallic = 0.0 * (1.0 - gold_mask) + 1.0 * gold_mask
    
    save_and_export("T_Luxury_Marble_Gold_Inlay", base_rgb, height, roughness, metallic, norm_strength=4.6)

# ==============================================================================
# 7. T_Luxury_Walnut_Wood_Panels
# ==============================================================================
def generate_luxury_walnut_wood_panels():
    print("[7/10] Sintetizando T_Luxury_Walnut_Wood_Panels...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    u_wood = x_idx / 120.0
    v_wood = y_idx / 800.0
    warp_wood = fbm_fft(res, beta=2.4, seed=71)
    
    grain_arg = u_wood * 12.0 + np.sin(v_wood * 6.28) * 4.0 + (warp_wood - 0.5) * 14.0
    wood_rings = np.sin(grain_arg) * 0.5 + 0.5
    micro_pores = np.abs(np.sin(x_idx * 0.8 + warp_wood * 10.0)) ** 12
    
    panel_split = np.abs(x_idx - res / 2.0)
    frame_outer = np.minimum(np.minimum(x_idx, res - x_idx), np.minimum(y_idx, res - y_idx))
    molding_dist = np.minimum(frame_outer, panel_split)
    
    height = 0.50 + 0.02 * wood_rings
    molding_step = np.clip((molding_dist - 55) / 55.0, 0.0, 1.0)
    height += np.sin(molding_step * (np.pi / 2)) * 0.28
    
    brass_bead = np.exp(-((molding_dist - 55) / 10.0)**2)
    height += brass_bead * 0.16
    
    c_walnut_dark = np.array([0.18, 0.09, 0.04], dtype=np.float32)
    c_walnut_mid = np.array([0.28, 0.15, 0.08], dtype=np.float32)
    c_walnut_light = np.array([0.38, 0.22, 0.12], dtype=np.float32)
    
    wood_rgb = c_walnut_dark + (c_walnut_mid - c_walnut_dark) * wood_rings[..., None]
    wood_rgb += (c_walnut_light - c_walnut_mid) * ((warp_wood[..., None] - 0.4) * 0.6)
    wood_rgb *= (1.0 - micro_pores[..., None] * 0.25)
    
    c_brass = np.array([0.94, 0.78, 0.28], dtype=np.float32)
    b_weight = np.clip(brass_bead * 1.5, 0.0, 1.0)[..., None]
    base_rgb = wood_rgb * (1.0 - b_weight) + c_brass * b_weight
    
    roughness = 0.24 * (1.0 - brass_bead) + 0.16 * brass_bead
    metallic = 0.0 * (1.0 - brass_bead) + 0.98 * brass_bead
    
    save_and_export("T_Luxury_Walnut_Wood_Panels", base_rgb, height, roughness, metallic, norm_strength=4.8)

# ==============================================================================
# 8. T_Luxury_ArtDeco_Gilded_Brass (REFORMULADO: ESCAMAS 3D FLUTED CONTINUAS)
# ==============================================================================
def generate_luxury_artdeco_gilded_brass():
    print("[8/10] Sintetizando T_Luxury_ArtDeco_Gilded_Brass...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    scale_w = 256.0
    scale_h = 160.0
    
    fan_height_accum = np.zeros((res, res), dtype=np.float32)
    groove_mask_accum = np.zeros((res, res), dtype=np.float32)
    flute_phase_accum = np.zeros((res, res), dtype=np.float32)
    
    for row in range(-2, int(res / scale_h) + 4):
        y_center = row * scale_h
        x_offset = (row % 2) * (scale_w / 2.0)
        
        for col in range(-2, int(res / scale_w) + 4):
            cx = col * scale_w + x_offset
            cy = y_center
            dx = x_idx - cx
            dy = y_idx - cy
            dist = np.sqrt(dx**2 + dy**2)
            angle = np.arctan2(dy, dx)
            
            in_fan = (dist <= scale_w * 0.72) & (dy >= -10.0)
            if not np.any(in_fan):
                continue
                
            dome = np.sin(np.clip(1.0 - dist / (scale_w * 0.72), 0.0, 1.0) * (np.pi / 2))
            flute_angle = angle * 11.0
            flutes = np.sin(flute_angle) * 0.5 + 0.5
            rim_edge = np.exp(-((dist - scale_w * 0.70) / 8.0)**2)
            
            scale_h_total = dome * 0.45 + flutes * 0.18
            fan_height_accum = np.maximum(fan_height_accum, scale_h_total * in_fan)
            groove_mask_accum = np.maximum(groove_mask_accum, rim_edge * in_fan)
            flute_phase_accum = np.maximum(flute_phase_accum, flutes * in_fan)
            
    height = 0.35 + fan_height_accum - groove_mask_accum * 0.12
    brush_noise = fbm_fft(res, beta=1.4, seed=81)
    
    c_brass_bright = np.array([0.96, 0.84, 0.36], dtype=np.float32)
    c_brass_mid = np.array([0.88, 0.72, 0.28], dtype=np.float32)
    c_patina_groove = np.array([0.28, 0.20, 0.10], dtype=np.float32)
    
    brass_color = c_brass_mid + (c_brass_bright - c_brass_mid) * (flute_phase_accum[..., None] * 0.8)
    brass_color += (brush_noise[..., None] - 0.5) * 0.04
    
    g_w = np.clip(groove_mask_accum * 1.5, 0.0, 1.0)[..., None]
    base_rgb = brass_color * (1.0 - g_w) + c_patina_groove * g_w
    
    metallic = np.ones((res, res), dtype=np.float32) * 0.98
    roughness = 0.16 + 0.12 * (1.0 - flute_phase_accum) + 0.35 * groove_mask_accum
    roughness = np.clip(roughness, 0.14, 0.70)
    
    save_and_export("T_Luxury_ArtDeco_Gilded_Brass", base_rgb, height, roughness, metallic, norm_strength=5.0)

# ==============================================================================
# 9. T_Luxury_Quilted_Velvet_Leather (SIN WARNINGS/NANs)
# ==============================================================================
def generate_luxury_quilted_velvet_leather():
    print("[9/10] Sintetizando T_Luxury_Quilted_Velvet_Leather...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    px = 256.0
    py = 320.0
    
    u = (x_idx / px + y_idx / py)
    v = (x_idx / px - y_idx / py)
    
    u_cell = (u % 1.0) - 0.5
    v_cell = (v % 1.0) - 0.5
    
    cushion_dist = np.maximum(np.abs(u_cell), np.abs(v_cell))
    # Protección matemática contra valores negativos
    cushion_cos = np.maximum(0.0, np.cos(np.clip(cushion_dist * 2.0, 0.0, 1.0) * (np.pi / 2)))
    cushion_puff = cushion_cos ** 1.4
    height = cushion_puff * 0.65
    
    button_mask = np.zeros((res, res), dtype=np.float32)
    button_wells = np.zeros((res, res), dtype=np.float32)
    
    btn_r = 16.0
    well_r = 50.0
    for i in range(-1, int(res / px) + 3):
        for j in range(-1, int(res / py) + 3):
            centers = [(i * px, j * py), ((i + 0.5) * px, (j + 0.5) * py)]
            for bx, by in centers:
                d = np.sqrt((x_idx - bx)**2 + (y_idx - by)**2)
                b = np.clip(1.0 - d / btn_r, 0.0, 1.0)
                button_mask = np.maximum(button_mask, b)
                w = np.clip(1.0 - d / well_r, 0.0, 1.0)
                button_wells = np.maximum(button_wells, w)
                
    height -= button_wells * 0.35
    button_dome = np.sin(button_mask * (np.pi / 2)) * 0.28
    height += button_dome
    
    crease_noise = fbm_fft(res, beta=2.2, seed=91)
    creases = np.abs(np.sin(u * np.pi * 2.0 + crease_noise * 3.0)) * np.abs(np.sin(v * np.pi * 2.0))
    height += creases * 0.05 * (button_wells > 0.1)
    
    leather_grain = fbm_fft(res, beta=1.2, seed=92)
    
    c_leather_dark = np.array([0.03, 0.05, 0.10], dtype=np.float32)
    c_leather_crest = np.array([0.08, 0.14, 0.26], dtype=np.float32)
    
    leather_rgb = c_leather_dark + (c_leather_crest - c_leather_dark) * cushion_puff[..., None]
    leather_rgb += (leather_grain[..., None] - 0.5) * 0.03
    
    c_btn_gold = np.array([0.95, 0.82, 0.30], dtype=np.float32)
    b_w = np.clip(button_mask * 1.8, 0.0, 1.0)[..., None]
    base_rgb = leather_rgb * (1.0 - b_w) + c_btn_gold * b_w
    base_rgb *= (1.0 - button_wells[..., None] * 0.35 * (1.0 - b_w))
    
    roughness = 0.42 - 0.10 * cushion_puff
    roughness = roughness * (1.0 - button_mask) + 0.15 * button_mask
    metallic = 0.0 * (1.0 - button_mask) + 1.0 * button_mask
    
    save_and_export("T_Luxury_Quilted_Velvet_Leather", base_rgb, height, roughness, metallic, norm_strength=4.8)

# ==============================================================================
# 10. T_Luxury_Smoked_Glass_Lattice
# ==============================================================================
def generate_luxury_smoked_glass_lattice():
    print("[10/10] Sintetizando T_Luxury_Smoked_Glass_Lattice...")
    res = RES
    y_idx, x_idx = np.indices((res, res), dtype=np.float32)
    
    cell_s = 512.0
    u_rel = np.abs((x_idx % cell_s) - cell_s / 2.0)
    v_rel = np.abs((y_idx % cell_s) - cell_s / 2.0)
    
    box_dist = np.maximum(u_rel, v_rel)
    mullion_mask = (box_dist > (cell_s / 2.0 - 24.0)).astype(np.float32)
    
    diamond_dist = (u_rel + v_rel)
    diamond_rim = np.abs(diamond_dist - 160.0)
    diamond_mask = np.clip(1.0 - diamond_rim / 16.0, 0.0, 1.0)
    
    center_dist = np.sqrt(u_rel**2 + v_rel**2)
    rosette_mask = np.clip(1.0 - center_dist / 36.0, 0.0, 1.0)
    
    brass_lattice = np.maximum(np.maximum(mullion_mask, diamond_mask), rosette_mask)
    glass_bevel = np.clip((cell_s / 2.0 - 24.0 - box_dist) / 48.0, 0.0, 1.0)
    
    height = 0.45 + glass_bevel * 0.08
    lattice_dome = np.sin(brass_lattice * (np.pi / 2)) * 0.32
    height += lattice_dome
    
    c_smoked_glass = np.array([0.05, 0.05, 0.06], dtype=np.float32)
    c_glass_edge = np.array([0.10, 0.10, 0.12], dtype=np.float32)
    glass_rgb = c_smoked_glass + (c_glass_edge - c_smoked_glass) * (glass_bevel[..., None] * 0.5)
    
    c_brass_lattice = np.array([0.90, 0.75, 0.30], dtype=np.float32)
    c_brass_crest = np.array([0.98, 0.88, 0.45], dtype=np.float32)
    brass_rgb = c_brass_lattice + (c_brass_crest - c_brass_lattice) * (lattice_dome[..., None] * 1.5)
    
    lat_w = brass_lattice[..., None]
    base_rgb = glass_rgb * (1.0 - lat_w) + brass_rgb * lat_w
    
    c_warm_light = np.array([1.0, 0.78, 0.42], dtype=np.float32)
    backlight_glow = np.clip(1.0 - np.abs(box_dist - (cell_s / 2.0 - 64.0)) / 50.0, 0.0, 1.0)
    backlight_glow *= (1.0 - brass_lattice)
    
    emissive_rgb = c_warm_light * (backlight_glow[..., None] * 4.2)
    base_rgb += c_warm_light * (backlight_glow[..., None] * 0.25)
    
    roughness = 0.05 * (1.0 - brass_lattice) + 0.18 * brass_lattice
    metallic = 0.05 * (1.0 - brass_lattice) + 0.98 * brass_lattice
    
    save_and_export("T_Luxury_Smoked_Glass_Lattice", base_rgb, height, roughness, metallic, emissive_rgb, norm_strength=4.6)

def main():
    print("=" * 70)
    print("SÍNTESIS V4 DE ALTA FIDELIDAD: 10 PACKS PBR (40 MAPAS)")
    print("=" * 70)
    t_start = time.time()
    
    generate_derelict_rust_plates()
    generate_battered_armor_impacts()
    generate_corroded_acid_pipes()
    generate_decayed_rusted_grating()
    generate_scorched_plasma_slag()
    
    generate_luxury_marble_gold_inlay()
    generate_luxury_walnut_wood_panels()
    generate_luxury_artdeco_gilded_brass()
    generate_luxury_quilted_velvet_leather()
    generate_luxury_smoked_glass_lattice()
    
    print("=" * 70)
    print(f"COMPLETADO EXITOSAMENTE EN {time.time() - t_start:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
