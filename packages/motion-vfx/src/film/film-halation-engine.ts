import { FilmHalationSpec, FilmHalationSpecInput, FilmHalationSpecSchema } from "./film-types.js";

/**
 * Motor de Film Halation (destellos carmesí en bordes de altas luces de película Kodak).
 */
export class FilmHalationEngine {
  /**
   * Evalúa la intensidad del destello de Halation en función de la luminancia local.
   */
  public static calculateHalationIntensity(
    luminanceY: number,
    threshold: number,
    maxIntensity: number
  ): number {
    const clampedY = Math.max(0.0, Math.min(1.0, luminanceY));
    if (clampedY <= threshold) return 0.0;

    const normalizedOver = (clampedY - threshold) / (1.0 - threshold + 1e-12);
    const intensity = maxIntensity * Math.pow(normalizedOver, 1.8);
    return Number(Math.min(maxIntensity, intensity).toFixed(6));
  }

  /**
   * Genera el código ExtendScript para ensamblar la capa de dispersión roja de Halation en After Effects.
   */
  public static exportToExtendScript(
    specInput: FilmHalationSpecInput,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const spec = FilmHalationSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    const redR = spec.tintRgb[0];
    const redG = spec.tintRgb[1];
    const redB = spec.tintRgb[2];

    lines.push(`  // === FILM HALATION LAYER (Kodak Vision3 Red Antihalation Glow) ===`);
    lines.push(`  try {`);
    lines.push(`    var haloLyr = ${layerVar}.duplicate();`);
    lines.push(`    haloLyr.name = "[HALATION] Red High-Contrast Glow";`);
    lines.push(`    haloLyr.blendingMode = BlendingMode.SCREEN;`);
    lines.push(`    haloLyr.opacity.setValue(${Math.round(spec.intensity * 100)});`);
    lines.push(`    // 1. Extraer Altas Luces`);
    lines.push(`    var extFx = haloLyr.property("Effects").addProperty("ADBE Extract");`);
    lines.push(`    if (extFx) {`);
    lines.push(`      extFx.property("Black Point").setValue(${Math.round(spec.threshold * 255)});`);
    lines.push(`      extFx.property("Black Softness").setValue(15);`);
    lines.push(`    }`);
    lines.push(`    // 2. Dispersión Óptica Gaussiana`);
    lines.push(`    var blurFx = haloLyr.property("Effects").addProperty("ADBE Gaussian Blur");`);
    lines.push(`    if (blurFx) {`);
    lines.push(`      blurFx.property("Blurriness").setValue(${spec.radiusPx.toFixed(1)});`);
    lines.push(`      blurFx.property("Repeat Edge Pixels").setValue(true);`);
    lines.push(`    }`);
    lines.push(`    // 3. Tinte Rojo Carmesí de Película Kodak`);
    lines.push(`    var tintFx = haloLyr.property("Effects").addProperty("ADBE Tint");`);
    lines.push(`    if (tintFx) {`);
    lines.push(`      tintFx.property("Map White To").setValue([${redR}, ${redG}, ${redB}]);`);
    lines.push(`      tintFx.property("Amount to Tint").setValue(100);`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
