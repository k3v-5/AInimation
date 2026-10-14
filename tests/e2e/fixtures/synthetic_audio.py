"""
Synthetic audio fixture generators for IANIMATION E2E tests.
Provides valid IEEE PCM .wav files, rhythmic beat pulses, silence, and corrupt audio files.
"""
from __future__ import annotations

import math
from pathlib import Path
import struct
import wave


def create_sine_wave_wav(
    file_path: Path,
    duration_seconds: float = 2.0,
    sample_rate: int = 44100,
    frequency: float = 440.0,
    amplitude: float = 0.5,
) -> Path:
    """Generate a clean single-tone PCM WAV file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_seconds * sample_rate)
    
    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            time_val = float(i) / float(sample_rate)
            sample_float = amplitude * math.sin(2.0 * math.pi * frequency * time_val)
            sample_int = int(sample_float * 32767.0)
            sample_int = max(-32768, min(32767, sample_int))
            frames.extend(struct.pack("<h", sample_int))
            
        wav_file.writeframes(bytes(frames))
        
    return file_path


def create_rhythmic_pulse_wav(
    file_path: Path,
    bpm: float = 120.0,
    duration_seconds: float = 4.0,
    sample_rate: int = 44100,
) -> Path:
    """
    Generate a rhythmic pulse track with distinct transient spikes at regular BPM intervals.
    Useful for validating beat tracking, BPM detection, and onset envelope algorithms.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_seconds * sample_rate)
    beat_interval_seconds = 60.0 / bpm
    samples_per_beat = int(beat_interval_seconds * sample_rate)
    
    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        pulse_width_samples = int(0.02 * sample_rate)  # 20ms click/pulse
        
        for i in range(num_samples):
            beat_offset = i % samples_per_beat if samples_per_beat > 0 else 0
            if beat_offset < pulse_width_samples:
                # High energy transient impulse
                decay = 1.0 - (beat_offset / pulse_width_samples)
                sample_float = 0.9 * decay * math.sin(2.0 * math.pi * 1000.0 * (beat_offset / sample_rate))
            else:
                # Low background rumble
                time_val = float(i) / float(sample_rate)
                sample_float = 0.05 * math.sin(2.0 * math.pi * 120.0 * time_val)
                
            sample_int = int(sample_float * 32767.0)
            sample_int = max(-32768, min(32767, sample_int))
            frames.extend(struct.pack("<h", sample_int))
            
        wav_file.writeframes(bytes(frames))
        
    return file_path


def create_silent_wav(
    file_path: Path,
    duration_seconds: float = 1.0,
    sample_rate: int = 44100,
) -> Path:
    """Generate a valid WAV file consisting entirely of digital silence."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_seconds * sample_rate)
    
    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Zeroes for 16-bit PCM
        zero_frames = bytes(num_samples * 2)
        wav_file.writeframes(zero_frames)
        
    return file_path


def create_corrupt_wav(file_path: Path) -> Path:
    """Generate a corrupt audio file with an invalid RIFF header and truncated payload."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt_bytes = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00CORRUPT_PAYLOAD"
    file_path.write_bytes(corrupt_bytes)
    return file_path
