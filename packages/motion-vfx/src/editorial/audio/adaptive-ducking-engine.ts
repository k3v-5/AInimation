import { AudioAutomation, AudioBusType } from "./audio-ir.types.js";

/**
 * REQ-045 & REQ-056: Adaptive Contextual Ducking Engine
 * Modula la música dinámicamente frente al diálogo preservando la espacialidad ambiental y los efectos críticos.
 */
export class AdaptiveDuckingEngine {
  /**
   * Genera las curvas de automatización de ganancia para cada bus dependiente
   */
  public static calculateDuckingAutomations(params: {
    dialogueIntervals: Array<{ startSeconds: number; endSeconds: number; importanceScore?: number }>;
    criticalSfxIntervals?: Array<{ startSeconds: number; endSeconds: number }>;
    musicDefaultGainDb?: number;
    musicDuckedGainDb?: number; // ej. -14 dB
    ambienceDefaultGainDb?: number;
    ambienceDuckedGainDb?: number; // ej. -14 dB -> suave atenuación a -15 dB
    attackTimeSeconds?: number;
    releaseTimeSeconds?: number;
  }): Map<AudioBusType, AudioAutomation> {
    const {
      dialogueIntervals,
      criticalSfxIntervals = [],
      musicDefaultGainDb = -6.0,
      musicDuckedGainDb = -16.0,
      ambienceDefaultGainDb = -12.0,
      ambienceDuckedGainDb = -14.0, // Apenas 2 dB de atenuación para no colapsar la sala
      attackTimeSeconds = 0.15,
      releaseTimeSeconds = 0.40,
    } = params;

    const musicPoints: Array<{ timestampSeconds: number; value: number }> = [];
    const ambiencePoints: Array<{ timestampSeconds: number; value: number }> = [];

    // Unir intervalos de atenuación de música (Diálogo + SFX Críticos)
    const combinedIntervals = [
      ...dialogueIntervals.map((d) => ({ start: d.startSeconds, end: d.endSeconds })),
      ...criticalSfxIntervals.map((s) => ({ start: s.startSeconds, end: s.endSeconds })),
    ].sort((a, b) => a.start - b.start);

    // Fusionar intervalos solapados
    const merged: Array<{ start: number; end: number }> = [];
    for (const item of combinedIntervals) {
      if (merged.length === 0) {
        merged.push({ ...item });
      } else {
        const last = merged[merged.length - 1];
        if (item.start <= last.end + 0.1) {
          last.end = Math.max(last.end, item.end);
        } else {
          merged.push({ ...item });
        }
      }
    }

    // Puntos iniciales en t=0
    musicPoints.push({ timestampSeconds: 0, value: musicDefaultGainDb });
    ambiencePoints.push({ timestampSeconds: 0, value: ambienceDefaultGainDb });

    for (const int of merged) {
      const duckStart = Math.max(0, int.start - attackTimeSeconds);
      const duckEnd = int.end + releaseTimeSeconds;

      // 1. Música: Entrada a ducking
      musicPoints.push({ timestampSeconds: Number(duckStart.toFixed(3)), value: musicDefaultGainDb });
      musicPoints.push({ timestampSeconds: Number(int.start.toFixed(3)), value: musicDuckedGainDb });

      // 1. Música: Salida de ducking
      musicPoints.push({ timestampSeconds: Number(int.end.toFixed(3)), value: musicDuckedGainDb });
      musicPoints.push({ timestampSeconds: Number(duckEnd.toFixed(3)), value: musicDefaultGainDb });

      // 2. Ambiente: Atenuación mínima para preservar espacialidad
      ambiencePoints.push({ timestampSeconds: Number(duckStart.toFixed(3)), value: ambienceDefaultGainDb });
      ambiencePoints.push({ timestampSeconds: Number(int.start.toFixed(3)), value: ambienceDuckedGainDb });
      ambiencePoints.push({ timestampSeconds: Number(int.end.toFixed(3)), value: ambienceDuckedGainDb });
      ambiencePoints.push({ timestampSeconds: Number(duckEnd.toFixed(3)), value: ambienceDefaultGainDb });
    }

    const automations = new Map<AudioBusType, AudioAutomation>();

    automations.set("MUSIC", {
      parameter: "gainDb",
      points: musicPoints.sort((a, b) => a.timestampSeconds - b.timestampSeconds),
    });

    automations.set("AMBIENCE", {
      parameter: "gainDb",
      points: ambiencePoints.sort((a, b) => a.timestampSeconds - b.timestampSeconds),
    });

    return automations;
  }
}
