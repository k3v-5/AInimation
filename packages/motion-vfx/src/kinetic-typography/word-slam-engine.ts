import {
  WordSlamSpec,
  WordSlamSpecInput,
  WordSlamSpecSchema,
} from "./kinetic-typography-types.js";

/**
 * Motor de impacto percusivo con rebote armónico subamortiguado (Word Slam).
 */
export class WordSlamEngine {
  /**
   * Evalúa la escala instantánea en un tiempo relativo t >= 0 mediante oscilador armónico subamortiguado:
   * S(t) = S_target + (S_initial - S_target) * e^(-zeta * w_n * t) * cos(w_d * t)
   */
  public static evaluateSlamScale(
    tRel: number,
    initialScale: number,
    targetScale: number = 100.0,
    dampingRatio: number = 0.55,
    naturalFrequency: number = 24.0
  ): number {
    if (tRel <= 0.0) return initialScale;
    const zeta = Math.max(0.1, Math.min(0.95, dampingRatio));
    const wd = naturalFrequency * Math.sqrt(1.0 - zeta * zeta);
    const decay = Math.exp(-zeta * naturalFrequency * tRel);
    const oscillation = Math.cos(wd * tRel);
    const scale = targetScale + (initialScale - targetScale) * decay * oscillation;
    return Number(scale.toFixed(2));
  }

  /**
   * Genera los pares [tiempo, escala] discretos para inyectar en After Effects.
   */
  public static generateScaleKeyframes(
    specInput: WordSlamSpecInput,
    fps: number,
    verticalStretchMultiplier: number = 1.0
  ): Array<{ timeSeconds: number; scaleX: number; scaleY: number }> {
    const spec = WordSlamSpecSchema.parse(specInput);
    const totalFrames = Math.max(2, Math.round(spec.durationSeconds * fps));
    const kfs: Array<{ timeSeconds: number; scaleX: number; scaleY: number }> = [];

    for (let f = 0; f <= totalFrames; f++) {
      const tRel = f / fps;
      const timelineSec = Number((spec.triggerTimeSeconds + tRel).toFixed(5));
      const s = this.evaluateSlamScale(
        tRel,
        spec.initialScalePercent,
        100.0,
        spec.dampingRatio,
        spec.naturalFrequency
      );

      kfs.push({
        timeSeconds: timelineSec,
        scaleX: s,
        scaleY: Number((s * verticalStretchMultiplier).toFixed(2)),
      });
    }

    return kfs;
  }

  /**
   * Genera las sentencias ExtendScript para animar el golpe de slam con rebote elástico.
   */
  public static exportToExtendScript(
    specInput: WordSlamSpecInput,
    fps: number,
    verticalStretchMultiplier: number = 1.0,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = WordSlamSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "textLyr";
    const kfs = this.generateScaleKeyframes(spec, fps, verticalStretchMultiplier);
    const lines: string[] = [];

    lines.push(`  // === WORD SLAM BOUNCE ANIMATION: ${spec.id} ===`);
    lines.push(`  try {`);
    lines.push(`    var scProp = ${layerVar}.property("Transform").property("Scale");`);
    for (const kf of kfs) {
      lines.push(
        `    scProp.setValueAtTime(${kf.timeSeconds.toFixed(4)}, [${kf.scaleX.toFixed(1)}, ${kf.scaleY.toFixed(1)}]);`
      );
    }
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in WordSlamEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
