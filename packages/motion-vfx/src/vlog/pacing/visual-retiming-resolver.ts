import { EPSILON } from "../contracts/vlog.constants.js";

export type VisualRetimingAction =
  | "KEEP"
  | "TRIM"
  | "EXTEND"
  | "HOLD"
  | "SPEED_UP"
  | "SLOW_DOWN"
  | "REPLACE"
  | "NO_VALID_SOLUTION";

/** Decisión declarativa de retiming visual */
export interface VisualRetimingDecision {
  clipId: string;
  action: VisualRetimingAction;
  sourceDurationSeconds: number;
  targetDurationSeconds: number;
  ratio: number;
  holdDurationSeconds: number;
  speedFactor: number;
  isPossible: boolean;
  reason: string;
}

export interface VisualRetimingOptions {
  maxHoldDurationSeconds?: number; // default: 2.0s
  maxSpeedFactor?: number; // default: 1.5x
  minSpeedFactor?: number; // default: 0.75x
  allowHold?: boolean; // default: true
}

/**
 * Resolutor Declarativo de Retiming Visual (Milestone 5-14 & 5-16).
 * Calcula si un clip debe ser recortado (trim), extendido, ralentizado,
 * acelerado o prolongado mediante fotograma congelado (hold/freeze) sin mutación destructiva.
 */
export class VisualRetimingResolver {
  public static resolve(
    clipId: string,
    sourceDurationSeconds: number,
    targetDurationSeconds: number,
    availableMediaDurationSeconds?: number,
    options: VisualRetimingOptions = {}
  ): VisualRetimingDecision {
    const maxHold = options.maxHoldDurationSeconds ?? 2.0;
    const maxSpeed = options.maxSpeedFactor ?? 1.5;
    const minSpeed = options.minSpeedFactor ?? 0.75;
    const allowHold = options.allowHold !== false;

    if (sourceDurationSeconds <= EPSILON || targetDurationSeconds <= EPSILON) {
      return {
        clipId,
        action: "NO_VALID_SOLUTION",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio: 1.0,
        holdDurationSeconds: 0,
        speedFactor: 1.0,
        isPossible: false,
        reason: "Source or target duration is non-positive",
      };
    }

    const delta = targetDurationSeconds - sourceDurationSeconds;
    const ratio = Number((targetDurationSeconds / sourceDurationSeconds).toFixed(4));

    // 1. Caso: Duraciones idénticas dentro de EPSILON
    if (Math.abs(delta) <= 0.04) {
      return {
        clipId,
        action: "KEEP",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio: 1.0,
        holdDurationSeconds: 0,
        speedFactor: 1.0,
        isPossible: true,
        reason: "Source duration matches target duration within tolerance",
      };
    }

    // 2. Caso: Se requiere recortar el clip visual (target < source)
    if (targetDurationSeconds < sourceDurationSeconds) {
      return {
        clipId,
        action: "TRIM",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio,
        holdDurationSeconds: 0,
        speedFactor: 1.0,
        isPossible: true,
        reason: `Clip trimmed from ${sourceDurationSeconds.toFixed(2)}s to ${targetDurationSeconds.toFixed(2)}s`,
      };
    }

    // 3. Caso: Se requiere extender el clip visual (target > source)
    // Opción A: Extender con metraje sobrante disponible en el asset
    if (availableMediaDurationSeconds && availableMediaDurationSeconds >= targetDurationSeconds) {
      return {
        clipId,
        action: "EXTEND",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio,
        holdDurationSeconds: 0,
        speedFactor: 1.0,
        isPossible: true,
        reason: `Clip extended to ${targetDurationSeconds.toFixed(2)}s using available source footage (${availableMediaDurationSeconds.toFixed(2)}s total)`,
      };
    }

    // Opción B: Hold/Freeze frame si el delta no excede maxHold
    const requiredHold = targetDurationSeconds - sourceDurationSeconds;
    if (allowHold && requiredHold <= maxHold) {
      return {
        clipId,
        action: "HOLD",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio,
        holdDurationSeconds: Number(requiredHold.toFixed(4)),
        speedFactor: 1.0,
        isPossible: true,
        reason: `Freeze frame hold of ${requiredHold.toFixed(2)}s applied at clip end (max allowed: ${maxHold.toFixed(2)}s)`,
      };
    }

    // Opción C: Ralentizar el clip si ratio está dentro de minSpeed
    const speed = Number((sourceDurationSeconds / targetDurationSeconds).toFixed(4));
    if (speed >= minSpeed) {
      return {
        clipId,
        action: "SLOW_DOWN",
        sourceDurationSeconds,
        targetDurationSeconds,
        ratio,
        holdDurationSeconds: 0,
        speedFactor: speed,
        isPossible: true,
        reason: `Clip slowed down to speed factor ${speed} (min allowed: ${minSpeed})`,
      };
    }

    // Si excedió hold y velocidad, no hay solución visual válida sin conflicto
    return {
      clipId,
      action: "NO_VALID_SOLUTION",
      sourceDurationSeconds,
      targetDurationSeconds,
      ratio,
      holdDurationSeconds: Number(requiredHold.toFixed(4)),
      speedFactor: speed,
      isPossible: false,
      reason: `Required extension of +${requiredHold.toFixed(2)}s exceeds max hold (${maxHold}s) and min speed limit (${minSpeed}x)`,
    };
  }
}
