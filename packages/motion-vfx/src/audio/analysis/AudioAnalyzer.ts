import { AudioBuffer } from "../core/AudioBuffer.js";
import { AudioMath } from "../core/AudioMath.js";
import { Beat, BeatMap, SilenceInterval, WaveformPeak } from "../types/index.js";

export interface BeatDetectionOptions {
  windowSizeMs?: number;
  sensitivity?: number;
  minIntervalMs?: number;
}

/**
 * Analizador acústico determinista para generación de forma de onda, detección de silencio y beats (Fase 5D).
 */
export class AudioAnalyzer {
  /**
   * Calcula la energía RMS (Root Mean Square) del buffer en todas sus pistas.
   */
  public static calculateRMS(buffer: AudioBuffer): number {
    if (buffer.frames === 0) return 0;

    let sumSquares = 0;
    const totalSamples = buffer.frames * buffer.channels;

    for (let c = 0; c < buffer.channels; c++) {
      const ch = buffer.data[c];
      for (let i = 0; i < buffer.frames; i++) {
        sumSquares += ch[i] * ch[i];
      }
    }

    return Math.sqrt(sumSquares / totalSamples);
  }

  /**
   * Obtiene la amplitud pico absoluta en el buffer.
   */
  public static calculatePeak(buffer: AudioBuffer): number {
    let peak = 0;
    for (let c = 0; c < buffer.channels; c++) {
      const ch = buffer.data[c];
      for (let i = 0; i < buffer.frames; i++) {
        const abs = Math.abs(ch[i]);
        if (abs > peak) peak = abs;
      }
    }
    return peak;
  }

  /**
   * Genera datos de forma de onda optimizados (min, max, rms) para renderizado de timeline.
   */
  public static generateWaveform(buffer: AudioBuffer, pointsCount = 100): WaveformPeak[] {
    if (buffer.frames === 0 || pointsCount <= 0) return [];

    const framesPerPoint = buffer.frames / pointsCount;
    const peaks: WaveformPeak[] = [];

    for (let p = 0; p < pointsCount; p++) {
      const start = Math.floor(p * framesPerPoint);
      const end = Math.min(buffer.frames, Math.floor((p + 1) * framesPerPoint));

      let min = 0;
      let max = 0;
      let sumSq = 0;
      let count = 0;

      for (let c = 0; c < buffer.channels; c++) {
        const ch = buffer.data[c];
        for (let i = start; i < end; i++) {
          const val = ch[i];
          if (val < min) min = val;
          if (val > max) max = val;
          sumSq += val * val;
          count++;
        }
      }

      const rms = count > 0 ? Math.sqrt(sumSq / count) : 0;
      peaks.push({ min, max, rms });
    }

    return peaks;
  }

  /**
   * Detecta intervalos de silencio continuo donde la energía cae por debajo de thresholdDb.
   */
  public static detectSilence(buffer: AudioBuffer, thresholdDb = -45, minDuration = 0.2): SilenceInterval[] {
    if (buffer.frames === 0) return [];

    const thresholdGain = AudioMath.dbToGain(thresholdDb);
    const windowFrames = Math.round(0.05 * buffer.sampleRate); // Ventanas de 50ms
    const totalWindows = Math.floor(buffer.frames / windowFrames);

    const intervals: SilenceInterval[] = [];
    let inSilence = false;
    let silenceStart = 0;

    for (let w = 0; w < totalWindows; w++) {
      const startFrame = w * windowFrames;
      const endFrame = startFrame + windowFrames;
      const slice = buffer.slice(startFrame, endFrame);
      const rms = this.calculateRMS(slice);

      const time = startFrame / buffer.sampleRate;

      if (rms < thresholdGain) {
        if (!inSilence) {
          inSilence = true;
          silenceStart = time;
        }
      } else {
        if (inSilence) {
          inSilence = false;
          const dur = time - silenceStart;
          if (dur >= minDuration) {
            intervals.push({ start: silenceStart, end: time, duration: dur });
          }
        }
      }
    }

    if (inSilence) {
      const endTime = buffer.duration;
      const dur = endTime - silenceStart;
      if (dur >= minDuration) {
        intervals.push({ start: silenceStart, end: endTime, duration: dur });
      }
    }

    return intervals;
  }

  /**
   * Detecta transitorios rítmicos y picos de energía para construir el BeatMap.
   */
  public static detectBeats(buffer: AudioBuffer, options: BeatDetectionOptions = {}): BeatMap {
    const windowMs = options.windowSizeMs ?? 20; // 20ms
    const sensitivity = options.sensitivity ?? 1.5;
    const minIntervalSec = (options.minIntervalMs ?? 150) / 1000; // Mínimo 150ms entre golpes

    const windowFrames = Math.round((windowMs / 1000) * buffer.sampleRate);
    if (windowFrames === 0 || buffer.frames === 0) {
      return { beats: [] };
    }

    const totalWindows = Math.floor(buffer.frames / windowFrames);
    const energies: number[] = [];

    for (let w = 0; w < totalWindows; w++) {
      const start = w * windowFrames;
      const slice = buffer.slice(start, start + windowFrames);
      energies.push(this.calculateRMS(slice));
    }

    // Calcular media móvil de energía local para detectar picos relativos
    const historySize = 10;
    const detectedBeats: Beat[] = [];
    let lastBeatTime = -minIntervalSec;

    for (let i = historySize; i < energies.length; i++) {
      const currentEnergy = energies[i];
      let localSum = 0;
      for (let j = i - historySize; j < i; j++) {
        localSum += energies[j];
      }
      const localAvg = localSum / historySize;
      const currentTime = (i * windowFrames) / buffer.sampleRate;

      if (currentEnergy > localAvg * sensitivity && currentEnergy > 0.05) {
        if (currentTime - lastBeatTime >= minIntervalSec) {
          const strength = Math.min(1.0, currentEnergy / (localAvg * 2 + 1e-6));
          detectedBeats.push({
            time: currentTime,
            strength,
            type: strength > 0.8 ? "downbeat" : "beat",
          });
          lastBeatTime = currentTime;
        }
      }
    }

    // Estimar BPM si hay suficientes beats
    let bpm: number | undefined;
    if (detectedBeats.length >= 4) {
      const intervals: number[] = [];
      for (let i = 1; i < detectedBeats.length; i++) {
        intervals.push(detectedBeats[i].time - detectedBeats[i - 1].time);
      }
      const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      if (avgInterval > 0) {
        bpm = Math.round(60 / avgInterval);
      }
    }

    return {
      bpm,
      beats: detectedBeats,
    };
  }
}
