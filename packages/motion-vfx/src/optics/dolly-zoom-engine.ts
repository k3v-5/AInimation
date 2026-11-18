import { DollyZoomSpec, DollyZoomSpecSchema } from "./optics-types.js";

/**
 * Motor de cálculo del efecto Dolly Zoom (Vértigo).
 * Mantiene invariable el encuadre del sujeto mientras deforma la perspectiva del fondo.
 */
export class DollyZoomEngine {
  /**
   * Calcula el factor de compensación de escala para mantener el tamaño del sujeto:
   * Factor(t) = tan(FOV_0 / 2) / tan(FOV(t) / 2)
   */
  public static calculateScaleCompensation(initialFovDegrees: number, targetFovDegrees: number): number {
    const rad0 = (initialFovDegrees * Math.PI) / 360.0;
    const radTarget = (targetFovDegrees * Math.PI) / 360.0;

    const tan0 = Math.tan(rad0);
    const tanTarget = Math.tan(radTarget);

    if (Math.abs(tanTarget) < 1e-6) return 1.0;
    return Number((tan0 / tanTarget).toFixed(6));
  }

  /**
   * Genera el conjunto de keyframes de compensación para la capa de sujeto y la cámara virtual.
   */
  public static generateKeyframes(
    specInput: DollyZoomSpec,
    fps = 30.0
  ): Array<{ timeSeconds: number; fovDegrees: number; scaleFactor: number }> {
    const spec = DollyZoomSpecSchema.parse(specInput);
    const keyframes: Array<{ timeSeconds: number; fovDegrees: number; scaleFactor: number }> = [];

    const frameStep = 1.0 / fps;
    const startT = spec.startTimeSeconds;
    const endT = spec.startTimeSeconds + spec.durationSeconds;

    for (let t = startT; t <= endT + 1e-6; t += frameStep) {
      const progress = Math.min(1.0, Math.max(0.0, (t - startT) / spec.durationSeconds));
      // Curva smoothstep para el travelling de la cámara
      const smoothP = progress * progress * (3 - 2 * progress);
      const currentFov = spec.initialFovDegrees + (spec.finalFovDegrees - spec.initialFovDegrees) * smoothP;
      const scaleFactor = this.calculateScaleCompensation(spec.initialFovDegrees, currentFov);

      keyframes.push({
        timeSeconds: Number(t.toFixed(4)),
        fovDegrees: Number(currentFov.toFixed(2)),
        scaleFactor: Number(scaleFactor.toFixed(4)),
      });
    }

    return keyframes;
  }

  /**
   * Genera sentencias ExtendScript para animar el Dolly Zoom en After Effects.
   */
  public static exportToExtendScript(
    spec: DollyZoomSpec,
    options: { layerVarName?: string; cameraVarName?: string; fps?: number } = {}
  ): string[] {
    const layerVar = options.layerVarName ?? "targetLayer";
    const keyframes = this.generateKeyframes(spec, options.fps ?? 30.0);
    const lines: string[] = [];

    lines.push(`// === DOLLY ZOOM (VERTIGO EFFECT) ID: ${spec.id} ===`);
    lines.push(`var scaleProp_${spec.id} = ${layerVar}.property("Transform").property("Scale");`);
    for (const kf of keyframes) {
      lines.push(
        `scaleProp_${spec.id}.setValueAtTime(${kf.timeSeconds.toFixed(3)}, [100.0 * ${kf.scaleFactor.toFixed(4)}, 100.0 * ${kf.scaleFactor.toFixed(4)}]);`
      );
    }

    return lines;
  }
}
