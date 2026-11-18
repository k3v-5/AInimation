import { PosterizeTimeSpec, PosterizeTimeSpecSchema } from "./temporal-types.js";

/**
 * Motor de cuantización de tasa de fotogramas (Posterize Time).
 * Genera la textura de celuloide clásico 16mm, animación tradicional a doses (12fps) o stop-motion (8fps).
 */
export class PosterizeTimeEngine {
  /**
   * Cuantiza matemáticamente un timestamp continuo a la tasa de fotogramas objetivo:
   * t_sampled = floor(t * targetFps) / targetFps
   */
  public static quantizeTimestamp(timeSeconds: number, targetFps: number): number {
    if (timeSeconds < 0) return 0.0;
    if (targetFps <= 0) return timeSeconds;
    const frameIndex = Math.floor(timeSeconds * targetFps);
    return Number((frameIndex / targetFps).toFixed(6));
  }

  /**
   * Genera las sentencias ExtendScript para inyectar el efecto Posterize Time en After Effects.
   */
  public static exportToExtendScript(
    specInput: PosterizeTimeSpec,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = PosterizeTimeSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    lines.push(`  // === POSTERIZE TIME ENGINE (Target: ${spec.targetFps} fps) ===`);
    lines.push(`  try {`);
    lines.push(`    var postFx = ${layerVar}.property("Effects").addProperty("ADBE Posterize Time");`);
    lines.push(`    if (postFx) {`);
    lines.push(`      postFx.property("Frame Rate").setValue(${spec.targetFps});`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
