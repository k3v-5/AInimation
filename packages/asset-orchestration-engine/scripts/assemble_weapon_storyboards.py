"""assemble_weapon_storyboards.py
================================================================================
ENSAMBLADOR DE STORYBOARDS DE ANIMACIÓN Y MATERIALIZACIÓN DE ARMAS
================================================================================
Lee los paneles renderizados en Blender y compone 4 storyboards en formato 2x2:
- storyboard_escopeta.png
- storyboard_subfusil.png
- storyboard_pistola.png
- storyboard_rifle.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
TEMP_RENDER_DIR = os.path.join(BRAIN_DIR, "temp_crafting_renders")

WEAPONS = [
    {
        'id': 'escopeta',
        'name': 'ESCOPETA BREACHER-S4',
        'sub': 'Calibre Cuántico Pesado // Dispersión de Pulso y Disipador Cerámico',
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_escopeta.png'),
        'p3_title': 'FRAME 60 | 3. MATERIALIZACION 3P (ESCOPETA)',
        'p3_desc': 'Contención bimanual sobre marcos exteriores con la escopeta terminada levitando.'
    },
    {
        'id': 'subfusil',
        'name': 'SUBFUSIL PHASE-SMG',
        'sub': 'Cadencia Cuántica // Tambor de Plasma y Módulo de Fuga de Fase',
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_subfusil.png'),
        'p3_title': 'FRAME 60 | 3. MATERIALIZACION 3P (SUBFUSIL)',
        'p3_desc': 'Contención bimanual sobre marcos exteriores con el subfusil terminado levitando.'
    },
    {
        'id': 'pistola',
        'name': 'PISTOLA APEX-6',
        'sub': 'Disipador Láser Compacto // Recámara de Alta Tensión y Núcleo de Plasma',
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_pistola.png'),
        'p3_title': 'FRAME 60 | 3. MATERIALIZACION 3P (PISTOLA)',
        'p3_desc': 'Contención bimanual sobre marcos exteriores con la pistola terminada levitando.'
    },
    {
        'id': 'rifle',
        'name': 'RIFLE VANGUARD-AR',
        'sub': 'Asalto Cinético // Cañón Magnetizado, Rail Táctico y Núcleo Violeta',
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_rifle.png'),
        'p3_title': 'FRAME 60 | 3. MATERIALIZACION 3P (RIFLE)',
        'p3_desc': 'Contención bimanual sobre marcos exteriores con el rifle terminado levitando.'
    }
]


def assemble_weapon(wep):
    canvas_w = 2160
    canvas_h = 2280
    header_h = 120
    panel_w = 1080
    panel_h = 1080

    storyboard = Image.new("RGB", (canvas_w, canvas_h), color=(10, 11, 15))
    draw = ImageDraw.Draw(storyboard)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 22)
        font_panel_title = ImageFont.truetype("arialbd.ttf", 24)
        font_panel_desc = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = font_sub = font_panel_title = font_panel_desc = ImageFont.load_default()

    # 1. Cabecera Principal HUD
    draw.rectangle([0, 0, canvas_w, header_h], fill=(14, 16, 24))
    draw.line([0, header_h - 2, canvas_w, header_h - 2], fill=(160, 50, 255), width=3)

    # Acento morado tech en esquina
    draw.rectangle([25, 25, 45, 95], fill=(160, 50, 255))
    draw.text((60, 25), f"MESA DE CRAFTEO SCI-FI // {wep['name']}", font=font_title, fill=(255, 255, 255))
    draw.text((60, 72), f"SECUENCIA DE INTERACCIÓN, CONVERGENCIA DE SCRAP Y MATERIALIZACIÓN CUÁNTICA  |  {wep['sub']}", font=font_sub, fill=(180, 160, 220))

    # Badge estado
    draw.rectangle([canvas_w - 320, 35, canvas_w - 40, 85], outline=(160, 50, 255), width=2)
    draw.text((canvas_w - 305, 48), "DARX CORE // 4 FRAMES", font=font_panel_title, fill=(200, 130, 255))

    panels_info = [
        (1, 'FRAME 20 | 1. DEPOSITO DE SCRAP', 'Convergencia bimanual en la fosa central y deposito de modulos de datos.'),
        (2, 'FRAME 45 | 2. ENERGIZACION Y APERTURA', 'Manos extendidas a los marcos exteriores, estallido de plasma y genesis del arma.'),
        (3, wep['p3_title'], wep['p3_desc']),
        (4, 'FRAME 65 | 4. VISTA OCULAR FPS (1P)', 'Perspectiva ocular del jugador: brazos extendidos sobre la mesa y arma terminada.')
    ]

    positions = [
        (0, header_h),
        (panel_w, header_h),
        (0, header_h + panel_h),
        (panel_w, header_h + panel_h)
    ]

    for idx, (p_num, title, desc) in enumerate(panels_info):
        pos_x, pos_y = positions[idx]
        img_path = os.path.join(TEMP_RENDER_DIR, f"{wep['id']}_panel_{p_num}.png")
        if not os.path.exists(img_path):
            print(f"[Error] Archivo no encontrado: {img_path}")
            continue

        panel_img = Image.open(img_path).convert("RGB")
        storyboard.paste(panel_img, (pos_x, pos_y))

        # Overlay HUD superior en cada panel
        hud_bar_h = 60
        overlay = Image.new("RGBA", (panel_w, hud_bar_h), (8, 10, 16, 215))
        storyboard.paste(overlay, (pos_x, pos_y), overlay)
        draw.line([pos_x, pos_y + hud_bar_h, pos_x + panel_w, pos_y + hud_bar_h], fill=(160, 50, 255), width=1)

        draw.text((pos_x + 20, pos_y + 10), title, font=font_panel_title, fill=(255, 255, 255))
        draw.text((pos_x + 20, pos_y + 36), desc, font=font_panel_desc, fill=(190, 190, 210))

        quad_txt = f"P{p_num}"
        draw.text((pos_x + panel_w - 55, pos_y + 16), quad_txt, font=font_panel_title, fill=(180, 90, 255))

    # Líneas divisorias
    draw.line([panel_w, header_h, panel_w, canvas_h], fill=(40, 45, 65), width=2)
    draw.line([0, header_h + panel_h, canvas_w, header_h + panel_h], fill=(40, 45, 65), width=2)

    storyboard.save(wep['storyboard'], quality=95)
    jpg_path = wep['storyboard'].replace('.png', '.jpg')
    storyboard.save(jpg_path, 'JPEG', quality=95)
    print(f"[OK] Storyboard ensamblado: {wep['storyboard']} ({os.path.getsize(wep['storyboard'])} bytes)")
    print(f"[OK] Storyboard JPEG: {jpg_path} ({os.path.getsize(jpg_path)} bytes)")


def main():
    print("=================================================================")
    print("   DARX | ENSAMBLAJE DE STORYBOARDS DE INTERACCIÓN (4 ARMAS)    ")
    print("=================================================================")
    for wep in WEAPONS:
        assemble_weapon(wep)
    print("=================================================================")
    print("   TODOS LOS STORYBOARDS FUERON ENSAMBLADOS EXITOSAMENTE        ")
    print("=================================================================")


if __name__ == "__main__":
    main()
