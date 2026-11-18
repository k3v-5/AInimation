import {
  LensBreathingSpec,
  LensBreathingSpecInput,
  LensBreathingSpecSchema,
} from "./mechanics-types.js";

/**
 * Motor de emulación de respiración óptica analógica en tirón de foco (Procedural Lens Breathing).
 */
export class LensBreathingEngine {
  /**
   * Genera las sentencias ExtendScript para aplicar respiración de distancia focal y desenfoque.
   */
  public static exportToExtendScript(
    specInput: LensBreathingSpecInput,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = LensBreathingSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "videoLyr";
    const tStart = spec.startTimeSeconds;
    const tEnd = Number((spec.startTimeSeconds + spec.durationSeconds).toFixed(5));

    const sStart = spec.focusPullDirection === "NEAR_TO_FAR" ? 100.0 : 100.0 + spec.breatheScalePercent;
    const sEnd = spec.focusPullDirection === "NEAR_TO_FAR" ? 100.0 + spec.breatheScalePercent : 100.0;

    const blurStart = spec.focusPullDirection === "NEAR_TO_FAR" ? spec.lensRackBlurPx : 0.0;
    const blurEnd = spec.focusPullDirection === "NEAR_TO_FAR" ? 0.0 : spec.lensRackBlurPx;

    const lines: string[] = [];

    lines.push(`  // === PROCEDURAL LENS BREATHING: ${spec.id} (${spec.focusPullDirection}) ===`);
    lines.push(`  try {`);
    lines.push(`    if (${layerVar}) {`);
    lines.push(`      // 1. Modulación de Escala Óptica Parásita (+${spec.breatheScalePercent.toFixed(1)}%)`);
    lines.push(`      var scProp = ${layerVar}.property("Transform").property("Scale");`);
    lines.push(`      scProp.setValueAtTime(${tStart.toFixed(4)}, [${sStart.toFixed(2)}, ${sStart.toFixed(2)}]);`);
    lines.push(`      scProp.setValueAtTime(${tEnd.toFixed(4)}, [${sEnd.toFixed(2)}, ${sEnd.toFixed(2)}]);`);
    lines.push(``);
    lines.push(`      // 2. Transición de Desenfoque de Foco Rack`);
    lines.push(`      var rackBlur = ${layerVar}.property("Effects").addProperty("ADBE Gaussian Blur");`);
    lines.push(`      if (rackBlur) {`);
    lines.push(`        rackBlur.property("Repeat Edge Pixels").setValue(true);`);
    lines.push(`        var blProp = rackBlur.property("Blurriness");`);
    lines.push(`        blProp.setValueAtTime(${tStart.toFixed(4)}, ${blurStart.toFixed(1)});`);
    lines.push(`        blProp.setValueAtTime(${tEnd.toFixed(4)}, ${blurEnd.toFixed(1)});`);
    lines.push(`      }`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in LensBreathingEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
