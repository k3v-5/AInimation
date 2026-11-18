import { SnapZoomSpec, SnapZoomSpecSchema } from "./optics-types.js";

/**
 * Motor de generación y cálculo de Snap / Crash Zooms percusivos con rebote inercial.
 */
export class SnapZoomEngine {
  /**
   * Evalúa matemáticamente la escala en el tiempo t para un Snap Zoom.
   */
  public static evaluateScaleAtTime(specInput: SnapZoomSpec, timeSeconds: number): number {
    const spec = SnapZoomSpecSchema.parse(specInput);
    const { triggerTimeSeconds, durationSeconds, startScalePercent, peakScalePercent, settleScalePercent, dampingRatio, frequencyHz } = spec;

    if (timeSeconds < triggerTimeSeconds) {
      return startScalePercent;
    }

    const elapsed = timeSeconds - triggerTimeSeconds;
    if (elapsed >= durationSeconds) {
      return settleScalePercent;
    }

    // Fase 1: Subida instantánea al pico (primeros 25% del tiempo de snap)
    const riseTime = durationSeconds * 0.25;
    if (elapsed <= riseTime) {
      const p = elapsed / riseTime;
      // Curva rápida exponencial de impacto
      const easeInScale = startScalePercent + (peakScalePercent - startScalePercent) * Math.pow(p, 2);
      return Number(easeInScale.toFixed(4));
    }

    // Fase 2: Rebote inercial armónico amortiguado hacia settleScale
    const tOsc = elapsed - riseTime;
    const omega = 2 * Math.PI * frequencyHz;
    const lambda = dampingRatio * omega;

    const delta = peakScalePercent - settleScalePercent;
    const oscillation = Math.exp(-lambda * tOsc) * Math.cos(omega * tOsc);
    const currentScale = settleScalePercent + delta * oscillation;

    return Number(currentScale.toFixed(4));
  }

  /**
   * Genera un conjunto de keyframes discretos para interpolación precisa en After Effects.
   */
  public static generateKeyframes(
    specInput: SnapZoomSpec,
    fps = 30.0
  ): Array<{ timeSeconds: number; scalePercent: number }> {
    const spec = SnapZoomSpecSchema.parse(specInput);
    const keyframes: Array<{ timeSeconds: number; scalePercent: number }> = [];

    const frameStep = 1.0 / fps;
    const startTime = spec.triggerTimeSeconds;
    const endTime = spec.triggerTimeSeconds + spec.durationSeconds;

    // Keyframe inicial previo al impacto
    if (startTime > 0.01) {
      keyframes.push({
        timeSeconds: Number((startTime - 0.01).toFixed(4)),
        scalePercent: spec.startScalePercent,
      });
    }

    for (let t = startTime; t <= endTime + 1e-6; t += frameStep) {
      keyframes.push({
        timeSeconds: Number(t.toFixed(4)),
        scalePercent: this.evaluateScaleAtTime(spec, t),
      });
    }

    // Keyframe final de reposo asegurado
    keyframes.push({
      timeSeconds: Number(endTime.toFixed(4)),
      scalePercent: spec.settleScalePercent,
    });

    return keyframes;
  }

  /**
   * Genera las sentencias ExtendScript para inyectar los keyframes de escala en una capa de After Effects.
   */
  public static exportToExtendScript(
    spec: SnapZoomSpec,
    options: { layerVarName?: string; fps?: number } = {}
  ): string[] {
    const layerVar = options.layerVarName ?? "targetLayer";
    const keyframes = this.generateKeyframes(spec, options.fps ?? 30.0);
    const lines: string[] = [];

    lines.push(`  // --- Snap Zoom Percusivo (ID: ${spec.id} @ ${spec.triggerTimeSeconds.toFixed(3)}s) ---`);
    lines.push(`  var scaleProp_${spec.id} = ${layerVar}.property("Transform").property("Scale");`);
    for (const kf of keyframes) {
      lines.push(
        `  scaleProp_${spec.id}.setValueAtTime(${kf.timeSeconds.toFixed(3)}, [${kf.scalePercent.toFixed(2)}, ${kf.scalePercent.toFixed(2)}]);`
      );
    }

    return lines;
  }
}
