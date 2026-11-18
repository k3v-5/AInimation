"""
Generador del Master Trim Sheet PBR (2048x2048) para Astra Hazard: Rescue Squad
Genera 4 mapas de textura PBR de alta fidelidad:
- T_TrimSheet_Industrial_BaseColor.png
- T_TrimSheet_Industrial_ORM.png (R=AO, G=Roughness, B=Metallic)
- T_TrimSheet_Industrial_Normal.png
- T_TrimSheet_Industrial_Emissive.png
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TEX_RES = 2048
OUT_DIR = r"f:\Dev\Game\Art\Textures\Environment"
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Generando Master Trim Sheet PBR en resolución {TEX_RES}x{TEX_RES}...")

# Inicializar buffers
# Coordenadas UV normalizadas (0 a 1)
# y=0 abajo, y=1 arriba (o Y de imagen de 0 arriba a TEX_RES abajo)
# Para trabajar en concordancia con UVs estándar de Blender/OpenGL:
# Banda A (Y_uv: 0.00 - 0.18): Franjas de Peligro (Hazard Stripes)
# Banda B (Y_uv: 0.18 - 0.40): Acero de Fuselaje / Blindaje Oscuro (Gunmetal Hull Plate)
# Banda C (Y_uv: 0.40 - 0.62): Mamparo Pintado Astra Cyan (Teal Bulkhead con desgaste)
# Banda D (Y_uv: 0.62 - 0.78): Rejilla Metálica Perforada (Industrial Floor Grate)
# Banda E (Y_uv: 0.78 - 0.90): Tuberías, Conductos y Gomas de Sellado (Corrugated Pipes & Rubber)
# Banda F (Y_uv: 0.90 - 1.00): Emisivos de Emergencia y Pantallas de Consola (Emergency Glow)

# Creamos imágenes con Pillow para dibujar formas vectoriales limpias
base_img = Image.new("RGBA", (TEX_RES, TEX_RES), (40, 42, 48, 255))
height_img = Image.new("L", (TEX_RES, TEX_RES), 128)
roughness_img = Image.new("L", (TEX_RES, TEX_RES), 128)
metallic_img = Image.new("L", (TEX_RES, TEX_RES), 200)
ao_img = Image.new("L", (TEX_RES, TEX_RES), 255)
emissive_img = Image.new("RGBA", (TEX_RES, TEX_RES), (0, 0, 0, 255))

draw_base = ImageDraw.Draw(base_img)
draw_height = ImageDraw.Draw(height_img)
draw_rough = ImageDraw.Draw(roughness_img)
draw_metal = ImageDraw.Draw(metallic_img)
draw_ao = ImageDraw.Draw(ao_img)
draw_emis = ImageDraw.Draw(emissive_img)

def uv_to_y(uv_y):
    # En imagen: Y=0 es arriba, UV=1 es arriba.
    # Por lo tanto image_y = int((1.0 - uv_y) * TEX_RES)
    return int((1.0 - uv_y) * TEX_RES)

# -------------------------------------------------------------
# 1. BANDA A: Franjas de Peligro (Hazard Stripes) [UV Y: 0.00 - 0.18]
# -------------------------------------------------------------
y_top_A = uv_to_y(0.18)
y_bot_A = uv_to_y(0.00)

# Fondo franja
draw_base.rectangle([0, y_top_A, TEX_RES, y_bot_A], fill=(235, 160, 25, 255)) # Amarillo peligro vibrante
draw_rough.rectangle([0, y_top_A, TEX_RES, y_bot_A], fill=110) # 0.43 rugosidad
draw_metal.rectangle([0, y_top_A, TEX_RES, y_bot_A], fill=40)  # Pintura sobre metal
draw_height.rectangle([0, y_top_A, TEX_RES, y_bot_A], fill=135)

# Franjas diagonales negras
stripe_w = 64
for x_start in range(-TEX_RES, TEX_RES * 2, stripe_w * 2):
    # Poligono inclinado a 45 grados
    poly = [
        (x_start, y_bot_A),
        (x_start + stripe_w, y_bot_A),
        (x_start + stripe_w + (y_bot_A - y_top_A), y_top_A),
        (x_start + (y_bot_A - y_top_A), y_top_A)
    ]
    draw_base.polygon(poly, fill=(28, 28, 32, 255))
    draw_rough.polygon(poly, fill=130)

# Bordes y remaches de la banda A
border_h = 24
# Reborde superior e inferior
draw_base.rectangle([0, y_top_A, TEX_RES, y_top_A + border_h], fill=(70, 75, 85, 255))
draw_base.rectangle([0, y_bot_A - border_h, TEX_RES, y_bot_A], fill=(70, 75, 85, 255))
draw_metal.rectangle([0, y_top_A, TEX_RES, y_top_A + border_h], fill=220)
draw_metal.rectangle([0, y_bot_A - border_h, TEX_RES, y_bot_A], fill=220)
draw_height.rectangle([0, y_top_A, TEX_RES, y_top_A + border_h], fill=160)
draw_height.rectangle([0, y_bot_A - border_h, TEX_RES, y_bot_A], fill=160)

# Pernos / remaches en la banda
bolt_spacing = 64
for x in range(32, TEX_RES, bolt_spacing):
    # Perno superior
    draw_base.ellipse([x - 6, y_top_A + 12 - 6, x + 6, y_top_A + 12 + 6], fill=(180, 185, 195, 255))
    draw_height.ellipse([x - 6, y_top_A + 12 - 6, x + 6, y_top_A + 12 + 6], fill=210)
    draw_metal.ellipse([x - 6, y_top_A + 12 - 6, x + 6, y_top_A + 12 + 6], fill=240)
    # Perno inferior
    draw_base.ellipse([x - 6, y_bot_A - 12 - 6, x + 6, y_bot_A - 12 + 6], fill=(180, 185, 195, 255))
    draw_height.ellipse([x - 6, y_bot_A - 12 - 6, x + 6, y_bot_A - 12 + 6], fill=210)
    draw_metal.ellipse([x - 6, y_bot_A - 12 - 6, x + 6, y_bot_A - 12 + 6], fill=240)

# Ranuras oscuras de bisel
draw_ao.rectangle([0, y_top_A - 3, TEX_RES, y_top_A + 3], fill=70)
draw_ao.rectangle([0, y_bot_A - 3, TEX_RES, y_bot_A + 3], fill=70)
draw_height.rectangle([0, y_top_A - 2, TEX_RES, y_top_A + 2], fill=100)


# -------------------------------------------------------------
# 2. BANDA B: Acero de Fuselaje Oscuro (Gunmetal Hull Plate) [UV Y: 0.18 - 0.40]
# -------------------------------------------------------------
y_top_B = uv_to_y(0.40)
y_bot_B = uv_to_y(0.18)

draw_base.rectangle([0, y_top_B, TEX_RES, y_bot_B], fill=(44, 48, 56, 255))
draw_rough.rectangle([0, y_top_B, TEX_RES, y_bot_B], fill=95)   # Metal semipulido ~0.37
draw_metal.rectangle([0, y_top_B, TEX_RES, y_bot_B], fill=225) # Muy metálico
draw_height.rectangle([0, y_top_B, TEX_RES, y_bot_B], fill=140)

# Dividir en 4 paneles grandes de 512px con costuras biseladas
panel_w = 512
for px in range(0, TEX_RES, panel_w):
    # Hendidura de costura vertical
    draw_base.rectangle([px, y_top_B, px + 8, y_bot_B], fill=(24, 26, 30, 255))
    draw_height.rectangle([px, y_top_B, px + 8, y_bot_B], fill=105)
    draw_ao.rectangle([px - 4, y_top_B, px + 12, y_bot_B], fill=60)
    
    # Subpanel central en cada placa con reborde reforzado
    pad = 32
    p_x0 = px + pad
    p_x1 = px + panel_w - pad
    p_y0 = y_top_B + pad
    p_y1 = y_bot_B - pad
    draw_base.rectangle([p_x0, p_y0, p_x1, p_y1], outline=(58, 64, 74, 255), width=6)
    draw_height.rectangle([p_x0, p_y0, p_x1, p_y1], outline=165, width=6)
    
    # Pernos en las 4 esquinas del subpanel
    for bx, by in [(p_x0 + 16, p_y0 + 16), (p_x1 - 16, p_y0 + 16), (p_x0 + 16, p_y1 - 16), (p_x1 - 16, p_y1 - 16)]:
        draw_base.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(170, 175, 185, 255))
        draw_height.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=215)
        draw_metal.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=240)


# -------------------------------------------------------------
# 3. BANDA C: Mamparo Pintado Astra Corp (Teal Bulkhead) [UV Y: 0.40 - 0.62]
# -------------------------------------------------------------
y_top_C = uv_to_y(0.62)
y_bot_C = uv_to_y(0.40)

draw_base.rectangle([0, y_top_C, TEX_RES, y_bot_C], fill=(28, 78, 92, 255)) # Azul verdoso corporativo
draw_rough.rectangle([0, y_top_C, TEX_RES, y_bot_C], fill=120)  # Pintura mate ~0.47
draw_metal.rectangle([0, y_top_C, TEX_RES, y_bot_C], fill=45)   # No metálico superficial
draw_height.rectangle([0, y_top_C, TEX_RES, y_bot_C], fill=145)

# Paneles reforzados y marcos biselados
for px in range(0, TEX_RES, 256):
    # Separador vertical metálico
    draw_base.rectangle([px, y_top_C, px + 12, y_bot_C], fill=(38, 42, 48, 255))
    draw_metal.rectangle([px, y_top_C, px + 12, y_bot_C], fill=210)
    draw_height.rectangle([px, y_top_C, px + 12, y_bot_C], fill=165)
    draw_ao.rectangle([px - 4, y_top_C, px + 16, y_bot_C], fill=75)

# Franja de señalización de rescate superior
draw_base.rectangle([0, y_top_C + 16, TEX_RES, y_top_C + 48], fill=(220, 225, 235, 255))
draw_rough.rectangle([0, y_top_C + 16, TEX_RES, y_top_C + 48], fill=90)
draw_height.rectangle([0, y_top_C + 16, TEX_RES, y_top_C + 48], fill=155)

# Textos stencil / marcas corporativas simuladas con bloques geométricos
for px in range(64, TEX_RES, 512):
    # Cuadro de stencil de advertencia
    draw_base.rectangle([px, y_top_C + 20, px + 140, y_top_C + 44], fill=(18, 48, 58, 255))
    # Pequeños bloques simulando texto "ASTRA-01 // HAZARD"
    for cx in range(px + 8, px + 130, 16):
        draw_base.rectangle([cx, y_top_C + 26, cx + 10, y_top_C + 38], fill=(240, 245, 255, 255))


# -------------------------------------------------------------
# 4. BANDA D: Rejilla Metálica Perforada (Industrial Floor Grate) [UV Y: 0.62 - 0.78]
# -------------------------------------------------------------
y_top_D = uv_to_y(0.78)
y_bot_D = uv_to_y(0.62)

draw_base.rectangle([0, y_top_D, TEX_RES, y_bot_D], fill=(65, 70, 78, 255)) # Metal base
draw_rough.rectangle([0, y_top_D, TEX_RES, y_bot_D], fill=100)
draw_metal.rectangle([0, y_top_D, TEX_RES, y_bot_D], fill=235)
draw_height.rectangle([0, y_top_D, TEX_RES, y_bot_D], fill=150)

# Patrón de rejilla / orificios de paso
hole_pitch_x = 32
hole_pitch_y = 28
for y in range(y_top_D + 16, y_bot_D - 16, hole_pitch_y):
    offset_x = 16 if ((y // hole_pitch_y) % 2 == 1) else 0
    for x in range(offset_x, TEX_RES, hole_pitch_x):
        # Orificio profundo de la rejilla
        draw_base.rectangle([x, y, x + 16, y + 14], fill=(12, 14, 16, 255))
        draw_height.rectangle([x, y, x + 16, y + 14], fill=50) # Muy profundo
        draw_rough.rectangle([x, y, x + 16, y + 14], fill=220)
        draw_metal.rectangle([x, y, x + 16, y + 14], fill=20)
        draw_ao.rectangle([x - 2, y - 2, x + 18, y + 16], fill=40) # Oclusión intensa


# -------------------------------------------------------------
# 5. BANDA E: Tuberías, Conductos y Gomas de Sellado [UV Y: 0.78 - 0.90]
# -------------------------------------------------------------
y_top_E = uv_to_y(0.90)
y_bot_E = uv_to_y(0.78)

# Fondo oscuro de hueco de conducto
draw_base.rectangle([0, y_top_E, TEX_RES, y_bot_E], fill=(22, 24, 28, 255))
draw_rough.rectangle([0, y_top_E, TEX_RES, y_bot_E], fill=180)
draw_metal.rectangle([0, y_top_E, TEX_RES, y_bot_E], fill=60)
draw_height.rectangle([0, y_top_E, TEX_RES, y_bot_E], fill=110)

# Tubería Corrugada Grande 1 (Cobre/Bronce industrial)
pipe1_top = y_top_E + 20
pipe1_bot = y_top_E + 90
draw_base.rectangle([0, pipe1_top, TEX_RES, pipe1_bot], fill=(160, 92, 45, 255)) # Bronce/cobre
draw_rough.rectangle([0, pipe1_top, TEX_RES, pipe1_bot], fill=80)
draw_metal.rectangle([0, pipe1_top, TEX_RES, pipe1_bot], fill=210)
draw_height.rectangle([0, pipe1_top, TEX_RES, pipe1_bot], fill=190)

# Anillos corrugados de la tubería
for x in range(0, TEX_RES, 24):
    draw_base.rectangle([x, pipe1_top, x + 10, pipe1_bot], fill=(195, 120, 65, 255))
    draw_height.rectangle([x, pipe1_top, x + 10, pipe1_bot], fill=225)
    draw_ao.rectangle([x + 10, pipe1_top, x + 16, pipe1_bot], fill=80)

# Tubería Corrugada 2 (Goma Negra de Alta Presión)
pipe2_top = y_top_E + 110
pipe2_bot = y_bot_E - 20
draw_base.rectangle([0, pipe2_top, TEX_RES, pipe2_bot], fill=(28, 30, 34, 255))
draw_rough.rectangle([0, pipe2_top, TEX_RES, pipe2_bot], fill=200) # Goma mate
draw_metal.rectangle([0, pipe2_top, TEX_RES, pipe2_bot], fill=10)  # No metálico
draw_height.rectangle([0, pipe2_top, TEX_RES, pipe2_bot], fill=180)

for x in range(0, TEX_RES, 16):
    draw_base.rectangle([x, pipe2_top, x + 6, pipe2_bot], fill=(42, 44, 50, 255))
    draw_height.rectangle([x, pipe2_top, x + 6, pipe2_bot], fill=205)
    draw_ao.rectangle([x + 6, pipe2_top, x + 10, pipe2_bot], fill=70)


# -------------------------------------------------------------
# 6. BANDA F: Emisivos de Emergencia y Pantallas [UV Y: 0.90 - 1.00]
# -------------------------------------------------------------
y_top_F = uv_to_y(1.00)
y_bot_F = uv_to_y(0.90)

# Base metálica oscura del panel de instrumentos
draw_base.rectangle([0, y_top_F, TEX_RES, y_bot_F], fill=(30, 32, 38, 255))
draw_rough.rectangle([0, y_top_F, TEX_RES, y_bot_F], fill=70)
draw_metal.rectangle([0, y_top_F, TEX_RES, y_bot_F], fill=180)
draw_height.rectangle([0, y_top_F, TEX_RES, y_bot_F], fill=140)

# 6.1 Baliza de Alarma Roja (Glow Red) [X: 0 - 512]
draw_base.rectangle([32, y_top_F + 24, 480, y_bot_F - 24], fill=(255, 30, 30, 255))
draw_emis.rectangle([32, y_top_F + 24, 480, y_bot_F - 24], fill=(255, 35, 35, 255))
draw_rough.rectangle([32, y_top_F + 24, 480, y_bot_F - 24], fill=40)
draw_height.rectangle([32, y_top_F + 24, 480, y_bot_F - 24], fill=210)

# 6.2 Barra LED Neón Cyan de Estado [X: 512 - 1024]
draw_base.rectangle([544, y_top_F + 36, 992, y_top_F + 64], fill=(0, 240, 255, 255))
draw_emis.rectangle([544, y_top_F + 36, 992, y_top_F + 64], fill=(0, 240, 255, 255))
draw_rough.rectangle([544, y_top_F + 36, 992, y_top_F + 64], fill=30)
draw_height.rectangle([544, y_top_F + 36, 992, y_top_F + 64], fill=210)

# Indicadores Ámbar / Alerta [X: 544 - 992 fila inferior]
for bx in range(544, 992, 48):
    draw_base.rectangle([bx, y_top_F + 90, bx + 32, y_bot_F - 30], fill=(255, 160, 10, 255))
    draw_emis.rectangle([bx, y_top_F + 90, bx + 32, y_bot_F - 30], fill=(255, 160, 10, 255))
    draw_rough.rectangle([bx, y_top_F + 90, bx + 32, y_bot_F - 30], fill=40)
    draw_height.rectangle([bx, y_top_F + 90, bx + 32, y_bot_F - 30], fill=200)

# 6.3 Pantalla de Terminal / Consola de Esclusa [X: 1024 - 1536]
draw_base.rectangle([1056, y_top_F + 24, 1504, y_bot_F - 24], fill=(10, 35, 45, 255))
draw_rough.rectangle([1056, y_top_F + 24, 1504, y_bot_F - 24], fill=25)
draw_metal.rectangle([1056, y_top_F + 24, 1504, y_bot_F - 24], fill=10)
draw_height.rectangle([1056, y_top_F + 24, 1504, y_bot_F - 24], fill=125)
# Líneas de interfaz en pantalla
for ly in range(y_top_F + 40, y_bot_F - 35, 20):
    draw_base.rectangle([1080, ly, 1480, ly + 6], fill=(0, 230, 255, 255))
    draw_emis.rectangle([1080, ly, 1480, ly + 6], fill=(0, 230, 255, 255))

# 6.4 Lámpara de Emergencia Estroboscópica Blanca/Amarilla [X: 1536 - 2048]
draw_base.rectangle([1568, y_top_F + 28, 2016, y_bot_F - 28], fill=(255, 245, 210, 255))
draw_emis.rectangle([1568, y_top_F + 28, 2016, y_bot_F - 28], fill=(255, 245, 210, 255))
draw_rough.rectangle([1568, y_top_F + 28, 2016, y_bot_F - 28], fill=20)
draw_height.rectangle([1568, y_top_F + 28, 2016, y_bot_F - 28], fill=220)


# -------------------------------------------------------------
# CÁLCULO DEL NORMAL MAP TANGENT-SPACE CON NUMPY
# -------------------------------------------------------------
print("Calculando Normal Map y empaquetado ORM...")
h_arr = np.array(height_img, dtype=np.float32) / 255.0

# Gradiente Sobel / Diferencias centrales
# En OpenGL/Unreal: X+ es derecha (Rojo), Y+ es arriba (Verde), Z+ es saliente (Azul)
# Recuerda que en arrays de imagen index 0 es arriba, por lo que invertimos gradiente Y para Unreal
dh_dx = (np.roll(h_arr, -1, axis=1) - np.roll(h_arr, 1, axis=1)) * 0.5
dh_dy = -(np.roll(h_arr, -1, axis=0) - np.roll(h_arr, 1, axis=0)) * 0.5

# Factor de intensidad de relieve
bump_strength = 7.5
nx = -dh_dx * bump_strength
ny = -dh_dy * bump_strength
nz = np.ones_like(nx)

# Normalizar vectores
norm = np.sqrt(nx**2 + ny**2 + nz**2)
nx = nx / norm
ny = ny / norm
nz = nz / norm

# Mapear de [-1, 1] a [0, 255]
norm_r = ((nx * 0.5 + 0.5) * 255.0).astype(np.uint8)
norm_g = ((ny * 0.5 + 0.5) * 255.0).astype(np.uint8)
norm_b = ((nz * 0.5 + 0.5) * 255.0).astype(np.uint8)

normal_img = Image.fromarray(np.stack([norm_r, norm_g, norm_b], axis=-1), mode="RGB")

# -------------------------------------------------------------
# EMPAQUETADO ORM (R=AO, G=Roughness, B=Metallic)
# -------------------------------------------------------------
ao_arr = np.array(ao_img, dtype=np.uint8)
rough_arr = np.array(roughness_img, dtype=np.uint8)
metal_arr = np.array(metallic_img, dtype=np.uint8)

orm_arr = np.stack([ao_arr, rough_arr, metal_arr], axis=-1)
orm_img = Image.fromarray(orm_arr, mode="RGB")

# Guardar texturas en disco
base_path = os.path.join(OUT_DIR, "T_TrimSheet_Industrial_BaseColor.png")
orm_path = os.path.join(OUT_DIR, "T_TrimSheet_Industrial_ORM.png")
norm_path = os.path.join(OUT_DIR, "T_TrimSheet_Industrial_Normal.png")
emis_path = os.path.join(OUT_DIR, "T_TrimSheet_Industrial_Emissive.png")

base_img.convert("RGB").save(base_path, quality=95)
orm_img.save(orm_path, quality=95)
normal_img.save(norm_path, quality=95)
emissive_img.convert("RGB").save(emis_path, quality=95)

print(f"Texturas PBR generadas exitosamente:")
print(f" - BaseColor: {base_path}")
print(f" - ORM:       {orm_path}")
print(f" - Normal:    {norm_path}")
print(f" - Emissive:  {emis_path}")
