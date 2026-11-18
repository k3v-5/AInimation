import { AudioAnalysisResult, BeatInfo, SpeechRegion } from "../types/index.js";

/**
 * Motor de análisis de audio, detección rítmica y regiones de voz (Fase 13).
 */
export class AudioAnalysisEngine {
  /**
   * Genera una cuadrícula sintética de beats determinista dado un BPM y duración.
   */
  public static generateBeatGrid(bpm: number, duration: number): BeatInfo[] {
    const beatInterval = 60 / bpm;
    const beats: BeatInfo[] = [];
    let t = 0;
    let count = 0;

    while (t < duration) {
      beats.push({
        time: Math.round(t * 1000) / 1000,
        strength: count % 4 === 0 ? 1.0 : 0.7,
        isDownbeat: count % 4 === 0,
      });
      t += beatInterval;
      count++;
    }

    return beats;
  }

  /**
   * Detecta intervalos de silencio a partir de regiones de voz.
   */
  public static detectSilenceRegions(
    speechRegions: SpeechRegion[],
    totalDuration: number,
    minSilenceDuration = 0.3
  ): { start: number; end: number }[] {
    const silences: { start: number; end: number }[] = [];
    let currentT = 0;

    for (const speech of speechRegions) {
      if (speech.start - currentT >= minSilenceDuration) {
        silences.push({ start: currentT, end: speech.start });
      }
      currentT = Math.max(currentT, speech.end);
    }

    if (totalDuration - currentT >= minSilenceDuration) {
      silences.push({ start: currentT, end: totalDuration });
    }

    return silences;
  }
}
