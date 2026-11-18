import { MotionFunction, SpringOptions, SpringPresetName } from "./types.js";

const SPRING_PRESETS: Record<SpringPresetName, { mass: number; stiffness: number; damping: number }> = {
  gentle: { mass: 1, stiffness: 100, damping: 15 },
  snappy: { mass: 1, stiffness: 200, damping: 20 },
  bouncy: { mass: 1, stiffness: 180, damping: 10 },
  heavy: { mass: 2, stiffness: 80, damping: 20 },
};

/**
 * Función de movimiento físico analítico determinista (Harmonic Spring Oscillator).
 */
export class SpringMotion implements MotionFunction {
  public readonly type = "spring";
  public readonly mass: number;
  public readonly stiffness: number;
  public readonly damping: number;
  public readonly velocity: number;
  public readonly preset?: SpringPresetName;

  private omega0: number;
  private zeta: number;
  private settlingTime: number;

  constructor(options: SpringOptions = {}) {
    if (options.preset && SPRING_PRESETS[options.preset]) {
      const p = SPRING_PRESETS[options.preset];
      this.mass = options.mass ?? p.mass;
      this.stiffness = options.stiffness ?? p.stiffness;
      this.damping = options.damping ?? p.damping;
      this.preset = options.preset;
    } else {
      this.mass = options.mass !== undefined && options.mass > 0 ? options.mass : 1.0;
      this.stiffness = options.stiffness !== undefined && options.stiffness > 0 ? options.stiffness : 100.0;
      this.damping = options.damping !== undefined && options.damping >= 0 ? options.damping : 10.0;
    }
    this.velocity = options.velocity ?? 0;

    this.omega0 = Math.sqrt(this.stiffness / this.mass);
    this.zeta = this.damping / (2 * Math.sqrt(this.mass * this.stiffness));

    // Tiempo de establecimiento aproximado para mapear progress [0, 1] al dominio temporal
    const decayRate = Math.max(0.1, this.zeta * this.omega0);
    this.settlingTime = Math.min(2.0, Math.max(0.5, 4.5 / decayRate));
  }

  public evaluate(progress: number): number {
    if (progress <= 0) return 0;
    if (progress >= 1) return 1;

    const t = progress * this.settlingTime;

    // 1. Sub-amortiguado (Underdamped: zeta < 1) -> Produce oscilaciones orgánicas
    if (this.zeta < 1) {
      const omegaD = this.omega0 * Math.sqrt(1 - this.zeta * this.zeta);
      const envelope = Math.exp(-this.zeta * this.omega0 * t);
      const cosTerm = Math.cos(omegaD * t);
      const sinTerm = ((this.zeta * this.omega0 - this.velocity) / omegaD) * Math.sin(omegaD * t);
      return 1 - envelope * (cosTerm + sinTerm);
    }

    // 2. Críticamente amortiguado (Critically damped: zeta == 1) -> Converge lo más rápido posible sin oscilar
    if (Math.abs(this.zeta - 1) < 1e-6) {
      const envelope = Math.exp(-this.omega0 * t);
      return 1 - envelope * (1 + (this.omega0 - this.velocity) * t);
    }

    // 3. Sobre-amortiguado (Overdamped: zeta > 1) -> Converge lentamente sin sobrepasos
    const r1 = -this.omega0 * (this.zeta - Math.sqrt(this.zeta * this.zeta - 1));
    const r2 = -this.omega0 * (this.zeta + Math.sqrt(this.zeta * this.zeta - 1));
    const denom = r2 - r1;
    return 1 - (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / denom;
  }

  public toJSON(): Record<string, unknown> {
    return {
      type: this.type,
      mass: this.mass,
      stiffness: this.stiffness,
      damping: this.damping,
      velocity: this.velocity,
      preset: this.preset,
    };
  }
}

export function spring(options: SpringOptions = {}): SpringMotion {
  return new SpringMotion(options);
}
