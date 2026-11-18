import { PACING_DEFAULTS } from "../contracts/vlog.constants.js";

/** Decisión explícita de estiramiento o compresión vocal */
export interface VoiceStretchDecision {
  originalDurationSeconds: number;
  targetDurationSeconds: number;
  ratio: number;
  allowedRange: [number, number];
  applied: boolean;
  mode: "AUTOMATIC" | "MANUAL_OVERRIDE";
  reason: string;
}

/**
 * Resolutor de Elasticidad y Estiramiento Temporal Vocal (Milestone 5-04 & 5-13).
 * Limita el stretch automático al intervalo seguro [0.95x, 1.05x] y restringe
 * el rango duro [0.85x, 1.15x] exclusivamente a intervenciones explícitas.
 */
export class VoiceStretchResolver {
  /**
   * Evalúa si una disparidad temporal puede ser resuelta mediante elasticidad de voz.
   */
  public static evaluateStretch(
    voiceDurationSeconds: number,
    visualDurationSeconds: number,
    allowManualOverride = false,
    customOverrideRange?: [number, number]
  ): VoiceStretchDecision {
    if (visualDurationSeconds <= 0 || voiceDurationSeconds <= 0) {
      return {
        originalDurationSeconds: voiceDurationSeconds,
        targetDurationSeconds: visualDurationSeconds,
        ratio: 1.0,
        allowedRange: [PACING_DEFAULTS.AUTOMATIC_STRETCH_MIN, PACING_DEFAULTS.AUTOMATIC_STRETCH_MAX],
        applied: false,
        mode: "AUTOMATIC",
        reason: "Invalid durations: cannot calculate stretch ratio for zero or negative duration",
      };
    }

    const ratio = Number((voiceDurationSeconds / visualDurationSeconds).toFixed(4));
    const autoMin = PACING_DEFAULTS.AUTOMATIC_STRETCH_MIN; // 0.95
    const autoMax = PACING_DEFAULTS.AUTOMATIC_STRETCH_MAX; // 1.05

    // 1. Verificación automática en rango [0.95, 1.05]
    if (ratio >= autoMin && ratio <= autoMax) {
      return {
        originalDurationSeconds: voiceDurationSeconds,
        targetDurationSeconds: visualDurationSeconds,
        ratio,
        allowedRange: [autoMin, autoMax],
        applied: true,
        mode: "AUTOMATIC",
        reason: `Ratio ${ratio} is within canonical automatic elasticity [${autoMin}, ${autoMax}]`,
      };
    }

    // 2. Verificación de override manual en rango duro [0.85, 1.15]
    if (allowManualOverride) {
      const hardMin = customOverrideRange?.[0] ?? PACING_DEFAULTS.HARD_STRETCH_LIMIT_MIN; // 0.85
      const hardMax = customOverrideRange?.[1] ?? PACING_DEFAULTS.HARD_STRETCH_LIMIT_MAX; // 1.15

      if (ratio >= hardMin && ratio <= hardMax) {
        return {
          originalDurationSeconds: voiceDurationSeconds,
          targetDurationSeconds: visualDurationSeconds,
          ratio,
          allowedRange: [hardMin, hardMax],
          applied: true,
          mode: "MANUAL_OVERRIDE",
          reason: `Ratio ${ratio} is within hard override elasticity [${hardMin}, ${hardMax}]`,
        };
      }
    }

    // 3. Fuera de rango de elasticidad
    return {
      originalDurationSeconds: voiceDurationSeconds,
      targetDurationSeconds: visualDurationSeconds,
      ratio,
      allowedRange: allowManualOverride
        ? [PACING_DEFAULTS.HARD_STRETCH_LIMIT_MIN, PACING_DEFAULTS.HARD_STRETCH_LIMIT_MAX]
        : [autoMin, autoMax],
      applied: false,
      mode: allowManualOverride ? "MANUAL_OVERRIDE" : "AUTOMATIC",
      reason: `Ratio ${ratio} exceeds permissible voice elasticity. Requires visual retiming or conflict resolution`,
    };
  }
}
