"""Master VFX & Editorial Compositor for 'Cross-Dimension Rescue' (5-Engine Monorepo Showcase).

Unifies outputs from all 5 monorepo engines into a 12.0s 1280x720 @ 24 FPS master film:
  Act 1 (F001..F072): stykanimate-mcp 2D IK Tactical Blueprint Pre-Viz + Wireframe Match-Cut
  Act 2 (F073..F144): blender-procedural-lab + ianimation-3d 2K PBR Sector 7 & Rigid SE(3) Showcase
  Act 3 (F145..F216): adobe-animation-mcp 2D Commander Comms HUD + 48kHz Lip-Sync & Kinetic Subtitles
  Act 4 (F217..F288): after-effects-motion-engine Editorial TIME Poster, 808 Snap-Zooms & Film Optical VFX

Also compiles a compliant After Effects ExtendScript (cross_dimension_rescue_comp.jsx)
and renders 4 act stills + 2x2 showcase contact sheet + H.264/AAC MP4 + preview GIF.

Usage:
  C:\\Python314\\python.exe scripts\\compose_showcase_master_vfx.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Tuple
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.produce_showcase_assets_2d_and_audio import (  # noqa: E402
    CH_VISEMES,
    _render_commander_layer_scaled,
)

OUT_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo"
FRAMES_3D_DIR = PROJECT_ROOT / "outputs" / "cache" / "showcase_3d_frames"
FRAMES_FINAL_DIR = PROJECT_ROOT / "outputs" / "cache" / "showcase_final_frames"
BRAIN_DIR = Path(r"C:\Users\sasuk\.gemini\antigravity\brain\25a9dd69-1a8e-409b-85e3-41655796e664")
FFMPEG_BIN = Path(
    r"C:\Users\sasuk\AppData\Roaming\Python\Python314\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
)

WIDTH = 1280
HEIGHT = 720
FPS = 24
TOTAL_FRAMES = 288

FONT_IMPACT = r"C:\Windows\Fonts\impact.ttf"
FONT_ARIAL_BLACK = r"C:\Windows\Fonts\ariblk.ttf"
FONT_SEGOE_BLACK = r"C:\Windows\Fonts\seguibl.ttf"
FONT_CONSOLAS_BOLD = r"C:\Windows\Fonts\consolab.ttf"

CRIMSON: Tuple[int, int, int] = (255, 20, 36)
PURE_WHITE: Tuple[int, int, int] = (250, 250, 250)
DEEP_SLATE: Tuple[int, int, int] = (8, 8, 13)
CYAN_ACCENT: Tuple[int, int, int] = (0, 229, 255)
AMBER_HAZARD: Tuple[int, int, int] = (255, 184, 0)
MUTED_SLATE: Tuple[int, int, int] = (145, 158, 178)

ENGINE_NAMES: Tuple[str, ...] = (
    "01 STYK-IK",
    "02 BLENDER-PBR",
    "03 3D-SE(3)",
    "04 ADOBE-CH",
    "05 AE-VFX",
    "06 AOE-UAF",
)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load TrueType font deterministically."""
    if Path(path).exists():
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def alpha_blend_rgba(dst_rgba: np.ndarray, src_rgba: np.ndarray, x0: int = 0, y0: int = 0) -> None:
    """Alpha composite src_rgba (H, W, 4) onto dst_rgba in-place at offset (x0, y0)."""
    sh, sw = src_rgba.shape[:2]
    dh, dw = dst_rgba.shape[:2]

    sx1 = max(0, -x0)
    sy1 = max(0, -y0)
    dx1 = max(0, x0)
    dy1 = max(0, y0)
    cw = min(sw - sx1, dw - dx1)
    ch = min(sh - sy1, dh - dy1)
    if cw <= 0 or ch <= 0:
        return

    src_crop = src_rgba[sy1 : sy1 + ch, sx1 : sx1 + cw].astype(np.float32)
    dst_crop = dst_rgba[dy1 : dy1 + ch, dx1 : dx1 + cw].astype(np.float32)

    sa = src_crop[:, :, 3:4] / 255.0
    dst_rgb = dst_crop[:, :, :3] * (1.0 - sa) + src_crop[:, :, :3] * sa
    dst_a = np.clip(dst_crop[:, :, 3:4] + src_crop[:, :, 3:4] * (1.0 - dst_crop[:, :, 3:4] / 255.0), 0.0, 255.0)
    dst_rgba[dy1 : dy1 + ch, dx1 : dx1 + cw, :3] = np.clip(dst_rgb, 0.0, 255.0).astype(np.uint8)
    dst_rgba[dy1 : dy1 + ch, dx1 : dx1 + cw, 3:4] = dst_a.astype(np.uint8)


