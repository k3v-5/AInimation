import { Time } from "../core/types.js";
import { InvalidKeyframeError, InvalidTimeError, ValidationError } from "../errors/index.js";

/**
 * Valida que un timestamp sea un número finito mayor o igual a cero.
 */
export function validateTime(time: unknown, fieldName = "time"): Time {
  if (typeof time !== "number" || !Number.isFinite(time) || Number.isNaN(time)) {
    throw new InvalidTimeError(time, `${fieldName} must be a valid finite number.`);
  }
  if (time < 0) {
    throw new InvalidTimeError(time, `${fieldName} cannot be negative.`);
  }
  return time;
}

/**
 * Valida que un número sea estrictamente positivo (> 0).
 */
export function validatePositiveNumber(value: unknown, fieldName: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || Number.isNaN(value) || value <= 0) {
    throw new ValidationError(`${fieldName} must be a finite positive number (> 0). Received: ${String(value)}`);
  }
  return value;
}

/**
 * Valida que un número sea no negativo (>= 0).
 */
export function validateNonNegativeNumber(value: unknown, fieldName: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || Number.isNaN(value) || value < 0) {
    throw new ValidationError(`${fieldName} must be a finite non-negative number (>= 0). Received: ${String(value)}`);
  }
  return value;
}

/**
 * Valida identificadores de texto no vacíos.
 */
export function validateId(id: unknown, fieldName = "id"): string {
  if (typeof id !== "string" || id.trim().length === 0) {
    throw new ValidationError(`${fieldName} must be a non-empty string.`);
  }
  return id.trim();
}

/**
 * Valida que el valor de un keyframe sea válido y no nulo.
 */
export function validateKeyframeValue(value: unknown): void {
  if (value === undefined || value === null) {
    throw new InvalidKeyframeError("Keyframe value cannot be null or undefined.");
  }
  if (typeof value === "number" && (!Number.isFinite(value) || Number.isNaN(value))) {
    throw new InvalidKeyframeError(`Keyframe numeric value must be finite. Received: ${String(value)}`);
  }
}
