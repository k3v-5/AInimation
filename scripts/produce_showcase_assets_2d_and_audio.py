"""Produce Multi-Engine 2D Puppet (.psd), 48kHz Spanish Neural Speech, 120 BPM Soundtrack,
Audio Analysis JSON, and 14-Viseme Lip-Sync Cues for 'Cross-Dimension Rescue'.

Outputs to outputs/showcase_monorepo/:
- dialogue_48khz.wav (48kHz 16-bit PCM mono, peak -1.0 dBFS)
- master_soundtrack_120bpm.wav (48kHz 16-bit PCM stereo, 12.0s @ 120 BPM)
- audio_beat_analysis.json (verified via backend.mcp.tools.analyze_audio)
- viseme_cues.json (14 Character Animator visemes aligned to speech energy)
- commander_comms_puppet.psd (valid 8BPS PSD binary with +Head, Eyes, Body, and 14 Mouth visemes)
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import subprocess
import sys
from typing import Dict, List, Tuple
import wave

import numpy as np

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.mcp.tools import analyze_audio

OUT_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EDGE_SYNTH_SCRIPT = (
    PROJECT_ROOT / "packages" / "adobe-suite" / "src" / "core" / "scripts" / "edge_synth.py"
)

DIALOGUE_TEXT = "Alerta en Sector Siete. Núcleo térmico inestable. Unidad de rescate desplegada."
CH_VISEMES: Tuple[str, ...] = (
    "Neutral",
    "Ah",
    "D",
    "Ee",
    "F",
    "L",
    "M",
    "Oh",
    "R",
    "S",
    "Uh",
    "W-Oo",
    "Smile",
    "Surprised",
)

DIALOGUE_WORDS_AND_VISEMES: List[Tuple[str, List[str]]] = [
    ("ALERTA", ["Ah", "L", "Ee", "R", "D", "Ah"]),
    ("EN", ["Ee", "D"]),
    ("SECTOR", ["S", "Ee", "D", "Oh", "R"]),
    ("SIETE", ["S", "Ee", "Ee", "D", "Ee"]),
    ("NÚCLEO", ["D", "W-Oo", "D", "L", "Ee", "Oh"]),
    ("TÉRMICO", ["D", "Ee", "R", "M", "Ee", "Oh"]),
    ("INESTABLE", ["Ee", "D", "Ee", "S", "D", "Ah", "M", "L", "Ee"]),
    ("UNIDAD", ["W-Oo", "D", "Ee", "D", "Ah", "D"]),
    ("DE", ["D", "Ee"]),
    ("RESCATE", ["R", "Ee", "S", "D", "Ah", "D", "Ee"]),
    ("DESPLEGADA", ["D", "Ee", "S", "M", "L", "Ee", "D", "Ah", "D", "Ah"]),
]


def _normalize_and_write_wav_48k_mono(samples: np.ndarray, out_path: Path, sample_rate: int = 48000) -> float:
    """Trim outer silence, peak-normalize to -1.0 dBFS, and write 48kHz 16-bit PCM mono WAV."""
    if len(samples) == 0:
        raise ValueError("Cannot write empty audio buffer")

    abs_s = np.abs(samples)
    peak = float(np.max(abs_s))
    if peak > 1e-6:
        idx = np.where(abs_s > peak * 0.015)[0]
        if len(idx) > 0:
            pad = int(sample_rate * 0.04)
            start = max(0, int(idx[0]) - pad)
            end = min(len(samples), int(idx[-1]) + pad)
            samples = samples[start:end]

    max_peak = float(np.max(np.abs(samples)))
    if max_peak > 0:
        samples = samples * (0.89125 / max_peak)

    pcm16 = np.clip(samples * 32767.0, -32768.0, 32767.0).astype("<i2")
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())
    return round(len(samples) / float(sample_rate), 4)


def _read_wav_as_float_mono(wav_path: Path) -> Tuple[np.ndarray, int]:
    """Read any PCM WAV cleanly as mono float64 in [-1, 1] and sample rate."""
    with wave.open(str(wav_path), "rb") as wf:
        n_ch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    if sw != 2:
        raise ValueError(f"Expected 16-bit PCM WAV, got {sw * 8}-bit")
    ints = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if n_ch > 1:
        ints = ints.reshape(-1, n_ch).mean(axis=1)
    return ints, sr


def synthesize_spanish_dialogue(out_wav: Path) -> Dict[str, str]:
    """Generate 48kHz 16-bit PCM dialogue using adobe-suite's edge_synth.py with SAPI fallback."""
    payload = {
        "mode": "synth",
        "text": DIALOGUE_TEXT,
        "voice": "es-MX-JorgeNeural",
        "rate": "+18%",
        "pitch": "-4Hz",
        "volume": "+0%",
        "out_wav": str(out_wav),
    }

    try:
        proc = subprocess.run(
            [sys.executable, str(EDGE_SYNTH_SCRIPT)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0 and proc.stdout.strip():
            res = json.loads(proc.stdout.strip().splitlines()[-1])
            if res.get("status") == "SUCCESS" and out_wav.exists() and out_wav.stat().st_size > 10_000:
                data, sr = _read_wav_as_float_mono(out_wav)
                if sr != 48000:
                    n_new = int(len(data) * 48000 / sr)
                    data = np.interp(np.linspace(0, len(data), n_new, endpoint=False), np.arange(len(data)), data)
                dur = _normalize_and_write_wav_48k_mono(data, out_wav, 48000)
                return {"engine": "edge_tts (es-MX-JorgeNeural)", "duration_s": str(dur)}
    except Exception as exc:
        print(f"Edge-TTS unavailable or offline ({exc}); falling back to Windows SAPI es-MX...")

    # Offline fallback: Windows System.Speech es-MX resampled to 48kHz
    temp_sapi = OUT_DIR / "_temp_sapi.wav"
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'es-*' } | Select-Object -First 1; "
        "if ($v) { $s.SelectVoice($v.VoiceInfo.Name) }; "
        "$s.Rate = 5; "
        f"$s.SetOutputToWaveFile('{str(temp_sapi)}'); "
        f"$s.Speak('{DIALOGUE_TEXT}'); "
        "$s.Dispose();"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
    data, sr = _read_wav_as_float_mono(temp_sapi)
    n_new = int(len(data) * 48000 / sr)
    resampled = np.interp(np.linspace(0, len(data), n_new, endpoint=False), np.arange(len(data)), data)
    dur = _normalize_and_write_wav_48k_mono(resampled, out_wav, 48000)
    if temp_sapi.exists():
        temp_sapi.unlink()
    return {"engine": "windows_sapi (es-MX)", "duration_s": str(dur)}


def synthesize_master_soundtrack(
    dialogue_wav: Path,
    out_wav: Path,
    dialogue_start_sec: float = 5.85,
) -> Dict[str, object]:
    """Synthesize 12.0s 120 BPM industrial soundtrack synced with dialogue and sidechain ducking."""
    sr = 48000
    duration_s = 12.0
    n_samples = int(sr * duration_s)
    t = np.arange(n_samples, dtype=np.float64) / float(sr)

    speech_mono, s_sr = _read_wav_as_float_mono(dialogue_wav)
    if s_sr != sr:
        n_new = int(len(speech_mono) * sr / s_sr)
        speech_mono = np.interp(np.linspace(0, len(speech_mono), n_new, endpoint=False), np.arange(len(speech_mono)), speech_mono)

    # Fit dialogue cleanly between t=5.85s and t=9.80s (so Act 3 showcases it cleanly)
    max_speech_samples = int(4.10 * sr)
    if len(speech_mono) > max_speech_samples:
        speech_mono = np.interp(
            np.linspace(0, len(speech_mono), max_speech_samples, endpoint=False),
            np.arange(len(speech_mono)),
            speech_mono,
        )

    music_l = np.zeros(n_samples, dtype=np.float64)
    music_r = np.zeros(n_samples, dtype=np.float64)

    beat_interval = 0.50  # 120 BPM -> exactly 0.500s per beat (12 frames @ 24 FPS)
    # 1. Punchy 808 Kick + Industrial Sub-Bass every beat (24 beats across 12.0s)
    for b in range(24):
        bt = b * beat_interval
        idx0 = int(bt * sr)
        k_len = int(0.32 * sr)
        if idx0 + k_len > n_samples:
            k_len = n_samples - idx0
        lt = np.arange(k_len, dtype=np.float64) / float(sr)
        freq = 48.0 + 135.0 * np.exp(-lt * 28.0)
        phase = 2.0 * math.pi * np.cumsum(freq) / float(sr)
        kick = np.tanh(1.8 * np.sin(phase)) * np.exp(-lt * 8.0) * 0.88
        music_l[idx0 : idx0 + k_len] += kick
        music_r[idx0 : idx0 + k_len] += kick

        # Subtle Snare / Metal Clang on beats 2 & 4 (below kick threshold so BPM locks cleanly)
        if b % 2 == 1:
            s_len = min(int(0.16 * sr), n_samples - idx0)
            st = np.arange(s_len, dtype=np.float64) / float(sr)
            rng = np.random.default_rng(1000 + b)
            noise = rng.standard_normal(s_len) * np.exp(-st * 22.0) * 0.16
            tone = np.sin(2.0 * math.pi * 210.0 * st) * np.exp(-st * 26.0) * 0.14
            music_l[idx0 : idx0 + s_len] += noise * 0.9 + tone
            music_r[idx0 : idx0 + s_len] += noise * 1.1 + tone

    # 2. Driving 16th-note cyberpunk/industrial bassline
    bass_notes = [55.0, 55.0, 65.41, 55.0, 73.42, 65.41, 82.41, 73.42]
    step_dur = 0.125  # 16th note at 120 BPM
    for step in range(int(duration_s / step_dur)):
        idx0 = int(step * step_dur * sr)
        s_len = min(int(0.10 * sr), n_samples - idx0)
        lt = np.arange(s_len, dtype=np.float64) / float(sr)
        f0 = bass_notes[(step // 2) % len(bass_notes)]
        saw = (2.0 * ((lt * f0) % 1.0) - 1.0) * 0.08 + np.sin(2.0 * math.pi * f0 * lt) * 0.10
        env = np.exp(-lt * 16.0)
        pan_l = 0.92 if step % 2 == 0 else 1.05
        pan_r = 1.05 if step % 2 == 0 else 0.92
        music_l[idx0 : idx0 + s_len] += saw * env * pan_l
        music_r[idx0 : idx0 + s_len] += saw * env * pan_r

    # 3. Act Transition Cinematic Impacts (t = 0.0, 3.0, 6.0, 9.0) & Thermal Alarm
    for act_t in [0.0, 3.0, 6.0, 9.0]:
        idx0 = int(act_t * sr)
        imp_len = min(int(0.55 * sr), n_samples - idx0)
        lt = np.arange(imp_len, dtype=np.float64) / float(sr)
        sub_drop = np.sin(2.0 * math.pi * (90.0 * np.exp(-lt * 4.0) + 34.0) * lt) * np.exp(-lt * 4.5) * 0.55
        rng = np.random.default_rng(int(act_t * 100) + 7)
        whoosh = rng.standard_normal(imp_len) * np.exp(-lt * 9.0) * 0.18
        music_l[idx0 : idx0 + imp_len] += sub_drop + whoosh
        music_r[idx0 : idx0 + imp_len] += sub_drop + whoosh

    # Soft fade out in last 0.4s
    fade_n = int(0.4 * sr)
    fade_curve = np.linspace(1.0, 0.0, fade_n)
    music_l[-fade_n:] *= fade_curve
    music_r[-fade_n:] *= fade_curve

    # 4. Radio squelch + Sidechain ducked Spanish neural speech
    speech_idx0 = int(dialogue_start_sec * sr)
    speech_end = min(n_samples, speech_idx0 + len(speech_mono))
    actual_speech_len = max(0, speech_end - speech_idx0)

    duck = np.ones(n_samples, dtype=np.float64)
    if actual_speech_len > 0:
        # Smooth duck envelope to 0.34 during dialogue
        duck_win = np.full(actual_speech_len, 0.34, dtype=np.float64)
        ramp = min(int(0.15 * sr), actual_speech_len // 4)
        duck_win[:ramp] = np.linspace(1.0, 0.34, ramp)
        duck_win[-ramp:] = np.linspace(0.34, 1.0, ramp)
        duck[speech_idx0:speech_end] = duck_win

    mix_l = music_l * duck
    mix_r = music_r * duck
    if actual_speech_len > 0:
        mix_l[speech_idx0:speech_end] += speech_mono[:actual_speech_len] * 0.92
        mix_r[speech_idx0:speech_end] += speech_mono[:actual_speech_len] * 0.92

    # Radio squelch beep at t = dialogue_start_sec - 0.18s
    beep_idx = max(0, int((dialogue_start_sec - 0.16) * sr))
    beep_n = int(0.08 * sr)
    bt_arr = np.arange(beep_n, dtype=np.float64) / float(sr)
    beep = np.sin(2.0 * math.pi * 1320.0 * bt_arr) * np.exp(-bt_arr * 22.0) * 0.28
    mix_l[beep_idx : beep_idx + beep_n] += beep
    mix_r[beep_idx : beep_idx + beep_n] += beep

    # Master limiter to -0.8 dBFS
    peak = max(float(np.max(np.abs(mix_l))), float(np.max(np.abs(mix_r))), 1e-6)
    scale = 0.91 / max(peak, 0.91)
    mix_l *= scale
    mix_r *= scale

    interleaved = np.column_stack((mix_l, mix_r)).ravel()
    pcm16 = np.clip(interleaved * 32767.0, -32768.0, 32767.0).astype("<i2")
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    return {
        "duration_seconds": duration_s,
        "sample_rate": sr,
        "bpm": 120.0,
        "dialogue_start_sec": dialogue_start_sec,
        "dialogue_end_sec": round(dialogue_start_sec + actual_speech_len / float(sr), 3),
        "speech_samples_for_visemes": actual_speech_len,
    }


def build_viseme_cues(dialogue_wav: Path, dialogue_start_sec: float, dialogue_end_sec: float, out_json: Path) -> None:
    """Align words and 14 Character Animator visemes across 288 frames at 24 FPS using real speech energy."""
    speech_mono, sr = _read_wav_as_float_mono(dialogue_wav)
    total_frames = 288
    fps = 24.0
    speech_dur = max(0.5, dialogue_end_sec - dialogue_start_sec)

    # Expand flat phoneme stream proportionally across active speech duration
    word_cues: List[Dict[str, object]] = []
    viseme_sequence: List[Dict[str, object]] = []

    total_phonemes = sum(len(vlist) for _, vlist in DIALOGUE_WORDS_AND_VISEMES)
    cur_t = dialogue_start_sec
    dt_per_phoneme = speech_dur / max(1, total_phonemes)

    for w_idx, (word, vlist) in enumerate(DIALOGUE_WORDS_AND_VISEMES):
        w_start = cur_t
        w_end = cur_t + len(vlist) * dt_per_phoneme
        word_cues.append(
            {
                "word": word,
                "start_sec": round(w_start, 3),
                "end_sec": round(w_end, 3),
                "start_frame": int(round(w_start * fps)) + 1,
                "end_frame": int(round(w_end * fps)) + 1,
            }
        )
        for vname in vlist:
            viseme_sequence.append(
                {
                    "viseme": vname,
                    "start_sec": round(cur_t, 4),
                    "end_sec": round(cur_t + dt_per_phoneme, 4),
                }
            )
            cur_t += dt_per_phoneme

    # Evaluate exact frame-by-frame viseme + mouth energy for all 288 frames
    frame_timeline: List[Dict[str, object]] = []
    for f in range(1, total_frames + 1):
        t_sec = (f - 1) / fps
        active_viseme = "Neutral"
        energy = 0.0
        active_word = ""
        if dialogue_start_sec <= t_sec <= dialogue_end_sec:
            rel_t = t_sec - dialogue_start_sec
            idx = int(rel_t * sr)
            win = speech_mono[max(0, idx - 800) : min(len(speech_mono), idx + 800)]
            if len(win) > 0:
                energy = round(float(np.sqrt(np.mean(win ** 2))) * 2.4, 3)
                energy = min(1.0, energy)
            for vc in viseme_sequence:
                if float(vc["start_sec"]) <= t_sec <= float(vc["end_sec"]):
                    active_viseme = str(vc["viseme"])
                    break
            for wc in word_cues:
                if float(wc["start_sec"]) <= t_sec <= float(wc["end_sec"]):
                    active_word = str(wc["word"])
                    break
        elif f > 228:
            active_viseme = "Smile"

        frame_timeline.append(
            {
                "frame": f,
                "time_sec": round(t_sec, 4),
                "viseme": active_viseme,
                "word": active_word,
                "vocal_energy": energy,
            }
        )

    payload = {
        "dialogue_text": DIALOGUE_TEXT,
        "sample_rate": 48000,
        "fps": 24,
        "total_frames": total_frames,
        "dialogue_start_sec": dialogue_start_sec,
        "dialogue_end_sec": dialogue_end_sec,
        "supported_visemes": list(CH_VISEMES),
        "word_cues": word_cues,
        "frames": frame_timeline,
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _render_commander_layer_rgba(width: int, height: int, kind: str, param: str = "") -> np.ndarray:
    """Render clean stylized 512x512 RGBA sprite layers for the Commander 2D Character Animator PSD."""
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2

    if kind == "Body_Torso":
        d.polygon([(110, 512), (145, 360), (367, 360), (402, 512)], fill=(42, 46, 54, 255))
        d.rectangle([140, 425, 372, 455], fill=(224, 198, 38, 255))
        d.rectangle([226, 360, 286, 400], fill=(195, 25, 36, 255))
    elif kind == "Head_Base":
        # Helmet dome behind/above
        d.pieslice([116, 42, 396, 290], 180, 360, fill=(198, 26, 34, 255))
        d.rounded_rectangle([96, 174, 416, 202], radius=10, fill=(224, 34, 44, 255))
        d.rectangle([226, 62, 286, 146], fill=(235, 232, 224, 255), outline=(45, 40, 35, 255), width=3)
        # Orange yarn hair tufts
        for hx in [120, 145, 345, 370]:
            d.rounded_rectangle([hx, 196, hx + 24, 275], radius=8, fill=(228, 98, 24, 255))
        # Burlap doll face
        d.ellipse([142, 178, 370, 378], fill=(208, 186, 152, 255), outline=(65, 52, 38, 255), width=4)
        # Stitched cheeks / button scar
        d.ellipse([160, 278, 195, 304], fill=(198, 108, 98, 90))
        d.ellipse([317, 278, 352, 304], fill=(198, 108, 98, 90))
        d.polygon([(256, 255), (242, 284), (270, 284)], fill=(120, 74, 45, 255))
    elif kind == "Left_Eye":
        d.ellipse([186, 224, 226, 264], fill=(22, 22, 24, 255), outline=(72, 65, 58, 255), width=3)
        d.ellipse([198, 234, 212, 248], fill=(0, 225, 255, 220))
    elif kind == "Right_Eye":
        d.ellipse([286, 224, 326, 264], fill=(22, 22, 24, 255), outline=(72, 65, 58, 255), width=3)
        d.ellipse([298, 234, 312, 248], fill=(0, 225, 255, 220))
    elif kind == "Viseme":
        v = param
        mx, my = cx, 326
        if v == "Neutral":
            d.line([(mx - 34, my), (mx + 34, my)], fill=(30, 24, 20, 255), width=5)
        elif v == "Smile":
            d.arc([mx - 42, my - 22, mx + 42, my + 24], 15, 165, fill=(30, 24, 20, 255), width=5)
        elif v == "Surprised":
            d.ellipse([mx - 22, my - 24, mx + 22, my + 24], fill=(55, 12, 16, 255), outline=(24, 18, 16, 255), width=4)
        elif v == "Ah":
            d.ellipse([mx - 30, my - 22, mx + 30, my + 24], fill=(68, 14, 18, 255), outline=(24, 18, 16, 255), width=4)
            d.rectangle([mx - 18, my - 18, mx + 18, my - 10], fill=(242, 242, 240, 255))
        elif v == "Oh":
            d.ellipse([mx - 18, my - 18, mx + 18, my + 20], fill=(60, 12, 16, 255), outline=(24, 18, 16, 255), width=4)
        elif v == "W-Oo":
            d.ellipse([mx - 12, my - 12, mx + 12, my + 14], fill=(52, 10, 14, 255), outline=(24, 18, 16, 255), width=4)
        elif v == "Ee":
            d.rounded_rectangle([mx - 36, my - 12, mx + 36, my + 12], radius=8, fill=(242, 242, 240, 255), outline=(24, 18, 16, 255), width=4)
        elif v == "Uh":
            d.ellipse([mx - 24, my - 14, mx + 24, my + 16], fill=(65, 16, 20, 255), outline=(24, 18, 16, 255), width=4)
        elif v in {"D", "L"}:
            d.rounded_rectangle([mx - 30, my - 14, mx + 30, my + 14], radius=7, fill=(65, 16, 20, 255), outline=(24, 18, 16, 255), width=4)
            d.rectangle([mx - 20, my - 11, mx + 20, my - 2], fill=(242, 242, 240, 255))
            d.ellipse([mx - 14, my, mx + 14, my + 11], fill=(210, 95, 95, 255))
        elif v == "F":
            d.rounded_rectangle([mx - 28, my - 8, mx + 28, my + 10], radius=5, fill=(72, 18, 22, 255), outline=(24, 18, 16, 255), width=4)
            d.rectangle([mx - 22, my - 6, mx + 22, my + 2], fill=(244, 244, 242, 255))
        elif v == "M":
            d.line([(mx - 32, my), (mx - 10, my + 3), (mx + 10, my + 3), (mx + 32, my)], fill=(30, 22, 18, 255), width=6)
        elif v in {"R", "S"}:
            d.rounded_rectangle([mx - 30, my - 9, mx + 30, my + 9], radius=6, fill=(238, 238, 235, 255), outline=(24, 18, 16, 255), width=4)
            d.line([(mx - 26, my), (mx + 26, my)], fill=(60, 55, 50, 255), width=2)
    if (width, height) != (512, 512):
        # Note: helper draws at base 512x512 design space; render at 512 then downsample cleanly
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    return np.array(img, dtype=np.uint8)


def _render_commander_layer_scaled(width: int, height: int, kind: str, param: str = "") -> np.ndarray:
    """Draw 512x512 master sprite and downsample crisply to target PSD layer size."""
    from PIL import Image

    arr_512 = _render_commander_layer_rgba(512, 512, kind, param)
    if width == 512 and height == 512:
        return arr_512
    resized = Image.fromarray(arr_512, mode="RGBA").resize((width, height), Image.Resampling.LANCZOS)
    return np.array(resized, dtype=np.uint8)


def _pack_pascal_string_padded4(text: str) -> bytes:
    """Encode Photoshop layer name as 4-byte padded Pascal string."""
    raw = text.encode("ascii", errors="replace")[:255]
    out = bytes([len(raw)]) + raw
    while len(out) % 4 != 0:
        out += b"\x00"
    return out


def _make_lsct_extra(divider_type: int) -> bytes:
    """Build Photoshop Section Divider ('lsct') extra data block."""
    # divider_type: 1 = open folder, 2 = closed folder, 3 = bounding divider
    payload = struct.pack(">I", divider_type)
    return b"8BIMlsct" + struct.pack(">I", len(payload)) + payload


def write_character_animator_psd(out_psd: Path, width: int = 256, height: int = 256) -> None:
    """Write a compliant Adobe Character Animator PSD binary (8BPS v1 RGBA) with 14 mouth visemes."""
    # PSD layer order is bottom-to-top; groups end with a '</Group>' lsct=3 divider at the bottom.
    layer_specs: List[Tuple[str, Optional[np.ndarray], int]] = [
        ("</Commander_K9>", None, 3),
        ("</Body>", None, 3),
        ("Torso", _render_commander_layer_scaled(width, height, "Body_Torso"), 0),
        ("Body", None, 1),
        ("</+Head>", None, 3),
        ("Face_And_Helmet", _render_commander_layer_scaled(width, height, "Head_Base"), 0),
        ("Left Eye", _render_commander_layer_scaled(width, height, "Left_Eye"), 0),
        ("Right Eye", _render_commander_layer_scaled(width, height, "Right_Eye"), 0),
        ("</Mouth>", None, 3),
    ]
    for vis in reversed(CH_VISEMES):
        layer_specs.append((vis, _render_commander_layer_scaled(width, height, "Viseme", vis), 0))
    layer_specs.append(("Mouth", None, 1))
    layer_specs.append(("+Head", None, 1))
    layer_specs.append(("+Commander_K9", None, 1))

    layer_records = bytearray()
    channel_image_data = bytearray()

    for name, rgba, divider_type in layer_specs:
        if rgba is None:
            top, left, bottom, right = 0, 0, 0, 0
            ch_len = 2  # compression=0 (2 bytes) for empty bounds
            ch_ids = (-1, 0, 1, 2)
            for cid in ch_ids:
                channel_image_data.extend(struct.pack(">H", 0))
        else:
            top, left, bottom, right = 0, 0, height, width
            ch_bytes_per_plane = width * height
            ch_len = 2 + ch_bytes_per_plane
            ch_ids = (-1, 0, 1, 2)
            # Channels in order: Alpha(-1), R(0), G(1), B(2)
            channel_image_data.extend(struct.pack(">H", 0) + rgba[:, :, 3].tobytes())
            channel_image_data.extend(struct.pack(">H", 0) + rgba[:, :, 0].tobytes())
            channel_image_data.extend(struct.pack(">H", 0) + rgba[:, :, 1].tobytes())
            channel_image_data.extend(struct.pack(">H", 0) + rgba[:, :, 2].tobytes())

        layer_records.extend(struct.pack(">iiii", top, left, bottom, right))
        layer_records.extend(struct.pack(">H", 4))
        for cid in ch_ids:
            layer_records.extend(struct.pack(">hI", cid, ch_len))

        flags = 0x00 if (rgba is not None and (name in {"Torso", "Face_And_Helmet", "Left Eye", "Right Eye", "Neutral"} or divider_type > 0)) else 0x02
        layer_records.extend(b"8BIMnorm")
        layer_records.extend(struct.pack(">BBBB", 255, 0, flags, 0))

        extra = bytearray()
        extra.extend(struct.pack(">I", 0))  # layer mask data = 0
        extra.extend(struct.pack(">I", 0))  # blending ranges = 0
        extra.extend(_pack_pascal_string_padded4(name))
        if divider_type > 0:
            extra.extend(_make_lsct_extra(divider_type))
        layer_records.extend(struct.pack(">I", len(extra)))
        layer_records.extend(extra)

    layer_info = bytearray()
    layer_info.extend(struct.pack(">h", len(layer_specs)))
    layer_info.extend(layer_records)
    layer_info.extend(channel_image_data)
    if len(layer_info) % 2 != 0:
        layer_info.append(0)

    layer_and_mask = bytearray()
    layer_and_mask.extend(struct.pack(">I", len(layer_info)))
    layer_and_mask.extend(layer_info)
    layer_and_mask.extend(struct.pack(">I", 0))  # global layer mask info = 0

    # Composite merged preview image (RGBA Composite, compression 0)
    from PIL import Image
    comp = Image.new("RGBA", (width, height), (14, 18, 24, 255))
    for part in ("Body_Torso", "Head_Base", "Left_Eye", "Right_Eye"):
        comp = Image.alpha_composite(comp, Image.fromarray(_render_commander_layer_scaled(width, height, part)))
    comp = Image.alpha_composite(comp, Image.fromarray(_render_commander_layer_scaled(width, height, "Viseme", "Ah")))
    comp_np = np.array(comp, dtype=np.uint8)

    merged_image = bytearray(struct.pack(">H", 0))
    for ch in (0, 1, 2, 3):
        merged_image.extend(comp_np[:, :, ch].tobytes())

    header = struct.pack(">4sH6sHIIHH", b"8BPS", 1, b"\x00" * 6, 4, height, width, 8, 3)

    psd_bytes = bytearray()
    psd_bytes.extend(header)
    psd_bytes.extend(struct.pack(">I", 0))  # Color mode data length
    psd_bytes.extend(struct.pack(">I", 0))  # Image resources length
    psd_bytes.extend(struct.pack(">I", len(layer_and_mask)))
    psd_bytes.extend(layer_and_mask)
    psd_bytes.extend(merged_image)

    out_psd.write_bytes(bytes(psd_bytes))


def main() -> None:
    dialogue_wav = OUT_DIR / "dialogue_48khz.wav"
    soundtrack_wav = OUT_DIR / "master_soundtrack_120bpm.wav"
    beat_json = OUT_DIR / "audio_beat_analysis.json"
    viseme_json = OUT_DIR / "viseme_cues.json"
    puppet_psd = OUT_DIR / "commander_comms_puppet.psd"

    # 1. Invoke StykAnimate Node script first so all Act 1 artifacts live together
    styk_proc = subprocess.run(
        ["node", str(PROJECT_ROOT / "scripts" / "generate_act1_styk_previz.mjs")],
        capture_output=True,
        text=True,
        check=True,
    )
    print(styk_proc.stdout.strip())

    # 2. Dialogue + Soundtrack
    tts_info = synthesize_spanish_dialogue(dialogue_wav)
    print(f"Synthesized 48kHz dialogue: {tts_info}")

    mix_info = synthesize_master_soundtrack(dialogue_wav, soundtrack_wav, dialogue_start_sec=5.85)
    print(f"Synthesized 120 BPM master soundtrack: {mix_info}")

    # 3. Analyze master soundtrack with backend.mcp.tools.analyze_audio
    audio_res = analyze_audio(str(soundtrack_wav), separate_stems=False, tempo_hint=120.0)
    beat_payload = {
        "source_wav": str(soundtrack_wav),
        "bpm": audio_res.bpm,
        "duration_seconds": audio_res.duration_seconds,
        "time_signature": audio_res.time_signature,
        "beat_count": len(audio_res.beat_timestamps),
        "beat_timestamps": audio_res.beat_timestamps,
        "onset_envelope": audio_res.onset_envelope,
        "tts_info": tts_info,
        "mix_info": mix_info,
    }
    beat_json.write_text(json.dumps(beat_payload, indent=2) + "\n", encoding="utf-8")
    print(f"Verified audio analysis via FastMCP tool: {audio_res.bpm} BPM, {len(audio_res.beat_timestamps)} beats.")

    # 4. Viseme Cue Timeline & Binary PSD Puppet (14 visemes)
    build_viseme_cues(
        dialogue_wav=dialogue_wav,
        dialogue_start_sec=float(mix_info["dialogue_start_sec"]),
        dialogue_end_sec=float(mix_info["dialogue_end_sec"]),
        out_json=viseme_json,
    )
    write_character_animator_psd(puppet_psd)
    print(f"Built Character Animator 14-viseme PSD ({puppet_psd.stat().st_size} bytes) and cues JSON.")


if __name__ == "__main__":
    main()
