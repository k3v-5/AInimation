import {
  InfiniteZoomPortalSpec,
  InfiniteZoomPortalSpecInput,
  InfiniteZoomPortalSpecSchema,
} from "./spatial-types.js";

/**
 * Motor de transición de agujero de gusano (Infinite Zoom Portal).
 */
export class InfiniteZoomPortalEngine {
  /**
   * Evalúa la escala instantánea en progreso normalizado tau en [0, 1] mediante modelo super-exponencial:
   * S(tau) = S_base * exp( ln(S_max / S_base) * tau^gamma )
   */
  public static evaluatePortalScale(
    tau: number,
    maxScalePercent: number = 6000.0,
    gamma: number = 3.0,
    baseScale: number = 100.0
  ): number {
    const clampedTau = Math.max(0.0, Math.min(1.0, tau));
    const k = Math.log(maxScalePercent / baseScale);
    const exponent = k * Math.pow(clampedTau, gamma);
    const scale = baseScale * Math.exp(exponent);
    return Number(scale.toFixed(2));
  }

  /**
   * Genera los keyframes discretos de Escala y Punto de Anclaje para inyectar en After Effects.
   */
  public static generatePortalKeyframes(
    specInput: InfiniteZoomPortalSpecInput,
    fps: number,
    initialAnchor: [number, number] = [540, 960]
  ): Array<{
    timeSeconds: number;
    scale: number;
    anchorPoint: [number, number];
  }> {
    const spec = InfiniteZoomPortalSpecSchema.parse(specInput);
    const totalFrames = Math.max(2, Math.round(spec.durationSeconds * fps));
    const kfs: Array<{ timeSeconds: number; scale: number; anchorPoint: [number, number] }> = [];

    for (let f = 0; f <= totalFrames; f++) {
      const tau = f / totalFrames;
      const t = Number((spec.startTimeSeconds + (f / fps)).toFixed(5));
      const scale = this.evaluatePortalScale(tau, spec.maxScalePercent, spec.accelerationExponent);

      // Desplazamiento acelerado del punto de anclaje hacia el centro del portal
      const anchorX = initialAnchor[0] + (spec.portalCenterPoint[0] - initialAnchor[0]) * Math.pow(tau, 2.0);
      const anchorY = initialAnchor[1] + (spec.portalCenterPoint[1] - initialAnchor[1]) * Math.pow(tau, 2.0);

      kfs.push({
        timeSeconds: t,
        scale,
        anchorPoint: [Number(anchorX.toFixed(1)), Number(anchorY.toFixed(1))],
      });
    }

    return kfs;
  }

  /**
   * Genera las sentencias ExtendScript para animar el crash zoom infinito en After Effects.
   */
  public static exportToExtendScript(
    specInput: InfiniteZoomPortalSpecInput,
    fps: number,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = InfiniteZoomPortalSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "sourceLayer";
    const kfs = this.generatePortalKeyframes(spec, fps);
    const lines: string[] = [];

    lines.push(`  // === INFINITE ZOOM PORTAL: ${spec.id} (Max Scale: ${spec.maxScalePercent}%) ===`);
    lines.push(`  try {`);
    lines.push(`    if (${layerVar}) {`);
    lines.push(`      ${layerVar}.motionBlur = true; // Invariante obligatoria`);
    lines.push(`      var scProp = ${layerVar}.property("Transform").property("Scale");`);
    lines.push(`      var apProp = ${layerVar}.property("Transform").property("Anchor Point");`);

    for (const kf of kfs) {
      lines.push(
        `      scProp.setValueAtTime(${kf.timeSeconds.toFixed(4)}, [${kf.scale.toFixed(1)}, ${kf.scale.toFixed(1)}]);`
      );
      lines.push(
        `      apProp.setValueAtTime(${kf.timeSeconds.toFixed(4)}, [${kf.anchorPoint[0].toFixed(1)}, ${kf.anchorPoint[1].toFixed(1)}]);`
      );
    }

    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in InfiniteZoomPortalEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
