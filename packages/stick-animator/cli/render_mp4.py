#!/usr/bin/env python3
import sys
import os
import json
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def render_animation(json_path, mp4_path, scale=2):
    print(f"🎬 Leyendo fotogramas de {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    width = data.get('canvas_width', 960)
    height = data.get('canvas_height', 540)
    fps = data.get('fps', 24)
    frames = data.get('frames', [])

    print(f"📹 Renderizando {len(frames)} fotogramas a {fps} FPS ({width}x{height}, supersampling {scale}x)...")

    # Crear VideoWriter con codec mp4v / avc1
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(mp4_path, fourcc, fps, (width, height))

    bg_color = (20, 22, 34) # #141622
    s_width = width * scale
    s_height = height * scale

    for idx, frame_drawables in enumerate(frames):
        # Crear imagen con escala para antialiasing de alta calidad
        img = Image.new('RGB', (s_width, s_height), bg_color)
        draw = ImageDraw.Draw(img)

        for d in frame_drawables:
            rgb = tuple(d.get('rgb', [200, 200, 200]))
            d_type = d.get('type')
            thickness = int(max(1, d.get('thickness', 6) * scale))
            code = d.get('code', 0)

            if d_type == 'poly' and d.get('points') and len(d['points']) >= 3:
                pts = [(p['x'] * scale, p['y'] * scale) for p in d['points']]
                draw.polygon(pts, fill=rgb)

            elif d_type == 'circle':
                length = d.get('length') or d.get('thickness') or 20
                r = (length / 2) * scale
                center = d.get('end') or (d.get('points') and d['points'][-1]) or d.get('start')
                if center:
                    cx = center['x'] * scale
                    cy = center['y'] * scale
                    bbox = [cx - r, cy - r, cx + r, cy + r]
                    if code == 3: # circleFill
                        draw.ellipse(bbox, fill=rgb)
                    else:
                        draw.ellipse(bbox, outline=rgb, width=thickness)

            elif d_type == 'line':
                pts = []
                if d.get('points') and len(d['points']) > 2:
                    pts = [(p['x'] * scale, p['y'] * scale) for p in d['points']]
                elif d.get('start') and d.get('end'):
                    pts = [
                        (d['start']['x'] * scale, d['start']['y'] * scale),
                        (d['end']['x'] * scale, d['end']['y'] * scale)
                    ]

                if len(pts) >= 2:
                    draw.line(pts, fill=rgb, width=thickness, joint='curve')
                    # Puntos redondos en los extremos para lineCap: round
                    cap_r = thickness / 2
                    for p in pts:
                        draw.ellipse([p[0] - cap_r, p[1] - cap_r, p[0] + cap_r, p[1] + cap_r], fill=rgb)

        # Redimensionar al tamaño final con anti-aliasing
        if scale > 1:
            img = img.resize((width, height), Image.Resampling.LANCZOS)

        # Convertir a formato OpenCV BGR
        frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

        if (idx + 1) % 15 == 0 or idx + 1 == len(frames):
            print(f"  Fotograma {idx + 1}/{len(frames)} procesado")

    out.release()
    size_bytes = os.path.getsize(mp4_path)
    print(f"🎉 ¡Video MP4 exportado con éxito a: {mp4_path} ({size_bytes / 1024:.1f} KB)!")

if __name__ == '__main__':
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'frames.json'
    mp4_file = sys.argv[2] if len(sys.argv) > 2 else 'cyber_samurai.mp4'
    render_animation(json_file, mp4_file)
