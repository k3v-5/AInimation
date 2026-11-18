import { EPSILON } from "../contracts/vlog.constants.js";

/** Segmento de mapeo temporal que relaciona un intervalo fuente con su intervalo derivado */
export interface TimeMapInterval {
  sourceStart: number;
  sourceEnd: number;
  derivedStart: number;
  derivedEnd: number;
  strategy: "KEEP" | "STRETCH" | "TRIM" | "HOLD";
  scaleFactor: number;
}

/**
 * Mapeador Temporal Determinista y Bidireccional (Milestone 5).
 * Modela transformaciones lineales y por tramos entre la timeline fuente y la timeline derivada.
 * Soporta estiramiento, recorte, pausas/holds y concatenación con semántica de intervalo semiabierto [start, end).
 */
export class TimeMapper {
  private intervals: TimeMapInterval[] = [];

  constructor(intervals: TimeMapInterval[] = []) {
    this.intervals = [...intervals].sort((a, b) => a.sourceStart - b.sourceStart);
  }

  public addInterval(interval: TimeMapInterval): void {
    this.intervals.push(interval);
    this.intervals.sort((a, b) => a.sourceStart - b.sourceStart);
  }

  public getIntervals(): readonly TimeMapInterval[] {
    return this.intervals;
  }

  /**
   * Mapea un tiempo de la timeline fuente hacia la timeline adaptada/derivada.
   * f: sourceTime -> derivedTime
   */
  public mapSourceToDerived(sourceTime: number): number {
    if (isNaN(sourceTime) || !isFinite(sourceTime)) return 0.0;
    if (this.intervals.length === 0) return sourceTime;

    // Antes del primer intervalo
    const first = this.intervals[0];
    if (sourceTime <= first.sourceStart) {
      return Number(first.derivedStart.toFixed(4));
    }

    // Después del último intervalo
    const last = this.intervals[this.intervals.length - 1];
    if (sourceTime >= last.sourceEnd) {
      const excess = sourceTime - last.sourceEnd;
      return Number((last.derivedEnd + excess).toFixed(4));
    }

    // Búsqueda binaria o lineal en intervalos ordenados
    for (const interval of this.intervals) {
      if (sourceTime >= interval.sourceStart - EPSILON && sourceTime < interval.sourceEnd + EPSILON) {
        const sourceSpan = interval.sourceEnd - interval.sourceStart;
        if (sourceSpan <= EPSILON) {
          return Number(interval.derivedStart.toFixed(4));
        }
        const progress = Math.max(0.0, Math.min(1.0, (sourceTime - interval.sourceStart) / sourceSpan));
        const derivedSpan = interval.derivedEnd - interval.derivedStart;
        return Number((interval.derivedStart + progress * derivedSpan).toFixed(4));
      }
    }

    return Number(sourceTime.toFixed(4));
  }

  /**
   * Mapea un tiempo de la timeline adaptada de vuelta a la timeline fuente original.
   * f^-1: derivedTime -> sourceTime
   */
  public mapDerivedToSource(derivedTime: number): number {
    if (isNaN(derivedTime) || !isFinite(derivedTime)) return 0.0;
    if (this.intervals.length === 0) return derivedTime;

    const first = this.intervals[0];
    if (derivedTime <= first.derivedStart) {
      return Number(first.sourceStart.toFixed(4));
    }

    const last = this.intervals[this.intervals.length - 1];
    if (derivedTime >= last.derivedEnd) {
      const excess = derivedTime - last.derivedEnd;
      return Number((last.sourceEnd + excess).toFixed(4));
    }

    for (const interval of this.intervals) {
      if (derivedTime >= interval.derivedStart - EPSILON && derivedTime < interval.derivedEnd + EPSILON) {
        if (interval.strategy === "HOLD") {
          // Durante un hold visual, el tiempo fuente está congelado en el final del clip
          return Number(interval.sourceEnd.toFixed(4));
        }

        const derivedSpan = interval.derivedEnd - interval.derivedStart;
        if (derivedSpan <= EPSILON) {
          return Number(interval.sourceStart.toFixed(4));
        }
        const progress = Math.max(0.0, Math.min(1.0, (derivedTime - interval.derivedStart) / derivedSpan));
        const sourceSpan = interval.sourceEnd - interval.sourceStart;
        return Number((interval.sourceStart + progress * sourceSpan).toFixed(4));
      }
    }

    return Number(derivedTime.toFixed(4));
  }
}
