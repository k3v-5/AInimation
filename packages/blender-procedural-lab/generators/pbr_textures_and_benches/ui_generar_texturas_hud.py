"""
Generador de texturas procedurales para el HUD diegético de casco y pantalla de radar táctico A.H.R.S.
Cumple con los estándares de arte PBR y UI diegética de Astra Hazard.
"""

import math
from PIL import Image, ImageDraw, ImageFilter

def create_radar_grid(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r_max = size // 2 - 16

    # Fondo circular oscuro con tinte CRT verde fósforo muy sutil
    draw.ellipse((cx - r_max, cy - r_max, cx + r_max, cy + r_max), fill=(6, 26, 10, 160))

    # Anillos de rango concéntricos (10m, 20m, 30m, 40m normalizados)
    color_ring = (50, 220, 90, 120)
    for frac in [0.25, 0.50, 0.75, 1.0]:
        r = int(r_max * frac)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color_ring, width=2 if frac < 1.0 else 3)

    # Retícula de ejes cardinales y diagonales
    color_axis = (60, 240, 100, 140)
    draw.line((cx, cy - r_max, cx, cy + r_max), fill=color_axis, width=2)
    draw.line((cx - r_max, cy, cx + r_max, cy), fill=color_axis, width=2)

    # Marcas angulares cada 30 grados
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x1 = cx + int((r_max - 8) * math.cos(rad))
        y1 = cy + int((r_max - 8) * math.sin(rad))
        x2 = cx + int(r_max * math.cos(rad))
        y2 = cy + int(r_max * math.sin(rad))
        draw.line((x1, y1, x2, y2), fill=(100, 255, 130, 180), width=2)

    # Ticks intermedios cada 10 grados
    for deg in range(0, 360, 10):
        if deg % 30 == 0:
            continue
        rad = math.radians(deg)
        x1 = cx + int((r_max - 4) * math.cos(rad))
        y1 = cy + int((r_max - 4) * math.sin(rad))
        x2 = cx + int(r_max * math.cos(rad))
        y2 = cy + int(r_max * math.sin(rad))
        draw.line((x1, y1, x2, y2), fill=(80, 200, 100, 110), width=1)

    # Punto central del sensor
    draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=(140, 255, 160, 255))
    return img

