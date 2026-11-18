import { CaptionDocument, CaptionWord } from "../../captions/types/index.js";
import { MotionEngineError } from "../../errors/index.js";

export class ViralClippingError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Viral Clipping Error: ${message}`);
  }
}

export interface AudioEnergySample {
  timestamp: number;
  rms: number; // 0.0 a 1.0
}

export interface ViralScoringWeights {
  hookWeight: number; // por defecto 0.40
  pacingWeight: number; // por defecto 0.35
  climaxWeight: number; // por defecto 0.25
}

export interface ViralCandidateClip {
  id: string;
  startTime: number;
  endTime: number;
  duration: number;
  hookScore: number; // 0 a 100
  pacingScore: number; // 0 a 100
  climaxScore: number; // 0 a 100
  viralityIndex: number; // 0 a 100 (Score Global Ponderado)
  transcriptSlice: string;
  wordCount: number;
  recommendedPreset: string;
}

const VIRAL_HOOK_TRIGGERS = [
  "secreto", "nunca", "por qué", "cómo", "el mayor", "nadie te dice",
  "descubrí", "mira esto", "error", "verdad", "increíble", "dinero",
  "millonario", "cuidado", "truco", "hack", "atención", "revelado",
  "secret", "never", "why", "how to", "biggest mistake", "nobody tells you"
];

/**
 * Detector algorítmico de momentos virales y generador de clips Long-to-Shorts (Suite de Automatización).
 */
export class ViralMomentDetector {
  public static readonly DEFAULT_WEIGHTS: ViralScoringWeights = {
    hookWeight: 0.40,
    pacingWeight: 0.35,
    climaxWeight: 0.25,
  };

  /**
   * Calcula el Hook Score (0 a 100) en base a los primeros 3 segundos de texto y energía vocal.
   */
  public static calculateHookScore(first3SecWords: CaptionWord[], initialRMS = 0.5): number {
    let score = 50.0; // Base neutral
    const textSnippet = first3SecWords.map(w => w.text.toLowerCase()).join(" ");

    // 1. Detección de disparadores psicológicos de curiosidad
    for (const trigger of VIRAL_HOOK_TRIGGERS) {
      if (textSnippet.includes(trigger)) {
        score += 15.0;
      }
    }

    // 2. Preguntas o signos de exclamación al inicio
    if (textSnippet.includes("?") || textSnippet.includes("¿") || textSnippet.includes("!")) {
      score += 10.0;
    }

    // 3. Modulación de energía vocal (RMS) en el primer segundo
    if (initialRMS > 0.6) {
      score += 15.0;
    } else if (initialRMS < 0.2) {
      score -= 15.0; // Inicio apagado o con silencio
    }

    return Math.max(0, Math.min(100, Math.round(score)));
  }

  /**
   * Calcula el Pacing Score (0 a 100) en base a la densidad de palabras por minuto (WPM).
   * Óptimo para TikTok/Shorts: 140 a 190 WPM (2.3 a 3.2 palabras/segundo).
   */
  public static calculatePacingScore(wordCount: number, durationSec: number): number {
    if (durationSec <= 0) return 0;
    const wpm = (wordCount / durationSec) * 60.0;

    let score = 100.0;
    if (wpm < 120) {
      score -= (120 - wpm) * 0.8; // Muy lento / aburrido
    } else if (wpm > 220) {
      score -= (wpm - 220) * 0.6; // Demasiado rápido / ininteligible
    }

    return Math.max(0, Math.min(100, Math.round(score)));
  }

  /**
   * Calcula el Climax Score (0 a 100) evaluando el crescendo de energía hacia el final del clip.
   */
  public static calculateClimaxScore(energySamples: AudioEnergySample[], startSec: number, endSec: number): number {
    const relevant = energySamples.filter(s => s.timestamp >= startSec && s.timestamp <= endSec);
    if (relevant.length === 0) return 70.0; // Fallback neutral

    const duration = endSec - startSec;
    const climaxThresholdTime = startSec + duration * 0.65;

    let preAvg = 0;
    let preCount = 0;
    let postMax = 0;

    for (const s of relevant) {
      if (s.timestamp < climaxThresholdTime) {
        preAvg += s.rms;
        preCount++;
      } else {
        if (s.rms > postMax) postMax = s.rms;
      }
    }

    preAvg = preCount > 0 ? preAvg / preCount : 0.4;
    const boostRatio = preAvg > 0 ? postMax / preAvg : 1.0;

    let score = 50.0 + (boostRatio - 1.0) * 40.0;
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  /**
   * Computa el índice global de viralidad ponderado.
   */
  public static computeViralityIndex(
    hook: number,
    pacing: number,
    climax: number,
    weights = this.DEFAULT_WEIGHTS
  ): number {
    const totalWeight = weights.hookWeight + weights.pacingWeight + weights.climaxWeight;
    const normalized = (
      hook * weights.hookWeight +
      pacing * weights.pacingWeight +
      climax * weights.climaxWeight
    ) / totalWeight;

    return Math.round(normalized * 10) / 10;
  }

  /**
   * Escanea una transcripción completa y extrae los mejores K clips virales.
   */
  public static detectViralMoments(
    transcript: CaptionDocument,
    energySamples: AudioEnergySample[] = [],
    targetDurationRangeSec: [number, number] = [30.0, 50.0],
    topK = 3,
    weights = this.DEFAULT_WEIGHTS
  ): ViralCandidateClip[] {
    const allWords: CaptionWord[] = [];
    for (const seg of transcript.segments) {
      allWords.push(...seg.words);
    }

    if (allWords.length === 0) {
      throw new ViralClippingError("Transcript has no words to analyze.");
    }

    const minDur = targetDurationRangeSec[0];
    const maxDur = targetDurationRangeSec[1];
    const totalDuration = transcript.duration > 0
      ? transcript.duration
      : allWords[allWords.length - 1].end;

    const candidates: ViralCandidateClip[] = [];
    const stepSec = 5.0; // Desplazamiento de ventana

    let windowStart = 0.0;
    let clipIndex = 1;

    while (windowStart + minDur <= totalDuration) {
      const windowEnd = Math.min(totalDuration, windowStart + maxDur);
      const actualDuration = windowEnd - windowStart;

      const wordsInWindow = allWords.filter(
        w => w.start >= windowStart && w.end <= windowEnd
      );

      if (wordsInWindow.length >= 10) {
        const first3SecWords = wordsInWindow.filter(w => w.start <= windowStart + 3.0);
        const hook = this.calculateHookScore(first3SecWords, 0.6);
        const pacing = this.calculatePacingScore(wordsInWindow.length, actualDuration);
        const climax = this.calculateClimaxScore(energySamples, windowStart, windowEnd);
        const virality = this.computeViralityIndex(hook, pacing, climax, weights);

        // Selección de preset recomendado en base a estilo
        let recommendedPreset = "hormozi_cashflow_captions";
        if (virality > 85) recommendedPreset = "mrbeast_hyper_retention";
        else if (hook > 80) recommendedPreset = "time_editorial_poster";

        candidates.push({
          id: `viral_clip_${clipIndex++}`,
          startTime: Number(windowStart.toFixed(2)),
          endTime: Number(windowEnd.toFixed(2)),
          duration: Number(actualDuration.toFixed(2)),
          hookScore: hook,
          pacingScore: pacing,
          climaxScore: climax,
          viralityIndex: virality,
          transcriptSlice: wordsInWindow.map(w => w.text).join(" "),
          wordCount: wordsInWindow.length,
          recommendedPreset,
        });
      }

      windowStart += stepSec;
    }

    // Ordenar de mayor a menor viralityIndex
    candidates.sort((a, b) => b.viralityIndex - a.viralityIndex);

    // Filtrar solapamientos excesivos (>50%) para garantizar variedad
    const nonOverlapping: ViralCandidateClip[] = [];
    for (const cand of candidates) {
      const overlaps = nonOverlapping.some(selected => {
        const startOverlap = Math.max(selected.startTime, cand.startTime);
        const endOverlap = Math.min(selected.endTime, cand.endTime);
        const overlapDuration = Math.max(0, endOverlap - startOverlap);
        return overlapDuration / cand.duration > 0.4;
      });

      if (!overlaps) {
        nonOverlapping.push(cand);
        if (nonOverlapping.length >= topK) break;
      }
    }

    return nonOverlapping;
  }
}
