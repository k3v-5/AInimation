import sys
import json
import asyncio
import os

async def list_voices():
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        return {"status": "SUCCESS", "voices": voices}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

async def synthesize(params):
    import edge_tts
    import soundfile as sf
    import numpy as np

    text = params.get("text", "")
    voice = params.get("voice", "es-MX-DaliaNeural")
    out_wav = params.get("out_wav", "")
    rate = params.get("rate", "+0%")
    pitch = params.get("pitch", "+0Hz")
    volume = params.get("volume", "+0%")

    if not text:
        return {"status": "ERROR", "error": "No text provided"}
    if not out_wav:
        return {"status": "ERROR", "error": "No output path provided"}

    temp_mp3 = out_wav + ".temp.mp3"
    try:
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
        await comm.save(temp_mp3)

        if not os.path.exists(temp_mp3) or os.path.getsize(temp_mp3) == 0:
            return {"status": "ERROR", "error": "Edge-TTS produced empty audio file"}

        data, sr = sf.read(temp_mp3)
        # Convert stereo to mono if needed
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        target_sr = 48000
        if sr != target_sr:
            num_samples = int(len(data) * target_sr / sr)
            resampled = np.interp(np.linspace(0, len(data), num_samples, endpoint=False), np.arange(len(data)), data)
        else:
            resampled = data

        # Peak normalization to -1.0 dBFS (approx 0.89125 max amplitude)
        max_peak = np.max(np.abs(resampled))
        if max_peak > 0:
            resampled = resampled * (0.89125 / max_peak)

        os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
        sf.write(out_wav, resampled, target_sr, subtype='PCM_16')

        duration = len(resampled) / target_sr
        return {
            "status": "SUCCESS",
            "file_path": os.path.abspath(out_wav),
            "duration_seconds": round(duration, 3),
            "sample_rate": target_sr,
            "channels": 1,
            "samples": len(resampled),
            "format": "PCM_16",
            "voice": voice,
            "normalization": "Peak -1.0 dBFS"
        }
    finally:
        if os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
            except Exception:
                pass

async def main():
    # Configure UTF-8 for stdin/stdout to avoid encoding issues with unicode dialogue
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    raw_input = sys.stdin.read()
    if not raw_input.strip():
        print(json.dumps({"status": "ERROR", "error": "Empty input"}))
        return

    try:
        payload = json.loads(raw_input)
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error": f"Invalid JSON input: {e}"}))
        return

    mode = payload.get("mode", "synth")
    if mode == "list":
        res = await list_voices()
        print(json.dumps(res))
    elif mode == "synth":
        res = await synthesize(payload)
        print(json.dumps(res))
    else:
        print(json.dumps({"status": "ERROR", "error": f"Unknown mode: {mode}"}))

if __name__ == "__main__":
    asyncio.run(main())
