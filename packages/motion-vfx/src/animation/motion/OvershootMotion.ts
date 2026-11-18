import { MotionFunction, OvershootOptions } from "./types.js";

/**
 * Función de movimiento con sobrepaso (Overshoot / Back).
 */
export class OvershootMotion implements MotionFunction {
  public readonly type = "overshoot";
  public readonly amount: number;

  constructor(options: OvershootOptions = {}) {
    this.amount = options.amount !== undefined ? Math.max(0, options.amount) : 1.0;
  }

  public evaluate(p: number): number {
    if (p <= 0) return 0;
    if (p >= 1) return 1;

    const s = this.amount * 1.70158;
    const inv = p - 1;
    return inv * inv * ((s + 1) * inv + s) + 1;
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      amount: this.amount,
    };
  }
}

export function overshoot(options: OvershootOptions = {}): OvershootMotion {
  return new OvershootMotion(options);
}
