import { ClipRange } from "../contracts/classification.types.js";
import { EPSILON } from "../contracts/vlog.constants.js";

export type BRollLockMode = "LOCKED" | "PREFERRED" | "FLEXIBLE";

export interface BRollPacingAssignment {
  mediaId: string;
  sourceStartSeconds: number;
  sourceEndSeconds: number;
  targetStartSeconds: number;
  targetEndSeconds: number;
  assetDurationSeconds: number;
  lockMode: BRollLockMode;
  semanticReason?: string;
  matchScore?: number;
}

export interface BRollPacingResult {
  mediaId: string;
  adaptedRange: ClipRange;
  targetDurationSeconds: number;
  isCovered: boolean;
  suppressPunchIn: boolean; // B-Roll > Punch-In
  strategyApplied: "KEEP" | "TRIMMED" | "EXTENDED" | "HOLD_APPLIED";
  holdDurationSeconds: number;
}

/**
 * Resolutor de Ritmo y Reajuste para B-Roll (Milestone 5-10, 5-11 & 5-12).
 * Adapta la duración de los clips de apoyo visual a la locución preservando
 * los límites de metraje físico (0 <= start < end <= assetDuration) y aplicando la regla B-Roll > Punch-In.
 */
export class BRollPacingResolver {
  public static retimeBRoll(
    assignment: BRollPacingAssignment,
    requiredDurationSeconds: number
  ): BRollPacingResult {
    const currentDuration = assignment.sourceEndSeconds - assignment.sourceStartSeconds;
    const maxAssetDuration = assignment.assetDurationSeconds;

    let finalStart = assignment.sourceStartSeconds;
    let finalEnd = assignment.sourceEndSeconds;
    let strategy: "KEEP" | "TRIMMED" | "EXTENDED" | "HOLD_APPLIED" = "KEEP";
    let holdDuration = 0.0;

    const delta = requiredDurationSeconds - currentDuration;

    if (Math.abs(delta) <= 0.04) {
      strategy = "KEEP";
    } else if (requiredDurationSeconds < currentDuration) {
      // Recortar metraje B-Roll
      strategy = "TRIMMED";
      finalEnd = Number((finalStart + requiredDurationSeconds).toFixed(4));
    } else {
      // Se requiere mayor duración
      const availableRemaining = maxAssetDuration - finalEnd;
      if (availableRemaining >= delta) {
        // Extender dentro del archivo original
        strategy = "EXTENDED";
        finalEnd = Number((finalEnd + delta).toFixed(4));
      } else {
        // Aprovechar todo el metraje disponible y aplicar hold al final
        finalEnd = Number(maxAssetDuration.toFixed(4));
        holdDuration = Number((requiredDurationSeconds - (finalEnd - finalStart)).toFixed(4));
        strategy = "HOLD_APPLIED";
      }
    }

    // Asegurar invariantes físicas: 0 <= start < end <= assetDuration
    finalStart = Math.max(0.0, Math.min(maxAssetDuration - EPSILON, finalStart));
    finalEnd = Math.max(finalStart + EPSILON, Math.min(maxAssetDuration, finalEnd));

    const adaptedRange: ClipRange = {
      assetId: assignment.mediaId,
      startSeconds: Number(finalStart.toFixed(4)),
      endSeconds: Number(finalEnd.toFixed(4)),
      durationSeconds: Number((finalEnd - finalStart).toFixed(4)),
    };

    return {
      mediaId: assignment.mediaId,
      adaptedRange,
      targetDurationSeconds: requiredDurationSeconds,
      isCovered: true,
      suppressPunchIn: true, // INVARIANTE M3/M5: B-Roll siempre suprime Punch-In
      strategyApplied: strategy,
      holdDurationSeconds: Math.max(0.0, holdDuration),
    };
  }
}
