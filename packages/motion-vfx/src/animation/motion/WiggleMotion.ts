import { MotionFunction, WiggleOptions } from "./types.js";

/**
 * Función de perturbación continua determinista para movimiento ambiental o flotante (Wiggle).
 */
export class WiggleMotion implements MotionFunction {
  public readonly type = "wiggle";
  public readonly amplitude: number;
  public readonly frequency: number;
  public readonly seed: number;

  constructor(options: WiggleOptions = {}) {
    this.amplitude = options.amplitude !== undefined ? options.amplitude : 1.0;
    this.frequency = options.frequency !== undefined ? Math.max(0.1, options.frequency) : 2.0;
    this.seed = options.seed ?? 123;
  }

  public evaluate(p: number): number {
    const f1 = this.frequency;
    const f2 = this.frequency * 1.5;

    const phi1 = (this.seed * 0.31) % (2 * Math.PI);
    const phi2 = (this.seed * 0.77) % (2 * Math.PI);

    const wave =
      0.6 * Math.sin(2 * Math.PI * f1 * p + phi1) +
      0.4 * Math.sin(2 * Math.PI * f2 * p + phi2);

    return this.amplitude * wave;
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      amplitude: this.amplitude,
      frequency: this.frequency,
      seed: this.seed,
    };
  }
}

export function wiggle(options: WiggleOptions = {}): WiggleMotion {
  return new WiggleMotion(options);
}
