import { FilmGrainSpec, FilmGrainSpecInput, FilmGrainSpecSchema } from "./film-types.js";

/**
 * Motor de generación y simulación física de grano de película analógica (Fase 22).
 */
export class FilmGrainEngine {
  /**
   * Calcula la densidad de grano efectiva en función de la luminancia local Y en [0.0, 1.0]:
   * G(Y) = baseIntensity * 4 * Y * (1 - Y)
   */
  public static calculateLuminanceCoupledDensity(baseIntensity: number, luminanceY: number): number {
    const clampedY = Math.max(0.0, Math.min(1.0, luminanceY));
    const factor = 4.0 * clampedY * (1.0 - clampedY);
    return Number((baseIntensity * factor).toFixed(6));
  }

  /**
   * Genera las sentencias ExtendScript para inyectar grano de película analógica en After Effects.
   */
  public static exportToExtendScript(
    specInput: FilmGrainSpecInput,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const spec = FilmGrainSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    const grainPercent = spec.gauge === "16MM" ? (spec.intensity * 18.0).toFixed(1) : (spec.intensity * 9.0).toFixed(1);

    lines.push(`  // === FILM GRAIN ENGINE (${spec.gauge} Analog Emulation) ===`);
    lines.push(`  try {`);
    lines.push(`    var grainFx = ${layerVar}.property("Effects").addProperty("ADBE Noise");`);
    lines.push(`    if (grainFx) {`);
    lines.push(`      grainFx.property("Amount of Noise").setValue(${grainPercent});`);
    lines.push(`      grainFx.property("Use Color Noise").setValue(${spec.colorNoise});`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
