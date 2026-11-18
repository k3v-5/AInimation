import { BounceOptions, MotionFunction } from "./types.js";

/**
 * Función de movimiento de rebote gravitacional por tramos parabólicos (Bounce).
 */
export class BounceMotion implements MotionFunction {
  public readonly type = "bounce";
  public readonly bounces: number;
  public readonly decay: number;

  constructor(options: BounceOptions = {}) {
    this.bounces = options.bounces !== undefined ? Math.max(1, options.bounces) : 3;
    this.decay = options.decay !== undefined ? Math.max(0.1, Math.min(0.9, options.decay)) : 0.5;
  }

  public evaluate(p: number): number {
    if (p <= 0) return 0;
    if (p >= 1) return 1;

    const n1 = 7.5625;
    const d1 = 2.75;

    if (p < 1 / d1) {
      return n1 * p * p;
    } else if (p < 2 / d1) {
      const p1 = p - 1.5 / d1;
      return n1 * p1 * p1 + 0.75;
    } else if (p < 2.5 / d1) {
      const p2 = p - 2.25 / d1;
      return n1 * p2 * p2 + 0.9375;
    } else {
      const p3 = p - 2.625 / d1;
      return n1 * p3 * p3 + 0.984375;
    }
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      bounces: this.bounces,
      decay: this.decay,
    };
  }
}

export function bounce(options: BounceOptions = {}): BounceMotion {
  return new BounceMotion(options);
}
