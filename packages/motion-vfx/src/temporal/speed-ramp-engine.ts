import {
  QuantizedSpeedRampSpec,
  QuantizedSpeedRampSpecSchema,
  TimeRemapKeyframe,
  TimeRemapKeyframeSchema,
} from "./temporal-types.js";

/**
 * Motor de Speed Ramping cuantizado y alineado a transientes musicales.
 * Genera curvas de Time Remapping continuas (C^1) con desaceleración dramática en el drop.
 */
export class SpeedRampEngine {
  /**
   * Evalúa la velocidad instantánea v(t) en la línea de tiempo.
   */
  public static evaluateVelocityAtTime(specInput: QuantizedSpeedRampSpec, t: number): number {
    const spec = QuantizedSpeedRampSpecSchema.parse(specInput);
    const { targetBeatDropTimeSeconds, fastMultiplier, slowMultiplier, transitionDurationSeconds } = spec;

    const tTransStart = Math.max(0, targetBeatDropTimeSeconds - transitionDurationSeconds);

    if (t < tTransStart) {
      return fastMultiplier;
    }

    if (t >= targetBeatDropTimeSeconds) {
      return slowMultiplier;
    }

    // Intervalo de transición Bézier suave (Smoothstep entre fast y slow)
    const p = (t - tTransStart) / (targetBeatDropTimeSeconds - tTransStart);
    const smoothP = p * p * (3 - 2 * p);
    const v = fastMultiplier + (slowMultiplier - fastMultiplier) * smoothP;
    return Number(v.toFixed(4));
  }

  /**
   * Genera los keyframes de Time Remap discretos integrando numéricamente la velocidad v(t).
   */
  public static generateTimeRemapKeyframes(
    specInput: QuantizedSpeedRampSpec,
    fps = 30.0
  ): TimeRemapKeyframe[] {
    const spec = QuantizedSpeedRampSpecSchema.parse(specInput);
    const keyframes: TimeRemapKeyframe[] = [];

    const dt = 1.0 / fps;
    const totalT = spec.totalTimelineDurationSeconds;

    let currentSourceTime = 0.0;

    for (let t = 0.0; t <= totalT + 1e-6; t += dt) {
      const v = this.evaluateVelocityAtTime(spec, t);
      currentSourceTime += v * dt;

      // Limitar a la duración del metraje disponible
      const clampedSourceTime = Math.min(spec.sourceClipDurationSeconds, currentSourceTime);

      keyframes.push(
        TimeRemapKeyframeSchema.parse({
          timelineSeconds: Number(t.toFixed(4)),
          sourceSeconds: Number(clampedSourceTime.toFixed(4)),
        })
      );
    }

    return keyframes;
  }

  /**
   * Genera las sentencias ExtendScript para aplicar el Time Remap en After Effects.
   */
  public static exportToExtendScript(
    spec: QuantizedSpeedRampSpec,
    options: { layerVarName?: string; fps?: number } = {}
  ): string[] {
    const layerVar = options.layerVarName ?? "targetLayer";
    const keyframes = this.generateTimeRemapKeyframes(spec, options.fps ?? 30.0);
    const lines: string[] = [];

    lines.push(`  // === QUANTIZED SPEED RAMPING (ID: ${spec.id} | Drop: ${spec.targetBeatDropTimeSeconds.toFixed(3)}s) ===`);
    lines.push(`  try {`);
    lines.push(`    ${layerVar}.enableTimeRemapping();`);
    lines.push(`    var trProp = ${layerVar}.property("Time Remap");`);
    lines.push(`    if (trProp) {`);
    // Limpiar keyframes por defecto
    lines.push(`      while (trProp.numKeys > 0) { trProp.removeKey(1); }`);
    for (const kf of keyframes) {
      lines.push(`      trProp.setValueAtTime(${kf.timelineSeconds.toFixed(3)}, ${kf.sourceSeconds.toFixed(3)});`);
    }
    lines.push(`    }`);
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
