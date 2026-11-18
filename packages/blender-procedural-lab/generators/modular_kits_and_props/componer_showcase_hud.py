import os
from PIL import Image, ImageDraw

RENDERS_DIR = r"F:\Dev\Game\Art\Renders"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

q1_path = os.path.join(RENDERS_DIR, "Q1_HelmetVisorHUD.png")
q2_path = os.path.join(RENDERS_DIR, "Q2_WristPDA_Hardware.png")
q3_path = os.path.join(RENDERS_DIR, "Q3_RadarScreen_Macro.png")
q4_path = os.path.join(RENDERS_DIR, "Q4_Forearm_Integration.png")

collage = Image.new("RGB", (1920, 1440), (10, 12, 16))
c_draw = ImageDraw.Draw(collage)

quad_images = [
    (q1_path, (0, 0), "1. HUD DIEGETICO DE VISOR DE CASCO (TELEMETRIA DE O2, TEMP Y ARCOS RADIALES)"),
    (q2_path, (960, 0), "2. HARDWARE 3D: TERMINAL DE ANTEBRAZO A.H.R.S. (PDA SCANNER CHASSIS)"),
    (q3_path, (0, 720), "3. INTERFAZ TACTICA: BIO-RADAR FOSFORICO CON BARRIDO Y BLIPS DE RESCATE"),
    (q4_path, (960, 720), "4. INTEGRACION ERGONOMICA EN EL TRAJE ESPACIAL DEL BOMBERO (ANTEBRAZO)")
]

for path, (px, py), title in quad_images:
    if os.path.exists(path):
        img = Image.open(path)
        collage.paste(img, (px, py))
        c_draw.rectangle([(px + 16, py + 16), (px + 944, py + 52)], fill=(12, 15, 20, 235), outline=(40, 180, 220, 200), width=2)
        c_draw.text((px + 28, py + 24), title, fill=(0, 240, 255))

c_draw.line((960, 0, 960, 1440), fill=(30, 45, 60), width=3)
c_draw.line((0, 720, 1920, 720), fill=(30, 45, 60), width=3)

showcase_path = os.path.join(RENDERS_DIR, "Showcase_Diegetic_HUD_and_Wrist_Scanner.png")
collage.save(showcase_path)
print(f"[OK] Showcase guardado: {showcase_path}")

artifact_dest = os.path.join(BRAIN_DIR, "Showcase_Diegetic_HUD_and_Wrist_Scanner.png")
collage.save(artifact_dest)
print(f"[OK] Showcase copiado a artefactos: {artifact_dest}")
