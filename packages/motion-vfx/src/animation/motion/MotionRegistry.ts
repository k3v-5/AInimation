import { SerializationError } from "../../errors/index.js";
import { bounce, BounceMotion } from "./BounceMotion.js";
import { elastic, ElasticMotion } from "./ElasticMotion.js";
import { overshoot, OvershootMotion } from "./OvershootMotion.js";
import { shake, ShakeMotion } from "./ShakeMotion.js";
import { spring, SpringMotion } from "./SpringMotion.js";
import { MotionFunction, MotionMetadata } from "./types.js";
import { wiggle, WiggleMotion } from "./WiggleMotion.js";

/**
 * Catálogo central de funciones de movimiento avanzadas, metadatos y deserialización.
 */
export class MotionRegistry {
  private static metadataList: MotionMetadata[] = [
    {
      type: "overshoot",
      name: "Overshoot / Back",
      description: "Produce un sobrepaso orgánico del destino antes de estabilizarse.",
      parameters: {
        amount: { type: "number", default: 1.0, min: 0, description: "Factor de sobrepaso" },
      },
    },
    {
      type: "spring",
      name: "Spring Physics",
      description: "Simulación armónica analítica de oscilador masa-resorte-amortiguador.",
      parameters: {
        mass: { type: "number", default: 1.0, min: 0.01, description: "Masa del objeto" },
        stiffness: { type: "number", default: 100, min: 1, description: "Rigidez del resorte" },
        damping: { type: "number", default: 10, min: 0, description: "Amortiguamiento" },
        preset: { type: "string", default: undefined, description: "Preset: gentle | snappy | bouncy | heavy" },
      },
    },
    {
      type: "bounce",
      name: "Gravitational Bounce",
      description: "Impactos y rebotes discretos simulados por tramos parabólicos.",
      parameters: {
        bounces: { type: "number", default: 3, min: 1, max: 10, description: "Número de rebotes" },
        decay: { type: "number", default: 0.5, min: 0.1, max: 0.9, description: "Decaimiento" },
      },
    },
    {
      type: "elastic",
      name: "Elastic Oscillation",
      description: "Oscilación sinusoidal amortiguada exponencialmente alrededor del destino.",
      parameters: {
        amplitude: { type: "number", default: 1.0, description: "Amplitud inicial" },
        period: { type: "number", default: 0.3, min: 0.05, description: "Período oscilatorio" },
      },
    },
    {
      type: "shake",
      name: "Deterministic Shake",
      description: "Vibración pseudo-aleatoria determinista con decaimiento temporal.",
      parameters: {
        amplitude: { type: "number", default: 1.0, description: "Amplitud" },
        frequency: { type: "number", default: 10, min: 1, description: "Frecuencia en Hz" },
      },
    },
    {
      type: "wiggle",
      name: "Continuous Wiggle",
      description: "Onda armónica continua determinista para movimiento ambiental.",
      parameters: {
        amplitude: { type: "number", default: 1.0, description: "Amplitud" },
        frequency: { type: "number", default: 2.0, min: 0.1, description: "Frecuencia" },
      },
    },
  ];

  /**
   * Retorna la lista completa de metadatos de las funciones de movimiento.
   */
  public static listMetadata(): MotionMetadata[] {
    return [...this.metadataList];
  }

  /**
   * Deserializa un objeto JSON en su correspondiente MotionFunction.
   */
  public static fromJSON(raw: any): MotionFunction {
    if (!raw || typeof raw !== "object") {
      throw new SerializationError("Motion JSON must be an object.");
    }

    const { type } = raw;

    switch (type) {
      case "overshoot":
        return overshoot({ amount: raw.amount });
      case "spring":
        return spring({
          mass: raw.mass,
          stiffness: raw.stiffness,
          damping: raw.damping,
          velocity: raw.velocity,
          preset: raw.preset,
        });
      case "bounce":
        return bounce({ bounces: raw.bounces, decay: raw.decay });
      case "elastic":
        return elastic({ amplitude: raw.amplitude, period: raw.period });
      case "shake":
        return shake({
          amplitude: raw.amplitude,
          frequency: raw.frequency,
          decay: raw.decay,
          seed: raw.seed,
        });
      case "wiggle":
        return wiggle({
          amplitude: raw.amplitude,
          frequency: raw.frequency,
          seed: raw.seed,
        });
      default:
        throw new SerializationError(`Unsupported motion function type '${type}'.`);
    }
  }
}