def create_radar_sweep(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size // 2, size // 2
    r_max = size // 2 - 16
    sweep_angle_span = 45.0  # Cono de barrido de 45°

    pixels = img.load()
    for y in range(size):
        for x in range(size):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= r_max and dist > 2:
                # Ángulo medido en sentido horario desde arriba (eje -Y)
                ang = math.degrees(math.atan2(dx, -dy))
                if ang < 0:
                    ang += 360.0
                
                # Suponemos el frente del haz en 0° (arriba) y la cola extendiéndose hacia la izquierda (360 - sweep_span)
                if ang <= sweep_angle_span:
                    factor = 1.0 - (ang / sweep_angle_span)
                elif ang >= (360.0 - sweep_angle_span):
                    factor = 0.0
                else:
                    factor = 0.0

                if factor > 0.0:
                    alpha = int(180 * (factor ** 1.8) * (1.0 - (dist / r_max) * 0.15))
                    g = int(255 * factor)
                    r = int(50 * factor)
                    b = int(70 * factor)
                    pixels[x, y] = (r, g, b, alpha)

    return img

def create_blip_civilian(size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = size // 2
    # Resplandor radial exterior
    for r in range(size // 2, 4, -2):
        alpha = int(255 * (1.0 - (r / (size // 2))) ** 2)
        draw.ellipse((c - r, c - r, c + r, c + r), fill=(50, 255, 100, alpha // 4))

    # Núcleo sólido brillante verde fósforo
    draw.ellipse((c - 8, c - 8, c + 8, c + 8), fill=(80, 255, 130, 220), outline=(200, 255, 220, 255), width=2)
    draw.ellipse((c - 3, c - 3, c + 3, c + 3), fill=(255, 255, 255, 255))
    return img

def create_blip_pet(size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = size // 2
    # Resplandor radial cian
    for r in range(size // 2, 4, -2):
        alpha = int(255 * (1.0 - (r / (size // 2))) ** 2)
        draw.ellipse((c - r, c - r, c + r, c + r), fill=(0, 220, 255, alpha // 4))

    # Rombo / diamante cian brillante
    pts = [(c, c - 10), (c + 10, c), (c, c + 10), (c - 10, c)]
    draw.polygon(pts, fill=(0, 230, 255, 240), outline=(220, 255, 255, 255))
    draw.ellipse((c - 3, c - 3, c + 3, c + 3), fill=(255, 255, 255, 255))
    return img

def create_airlock_pointer(size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = size // 2
    # Flecha triangular ámbar de rescate apuntando hacia arriba
    pts = [(c, 8), (size - 12, size - 14), (c, size - 22), (12, size - 14)]
    draw.polygon(pts, fill=(255, 180, 20, 240), outline=(255, 240, 160, 255))
    return img

def create_radial_gauge_arc(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r_outer = size // 2 - 12
    r_inner = r_outer - 24

    # Arco de 120° (de 120° a 240°)
    draw.arc((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), start=120, end=240, fill=(0, 220, 255, 180), width=6)
    draw.arc((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), start=120, end=240, fill=(0, 180, 220, 100), width=2)

    # Segmentos y ticks
    for deg in range(120, 241, 10):
        rad = math.radians(deg)
        x1 = cx + int((r_inner - 4) * math.cos(rad))
        y1 = cy + int((r_inner - 4) * math.sin(rad))
        x2 = cx + int((r_outer + 4) * math.cos(rad))
        y2 = cy + int((r_outer + 4) * math.sin(rad))
        draw.line((x1, y1, x2, y2), fill=(0, 240, 255, 200), width=2 if deg % 30 == 0 else 1)

    return img

def create_helmet_visor_frame(width=1920, height=1080):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2

    # Viñeta oscura periférica simulando el sello de goma del casco
    # Creamos un degradado oval elíptico en un canal de máscara
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    # Área visible translúcida en el centro
    rx, ry = width // 2 - 40, height // 2 - 30
    mask_draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=60))

    # Invertir para que los bordes sean opacos (sello de goma negro/gris grafito)
    pixels = img.load()
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            vis = mask_pixels[x, y]
            if vis < 250:
                darkness = 255 - vis
                alpha = min(255, int(darkness * 1.3))
                pixels[x, y] = (12, 14, 18, alpha)

    # Bordes sutiles de escáner cian diegético
    cyan_line = (0, 230, 255, 90)
    # Esquinas tácticas
    m = 70
    L = 90
    # Top-Left
    draw.line((m, m, m + L, m), fill=cyan_line, width=2)
    draw.line((m, m, m, m + L), fill=cyan_line, width=2)
    # Top-Right
    draw.line((width - m, m, width - m - L, m), fill=cyan_line, width=2)
    draw.line((width - m, m, width - m, m + L), fill=cyan_line, width=2)
    # Bottom-Left
    draw.line((m, height - m, m + L, height - m), fill=cyan_line, width=2)
    draw.line((m, height - m, m, height - m - L), fill=cyan_line, width=2)
    # Bottom-Right
    draw.line((width - m, height - m, width - m - L, height - m), fill=cyan_line, width=2)
    draw.line((width - m, height - m, width - m, height - m - L), fill=cyan_line, width=2)

    return img

def main():
    import os
    base_dir = "F:/Dev/Game/Art/Textures/UI"
    os.makedirs(base_dir, exist_ok=True)

    print("Generando texturas de UI diegética...")
    create_radar_grid().save(os.path.join(base_dir, "T_HUD_Radar_Grid_Phosphor.png"), "PNG")
    create_radar_sweep().save(os.path.join(base_dir, "T_HUD_Radar_Sweep_Gradient.png"), "PNG")
    create_blip_civilian().save(os.path.join(base_dir, "T_HUD_Blip_Civilian.png"), "PNG")
    create_blip_pet().save(os.path.join(base_dir, "T_HUD_Blip_Pet.png"), "PNG")
    create_airlock_pointer().save(os.path.join(base_dir, "T_HUD_Airlock_Pointer.png"), "PNG")
    create_radial_gauge_arc().save(os.path.join(base_dir, "T_HUD_Radial_Gauge_Arc.png"), "PNG")
    create_helmet_visor_frame().save(os.path.join(base_dir, "T_HUD_Helmet_Visor_Frame.png"), "PNG")
    print("¡Todas las texturas de UI generadas exitosamente en Art/Textures/UI!")

if __name__ == "__main__":
    main()
