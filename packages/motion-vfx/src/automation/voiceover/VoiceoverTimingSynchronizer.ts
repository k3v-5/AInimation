import { CaptionWord } from "../../captions/types/index.js";
import { MotionEngineError } from "../../errors/index.js";

export class TimingSyncError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Timing Sync Error: ${message}`);
  }
}

export interface BreathPause {
  startTime: number;
  endTime: number;
  duration: number;
}

export interface VisualSceneBeat {
  id: string;
  nominalDurationSec: number;
  label?: string;
  minDurationSec?: number;
  maxDurationSec?: number;
}

export interface AlignedSceneCut {
  sceneId: string;
  startTimeSec: number;
  endTimeSec: number;
  durationSec: number;
  snapCutToPause: boolean;
}

/**
 * Sincronizador determinista de locución y cortes visuales (Suite de Automatización).
 */
export class VoiceoverTimingSynchronizer {
  /**
   * Detecta pausas naturales de respiración y silencios entre palabras (> 0.30s).
   */
  public static detectBreathPauses(words: CaptionWord[], minGapSec = 0.30): BreathPause[] {
    const pauses: BreathPause[] = [];
    if (!words || words.length < 2) return pauses;

    const sortedWords = [...words].sort((a, b) => a.start - b.start);

    for (let i = 0; i < sortedWords.length - 1; i++) {
      const currentEnd = sortedWords[i].end;
      const nextStart = sortedWords[i + 1].start;
      const gap = nextStart - currentEnd;

      if (gap >= minGapSec) {
        pauses.push({
          startTime: Number(currentEnd.toFixed(3)),
          endTime: Number(nextStart.toFixed(3)),
          duration: Number(gap.toFixed(3)),
        });
      }
    }

    return pauses;
  }

  /**
   * Alinea los cortes de escena visuales para que coincidan con pausas naturales de respiración.
   */
  public static alignScenesToVoiceover(
    scenes: VisualSceneBeat[],
    words: CaptionWord[],
    minGapSec = 0.30
  ): AlignedSceneCut[] {
    if (!scenes || scenes.length === 0) {
      throw new TimingSyncError("Scenes array cannot be empty.");
    }

    const pauses = this.detectBreathPauses(words, minGapSec);
    const alignedCuts: AlignedSceneCut[] = [];

    let currentTime = 0.0;

    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      const targetEnd = currentTime + scene.nominalDurationSec;

      // Buscar si hay una pausa de respiración cercana (±1.5s) al corte nominal
      const nearbyPause = pauses.find(
        p => Math.abs(p.startTime - targetEnd) <= 1.5 && p.startTime > currentTime + (scene.minDurationSec ?? 1.0)
      );

      let finalEnd = targetEnd;
      let snapped = false;

      if (nearbyPause) {
        // Cortar en el punto medio de la pausa de respiración
        finalEnd = (nearbyPause.startTime + nearbyPause.endTime) / 2;
        snapped = true;
      }

      const duration = finalEnd - currentTime;

      alignedCuts.push({
        sceneId: scene.id,
        startTimeSec: Number(currentTime.toFixed(3)),
        endTimeSec: Number(finalEnd.toFixed(3)),
        durationSec: Number(duration.toFixed(3)),
        snapCutToPause: snapped,
      });

      currentTime = finalEnd;
    }

    return alignedCuts;
  }

  /**
   * Calcula el factor de dilatación temporal seguro para ajustar audio/video sin distorsión.
   */
  public static computeSafePacingDilation(targetDuration: number, actualDuration: number): number {
    if (actualDuration <= 0 || targetDuration <= 0) return 1.0;
    const rawRatio = targetDuration / actualDuration;
    // Límite estricto de seguridad perceptual entre 0.85x y 1.15x
    return Number(Math.max(0.85, Math.min(1.15, rawRatio)).toFixed(3));
  }
}
