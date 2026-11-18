import {
  DuckingEnvelope,
  DuckingKeyframe,
} from "../contracts/audio.types.js";
import { AUDIO_MIX_DEFAULTS, EPSILON } from "../contracts/vlog.constants.js";

export interface DialogueInterval {
  startSeconds: number;
  endSeconds: number;
}

export interface DuckingOptions {
  duckAmountDb?: number; // default: -10.0 dB
  attackSeconds?: number; // default: 0.12 s
  releaseSeconds?: number; // default: 0.40 s
  minPauseToReleaseSeconds?: number; // default: 0.52 s (para evitar bombeo/jitter)
}

/**
 * Motor de Atenuación Automática de Música (Auto-Ducking Engine) (Milestone 7).
 * Genera envolventes de ganancia suaves y deterministas para la música cuando hay locución,
 * evitando bombeo audible en pausas cortas mediante un umbral de histéresis.
 */
export class AudioDuckingEngine {
  /**
   * Genera la envolvente de keyframes de ducking para un conjunto de intervalos de diálogo.
   */
  public static generateDuckingEnvelope(
    targetMusicTrackId: string,
    triggerVoiceTrackId: string,
    dialogueIntervals: DialogueInterval[],
    options: DuckingOptions = {}
  ): DuckingEnvelope {
    const duckDb = options.duckAmountDb ?? AUDIO_MIX_DEFAULTS.MUSIC_DUCKING_DB; // -10.0 dB
    const attack = options.attackSeconds ?? AUDIO_MIX_DEFAULTS.DUCKING_ATTACK_SECONDS; // 0.12 s
    const release = options.releaseSeconds ?? AUDIO_MIX_DEFAULTS.DUCKING_RELEASE_SECONDS; // 0.40 s
    const minPause = options.minPauseToReleaseSeconds ?? (attack + release); // 0.52 s

    if (!dialogueIntervals || dialogueIntervals.length === 0) {
      return {
        targetTrackId: targetMusicTrackId,
        triggerTrackId: triggerVoiceTrackId,
        duckAmountDb: duckDb,
        attackSeconds: attack,
        releaseSeconds: release,
        keyframes: [
          { timeSeconds: 0.0, gainDb: 0.0 },
        ],
      };
    }

    // 1. Ordenar y fusionar diálogos con pausas menores a minPause (anti-pumping)
    const sorted = [...dialogueIntervals]
      .filter((d) => d.endSeconds > d.startSeconds)
      .sort((a, b) => a.startSeconds - b.startSeconds);

    const merged: DialogueInterval[] = [];
    if (sorted.length > 0) {
      let current = { ...sorted[0] };
      for (let i = 1; i < sorted.length; i++) {
        const next = sorted[i];
        const gap = next.startSeconds - current.endSeconds;
        if (gap < minPause) {
          // Fusionar intervalos cercanos para mantener la música atenuada y evitar bombeo
          current.endSeconds = Math.max(current.endSeconds, next.endSeconds);
        } else {
          merged.push(current);
          current = { ...next };
        }
      }
      merged.push(current);
    }

    // 2. Generar keyframes de rampa suave
    const rawKeyframes: DuckingKeyframe[] = [];

    // Estado inicial
    rawKeyframes.push({ timeSeconds: 0.0, gainDb: 0.0 });

    for (const segment of merged) {
      const attackStart = Math.max(0.0, segment.startSeconds - attack);
      const duckStart = segment.startSeconds;
      const duckEnd = segment.endSeconds;
      const releaseEnd = segment.endSeconds + release;

      // Inicio del ataque (0 dB)
      rawKeyframes.push({
        timeSeconds: Number(attackStart.toFixed(4)),
        gainDb: 0.0,
      });

      // Fin del ataque / Inicio de atenuación plena (-10 dB)
      rawKeyframes.push({
        timeSeconds: Number(duckStart.toFixed(4)),
        gainDb: duckDb,
      });

      // Fin de atenuación plena (-10 dB)
      rawKeyframes.push({
        timeSeconds: Number(duckEnd.toFixed(4)),
        gainDb: duckDb,
      });

      // Fin de recuperación / Regreso a nivel normal (0 dB)
      rawKeyframes.push({
        timeSeconds: Number(releaseEnd.toFixed(4)),
        gainDb: 0.0,
      });
    }

    // 3. Ordenar por tiempo y desduplicar timestamps idénticos
    rawKeyframes.sort((a, b) => a.timeSeconds - b.timeSeconds);

    const keyframes: DuckingKeyframe[] = [];
    for (let i = 0; i < rawKeyframes.length; i++) {
      const kf = rawKeyframes[i];
      if (
        keyframes.length === 0 ||
        Math.abs(kf.timeSeconds - keyframes[keyframes.length - 1].timeSeconds) > EPSILON
      ) {
        keyframes.push(kf);
      } else {
        // En caso de timestamp coincidente, conservar el valor de mayor atenuación (menor gainDb)
        const prev = keyframes[keyframes.length - 1];
        prev.gainDb = Math.min(prev.gainDb, kf.gainDb);
      }
    }

    return {
      targetTrackId: targetMusicTrackId,
      triggerTrackId: triggerVoiceTrackId,
      duckAmountDb: duckDb,
      attackSeconds: attack,
      releaseSeconds: release,
      keyframes,
    };
  }
}
