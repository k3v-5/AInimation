import { MotionFunction, ShakeOptions } from "./types.js";

/**
 * Función de perturbación determinista de corta duración con envolvente de decaimiento (Shake).
 * Garantiza cero aleatoriedad en tiempo de ejecución (sin Math.random).
 */
export class ShakeMotion implements MotionFunction {
  public readonly type = "shake";
  public readonly amplitude: number;
  public readonly frequency: number;
  public readonly decay: boolean;
  public readonly seed: number;

  constructor(options: ShakeOptions = {}) {
    this.amplitude = options.amplitude !== undefined ? options.amplitude : 1.0;
    this.frequency = options.frequency !== undefined ? Math.max(1, options.frequency) : 10;
    this.decay = options.decay ?? true;
    this.seed = options.seed ?? 42;
  }

  public evaluate(p: number): number {
    if (p <= 0 || p >= 1) {
      return 0;
    }

    const envelope = this.decay ? (1 - p) * (1 - p) : 1.0;
    const f1 = this.frequency;
    const f2 = this.frequency * 1.61803398875; // Proporción áurea determinista
    const f3 = this.frequency * 2.71828182845; // Constante e determinista

    const phi1 = (this.seed * 0.17) % (2 * Math.PI);
    const phi2 = (this.seed * 0.43) % (2 * Math.PI);
    const phi3 = (this.seed * 0.89) % (2 * Math.PI);

    const wave =
      0.5 * Math.sin(2 * Math.PI * f1 * p + phi1) +
      0.3 * Math.sin(2 * Math.PI * f2 * p + phi2) +
      0.2 * Math.sin(2 * Math.PI * f3 * p + phi3);

    return this.amplitude * envelope * wave;
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      amplitude: this.amplitude,
      frequency: this.frequency,
      decay: this.decay,
      seed: this.seed,
    };
  }
}

export function shake(options: ShakeOptions = {}): ShakeMotion {
  return new ShakeMotion(options);
}