def draw_editorial_text(
    canvas: Image.Image,
    text: str,
    center_xy: Tuple[int, int],
    font: ImageFont.FreeTypeFont,
    color_rgb: Tuple[int, int, int],
    alpha: int = 255,
    vertical_stretch: float = 1.35,
    letter_spacing: int = -2,
    glow_rgb: Optional[Tuple[int, int, int]] = None,
    shadow_offset: int = 4,
) -> None:
    """Render center-justified editorial text with vertical scale stretch, tracking & optional glow."""
    if alpha <= 2:
        return

    # Measure glyphs character by character for explicit tracking control
    dummy_img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)

    widths: List[int] = []
    for ch in text:
        cw = max(1, int(math.ceil(dummy_draw.textlength(ch, font=font))))
        widths.append(cw)

    total_w = max(8, sum(widths) + max(0, len(text) - 1) * letter_spacing + 64)
    raw_h = max(16, int(font.size * 1.45) + 40)

    txt_layer = Image.new("RGBA", (total_w, raw_h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(txt_layer)
    x_cursor = 24
    y_cursor = 18

    if shadow_offset > 0:
        xs = x_cursor
        for ch, cw in zip(text, widths):
            tdraw.text((xs + shadow_offset, y_cursor + shadow_offset), ch, font=font, fill=(4, 4, 8, int(alpha * 0.78)))
            xs += cw + letter_spacing

    xs = x_cursor
    for ch, cw in zip(text, widths):
        tdraw.text((xs, y_cursor), ch, font=font, fill=(color_rgb[0], color_rgb[1], color_rgb[2], alpha))
        xs += cw + letter_spacing

    if glow_rgb is not None:
        glow_mask = Image.new("RGBA", (total_w, raw_h), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_mask)
        xs = x_cursor
        for ch, cw in zip(text, widths):
            gdraw.text((xs, y_cursor), ch, font=font, fill=(glow_rgb[0], glow_rgb[1], glow_rgb[2], int(alpha * 0.55)))
            xs += cw + letter_spacing
        glow_arr = cv2.GaussianBlur(np.array(glow_mask), (0, 0), sigmaX=7.5, sigmaY=7.5)
        glow_img = Image.fromarray(glow_arr, mode="RGBA")
        txt_layer = Image.alpha_composite(glow_img, txt_layer)

    if abs(vertical_stretch - 1.0) > 1e-3:
        new_h = max(4, int(round(raw_h * vertical_stretch)))
        txt_layer = txt_layer.resize((total_w, new_h), Image.Resampling.LANCZOS)

    paste_x = int(center_xy[0] - txt_layer.width // 2)
    paste_y = int(center_xy[1] - txt_layer.height // 2)
    canvas.alpha_composite(txt_layer, dest=(paste_x, paste_y))


def compute_audio_envelopes(
    wav_path: Path, total_frames: int, fps: int, num_bars: int = 16
) -> Tuple[List[List[float]], List[float]]:
    """Compute per-frame multi-band visualizer bars and normalized RMS from stereo WAV."""
    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        raw = wf.readframes(wf.getnframes())

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    hop = max(1, int(round(sr / fps)))
    bars_per_frame: List[List[float]] = []
    rms_per_frame: List[float] = []

    for f_idx in range(total_frames):
        s0 = f_idx * hop
        s1 = min(len(samples), s0 + hop * 2)
        chunk = samples[s0:s1]
        if len(chunk) < 64:
            bars_per_frame.append([0.08] * num_bars)
            rms_per_frame.append(0.05)
            continue

        rms_val = float(np.sqrt(np.mean(chunk * chunk)))
        rms_per_frame.append(min(1.0, rms_val * 3.2))

        window = np.hanning(len(chunk))
        spec = np.abs(np.fft.rfft(chunk * window))
        freqs = np.fft.rfftfreq(len(chunk), d=1.0 / sr)

        bar_vals: List[float] = []
        edges = np.geomspace(55.0, 9500.0, num_bars + 1)
        for b in range(num_bars):
            mask = (freqs >= edges[b]) & (freqs < edges[b + 1])
            energy = float(np.mean(spec[mask])) if np.any(mask) else 0.0
            norm_bar = min(1.0, max(0.08, math.log1p(energy * 0.14) / 2.6))
            bar_vals.append(norm_bar)
        bars_per_frame.append(bar_vals)

    return bars_per_frame, rms_per_frame


def compute_beat_impulse(t_sec: float, beat_timestamps: Sequence[float]) -> float:
    """Compute punchy 808 beat envelope [0..1] decaying sharply after each detected beat."""
    best = 0.0
    for bt in beat_timestamps:
        dt = t_sec - bt
        if 0.0 <= dt < 0.42:
            val = math.exp(-10.5 * dt)
            if val > best:
                best = val
    return best


def emit_after_effects_jsx(
    out_path: Path,
    beat_timestamps: Sequence[float],
    word_cues: Sequence[Dict[str, object]],
) -> None:
    """Compile USER_DESIGN_PREFERENCES-compliant After Effects ExtendScript (.jsx)."""
    fonts_js = '["Impact", "Arial-Black", "Haettenschweiler", "Anton", "BebasNeue", "SegoeUI-Black", "Arial-BoldMT"]'
    cues_json = json.dumps(list(word_cues), ensure_ascii=False, indent=2)
    beats_json = json.dumps([round(float(b), 4) for b in beat_timestamps])

    jsx = f"""// Cross-Dimension Rescue — After Effects Master Composition Script
// Compiled automatically by after-effects-motion-engine for IANIMATION 5-Engine Monorepo
// Strictly adheres to Editorial Poster / TIME Style (USER_DESIGN_PREFERENCES.md)

(function buildCrossDimensionRescueComp() {{
    app.beginUndoGroup("Build Cross-Dimension Rescue Master Comp");

    var COMP_NAME = "CrossDimensionRescue_Master_1280x720";
    var COMP_W = 1280;
    var COMP_H = 720;
    var COMP_FPS = 24;
    var COMP_DUR = 12.0;

    var APPROVED_FONTS = {fonts_js};
    var COL_CRIMSON = [1.0, 0.08, 0.14];   // #FF1424
    var COL_WHITE   = [0.98, 0.98, 0.98];  // #FAFAFA
    var COL_SLATE   = [0.03, 0.03, 0.05];  // #08080D
    var BEAT_TIMESTAMPS = {beats_json};
    var WORD_CUES = {cues_json};

    var proj = app.project || app.newProject();
    var comp = proj.items.addComp(COMP_NAME, COMP_W, COMP_H, 1.0, COMP_DUR, COMP_FPS);
    comp.bgColor = COL_SLATE;
    comp.motionBlur = true;
    comp.shutterAngle = 180;

    // 1. Background Slate Solid & Contrast Vignette Layer
    var bgLayer = comp.layers.addSolid(COL_SLATE, "Backdrop_DeepSlate", COMP_W, COMP_H, 1.0, COMP_DUR);
    bgLayer.motionBlur = true;

    // 2. Minimalist 24-Tick Rotating Vector Clock Dial (Editorial Poster Style)
    var dialLayer = comp.layers.addShape();
    dialLayer.name = "Editorial_ClockDial_24Ticks";
    dialLayer.motionBlur = true;
    dialLayer.property("Transform").property("Position").setValue([COMP_W / 2, COMP_H / 2]);
    dialLayer.property("Transform").property("Opacity").setValue(28);
    dialLayer.property("Transform").property("Rotation").expression = "time * 15;";
    var rootGroup = dialLayer.property("Contents").addProperty("ADBE Vector Group");
    var tickRect = rootGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
    tickRect.property("Size").setValue([3, 18]);
    tickRect.property("Position").setValue([0, -250]);
    var tickFill = rootGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
    tickFill.property("Color").setValue(COL_WHITE);
    var repeater = rootGroup.property("Contents").addProperty("ADBE Vector Filter - Repeater");
    repeater.property("Copies").setValue(24);
    repeater.property("Transform").property("Rotation").setValue(15);

    // 3. 808 Beat-Reactive Snap Zoom Null Driver
    var beatNull = comp.layers.addNull(COMP_DUR);
    beatNull.name = "808_SnapZoom_Controller";
    beatNull.motionBlur = true;
    beatNull.property("Transform").property("Scale").expression = [
        "var beats = " + JSON.stringify(BEAT_TIMESTAMPS) + ";",
        "var boost = 0;",
        "for (var i = 0; i < beats.length; i++) {{",
        "  var dt = time - beats[i];",
        "  if (dt >= 0 && dt < 0.35) boost = Math.max(boost, Math.exp(-10.5 * dt));",
        "}}",
        "var s = 100 + 7.5 * boost;",
        "[s, s];"
    ].join("\\n");

    function addEditorialTextLayer(name, content, fontSize, colorRGB, yPos, inPt, outPt, trackingVal, stretchY) {{
        var tl = comp.layers.addText(content);
        tl.name = name;
        tl.startTime = 0;
        tl.inPoint = inPt;
        tl.outPoint = outPt;
        tl.motionBlur = true;

        var textProp = tl.property("Source Text");
        var textDoc = textProp.value;
        textDoc.font = APPROVED_FONTS[0];
        textDoc.fontSize = fontSize;
        textDoc.fillColor = colorRGB;
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        textDoc.tracking = trackingVal;
        textProp.setValue(textDoc);

        var rect = tl.sourceRectAtTime(inPt + 0.05, false);
        tl.property("Transform").property("Anchor Point").setValue([rect.left + rect.width / 2, rect.top + rect.height / 2]);
        tl.property("Transform").property("Position").setValue([COMP_W / 2, yPos]);
        tl.property("Transform").property("Scale").setValue([100, stretchY]);
        tl.property("Transform").property("Scale").expression = [
            "var freq = 4.0; var decay = 7.0; var amp = 0.04;",
            "var t = Math.max(0, time - inPoint);",
            "var bounce = 1.0 + amp * Math.exp(-decay * t) * Math.sin(freq * t * 2 * Math.PI);",
            "[value[0] * bounce, value[1] * bounce];"
        ].join("\\n");
        return tl;
    }}

    // 4. Act 3 Kinetic Dialogue Word Cues (6.0s .. 9.5s)
    for (var w = 0; w < WORD_CUES.length; w++) {{
        var cue = WORD_CUES[w];
        var isKeyWord = (cue.word === "SIETE." || cue.word === "NÚCLEO" || cue.word === "INESTABLE." || cue.word === "RESCATE");
        addEditorialTextLayer(
            "DialogueCue_" + w + "_" + cue.word,
            cue.word,
            isKeyWord ? 54 : 44,
            isKeyWord ? COL_CRIMSON : COL_WHITE,
            602,
            cue.start_sec,
            cue.end_sec + 0.12,
            -12,
            122
        );
    }}

    // 5. Act 4 Hero TIME-Style Poster Titles (9.0s .. 12.0s)
    addEditorialTextLayer("Tag_Header", "IANIMATION MONOREPO", 26, COL_WHITE, 110, 10.65, 12.0, 32, 100);
    addEditorialTextLayer("Poster_Title_White", "CROSS-DIMENSION", 92, COL_WHITE, 244, 10.72, 12.0, -15, 135);
    addEditorialTextLayer("Poster_Title_Crimson", "RESCUE", 156, COL_CRIMSON, 398, 10.80, 12.0, -18, 138);
    addEditorialTextLayer("Poster_Badge_Footer", "[ 6 ENGINES // 166 MCP TOOLS // 2026 ]", 24, COL_WHITE, 588, 10.90, 12.0, 28, 100);

    app.endUndoGroup();
}})();
"""
    out_path.write_text(jsx, encoding="utf-8")


def build_commander_sprite_cache() -> Dict[str, np.ndarray]:
    """Pre-render 220x220 Commander sprite layers from 512x512 master puppet generator."""
    size = 220
    cache: Dict[str, np.ndarray] = {
        "Body_Torso": _render_commander_layer_scaled(size, size, "Body_Torso"),
        "Head_Base": _render_commander_layer_scaled(size, size, "Head_Base"),
        "Left_Eye": _render_commander_layer_scaled(size, size, "Left_Eye"),
        "Right_Eye": _render_commander_layer_scaled(size, size, "Right_Eye"),
    }
    for v in CH_VISEMES:
        cache[f"Viseme_{v}"] = _render_commander_layer_scaled(size, size, "Viseme", v)
    return cache


def render_act1_blueprint_frame(
    frame_idx: int,
    ik_frame_drawables: Sequence[Dict[str, object]],
    telemetry_rows: Sequence[Dict[str, object]],
    bg_3d_bgr: Optional[np.ndarray],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> np.ndarray:
    """Render Act 1 (F1..F72) stykanimate-mcp 2D IK Tactical Blueprint + F60-F72 3D match-cut."""
    canvas_bgr = np.full((HEIGHT, WIDTH, 3), (20, 12, 8), dtype=np.uint8)

    # Subtle blueprint drafting grid
    for gx in range(0, WIDTH, 40):
        col = (44, 30, 18) if gx % 160 != 0 else (72, 48, 24)
        cv2.line(canvas_bgr, (gx, 0), (gx, HEIGHT), col, 1)
    for gy in range(0, HEIGHT, 40):
        col = (44, 30, 18) if gy % 160 != 0 else (72, 48, 24)
        cv2.line(canvas_bgr, (0, gy), (WIDTH, gy), col, 1)

    # Draw STYK drawables sorted by z
    ordered = sorted(ik_frame_drawables, key=lambda d: float(d.get("z", 0)))  # type: ignore[arg-type]
    glow_layer = np.zeros_like(canvas_bgr, dtype=np.uint8)

    for drw in ordered:
        sx = int(round(float(drw["start"]["x"])))  # type: ignore[index]
        sy = int(round(float(drw["start"]["y"])))  # type: ignore[index]
        ex = int(round(float(drw["end"]["x"])))    # type: ignore[index]
        ey = int(round(float(drw["end"]["y"])))    # type: ignore[index]
        rgb = drw["rgb"]                           # type: ignore[index]
        bgr = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
        thick = max(2, int(round(float(drw.get("thickness", 6)))))  # type: ignore[arg-type]
        code = int(drw.get("code", 0))  # type: ignore[arg-type]
        name = str(drw.get("name", ""))

        if code == 3:
            cx = (sx + ex) // 2
            cy = (sy + ey) // 2
            rad = max(6, int(round(float(drw.get("length", 30)) * 0.5)))  # type: ignore[arg-type]
            cv2.circle(glow_layer, (cx, cy), rad + 5, (255, 229, 0) if "Core" not in name else (36, 120, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas_bgr, (cx, cy), rad, bgr, -1, cv2.LINE_AA)
            cv2.circle(canvas_bgr, (cx, cy), rad, (255, 235, 110), 2, cv2.LINE_AA)
        else:
            is_hero_piece = name not in ("FloorDeck", "FloorGridLine")
            if is_hero_piece:
                cv2.line(glow_layer, (sx, sy), (ex, ey), (255, 210, 40), thick + 4, cv2.LINE_AA)
            cv2.line(canvas_bgr, (sx, sy), (ex, ey), bgr, thick, cv2.LINE_AA)
            if is_hero_piece and thick >= 10:
                cv2.circle(canvas_bgr, (sx, sy), max(2, thick // 4), (240, 245, 255), -1, cv2.LINE_AA)

    glow_blur = cv2.GaussianBlur(glow_layer, (0, 0), sigmaX=7.0, sigmaY=7.0)
    canvas_bgr = np.clip(canvas_bgr.astype(np.float32) + glow_blur.astype(np.float32) * 0.34, 0, 255).astype(np.uint8)

    # Interpolate IK telemetry for vector overlay
    idx_kf = min(len(telemetry_rows) - 1, max(0, (frame_idx - 1) // 6))
    t_row = telemetry_rows[idx_kf]
    root_pt = (int(round(float(t_row["root"]["x"]))), int(round(float(t_row["root"]["y"]))))  # type: ignore[index]
    lk_pt = (int(round(float(t_row["left_knee"]["x"]))), int(round(float(t_row["left_knee"]["y"]))))  # type: ignore[index]
    rk_pt = (int(round(float(t_row["right_knee"]["x"]))), int(round(float(t_row["right_knee"]["y"]))))  # type: ignore[index]
    lf_pt = (int(round(float(t_row["left_foot_target"]["x"]))), int(round(float(t_row["left_foot_target"]["y"]))))  # type: ignore[index]
    rf_pt = (int(round(float(t_row["right_foot_target"]["x"]))), int(round(float(t_row["right_foot_target"]["y"]))))  # type: ignore[index]

    for a, b in ((root_pt, lk_pt), (lk_pt, lf_pt), (root_pt, rk_pt), (rk_pt, rf_pt)):
        cv2.line(canvas_bgr, a, b, (255, 229, 0), 1, cv2.LINE_AA)
    for target_pt in (lf_pt, rf_pt):
        cv2.drawMarker(canvas_bgr, target_pt, (36, 20, 255), cv2.MARKER_CROSS, 16, 2, cv2.LINE_AA)

    # Match-cut horizontal laser portal wipe (F58..F72) into 3D Corridor render
    if frame_idx >= 58 and bg_3d_bgr is not None:
        prog = min(1.0, (frame_idx - 58) / 14.0)
        prog_smooth = prog * prog * (3.0 - 2.0 * prog)
        split_x = int(WIDTH * prog_smooth)
        if split_x > 0:
            canvas_bgr[:, :split_x] = bg_3d_bgr[:, :split_x]
            if split_x < WIDTH - 4:
                cv2.line(canvas_bgr, (split_x, 0), (split_x, HEIGHT), (255, 229, 0), 4, cv2.LINE_AA)
                cv2.line(canvas_bgr, (split_x - 3, 0), (split_x - 3, HEIGHT), (255, 255, 255), 2, cv2.LINE_AA)

    # HUD Panels
    img_rgba = Image.fromarray(cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGBA), mode="RGBA")
    draw = ImageDraw.Draw(img_rgba)

    # Left Act Tag
    draw.rounded_rectangle((32, 28, 446, 114), radius=12, fill=(8, 12, 20, 215), outline=(0, 229, 255, 220), width=2)
    draw.text((52, 42), "ACT 01 // STYKANIMATE-MCP", font=fonts["hud_title"], fill=(0, 229, 255, 255))
    draw.text((52, 74), "2D TWO-BONE IK TACTICAL PRE-VIZ (.STYK)", font=fonts["hud_sub"], fill=(240, 245, 255, 235))

    # Right IK Telemetry Box
    draw.rounded_rectangle((874, 28, 1248, 156), radius=12, fill=(8, 12, 20, 215), outline=(255, 20, 36, 210), width=2)
    draw.text((894, 42), "TWO-BONE IK TELEMETRY", font=fonts["hud_title"], fill=(255, 20, 36, 255))
    draw.text(
        (894, 72),
        f"ROOT: ({root_pt[0]:4d}, {root_pt[1]:3d}) px",
        font=fonts["mono"],
        fill=(245, 248, 255, 240),
    )
    draw.text(
        (894, 96),
        f"L-THIGH: {float(t_row['left_thigh_deg']):5.1f} deg | R: {float(t_row['right_thigh_deg']):5.1f}",
        font=fonts["mono"],
        fill=(0, 229, 255, 240),
    )
    draw.text(
        (894, 120),
        "SEGMENT RIGIDITY: 0.00 px VAR",
        font=fonts["mono"],
        fill=(255, 184, 0, 240),
    )

    return np.array(img_rgba)


def add_act2_hud(
    frame_bgr: np.ndarray,
    frame_idx: int,
    aoe_radar_rgba: Optional[np.ndarray],
    aoe_summary: Dict[str, object],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> np.ndarray:
    """Apply PBR contrast HUD + live AOE-UAF Sector 7 Terrain (.r16) & WFC Radar card for Act 2."""
    img_rgba = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGBA), mode="RGBA")
    draw = ImageDraw.Draw(img_rgba)

    # Top-left Act Tag (does not occlude Ragdoll centered lower down)
    draw.rounded_rectangle((32, 28, 494, 140), radius=12, fill=(8, 10, 16, 205), outline=(255, 184, 0, 210), width=2)
    draw.text((52, 42), "ACT 02 // BLENDER PBR + 3D SE(3)", font=fonts["hud_title"], fill=(255, 184, 0, 255))
    draw.text((52, 72), "WATERTIGHT RAGDOLL 1.80m // BURLAP R: 0.78", font=fonts["mono"], fill=(245, 248, 255, 240))
    draw.text((52, 98), "HERO_FIREAXE + HEAD SE(3) VAR: < 1.0e-10", font=fonts["mono"], fill=(0, 229, 255, 240))

    # Top-right AOE-UAF Sector 7 World & WFC Tactical Radar Card
    card_x0, card_y0, card_x1, card_y1 = 918, 28, 1248, 230
    pulse_on = ((frame_idx // 6) % 2) == 0
    dot_col = (255, 20, 36, 255) if pulse_on else (120, 20, 30, 180)
    draw.rounded_rectangle((card_x0, card_y0, card_x1, card_y1), radius=12, fill=(8, 12, 20, 215), outline=(0, 229, 255, 220), width=2)
    draw.ellipse((card_x0 + 14, card_y0 + 14, card_x0 + 26, card_y0 + 26), fill=dot_col)
    draw.text((card_x0 + 34, card_y0 + 12), "AOE-UAF // SECTOR 07 WORLD", font=fonts["mono_sm"], fill=(0, 229, 255, 255))

    if aoe_radar_rgba is not None:
        arr_out = np.array(img_rgba)
        rx0, ry0 = card_x0 + 14, card_y0 + 40
        alpha_blend_rgba(arr_out, aoe_radar_rgba, rx0, ry0)
        img_rgba = Image.fromarray(arr_out, mode="RGBA")
        draw = ImageDraw.Draw(img_rgba)
        # Animated rotating tactical radar sweep ray inside 144x144 radar box
        rcx, rcy = rx0 + 72, ry0 + 72
        ang = math.radians((frame_idx - 72) * 8.0)
        draw.line((rcx, rcy, rcx + int(68 * math.cos(ang)), rcy + int(68 * math.sin(ang))), fill=(0, 229, 255, 215), width=2)
        draw.rectangle((rx0, ry0, rx0 + 144, ry0 + 144), outline=(0, 229, 255, 210), width=1)

    tx = card_x0 + 170
    wfc_info = aoe_summary.get("wfc_level", {})
    land_info = aoe_summary.get("landscape", {})
    tiles_n = int(wfc_info.get("total_tiles_solved", 49)) if isinstance(wfc_info, dict) else 49
    r16_kb = int(land_info.get("r16_bytes", 32768)) // 1024 if isinstance(land_info, dict) else 32
    draw.text((tx, card_y0 + 46), "WFC 2D GRID:", font=fonts["mono_sm"], fill=(160, 178, 200, 235))
    draw.text((tx, card_y0 + 64), f"7x7 ({tiles_n} TILES)", font=fonts["mono_sm"], fill=(250, 250, 250, 250))
    draw.text((tx, card_y0 + 92), "UE5 TERRAIN:", font=fonts["mono_sm"], fill=(160, 178, 200, 235))
    draw.text((tx, card_y0 + 110), f".R16 ({r16_kb} KB)", font=fonts["mono_sm"], fill=(0, 229, 255, 250))
    draw.text((tx, card_y0 + 138), "EROSION SIM:", font=fonts["mono_sm"], fill=(160, 178, 200, 235))
    draw.text((tx, card_y0 + 156), "HYDR + THERM", font=fonts["mono_sm"], fill=(255, 184, 0, 250))

    return np.array(img_rgba)


def add_act3_adobe_comms_hud(
    frame_bgr: np.ndarray,
    frame_idx: int,
    cue_row: Dict[str, object],
    word_cues: Sequence[Dict[str, object]],
    waveform_bars: Sequence[float],
    commander_cache: Dict[str, np.ndarray],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> np.ndarray:
    """Composite Adobe Character Animator 2D Commander PiP, waveform & kinetic subtitles."""
    img_rgba = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGBA), mode="RGBA")
    arr_rgba = np.array(img_rgba)

    # Glassmorphic Commander PiP Card cleanly seated in top-left quadrant (leaving right-side 3D character open)
    pip_x, pip_y, pip_w, pip_h = 32, 30, 434, 248
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle(
        (pip_x, pip_y, pip_x + pip_w, pip_y + pip_h),
        radius=16,
        fill=(10, 14, 22, 220),
        outline=(0, 229, 255, 235),
        width=2,
    )
    odraw.rectangle((pip_x + 14, pip_y + 12, pip_x + pip_w - 14, pip_y + 38), fill=(18, 28, 44, 210))
    odraw.ellipse((pip_x + 22, pip_y + 19, pip_x + 34, pip_y + 31), fill=(255, 20, 36, 255))
    odraw.text((pip_x + 42, pip_y + 16), "ADOBE-CH COMMS // SECTOR 7", font=fonts["mono"], fill=(250, 250, 250, 250))

    arr_rgba = np.array(Image.alpha_composite(Image.fromarray(arr_rgba, "RGBA"), overlay))

    # Composite Multi-Layer Commander PSD Sprite inside left half of PiP card
    spr_x = pip_x + 6
    spr_y = pip_y + 30
    alpha_blend_rgba(arr_rgba, commander_cache["Body_Torso"], spr_x, spr_y)
    alpha_blend_rgba(arr_rgba, commander_cache["Head_Base"], spr_x, spr_y)

    # Blink occasionally (e.g. frames 162-164, 198-200)
    is_blinking = (frame_idx % 44) in (18, 19)
    if not is_blinking:
        alpha_blend_rgba(arr_rgba, commander_cache["Left_Eye"], spr_x, spr_y)
        alpha_blend_rgba(arr_rgba, commander_cache["Right_Eye"], spr_x, spr_y)
    else:
        tmp_img = Image.fromarray(arr_rgba, "RGBA")
        td = ImageDraw.Draw(tmp_img)
        td.line((spr_x + 80, spr_y + 92, spr_x + 98, spr_y + 92), fill=(24, 16, 12, 255), width=4)
        td.line((spr_x + 122, spr_y + 92, spr_x + 140, spr_y + 92), fill=(24, 16, 12, 255), width=4)
        arr_rgba = np.array(tmp_img)

    active_viseme = str(cue_row.get("viseme", "Neutral"))
    v_key = f"Viseme_{active_viseme}" if f"Viseme_{active_viseme}" in commander_cache else "Viseme_Neutral"
    alpha_blend_rgba(arr_rgba, commander_cache[v_key], spr_x, spr_y)

    # Right half of PiP Card: Telemetry + Active Viseme Badge + 16 Live Audio Bars
    img_final = Image.fromarray(arr_rgba, "RGBA")
    draw = ImageDraw.Draw(img_final)
    rx = pip_x + 226
    draw.text((rx, pip_y + 52), "CMDR. K-9", font=fonts["hud_title"], fill=(0, 229, 255, 255))
    draw.text((rx, pip_y + 82), "48 kHz PCM LIP-SYNC", font=fonts["mono_sm"], fill=(190, 205, 225, 240))

    draw.rounded_rectangle((rx, pip_y + 106, pip_x + pip_w - 16, pip_y + 136), radius=6, fill=(255, 20, 36, 225))
    draw.text((rx + 8, pip_y + 112), f"VISEME: {active_viseme.upper()}", font=fonts["mono_sm"], fill=(255, 255, 255, 255))

    # 16 Live Waveform Equalizer Bars
    base_y = pip_y + 224
    bar_w = 8
    gap = 3
    for i, val in enumerate(waveform_bars):
        bh = int(8 + val * 62)
        bx0 = rx + i * (bar_w + gap)
        b_col = CRIMSON + (245,) if val > 0.55 else CYAN_ACCENT + (235,)
        draw.rectangle((bx0, base_y - bh, bx0 + bar_w, base_y), fill=b_col)

    # Word-by-Word Kinetic Spanish Subtitles centered above bottom engine status bar
    t_sec = (frame_idx - 1) / float(FPS)
    active_word_idx = -1
    for i, wc in enumerate(word_cues):
        if float(wc["start_sec"]) <= t_sec <= float(wc["end_sec"]) + 0.10:  # type: ignore[arg-type]
            active_word_idx = i
            break

    if word_cues:
        # Show clause window (words 0..3 or 4..6 or 7..10) cleanly
        if active_word_idx < 0:
            active_word_idx = 0 if frame_idx < 165 else len(word_cues) - 1
        if active_word_idx <= 3:
            clause = list(word_cues[0:4])
            clause_offset = 0
        elif active_word_idx <= 6:
            clause = list(word_cues[4:7])
            clause_offset = 4
        else:
            clause = list(word_cues[7:])
            clause_offset = 7

        words_str = [str(w["word"]).upper() for w in clause]
        sub_font = fonts["sub_kinetic"]
        widths = [int(draw.textlength(w + " ", font=sub_font)) for w in words_str]
        total_sw = sum(widths) + 44
        sx_start = (WIDTH - total_sw) // 2
        sy_box = 578

        draw.rounded_rectangle(
            (sx_start, sy_box - 10, sx_start + total_sw, sy_box + 54),
            radius=12,
            fill=(8, 8, 13, 215),
            outline=(255, 20, 36, 175),
            width=2,
        )
        cx = sx_start + 22
        for j, (w_txt, w_px) in enumerate(zip(words_str, widths)):
            is_active = (clause_offset + j) == active_word_idx
            fill_c = (255, 20, 36, 255) if is_active else (250, 250, 250, 235)
            y_off = sy_box + (2 if not is_active else -2)
            draw.text((cx + 2, y_off + 2), w_txt, font=sub_font, fill=(0, 0, 0, 200))
            draw.text((cx, y_off), w_txt, font=sub_font, fill=fill_c)
            cx += w_px

    return np.array(img_final)


def apply_act4_motion_vfx_and_poster(
    frame_bgr: np.ndarray,
    frame_idx: int,
    beat_timestamps: Sequence[float],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> np.ndarray:
    """Apply 808 snap-zooms, anamorphic streak flares, Kodak red halation, grain & TIME Poster slam."""
    t_sec = (frame_idx - 1) / float(FPS)
    impulse = compute_beat_impulse(t_sec, beat_timestamps)

    # 1. 808 Snap-Zoom centered around frame center
    zoom = 1.0 + 0.068 * impulse
    if zoom > 1.001:
        nw, nh = WIDTH / zoom, HEIGHT / zoom
        x1 = (WIDTH - nw) / 2.0
        y1 = (HEIGHT - nh) / 2.0
        M = cv2.getRotationMatrix2D((WIDTH / 2.0, HEIGHT / 2.0), 0.0, zoom)
        frame_bgr = cv2.warpAffine(frame_bgr, M, (WIDTH, HEIGHT), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)

    img_f = frame_bgr.astype(np.float32)

    # 2. Horizontal Anamorphic Cyan/Amber Streak Flares on reactor/LED highlights
    luma = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    bright_mask = (luma > 234).astype(np.float32) * 255.0
    streak = cv2.GaussianBlur(bright_mask, (0, 0), sigmaX=48.0, sigmaY=1.2)
    streak_bgr = np.zeros_like(img_f)
    streak_bgr[:, :, 0] = streak * 0.42  # Cyan-blue
    streak_bgr[:, :, 1] = streak * 0.28
    streak_bgr[:, :, 2] = streak * (0.14 + 0.22 * impulse)

    # 3. Kodak Vision3 500T Warm Red Halation around specular highlights
    halation_mask = (luma > 224).astype(np.float32) * 255.0
    halation = cv2.GaussianBlur(halation_mask, (0, 0), sigmaX=14.0, sigmaY=14.0)
    hal_bgr = np.zeros_like(img_f)
    hal_bgr[:, :, 0] = halation * 0.04
    hal_bgr[:, :, 1] = halation * 0.12
    hal_bgr[:, :, 2] = halation * 0.45

    img_f = np.clip(img_f + streak_bgr + hal_bgr, 0.0, 255.0)

    # 4. Crisp 35mm Film Grain (deterministic per frame)
    rng = np.random.default_rng(1000 + frame_idx)
    grain = rng.normal(0.0, 3.8, size=(HEIGHT, WIDTH, 1)).astype(np.float32)
    img_bgr = np.clip(img_f + grain, 0.0, 255.0).astype(np.uint8)

    img_rgba = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGBA), mode="RGBA")
    draw = ImageDraw.Draw(img_rgba)

    # Top-left Act 4 VFX badge before poster slam
    if frame_idx < 258:
        draw.rounded_rectangle((32, 28, 505, 114), radius=12, fill=(8, 8, 13, 210), outline=(255, 20, 36, 225), width=2)
        draw.text((52, 42), "ACT 04 // AFTER EFFECTS MOTION-VFX", font=fonts["hud_title"], fill=(255, 20, 36, 255))
        draw.text(
            (52, 74),
            f"808 SNAP-ZOOM: {zoom:0.3f}x // KODAK HALATION // FLARE",
            font=fonts["mono_sm"],
            fill=(250, 250, 250, 240),
        )

    # Mid-Act 4 Editorial Kinetic Callouts (F220..F257) framing cleanly on left/right without blocking face
    if 220 <= frame_idx < 258:
        pop_t = min(1.0, (frame_idx - 220) / 8.0)
        stretch_pop = 1.32 + 0.12 * (1.0 - pop_t)
        draw_editorial_text(
            img_rgba,
            "CORE" if frame_idx < 240 else "6 ENGINES",
            (215, 210),
            fonts["poster_mid"],
            PURE_WHITE,
            alpha=245,
            vertical_stretch=stretch_pop,
            letter_spacing=-2,
        )
        draw_editorial_text(
            img_rgba,
            "CRITICAL" if frame_idx < 240 else "UNIFIED",
            (215, 298),
            fonts["poster_mid"],
            CRIMSON,
            alpha=250,
            vertical_stretch=stretch_pop,
            letter_spacing=-3,
            glow_rgb=CRIMSON,
        )

    # Final TIME-Style High-Impact Editorial Poster Slam (F258..F288)
    if frame_idx >= 258:
        slam_u = min(1.0, (frame_idx - 258) / 8.0)
        veil_alpha = int(165 * slam_u)
        veil = Image.new("RGBA", (WIDTH, HEIGHT), (8, 8, 13, veil_alpha))
        img_rgba = Image.alpha_composite(img_rgba, veil)
        d2 = ImageDraw.Draw(img_rgba)

        # Rotating 24-tick minimalist vector clock dial framing the hero title centerpiece (time * 15 deg)
        cx, cy = WIDTH // 2, 336
        dial_rad = 205
        rot_offset = math.radians(t_sec * 15.0)
        d2.ellipse(
            (cx - dial_rad, cy - dial_rad, cx + dial_rad, cy + dial_rad),
            outline=(250, 250, 250, int(68 * slam_u)),
            width=2,
        )
        for tick in range(24):
            ang = rot_offset + (tick * 2.0 * math.pi / 24.0)
            r0 = dial_rad - 14 if tick % 6 == 0 else dial_rad - 8
            r1 = dial_rad
            x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
            x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
            tcol = (255, 20, 36, int(185 * slam_u)) if tick % 6 == 0 else (250, 250, 250, int(110 * slam_u))
            d2.line((x0, y0, x1, y1), fill=tcol, width=3 if tick % 6 == 0 else 1)

        bounce = 1.0 + 0.08 * math.exp(-5.0 * max(0.0, t_sec - (258.0 / FPS))) * math.sin(14.0 * max(0.0, t_sec - (258.0 / FPS)))
        alpha_txt = int(min(255, slam_u * 320))

        # Draw crisp vector 4-point editorial stars flanking header tag (avoids missing font glyph boxes)
        draw_editorial_text(
            img_rgba,
            "IANIMATION MONOREPO",
            (cx, 92),
            fonts["badge"],
            PURE_WHITE,
            alpha=alpha_txt,
            vertical_stretch=1.0,
            letter_spacing=4,
        )
        d_star = ImageDraw.Draw(img_rgba)
        for sx in (cx - 210, cx + 210):
            sy = 92
            star_pts = [
                (sx, sy - 10),
                (sx + 3, sy - 3),
                (sx + 10, sy),
                (sx + 3, sy + 3),
                (sx, sy + 10),
                (sx - 3, sy + 3),
                (sx - 10, sy),
                (sx - 3, sy - 3),
            ]
            d_star.polygon(star_pts, fill=(255, 20, 36, alpha_txt))

        draw_editorial_text(
            img_rgba,
            "CROSS-DIMENSION",
            (cx, 244),
            fonts["poster_sub"],
            PURE_WHITE,
            alpha=alpha_txt,
            vertical_stretch=1.35 * bounce,
            letter_spacing=-2,
        )
        draw_editorial_text(
            img_rgba,
            "RESCUE",
            (cx, 398),
            fonts["poster_hero"],
            CRIMSON,
            alpha=alpha_txt,
            vertical_stretch=1.38 * bounce,
            letter_spacing=-4,
            glow_rgb=CRIMSON,
        )
        draw_editorial_text(
            img_rgba,
            "[ 6 ENGINES // 166 MCP TOOLS // 2026 ]",
            (cx, 588),
            fonts["badge"],
            PURE_WHITE,
            alpha=alpha_txt,
            vertical_stretch=1.0,
            letter_spacing=2,
        )

    return np.array(img_rgba)


def add_bottom_engine_bar(
    arr_rgba: np.ndarray,
    frame_idx: int,
    active_engines: Sequence[int],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> np.ndarray:
    """Draw compact bottom status bar highlighting active subsystem(s) & frame timecode."""
    img = Image.fromarray(arr_rgba, mode="RGBA")
    draw = ImageDraw.Draw(img)

    bar_y0, bar_y1 = 668, 708
    draw.rounded_rectangle((28, bar_y0, WIDTH - 28, bar_y1), radius=10, fill=(8, 10, 16, 212), outline=(65, 82, 105, 190), width=1)

    pill_x = 38
    for idx, label in enumerate(ENGINE_NAMES):
        is_on = idx in active_engines
        pw = 152
        fill_c = (255, 20, 36, 235) if is_on else (22, 28, 40, 180)
        outline_c = (255, 120, 130, 240) if is_on else (55, 68, 86, 160)
        txt_c = (255, 255, 255, 255) if is_on else (130, 145, 165, 210)
        draw.rounded_rectangle((pill_x, bar_y0 + 6, pill_x + pw, bar_y1 - 6), radius=6, fill=fill_c, outline=outline_c, width=1)
        tw = draw.textlength(label, font=fonts["mono_sm"])
        draw.text((pill_x + (pw - tw) / 2, bar_y0 + 12), label, font=fonts["mono_sm"], fill=txt_c)
        pill_x += pw + 8

    t_sec = (frame_idx - 1) / float(FPS)
    tc_str = f"F{frame_idx:03d}/{TOTAL_FRAMES}  {t_sec:05.2f}s  120 BPM"
    tw_tc = draw.textlength(tc_str, font=fonts["mono_sm"])
    draw.text((WIDTH - 46 - tw_tc, bar_y0 + 12), tc_str, font=fonts["mono_sm"], fill=(0, 229, 255, 240))
    return np.array(img)


def compose_all() -> None:
    """Run complete 288-frame VFX composition, MP4/GIF encoding, stills & artifact copy."""
    FRAMES_FINAL_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    with (OUT_DIR / "act1_ik_frames.json").open("r", encoding="utf-8") as f:
        ik_data = json.load(f)
    with (OUT_DIR / "viseme_cues.json").open("r", encoding="utf-8") as f:
        vis_data = json.load(f)
    with (OUT_DIR / "audio_beat_analysis.json").open("r", encoding="utf-8") as f:
        beat_data = json.load(f)

    aoe_summary: Dict[str, object] = {}
    aoe_summary_path = OUT_DIR / "aoe_sector7_summary.json"
    if aoe_summary_path.exists():
        aoe_summary = json.loads(aoe_summary_path.read_text(encoding="utf-8"))

    aoe_radar_rgba: Optional[np.ndarray] = None
    aoe_radar_path = OUT_DIR / "aoe_sector7_radar.png"
    if aoe_radar_path.exists():
        r_bgr = cv2.imread(str(aoe_radar_path), cv2.IMREAD_COLOR)
        if r_bgr is not None:
            r_small = cv2.resize(r_bgr, (144, 144), interpolation=cv2.INTER_AREA)
            aoe_radar_rgba = cv2.cvtColor(r_small, cv2.COLOR_BGR2RGBA)

    ik_frames: List[List[Dict[str, object]]] = ik_data["frames"]
    telemetry_rows: List[Dict[str, object]] = ik_data["ik_telemetry"]
    viseme_frames: List[Dict[str, object]] = vis_data["frames"]
    word_cues: List[Dict[str, object]] = vis_data["word_cues"]
    beat_timestamps: List[float] = [float(b) for b in beat_data["beat_timestamps"]]

    wav_path = OUT_DIR / "master_soundtrack_120bpm.wav"
    waveform_bars, _ = compute_audio_envelopes(wav_path, TOTAL_FRAMES, FPS, num_bars=16)
    commander_cache = build_commander_sprite_cache()

    fonts: Dict[str, ImageFont.FreeTypeFont] = {
        "poster_hero": load_font(FONT_IMPACT, 138),
        "poster_sub": load_font(FONT_IMPACT, 88),
        "poster_mid": load_font(FONT_IMPACT, 56),
        "badge": load_font(FONT_ARIAL_BLACK, 22),
        "hud_title": load_font(FONT_SEGOE_BLACK, 20),
        "hud_sub": load_font(FONT_CONSOLAS_BOLD, 15),
        "mono": load_font(FONT_CONSOLAS_BOLD, 16),
        "mono_sm": load_font(FONT_CONSOLAS_BOLD, 13),
        "sub_kinetic": load_font(FONT_ARIAL_BLACK, 34),
    }

    # Emit compliant After Effects .jsx + scene manifest
    jsx_path = OUT_DIR / "cross_dimension_rescue_comp.jsx"
    emit_after_effects_jsx(jsx_path, beat_timestamps, word_cues)

    manifest = {
        "title": "Cross-Dimension Rescue",
        "resolution": [WIDTH, HEIGHT],
        "fps": FPS,
        "total_frames": TOTAL_FRAMES,
        "duration_seconds": TOTAL_FRAMES / FPS,
        "bpm": beat_data["bpm"],
        "engines_used": [
            "stykanimate-mcp",
            "blender-procedural-lab",
            "ianimation-3d",
            "adobe-animation-mcp",
            "after-effects-motion-engine",
            "aoe-blender-mcp",
        ],
        "aoe_world_artifacts": aoe_summary,
        "user_design_preferences_compliance": {
            "style": "Editorial Poster / TIME Style",
            "crimson_hex": "#FF1424",
            "pure_white_hex": "#FAFAFA",
            "motion_blur": True,
            "justification": "ParagraphJustification.CENTER_JUSTIFY",
            "serif_fallback": False,
        },
        "acts": [
            {"act": 1, "frames": [1, 72], "engine": "stykanimate-mcp", "focus": "2D IK Tactical Pre-Viz & Match Cut"},
            {"act": 2, "frames": [73, 144], "engine": "blender-procedural-lab + ianimation-3d + aoe-blender-mcp", "focus": "2K PBR Corridor, SE(3) Ragdoll + Axe & AOE-UAF WFC/.r16 Radar"},
            {"act": 3, "frames": [145, 216], "engine": "adobe-animation-mcp", "focus": "2D Commander Comms PiP & 48kHz Lip-Sync"},
            {"act": 4, "frames": [217, 288], "engine": "after-effects-motion-engine", "focus": "808 Snap-Zooms, Halation, Flare & TIME Poster (6 Engines / 166 MCP Tools)"},
        ],
    }
    (OUT_DIR / "scene_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Composite all 288 frames
    hero_still_frames: Dict[int, Path] = {
        36: OUT_DIR / "act1_previz_ik.png",
        108: OUT_DIR / "act2_blender_corridor_3d.png",
        178: OUT_DIR / "act3_adobe_comms_lipsync.png",
        268: OUT_DIR / "act4_motion_vfx_climax.png",
    }

    for frame_idx in range(1, TOTAL_FRAMES + 1):
        f3d_path = FRAMES_3D_DIR / f"frame_{frame_idx:04d}.png"
        frame_3d_bgr = cv2.imread(str(f3d_path), cv2.IMREAD_COLOR)
        if frame_3d_bgr is None:
            raise FileNotFoundError(f"Missing 3D corridor frame: {f3d_path}")

        if frame_idx <= 72:
            active = [0] if frame_idx < 58 else [0, 1, 2]
            arr_rgba = render_act1_blueprint_frame(
                frame_idx, ik_frames[frame_idx - 1], telemetry_rows, frame_3d_bgr, fonts
            )
        elif frame_idx <= 144:
            active = [1, 2, 5]
            arr_rgba = add_act2_hud(frame_3d_bgr, frame_idx, aoe_radar_rgba, aoe_summary, fonts)
        elif frame_idx <= 216:
            active = [2, 3]
            arr_rgba = add_act3_adobe_comms_hud(
                frame_3d_bgr,
                frame_idx,
                viseme_frames[frame_idx - 1],
                word_cues,
                waveform_bars[frame_idx - 1],
                commander_cache,
                fonts,
            )
        else:
            active = [0, 1, 2, 3, 4, 5] if frame_idx >= 258 else [2, 4, 5]
            arr_rgba = apply_act4_motion_vfx_and_poster(frame_3d_bgr, frame_idx, beat_timestamps, fonts)

        arr_rgba = add_bottom_engine_bar(arr_rgba, frame_idx, active, fonts)
        out_bgr = cv2.cvtColor(arr_rgba[:, :, :3], cv2.COLOR_RGB2BGR)

        final_frame_path = FRAMES_FINAL_DIR / f"final_{frame_idx:04d}.png"
        cv2.imwrite(str(final_frame_path), out_bgr)

        if frame_idx in hero_still_frames:
            cv2.imwrite(str(hero_still_frames[frame_idx]), out_bgr)

    # Assemble 2560x1440 2x2 Showcase Contact Sheet
    stills_order = [
        OUT_DIR / "act1_previz_ik.png",
        OUT_DIR / "act2_blender_corridor_3d.png",
        OUT_DIR / "act3_adobe_comms_lipsync.png",
        OUT_DIR / "act4_motion_vfx_climax.png",
    ]
    sheet = Image.new("RGB", (WIDTH * 2, HEIGHT * 2), (8, 8, 13))
    positions = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
    for p_img, pos in zip(stills_order, positions):
        with Image.open(p_img) as tile:
            sheet.paste(tile.convert("RGB"), pos)
    contact_sheet_path = OUT_DIR / "showcase_4acts_contact_sheet.png"
    sheet.save(str(contact_sheet_path))

    # Encode Master MP4 (H.264 + AAC 192k stereo) via ffmpeg
    mp4_path = OUT_DIR / "cross_dimension_rescue_master.mp4"
    subprocess.run(
        [
            str(FFMPEG_BIN),
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAMES_FINAL_DIR / "final_%04d.png"),
            "-i",
            str(wav_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "17",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(mp4_path),
        ],
        check=True,
    )

    # Encode optimized 640x360 12 FPS GIF preview
    gif_path = OUT_DIR / "cross_dimension_rescue_preview.gif"
    subprocess.run(
        [
            str(FFMPEG_BIN),
            "-y",
            "-i",
            str(mp4_path),
            "-vf",
            "fps=12,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192[p];[s1][p]paletteuse",
            str(gif_path),
        ],
        check=True,
    )

    # Mirror deliverables cleanly into artifact folder for rich preview
    for copy_target in [
        mp4_path,
        gif_path,
        contact_sheet_path,
        *stills_order,
    ]:
        shutil.copy2(copy_target, BRAIN_DIR / copy_target.name)

    print(f"Master showcase MP4 written: {mp4_path} ({mp4_path.stat().st_size} bytes)")
    print(f"Preview GIF written: {gif_path} ({gif_path.stat().st_size} bytes)")
    print(f"Contact sheet written: {contact_sheet_path}")


if __name__ == "__main__":
    compose_all()
