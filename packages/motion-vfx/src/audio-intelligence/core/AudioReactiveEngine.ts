import { Time } from "../../core/types.js";
import { AudioBinding, AudioMapping } from "../types/index.js";
import { AudioSignal } from "./AudioSignal.js";

/**
 * Evaluador de transformaciones de propiedades reactivas al audio (Fase 5I).
 */
export class AudioReactiveEngine {
  /**
   * Mapea un valor normalizado según la configuración de AudioMapping.
   */
  public static mapValue(value: number, mapping: AudioMapping): number {
    // 1. Manejar umbral si está definido
    if (mapping.threshold) {
      if (value < mapping.threshold.value) {
        return mapping.threshold.below;
      }
      return mapping.threshold.above;
    }

    const [inMin, inMax] = mapping.inputRange;
    const [outMin, outMax] = mapping.outputRange;

    // Normalizar entrada al rango [0, 1]
    const inRange = inMax - inMin;
    let t = inRange !== 0 ? (value - inMin) / inRange : 0;
    t = Math.max(0, Math.min(1, t));

    // Aplicar función de transferencia
    switch (mapping.mode) {
      case "exponential":
        t = Math.pow(t, 2);
        break;
      case "logarithmic":
        t = Math.sqrt(t);
        break;
      case "linear":
      case "clamp":
      default:
        break;
    }

    return outMin + t * (outMax - outMin);
  }

  /**
   * Evalúa un AudioBinding contra una señal dada a un tiempo específico.
   */
  public static evaluateBinding(
    binding: AudioBinding,
    signal: AudioSignal,
    time: Time
  ): number {
    let rawValue = 0;
    if (binding.envelope) {
      rawValue = signal.sampleEnvelope(
        time,
        binding.envelope.attackTime,
        binding.envelope.releaseTime
      );
    } else {
      rawValue = signal.sample(time);
    }

    return this.mapValue(rawValue, binding.mapping);
  }
}
