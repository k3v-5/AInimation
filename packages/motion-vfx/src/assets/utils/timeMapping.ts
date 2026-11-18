import { ValidationError } from "../../errors/index.js";

/**
 * Utilidades matemáticas para la conversión entre Composition Time y Source Time (Fase 5A).
 */

/**
 * Convierte un instante de la composición a tiempo relativo del medio fuente original.
 * sourceTime = sourceStart + (compositionTime * speed)
 */
export function toSourceTime(compositionTime: number, sourceStart = 0, speed = 1): number {
  if (speed <= 0) {
    throw new ValidationError(`Speed must be a positive number (> 0). Received: ${speed}`);
  }
  return sourceStart + compositionTime * speed;
}

/**
 * Convierte un instante del archivo fuente original al tiempo correspondiente en la composición.
 * compositionTime = (sourceTime - sourceStart) / speed
 */
export function toCompositionTime(sourceTime: number, sourceStart = 0, speed = 1): number {
  if (speed <= 0) {
    throw new ValidationError(`Speed must be a positive number (> 0). Received: ${speed}`);
  }
  return (sourceTime - sourceStart) / speed;
}
