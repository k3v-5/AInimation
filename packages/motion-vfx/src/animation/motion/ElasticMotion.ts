import { ElasticOptions, MotionFunction } from "./types.js";

/**
 * Función de movimiento elástica con oscilaciones sinusoidales amortiguadas exponencialmente.
 */
export class ElasticMotion implements MotionFunction {
  public readonly type = "elastic";
  public readonly amplitude: number;
  public readonly period: number;

  constructor(options: ElasticOptions = {}) {
    this.amplitude = options.amplitude !== undefined ? options.amplitude : 1.0;
    this.period = options.period !== undefined ? Math.max(0.05, options.period) : 0.3;
  }

  public evaluate(p: number): number {
    if (p <= 0) return 0;
    if (p >= 1) return 1;

    const s = this.period / 4;
    return this.amplitude * Math.pow(2, -10 * p) * Math.sin(((p - s) * (2 * Math.PI)) / this.period) + 1;
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      amplitude: this.amplitude,
      period: this.period,
    };
  }
}

export function elastic(options: ElasticOptions = {}): ElasticMotion {
  return new ElasticMotion(options);
}
